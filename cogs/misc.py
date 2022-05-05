import discord
import platform
import pygit2
import itertools
import datetime
from discord import Interaction
from discord import ui, Object
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt, utcnow
from utils.checks import cooldown_for_everyone_but_me

from utils import Cog
from utils.emojis import latte_emoji

default_guild = Object(id=840379510704046151)

def format_commit(commit) -> str:
    short, _, _ = commit.message.partition('\n')
    short = short[0:40] + '...' if len(short) > 40 else short
    short_sha2 = commit.hex[0:6]
    commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
    commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(commit_tz)
    offset = format_dt(commit_time, style='R')
    return f'[`{short_sha2}`](https://github.com/staciax/Latte_bot/commits/{commit.hex}) {short} ({offset})'

def get_latest_commits(limit: int = 5) -> str:
    repo = pygit2.Repository('./.git')
    commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), limit))
    return '\n'.join(format_commit(c) for c in commits)

class Misc(Cog):
    """Miscellaneous commands"""

    @property
    def display_emoji(self) -> discord.Emoji:
        return self.bot.get_emoji(914142887854358588)
    
    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def ping(self, interaction: Interaction) -> None:
        """Show Bot latency."""
        latency = self.bot.latency * 1000
        embed = discord.Embed(color=self.bot.theme)
        embed.add_field(name=f"{latte_emoji('cursor')} Latency", value=f"```nim\n{round(latency)} ms```")
        embed.set_footer(text=f'{self.bot.user.name} | v{self.bot.bot_version}')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='invite')
    @app_commands.checks.bot_has_permissions(embed_links=True, send_messages=True)
    async def invite(self, interaction: Interaction) -> None:
        """Add the Latte bot to your server"""

        invite_url = self.bot.invite_url
        bot_name = self.bot.user.name
        bot_avatar = self.bot.user.avatar
        servers_count = len(self.bot.guilds)
        # users_count = len(self.bot.users)
        users_count = sum(g.member_count for g in self.bot.guilds)
        support_url = self.bot.latte_supprt_url
        invite_emoji = self.bot.get_emoji(966016885445492757)

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
    @app_commands.checks.bot_has_permissions(embed_links=True, send_messages=True)
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def about(self, interaction: Interaction) -> None:
        """Shows basic information about the bot."""

        owner_bot = await self.bot.stacia
        bot_name = self.bot.user.name
        bot_version = self.bot.bot_version
        server_count = len(self.bot.guilds)
        # member_count = len(self.bot.get_all_members())
        member_count = 0
        for guild in self.bot.guilds: member_count += guild.member_count
        total_commands = len(self.bot.tree.get_commands())
        # total_commands = len(self.bot.tree._get_all_commands(guild=discord.Object(id=default_guild)))

        #emoji
        latte_icon = latte_emoji('latte_icon')
        member_emoji = latte_emoji('member')
        bot_cmd = latte_emoji('bot_commands')
        python_icon = latte_emoji('python')
        dpy_icon = latte_emoji('dpy')
        cursor_emoji = latte_emoji('cursor')

        embed = discord.Embed(color=self.bot.theme)
        embed.set_author(name=f"About Me", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=owner_bot.avatar)
        embed.add_field(
            name='ᴀʙᴏᴜᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ:',
            value=f"ᴏᴡɴᴇʀ: [{owner_bot}](https://discord.com/users/{owner_bot.id}, '┐(・。・┐) ♪')",
            inline=False
        )
        embed.add_field(
            name='ʟᴀᴛᴇꜱᴛ ᴜᴘᴅᴀᴛᴇꜱ:',
            value=get_latest_commits(5),
            inline=False
        )
        embed.add_field(
            name='ꜱᴛᴀᴛꜱ:',
            value=f"{cursor_emoji} ʟɪɴᴇ ᴄᴏᴜɴᴛ: `{self.bot.line_count}`\n{latte_icon} ꜱᴇʀᴠᴇʀꜱ: `{server_count}`\n{member_emoji} ᴜꜱᴇʀꜱ: `{member_count}`\n{bot_cmd} ᴄᴏᴍᴍᴀɴᴅꜱ: `{total_commands}`", 
            inline=False
        )
        embed.add_field(
            name='ʙᴏᴛ ɪɴꜰᴏ:',
            value=f"{latte_icon} ʟᴀᴛᴛᴇ_ʙᴏᴛ: `{bot_version}`\n{python_icon} ᴘʏᴛʜᴏɴ: `{platform.python_version()}`\n{dpy_icon} ᴅɪꜱᴄᴏʀᴅ.ᴘʏ: `{discord.__version__}`",
            inline=False
        )
        embed.add_field(name='ᴜᴘᴛɪᴍᴇ:', value=f"{self.bot.launch_time}", inline=False)

        # emoji 
        staciax_emoji = self.bot.get_emoji(941961591610556457)
        latte_support_emoji = self.bot.get_emoji(941971854728511529)

        owner_ = owner_bot.name, f'https://discord.com/users/{owner_bot.id}', staciax_emoji
        server_ = 'ꜱᴇʀᴠᴇʀ', self.bot.latte_supprt_url, latte_support_emoji

        view = ui.View()
        view.add_item(ui.Button(label=owner_[0], emoji=owner_[2], url=owner_[1]))
        view.add_item(ui.Button(label=server_[0], emoji=server_[2], url=server_[1]))
    
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='support')
    @app_commands.checks.bot_has_permissions(embed_links=True, send_messages=True)
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def support(self, interaction: Interaction) -> None:
        """Sends the support server of the bot."""

        owner_bot = await self.bot.stacia
        bot_avatar = self.bot.user.avatar
        support_url = self.bot.latte_supprt_url
        support_guild = self.bot.latte_support
        support_guild_icon = support_guild.icon
        support_emoji = self.bot.get_emoji(941971854728511529)
        stacia_emoji = self.bot.get_emoji(948850880617250837)

        embed = discord.Embed(color=self.bot.theme)
        embed.description = f'ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀꜱ: {support_guild.member_count}'
        embed.set_author(name=f"ꜱᴜᴘᴘᴏʀᴛ ꜱᴇʀᴠᴇʀ:", icon_url=bot_avatar, url=support_url)
        embed.set_thumbnail(url=support_guild_icon)

        #support@lattebot.xyz

        view = ui.View()
        view.add_item(ui.Button(label='ᴄʟɪᴄᴋ ᴛᴏ ᴊᴏɪɴ', url=support_url, emoji=support_emoji))
        view.add_item(ui.Button(label='ᴅᴇᴠ', url=f'https://discord.com/users/{owner_bot.id}', emoji=stacia_emoji))

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='report')
    @app_commands.describe(message='Input report message"')
    @app_commands.checks.bot_has_permissions(embed_links=True, send_messages=True)
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
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

async def setup(bot):
    await bot.add_cog(Misc(bot))