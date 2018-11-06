import discord, traceback, aiosqlite, asyncio, sqlite3, random, aiohttp, sys, os, psutil, random
from datetime import datetime, timedelta
from time import time
from pathlib import Path
from discord.ext import commands
from settings import config, constant

#generates discord.Embed objects
def embed_gen(description):
    """generates a discord.Embed object"""
    if type(description) is not None and type(description) != str:
        description = "GenError: description must be NoneType or String"
    return discord.Embed(color=config.color, description=description).set_author(name=config.bot_name, icon_url=config.avatar_url)

#prefix memory on-boot load
async def prefix_bootup():
    async with aiosqlite.connect('{}.db'.format(config.database)) as cur:
        await cur.execute('CREATE TABLE IF NOT EXISTS PrefixList(ID, Prefix)')
        IDQuery = await cur.execute('SELECT ID FROM PrefixList')
        ID = await IDQuery.fetchall()
        PrefixQuery = await cur.execute('SELECT Prefix FROM PrefixList')
        Prefix = await PrefixQuery.fetchall()
        for _ in range(len(ID)):
            constant.prefix_dict[ID[_][0]] = Prefix[_][0]

#on_message prefix check
async def get_prefix(bot, message):
    """gets the server prefix (allows custom prefixes)"""
    try:
        return constant.prefix_dict.get(message.guild.id, config.prefix)
    except TypeError and ValueError and KeyError and AttributeError:
        return config.prefix

#generates a discord bot object
bot = commands.AutoShardedBot(command_prefix=get_prefix)

#loads discord bot cogs
async def load_cog():
    """loads all cogs in the cogs folder onto the commission bot"""
    cog_dir = Path('./cogs')
    cog_dir.mkdir(exist_ok=True)
    for ex in cog_dir.iterdir():
        if ex.suffix == '.py':
            path = '.'.join(ex.with_suffix('').parts)
            bot.load_extension(path)

#displays information about the command being executed
@bot.event
async def on_command_completion(ctx):
    var = "{} used {} at {:%Y-%b-%d %H:%M}".format(ctx.author, ctx.command.name, datetime.now())

#loads cogs and prints a bot is connected notification
@bot.event
async def on_ready():
    print("{} has successfully logged into discord at {:%Y-%b-%d %H:%M}".format(config.bot_name, datetime.now()))
    await prefix_bootup()
    await load_cog()

#displays the statistics for the discord bot
@bot.command()
async def statistics(ctx):
    """displays the current servers and users the bot is connected to"""
    await ctx.send(embed=embed_gen('Bot is in {} Servers\nConnected to {} Users'.format(len(bot.guilds), len(bot.users))))

#sets the discord server(s) prefix (requires Administrator)
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def prefix(ctx, newprefix: str):
    """sets the discord server(s) prefix (requires Administrator)"""
    async with aiosqlite.connect('{}.db'.format(config.database)) as cur:
        if newprefix in config.allowed_prefix:
            if ctx.guild.id in list(constant.prefix_dict):
                await cur.execute("UPDATE PrefixList SET Prefix=? WHERE ID=?", (newprefix, ctx.guild.id,))
            else:
                await cur.execute("INSERT INTO PrefixList(ID, Prefix) VALUES(?, ?)",(ctx.guild.id, newprefix,))
            constant.prefix_dict[ctx.guild.id] = newprefix
            await cur.commit()
            await ctx.send(embed=embed_gen("{} has successfully set {}'s prefix to {}".format(ctx.author.name, ctx.guild.name, newprefix)))
        else:
            prefix_format = ""
            for item in config.allowed_prefix:
                prefix_format += "\n{}".format(item)
            await ctx.send(embed=embed_gen("{} is not a allowed prefix {}!\n```Valid Prefixes{}```".format(newprefix, ctx.author.name, prefix_format)))

#Connects to the Bot and Runs
bot.run(config.token)