import discord
import random
import json
import os
import asyncio
import pytz
import datetime
from datetime import datetime
from time import strftime
from discord.utils import get
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='~', intents=intents)
client.remove_command('help')


@client.event
async def on_ready():
	activity = discord.Game(name="fogc.ddns.net", type=3)
	await client.change_presence(status=discord.Status.dnd, activity=activity)
	print('Bot is up and running :)'.format(client))


@client.command()
async def suggest(ctx, command, *, description):
	embed = discord.Embed(
	    title='Suggestion',
	    description=
	    f'Suggested by: {ctx.author.mention}\n \nSuggestion: **{command}**',
	    color=discord.Color.green())
	embed.add_field(name='Suggestion Desc:', value=description)
	channel = ctx.guild.get_channel(535969988427776040)
	msg = await channel.send(embed=embed)
	await msg.add_reaction('👍')
	await msg.add_reaction('👎')
	await ctx.send("Thank you for your suggestion {}! It will be put in <#535969988427776040>.".format(ctx.author.mention), delete_after=15)
	await ctx.message.delete()

#The code below makes tickets.
@client.command()
async def new(ctx, *, args=None):

	await client.wait_until_ready()

	if args == None:
		message_content = "Please wait, we will be with you shortly!"

	else:
		message_content = "".join(args)

	with open("data.json") as f:
		data = json.load(f)

	ticket_number = int(data["ticket-counter"])
	ticket_number += 1

	category_channel = ctx.guild.get_channel(809637607260553217)
	ticket_channel = await category_channel.create_text_channel(
	    "ticket-{}".format(ticket_number))
	await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id),
	                                     send_messages=False,
	                                     read_messages=False)

	for role_id in data["valid-roles"]:
		role = ctx.guild.get_role(role_id)

		await ticket_channel.set_permissions(role,
		                                     send_messages=True,
		                                     read_messages=True,
		                                     add_reactions=True,
		                                     embed_links=True,
		                                     attach_files=True,
		                                     read_message_history=True,
		                                     external_emojis=True)

	await ticket_channel.set_permissions(ctx.author,
	                                     send_messages=True,
	                                     read_messages=True,
	                                     add_reactions=True,
	                                     embed_links=True,
	                                     attach_files=True,
	                                     read_message_history=True,
	                                     external_emojis=True)

	em = discord.Embed(title="New ticket from {}#{}".format(
	    ctx.author.name, ctx.author.discriminator),
	                   description="{}".format(message_content),
	                   color=0x00a8ff)

	m = await ticket_channel.send(embed=em)
	await m.add_reaction("✅")

	staff_role = discord.utils.get(ctx.guild.roles, name="STAFF")
	admin_role = discord.utils.get(ctx.guild.roles, name="ADMINISTRATION")
	await ticket_channel.send(
	    f'Support will be with you shortly, {ctx.author.mention}\n \n`Tags: \n{staff_role.mention} \n{admin_role.mention}`'
	)

	pinged_msg_content = ""
	non_mentionable_roles = []

	if data["pinged-roles"] != []:

		for role_id in data["pinged-roles"]:
			role = ctx.guild.get_role(role_id)

			pinged_msg_content += role.mention
			pinged_msg_content += " "

			if role.mentionable:
				pass
			else:
				await role.edit(mentionable=True)
				non_mentionable_roles.append(role)

		await ticket_channel.send(pinged_msg_content)

		for role in non_mentionable_roles:
			await role.edit(mentionable=False)

	data["ticket-channel-ids"].append(ticket_channel.id)

	data["ticket-counter"] = int(ticket_number)
	with open("data.json", 'w') as f:
		json.dump(data, f)

	created_em = discord.Embed(
	    title="FOGC Tickets",
	    description="Your ticket has been created at {}".format(
	        ticket_channel.mention),
	    color=0x00a8ff)

	await ctx.send(embed=created_em, delete_after=10)
	await ctx.message.delete()

@client.command()
async def close(ctx):
	with open('data.json') as f:
		data = json.load(f)

	if ctx.channel.id in data["ticket-channel-ids"]:

		channel_id = ctx.channel.id

		def check(message):
			return message.author == ctx.author and message.channel == ctx.channel and message.content.lower(
			) == "close"

		try:

			em = discord.Embed(
			    title="FOGC Tickets",
			    description=
			    "Are you sure you want to close this ticket? Reply with `close` if you are sure.",
			    color=0x00a8ff)

			await ctx.send(embed=em)
			await client.wait_for('message', check=check, timeout=60)
			await ctx.channel.delete()

			index = data["ticket-channel-ids"].index(channel_id)
			del data["ticket-channel-ids"][index]

			with open('data.json', 'w') as f:
				json.dump(data, f)

		except asyncio.TimeoutError:
			em = discord.Embed(
			    title="FOGC Tickets",
			    description=
			    "You have run out of time to close this ticket. Please run the command again.",
			    color=0x00a8ff)
			await ctx.send(embed=em)

