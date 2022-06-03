import os
import discord
import platform
import pygit2
import itertools
import datetime
import psutil
from discord import ui, Object, Interaction, app_commands
from discord.utils import format_dt, utcnow
from discord.app_commands.checks import dynamic_cooldown
from utils.checks import cooldown_5s

from utils import Cog
from utils.emojis import LATTE_EMOJI

default_guild = Object(id=840379510704046151)

def format_commit(commit) -> str:
    short, _, _ = commit.message.partition('\n')
    short = short[0:40] + '...' if len(short) > 40 else short
    short_sha2 = commit.hex[0:6]
    commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
    commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(commit_tz)
    offset = format_dt(commit_time, style='R')
    return f'[`{short_sha2}`](https://github.com/staciax/lattebot/commits/{commit.hex}) {short} ({offset})'

def get_latest_commits(limit: int = 5) -> str:
    repo = pygit2.Repository('./.git')
    commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), limit))
    return '\n'.join(format_commit(c) for c in commits)

class Misc(Cog):
    """Miscellaneous commands"""

    process = psutil.Process()

    @property
    def display_emoji(self) -> discord.Emoji:
        return str(LATTE_EMOJI.MISC)
        # return self.bot.get_emoji(914142887854358588)
    
    @app_commands.command()
    @dynamic_cooldown(cooldown_5s)
    async def ping(self, interaction: Interaction) -> None:
        """Show Bot latency."""
        latency = self.bot.latency * 1000
        embed = discord.Embed(color=self.bot.theme)
        embed.add_field(name=f"{LATTE_EMOJI.CURSOR} Latency", value=f"```nim\n{round(latency)} ms```")
        embed.set_footer(text=f'{self.bot.user.name} | v{self.bot.bot_version}', icon_url=self.bot.user.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='invite')
    async def invite(self, interaction: Interaction) -> None:
        """Add the Latte bot to your server"""

        invite_url = self.bot.invite_url
        bot_name = self.bot.user.name
        bot_avatar = self.bot.user.avatar
        servers_count = len(self.bot.guilds)
        # users_count = len(self.bot.users)
        users_count = sum(g.member_count for g in self.bot.guilds)
        support_url = self.bot.latte_supprt_url
        invite_emoji = str(LATTE_EMOJI.MOON)

        view = ui.View()
        view.add_item(ui.Button(label='ɪɴᴠɪᴛᴇ ᴍᴇ', url=invite_url, emoji=invite_emoji))
        # view.add_item(ui.Button(label='ꜱᴜᴘᴘᴏʀᴛ ꜱᴇʀᴠᴇʀ', url=support_url))

        embed = discord.Embed(color=self.bot.theme)
        # embed.add_field(name='ᴛᴏᴛᴀʟ ꜱᴇʀᴠᴇʀꜱ:',value=servers_count)
        # embed.add_field(name='ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ:',value=users_count)
        embed.set_author(name=f"{bot_name} ɪɴᴠɪᴛᴇ", url=invite_url, icon_url=bot_avatar)
        embed.set_thumbnail(url=bot_avatar)
        
        embed.set_footer(text=f'{self.bot.user.name} | v{self.bot.bot_version}')
        
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name='about')
    @dynamic_cooldown(cooldown_5s)
    async def about(self, interaction: Interaction) -> None:
        """Shows basic information about the bot."""

        owner_bot = await self.bot.stacia
        bot_version = self.bot.bot_version
        server_count = len(self.bot.guilds)
        # member_count = len(self.bot.get_all_members())
        channel_count = len(list(self.bot.get_all_channels()))
        member_count = 0
        for guild in self.bot.guilds: member_count += guild.member_count
        total_commands = len(self.bot.tree.get_commands())
        # total_commands = len(self.bot.tree._get_all_commands(guild=discord.Object(id=default_guild)))
        memory_usage = self.process.memory_full_info().uss / 1024 / 1024

        embed = discord.Embed(color=self.bot.theme, timestamp=discord.utils.utcnow())
        embed.set_author(name=f"About Me", icon_url=self.bot.user.avatar)
        # embed.set_thumbnail(url=owner_bot.avatar)
        # embed.add_field(
        #     name='ᴀʙᴏᴜᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ:',
        #     value=f"ᴏᴡɴᴇʀ: [{owner_bot}](https://discord.com/users/{owner_bot.id}, '┐(・。・┐) ♪')",
        #     inline=False
        # )
        embed.add_field(name='ʟᴀᴛᴇꜱᴛ ᴜᴘᴅᴀᴛᴇꜱ:', value=get_latest_commits(5), inline=False)
        embed.add_field(
            name='ꜱᴛᴀᴛꜱ:',
            value=f"{LATTE_EMOJI.LATTE_ICON} ꜱᴇʀᴠᴇʀꜱ: `{server_count}`\n{LATTE_EMOJI.MEMBER} ᴜꜱᴇʀꜱ: `{member_count}`\n{LATTE_EMOJI.BOT_COMMANDS} ᴄᴏᴍᴍᴀɴᴅꜱ: `{total_commands}`\n{LATTE_EMOJI.CHANNEL} ᴄʜᴀɴɴᴇʟ: `{channel_count}`", 
            inline=True
        )
        embed.add_field(
            name='ʙᴏᴛ ɪɴꜰᴏ:',
            value=f"{LATTE_EMOJI.CURSOR} ʟɪɴᴇ ᴄᴏᴜɴᴛ: `{(self.bot.line_count('.') + self.bot.line_count('ext/valorant'))}`\n{LATTE_EMOJI.LATTE_ICON} ʟᴀᴛᴛᴇ_ʙᴏᴛ: `{bot_version}`\n{LATTE_EMOJI.PYTHON} ᴘʏᴛʜᴏɴ: `{platform.python_version()}`\n{LATTE_EMOJI.DPY} ᴅɪꜱᴄᴏʀᴅ.ᴘʏ: `{discord.__version__}`",
            inline=True
        )
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.add_field(name='ᴘʀᴏᴄᴇꜱꜱ:', value=f"ᴏꜱ: `{platform.system()}`\nᴄᴘᴜ ᴜꜱᴀɢᴇ: `{psutil.cpu_percent()}%`\nᴍᴇᴍᴏʀʏ ᴜꜱᴀɢᴇ: `{memory_usage:.2f} MB`", inline=True)
        embed.add_field(name='ᴜᴘᴛɪᴍᴇ:', value=f"{self.bot.launch_time}", inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)

        embed.set_footer(text='ᴍᴀᴅᴇ ʙʏ ꜱᴛᴀᴄɪᴀ.#7475', icon_url=owner_bot.avatar)

        # emoji 
        staciax_emoji = str(LATTE_EMOJI.STACIA)
        latte_support_emoji = str(LATTE_EMOJI.LATTE_SUPPORT)

        owner_ = owner_bot.name, f'https://discord.com/users/{owner_bot.id}', staciax_emoji
        server_ = 'ꜱᴇʀᴠᴇʀ', self.bot.latte_supprt_url, latte_support_emoji

        view = ui.View()
        view.add_item(ui.Button(label=owner_[0], emoji=owner_[2], url=owner_[1]))
        # view.add_item(ui.Button(label=server_[0], emoji=server_[2], url=server_[1]))
    
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='support')
    @dynamic_cooldown(cooldown_5s)
    async def support(self, interaction: Interaction) -> None:
        """Sends the support server of the bot."""

        owner_bot = await self.bot.stacia
        support_guild = self.bot.latte_support

        embed = discord.Embed(color=self.bot.theme)
        embed.description = f'ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀꜱ: {support_guild.member_count}'
        embed.set_author(name=f"ꜱᴜᴘᴘᴏʀᴛ ꜱᴇʀᴠᴇʀ:", icon_url=self.bot.user.avatar, url=self.bot.latte_supprt_url)
        embed.set_thumbnail(url=support_guild.icon)

        #support@lattebot.xyz

        view = ui.View()
        view.add_item(ui.Button(label='ᴄʟɪᴄᴋ ᴛᴏ ᴊᴏɪɴ', url= self.bot.latte_supprt_url, emoji=str(LATTE_EMOJI.LATTE_SUPPORT)))
        view.add_item(ui.Button(label='ᴅᴇᴠ', url=f'https://discord.com/users/{owner_bot.id}', emoji=str(LATTE_EMOJI.STACIA)))

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='report')
    @app_commands.describe(message='Input report message"')
    @dynamic_cooldown(cooldown_5s)
    async def report(self, interaction: Interaction, message: str) -> None:
        """Report to owner bot"""

        if len(message) >= 2000:
            raise RuntimeError('Report message is too long.')

        await interaction.response.defer(ephemeral=True)
        
        user = interaction.user
        guild = interaction.guild
        
        embed = discord.Embed(
            description = '`' * 3 + f"{message}" + '`' * 3,
            color=self.bot.theme,
            timestamp=utcnow()
        )
        embed.set_author(name=f'{guild.name} | Report', icon_url= interaction.guild.icon)
        embed.set_footer(text=f"{user}", icon_url=user.display_avatar)      

        try:
            owner = await self.bot.stacia
            await owner.send(embed=embed)
        except (discord.HTTPException, discord.Forbidden):
            raise RuntimeError(f"Failed to send message to owner bot")

        embed = discord.Embed(
            description='Thanks you, Message successfully sent! <3',
            color=self.bot.theme,
            timestamp=utcnow()
        )
        await interaction.followup.send(embed=embed)

    # @app_commands.command(name='donate')
    # @app_commands.checks.bot_has_permissions(embed_links=True, send_messages=True)
    # @dynamic_cooldown(cooldown_5s)
    # async def donate(self, interaction: Interaction) -> None:
        
    #     tipme_url = 'https://tipme.in.th/renlyx'
    #     kofi_irl = 'https://ko-fi.com/staciax'

        

async def setup(bot):
    await bot.add_cog(Misc(bot))