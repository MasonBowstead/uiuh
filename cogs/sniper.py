import discord, traceback, aiosqlite, asyncio, sqlite3, random, aiohttp, sys, os, psutil, random, youtube_dl
from datetime import datetime, timedelta
from time import time
from settings import config, constant
from discord.ext import commands
from io import BytesIO
from PIL import Image

ydl_opts = { #Settings for YouTubeDL (Best Audio)
    'format': 'bestaudio/best',
    'audioformat': 'mp3',
    'outtmpl': './soundtrack/%(title)s-%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
button = [ '⏮', '⬅', '➡', '⏭', '⏹'] #Don't Touch!
button_command = {'⏮': 0, '⬅': -1, '➡': +1, '⏭': 4, '⏹': False} #Don't Touch!
color_choice = [discord.Colour.red(), discord.Colour.magenta(), discord.Colour.orange(), discord.Colour.gold()]

class OctoSniper:
    """OctoSniper Sniping Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.CanExist = True
        self.GuildObject = self.bot.get_guild(508317163895914506) #Server Integer in Parenthesis
        self.ChannelObject = self.GuildObject.get_channel(509104650201595906) #Channel Integer in Parenthesis
        self.VoiceChannelObject = self.GuildObject.get_channel(509126572771377162) #VoiceChannel Integer in Parenthesis
        self.role = discord.utils.get(self.GuildObject.roles, name="Snipe Announcement")
        self.sniperole = discord.utils.get(self.GuildObject.roles, name="Snipe Announcement")
        self.bot.remove_command('help') #Removes the Specified "Commands Bot" Commands
        self.voi_conn = False
        self.is_running = False

    #generates discord.Embed objects
    def embed_gen(self, description=None):
        """generates a discord.Embed object"""
        return discord.Embed(color=discord.Colour.blue(), description=description)

    #on_message prefix check
    async def get_prefix(self, ctx):
        """gets the server prefix (allows custom prefixes)"""
        try:
            return constant.prefix_dict.get(ctx.guild.id, config.prefix[0])
        except TypeError and ValueError and KeyError and AttributeError:
            return config.prefix[0]

    @commands.command(description="Enables and Starts Snipes (Requires Manage Webhooks)", brief="///snipestart")
    @commands.has_permissions(manage_webhooks=True)
    async def snipestart(self, ctx):
        if self.CanExist is True:
            self.CanExist = False
        self.CanExist = True
        msg = "You cannot run Snipes if it is already Running!"
        if self.is_running is False:
            await self.sniper()
            msg = "Enabled Snipes!"
        await ctx.send(embed=self.embed_gen(msg))

    @commands.command(description="Disables Snipes (Requires Manage Webhooks)", brief="///snipestop")
    @commands.has_permissions(manage_webhooks=True)
    async def snipestop(self, ctx):
        if self.is_running is True:
            if self.CanExist is False:
                msg = "Please wait for the current Snipes to stop!"
            else:
                self.CanExist = False
                msg= "Disabled Snipes!"
        else:
            msg = "No Snipes Running! Enable with snipestart"
        await ctx.send(embed=self.embed_gen(msg))

    @commands.command(description="Announces a Snipe", brief="///announce Snipers r happenin!!!")
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx, *, message):
        await ctx.send(embed=self.embed_gen('**VS** {}\n{}'.format(self.sniperole.mention, message)))

    async def sniper(self):
        "Forever Loops OctoSniper-Snipes"
        ###Commission Block-Base###
        def check(message):
            if message.author.bot is False and len(message.content) == 3 and message.channel == self.ChannelObject:
                return True
        if self.voi_conn is False:
            self.voi_conn = await self.VoiceChannelObject.connect()
        while self.CanExist is True:
            if self.is_running is False:
                await self.ChannelObject.set_permissions(target=self.role, send_messages=False)
                self.is_running = True
                snipe_entry = {}
                await self.ChannelObject.send(self.sniperole.mention, embed=discord.Embed(color=random.choice(color_choice)).add_field(name='Incoming Snipe!', value='- A Snipe match is starting soon.\n- Join the voice chat for Voice-Updates!', inline=False).set_author(name=self.GuildObject.name, icon_url=config.avatar_url))
                await asyncio.sleep(56)
                self.voi_conn.play(discord.FFmpegPCMAudio('./FortniteAudio.mp3'))
                await asyncio.sleep(2)
                timer = time()
                await self.ChannelObject.set_permissions(target=self.role, send_messages=True)
                await self.ChannelObject.send(embed=discord.Embed(color=random.choice(color_choice)).add_field(name='Accepting Server Codes', value='Please Type the Last 3 Digits of your Server Identifier', inline=True).set_author(name=self.GuildObject.name, icon_url=config.avatar_url).set_image(url='https://cdn.discordapp.com/attachments/501741105667244057/502525070472773639/ID_Example.jpg'))
                msg = await self.ChannelObject.send(embed=discord.Embed(color=random.choice(color_choice), description='**Current Servers**').set_author(name=self.GuildObject.name, icon_url=config.avatar_url))
                while int(time() - timer) < 30:
                    try:
                        message = await self.bot.wait_for('message', timeout=1, check=check)
                        for item in list(snipe_entry):
                            if message.author in snipe_entry[item]:
                                snipe_entry[item].remove(message.author)
                                if len(snipe_entry[item]) == 0:
                                    del snipe_entry[item]
                        msg_check = snipe_entry.get(message.content, None)
                        if msg_check is not None:
                            snipe_entry[message.content].append(message.author)
                        else:
                            snipe_entry[message.content] = [message.author]
                        await message.delete()
                        embed = discord.Embed(color=random.choice(color_choice), title='**Current Servers**').set_author(name=self.GuildObject.name, icon_url=config.avatar_url)
                        for item in list(snipe_entry):
                            value = ''
                            header = 'ID {}: ({} User)'.format(item, len(snipe_entry[item]))
                            for item_list in snipe_entry[item]:
                                value += '\n{}'.format(item_list.mention)
                            embed.add_field(name=header, value=value, inline=True)
                        await msg.edit(embed=embed)
                    except asyncio.TimeoutError:
                        pass
                await msg.edit(embed=embed.set_footer(text='No Longer Accepting Snipe Codes!'))
                await self.ChannelObject.set_permissions(target=self.role, send_messages=False)
                self.is_running = False
                await asyncio.sleep(1800)
        ###Commission Block-End###

    async def button_event(self, ctx, CMDPG, MSG=None, Index:int=0, reaction:str=None, V:str=''):
        try:
            event = button_command[reaction.emoji]
        except:
            event = 0
        if event is not False:
            NewIndex = Index + event
            if NewIndex < len(CMDPG):
                NewIndex = 4
            if NewIndex > len(CMDPG) - 1:
                NewIndex = 0
            if event == 0:
                NewIndex = 0
            for item in CMDPG[NewIndex]:
                if item.hidden is not True:
                    V += '`{}{} - {}`\n'.format(await self.get_prefix(ctx), item.name, item.description)
            embed = self.embed_gen(V).set_author(name="{} - Help Command Page {}/{}".format(config.bot_name, NewIndex + 1, len(CMDPG))).set_footer(text="The Current Prefix is {}".format(await self.get_prefix(ctx)))
            if MSG is None:
                MSG = await ctx.send(embed=embed)
            else:
                await MSG.edit(embed=embed)
            for bttn in button:
                await MSG.add_reaction(bttn)
            return MSG
        else:
            await MSG.delete()

    #help command
    @commands.command(hidden=True, pass_context=True, name='help', description="Displays Cog and Command Information")
    async def help(self, ctx):
        def check(reaction, user):
            return reaction.emoji in button and user.id == ctx.author.id
        Index, CMDPG, V = 0, [], ''
        for cog in self.bot.cogs:
            CMDPG.append(list(self.bot.get_cog_commands(cog)))
        MSG = await self.button_event(ctx, CMDPG)
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
                await self.button_event(ctx, CMDPG, MSG, Index, reaction)
            except asyncio.TimeoutError:
                break

def setup(bot):
    bot.add_cog(OctoSniper(bot))