@client.command()
async def addaccess(ctx, role_id=None):

	with open('data.json') as f:
		data = json.load(f)

	valid_user = False

	for role_id in data["verified-roles"]:
		try:
			if ctx.guild.get_role(role_id) in ctx.author.roles:
				valid_user = True
		except:
			pass

	if valid_user or ctx.author.guild_permissions.administrator:
		role_id = int(role_id)

		if role_id not in data["valid-roles"]:

			try:
				role = ctx.guild.get_role(role_id)

				with open("data.json") as f:
					data = json.load(f)

				data["valid-roles"].append(role_id)

				with open('data.json', 'w') as f:
					json.dump(data, f)

				em = discord.Embed(
				    title="FOGC Tickets",
				    description=
				    "You have successfully added `{}` to the list of roles with access to tickets."
				    .format(role.name),
				    color=0x00a8ff)

				await ctx.send(embed=em)

			except:
				em = discord.Embed(
				    title="FOGC Tickets",
				    description=
				    "That isn't a valid role ID. Please try again with a valid role ID."
				)
				await ctx.send(embed=em)

		else:
			em = discord.Embed(
			    title="FOGC Tickets",
			    description="That role already has access to tickets!",
			    color=0x00a8ff)
			await ctx.send(embed=em)

	else:
		em = discord.Embed(
		    title="FOGC Tickets",
		    description="Sorry, you don't have permission to run that command.",
		    color=0x00a8ff)
		await ctx.send(embed=em)


@client.command()
async def delaccess(ctx, role_id=None):
	with open('data.json') as f:
		data = json.load(f)

	valid_user = False

	for role_id in data["verified-roles"]:
		try:
			if ctx.guild.get_role(role_id) in ctx.author.roles:
				valid_user = True
		except:
			pass

	if valid_user or ctx.author.guild_permissions.administrator:

		try:
			role_id = int(role_id)
			role = ctx.guild.get_role(role_id)

			with open("data.json") as f:
				data = json.load(f)

			valid_roles = data["valid-roles"]

			if role_id in valid_roles:
				index = valid_roles.index(role_id)

				del valid_roles[index]

				data["valid-roles"] = valid_roles

				with open('data.json', 'w') as f:
					json.dump(data, f)

				em = discord.Embed(
				    title="FOGC Tickets",
				    description=
				    "You have successfully removed `{}` from the list of roles with access to tickets."
				    .format(role.name),
				    color=0x00a8ff)

				await ctx.send(embed=em)

			else:

				em = discord.Embed(
				    title="FOGC Tickets",
				    description=
				    "That role already doesn't have access to tickets!",
				    color=0x00a8ff)
				await ctx.send(embed=em)

		except:
			em = discord.Embed(
			    title="FOGC Tickets",
			    description=
			    "That isn't a valid role ID. Please try again with a valid role ID."
			)
			await ctx.send(embed=em)

	else:
		em = discord.Embed(
		    title="FOGC Tickets",
		    description="Sorry, you don't have permission to run that command.",
		    color=0x00a8ff)
		await ctx.send(embed=em)


@client.command()
async def addpingedrole(ctx, role_id=None):

	with open('data.json') as f:
		data = json.load(f)

	valid_user = False

	for role_id in data["verified-roles"]:
		try:
			if ctx.guild.get_role(role_id) in ctx.author.roles:
				valid_user = True
		except:
			pass

	if valid_user or ctx.author.guild_permissions.administrator:

		role_id = int(role_id)

		if role_id not in data["pinged-roles"]:

			try:
				role = ctx.guild.get_role(role_id)

				with open("data.json") as f:
					data = json.load(f)

				data["pinged-roles"].append(role_id)

				with open('data.json', 'w') as f:
					json.dump(data, f)

				em = discord.Embed(
				    title="FOGC Tickets",
				    description=
				    "You have successfully added `{}` to the list of roles that get pinged when new tickets are created!"
				    .format(role.name),
				    color=0x00a8ff)

				await ctx.send(embed=em)

			except:
				em = discord.Embed(
				    title="FOGC Tickets",
				    description=
				    "That isn't a valid role ID. Please try again with a valid role ID."
				)
				await ctx.send(embed=em)

		else:
			em = discord.Embed(
			    title="FOGC Tickets",
			    description=
			    "That role already receives pings when tickets are created.",
			    color=0x00a8ff)
			await ctx.send(embed=em)

	else:
		em = discord.Embed(
		    title="FOGC Tickets",
		    description="Sorry, you don't have permission to run that command.",
		    color=0x00a8ff)
		await ctx.send(embed=em)


@client.command()
async def delpingedrole(ctx, role_id=None):

	with open('data.json') as f:
		data = json.load(f)

	valid_user = False

	for role_id in data["verified-roles"]:
		try:
			if ctx.guild.get_role(role_id) in ctx.author.roles:
				valid_user = True
		except:
			pass

	if valid_user or ctx.author.guild_permissions.administrator:

		try:
			role_id = int(role_id)
			role = ctx.guild.get_role(role_id)

			with open("data.json") as f:
				data = json.load(f)

			pinged_roles = data["pinged-roles"]

			if role_id in pinged_roles:
				index = pinged_roles.index(role_id)

				del pinged_roles[index]

				data["pinged-roles"] = pinged_roles

				with open('data.json', 'w') as f:
					json.dump(data, f)

				em = discord.Embed(
				    title="FOGC Tickets",
				    description=
				    "You have successfully removed `{}` from the list of roles that get pinged when new tickets are created."
				    .format(role.name),
				    color=0x00a8ff)
				await ctx.send(embed=em)

			else:
				em = discord.Embed(
				    title="FOGC Tickets",
				    description=
				    "That role already isn't getting pinged when new tickets are created!",
				    color=0x00a8ff)
				await ctx.send(embed=em)

		except:
			em = discord.Embed(
			    title="FOGC Tickets",
			    description=
			    "That isn't a valid role ID. Please try again with a valid role ID."
			)
			await ctx.send(embed=em)

	else:
		em = discord.Embed(
		    title="FOGC Tickets",
		    description="Sorry, you don't have permission to run that command.",
		    color=0x00a8ff)
		await ctx.send(embed=em)


@client.command()
@has_permissions(administrator=True)
async def addadminrole(ctx, role_id=None):

	try:
		role_id = int(role_id)
		role = ctx.guild.get_role(role_id)

		with open("data.json") as f:
			data = json.load(f)

		data["verified-roles"].append(role_id)

		with open('data.json', 'w') as f:
			json.dump(data, f)

		em = discord.Embed(
		    title="FOGC Tickets",
		    description=
		    "You have successfully added `{}` to the list of roles that can run admin-level commands!"
		    .format(role.name),
		    color=0x00a8ff)
		await ctx.send(embed=em)

	except:
		em = discord.Embed(
		    title="FOGC Tickets",
		    description=
		    "That isn't a valid role ID. Please try again with a valid role ID."
		)
		await ctx.send(embed=em)


@client.command()
@has_permissions(administrator=True)
async def deladminrole(ctx, role_id=None):
	try:
		role_id = int(role_id)
		role = ctx.guild.get_role(role_id)

		with open("data.json") as f:
			data = json.load(f)

		admin_roles = data["verified-roles"]

		if role_id in admin_roles:
			index = admin_roles.index(role_id)

			del admin_roles[index]

			data["verified-roles"] = admin_roles

			with open('data.json', 'w') as f:
				json.dump(data, f)

			em = discord.Embed(
			    title="FOGC Tickets",
			    description=
			    "You have successfully removed `{}` from the list of roles that get pinged when new tickets are created."
			    .format(role.name),
			    color=0x00a8ff)

			await ctx.send(embed=em)

		else:
			em = discord.Embed(
			    title="FOGC Tickets",
			    description=
			    "That role isn't getting pinged when new tickets are created!",
			    color=0x00a8ff)
			await ctx.send(embed=em)

	except:
		em = discord.Embed(
		    title="FOGC Tickets",
		    description=
		    "That isn't a valid role ID. Please try again with a valid role ID."
		)
		await ctx.send(embed=em)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def clean(ctx, limit: int):
	await ctx.channel.purge(limit=limit + 1)
	await ctx.send('Cleared By: {}'.format(ctx.author.mention), delete_after=2)
	await ctx.message.delete()


@clean.error
async def clear_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You cannot do that!")

client.run('')
