# Standard 
import discord
import re
import asyncio
from discord import Interaction, ui
from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice
from datetime import datetime, timedelta
from typing import Literal, Optional, Any

from contextlib import suppress

# Third
from googletrans import Translator
from discord_together import DiscordTogether

# Local
from utils import Latte_Bot
from utils.context_managers import UserLock
from utils.emojis import LATTE_EMOJI
from utils.checks import cooldown_for_everyone_but_me

activity_list = {
    'Youtube Together': 'youtube',
    'Blazing 8s (OCHO)': 'blazing-8s',
    'Poker Night': 'poker',
    'Sketch Heads': 'doodlecrew',
    'Chess in the Park': 'chess',
    'Betrayal.io': 'betrayal',
    'Letter League': 'letter-league',
    'Word Snack': 'word-snack',
    'Sketch Heads': 'sketch-heads',
    'SpellCast': 'spellcast',
    'Awkword': 'awkword',
    'Checkers in the Park': 'checkers',
    'Land-io': 'land-io',
    'Putt Party': 'putt-party',
    'Fishington.io (Broken)': 'fishing'
}

class Utility(commands.Cog):
    """Some useful commands"""

    def __init__(self, bot: Latte_Bot) -> None:
        self.bot = bot
        self.sleeped.start()

    def cog_unload(self) -> None:
        self.sleeped.cancel()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.togetherControl = await DiscordTogether(self.bot.http.token)

    @tasks.loop(minutes=1)
    async def sleeped(self):
        dt = datetime.utcnow().timestamp()
        with suppress(Exception):
            for key in self.bot.sleeped_users.keys():
                data = self.bot.sleeped_users[key]
                if int(data["time"]) <= int(dt):
                    guild = self.bot.get_guild(data['guild_id'])
                    member = guild.get_member(int(key)) or await guild.fetch_member(int(key))
                    await member.move_to(channel=None)
                    del self.bot.sleeped_users[key]
    
    @sleeped.before_loop
    async def before_sleeped(self):
        await self.bot.wait_until_ready()

    @property
    def display_emoji(self) -> discord.Emoji:
        return str(LATTE_EMOJI.GIFT_BLUE)
        # return self.bot.get_emoji(903339694098628618)

    @app_commands.command()
    @app_commands.choices(activity=[app_commands.Choice(name=name, value=value) for name, value in activity_list.items()])
    @app_commands.describe(activity='Which activity to do in the channel', channel='Which channel to do the activity in')
    @app_commands.checks.bot_has_permissions(create_instant_invite=True)
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def activity(self, interaction: Interaction, activity: str, channel: Optional[discord.VoiceChannel] = None) -> None:
        """Start Discord Together activity"""

        if not interaction.user.voice and channel is None:
            raise RuntimeError('You are not in a voice channel')

        Boosting_required = ['putt-party', 'land-io', 'poker', 'chess', 'checkers', 'blazing-8s', 'letter-league', 'spellcast']
        if activity in Boosting_required and interaction.guild.premium_tier < 1:
            raise RuntimeError('Activity requires server boosting level 1')

        channel = channel or interaction.user.voice.channel

        url = await self.togetherControl.create_link(channel.id, activity, max_age=86400)

        emoji = str(LATTE_EMOJI.YOUTUBE) if activity == 'youtube' else '🎮'
        label = 'Watch Together' if activity == 'youtube' else 'Play Together'
        
        view = ui.View()
        view.add_item(ui.Button(label=label, url=url, emoji=emoji))

        await interaction.response.send_message(f"{url}", view=view)

    # @app_commands.command()
    # @app_commands.describe(reason='The reason of afk.')
    # async def afk(self, interaction: Interaction, reason: str = '...') -> None:
    #     """Set your status to AFK."""
        
    #     member = interaction.user
        
    #     if member.id in self.bot.afk_user.keys():
    #         raise RuntimeError(f"**You already have afk status**\n*reason:* {self.bot.afk_user[member.id]['reason']}")

    #     embed = discord.Embed(description=f'I have set your afk: {reason}', color=self.bot.theme)

    #     if len(reason) > 100:
    #         raise RuntimeError("**reason** is a maximum of 100 characters.")
        
    #     self.bot.afk_user[member.id] = {"reason": reason, "name": member.display_name}
        
    #     # try:
    #     #     await member.edit(nick=f'[AFK] {member.display_name}')
    #     # except:
    #     #     pass

    #     await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.describe(site='URL of the site.')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def screenshot(self, interaction: Interaction, site: str) -> None:
        """Take a screenshot from the specified url."""
        
        URL_REGEX = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        site = site.strip('<>')
        if not re.fullmatch(URL_REGEX, site):
            raise RuntimeError("Invalid URL! Try to give url in this format > `http://url.com`")

        embed = discord.Embed(title=f'{site}', color=self.bot.theme)
        embed.set_image(url=(f"https://image.thum.io/get/width/1920/crop/675/maxAge/1/noanimate/{site}"))
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command()
    @app_commands.describe(to_lang='Language to translate to.', source='Source content language.')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def translate(self, interaction: Interaction, to_lang:str, source:str) -> None:
        """Translate your message"""
        
        await interaction.response.defer()
        
        if len(source) > 1000:
            raise RuntimeError(f"The message character a maximum of 1000 characters.")
    
        translator = Translator()
        try:
            a = translator.detect(str(source))
        except:
            raise RuntimeError(f"**{to_lang}** <- This language is not found")

        try:
            result =  translator.translate(f'{source}' , dest=f'{to_lang}')
            b = translator.detect(str(result.text))
        except:
            raise RuntimeError("An unknown error occurred, sorry")

        embed = discord.Embed(color=self.bot.theme)
        embed.set_author(name="Translate" , icon_url="https://i.imgur.com/UV2H9KU.png")
        embed.add_field(name=f"Original ({str(a.lang)})", value=f"```{source}```", inline=False)
        embed.add_field(name=f"Translated ({str(b.lang)})", value=f"```{result.text}```", inline=False)
        
        await interaction.followup.send(embed=embed)
                

    # sleep = app_commands.Group(name='sleep', description='sleep timer commands', guild_ids=[840379510704046151])

    # @sleep.command(name='timer')
    # @app_commands.describe(time='time in seconds')
    # async def sleep_timer(self, interaction: Interaction, time: int) -> None:
    #     """Sleep timer."""
        
    #     member = interaction.user
    #     guild = interaction.guild

    #     await self.bot.check_user_lock(member)

    #     if member.voice is None:
    #         raise RuntimeError("You are not in a voice channel.")

    #     if member.id in self.bot.sleeped_users.keys():
    #         raise RuntimeError(f"**You already have sleep status!")

    #     if time <= 0: raise RuntimeError("**time** must be greater than 0.")
    #     if time > 86400: raise RuntimeError("You can't set timer duration more than 24 hours")
    #     future_time = datetime.utcnow() + timedelta(seconds=time)

    #     embed = discord.Embed(color=self.bot.theme)
    #     embed.description = f'You will be sleep in {time} seconds.'
    #     embed.set_footer(text=f'{member.display_name}', icon_url=member.display_avatar)
        
    #     if time > 600:
    #         self.bot.sleeped_users[member.id] = {"time": future_time.timestamp(), "guild_id": guild.id}
    #         await interaction.response.send_message(f'**Sleep timer started**\n*time:* {time} minutes')
    #         return
        
    #     self.bot.add_user_lock(UserLock(member, 'You already have sleep status.'))
    #     await interaction.response.send_message(embed=embed)
        
    #     await asyncio.sleep(time)
    #     if member.voice is not None and self.bot.user_lock.get(member.id, None) is not None:
    #         with suppress(Exception):
    #             await member.move_to(channel=None)
    #     self.bot.user_lock.pop(member.id, None)
    
    # @sleep.command(name='cancel')
    # async def sleep_cancel(self, interaction: Interaction) -> None:
    #     """Cancel sleep timer."""

    #     member = interaction.user    
    #     lock = self.bot.user_lock.get(member.id, None)
    #     if member not in self.bot.sleeped_users.keys() and lock is None:
    #         raise RuntimeError("You don't have a sleep timer")
        
    #     self.bot.sleeped_users.pop(member.id, None)
    #     self.bot.user_lock.pop(member.id, None)

    #     embed = discord.Embed(
    #         color=self.bot.theme,
    #         description=f'**Sleep timer canceled**'
    #     )
    #     await interaction.response.send_message(embed=embed)

    # reminder = app_commands.Group(name='remind', description='Reminder', guild_ids=[840379510704046151])

    # @reminder.command(name='add')
    # @app_commands.describe(time='Time of the reminder.', content='Content of the reminder.')
    # async def reminder_add(self, interaction: Interaction, time: int, content: str) -> None:
    #     """Remind you in the specified time."""
        
    #     member = interaction.user
    #     guild = interaction.guild
    #     time = time.split(':')
    #     if len(time) != 2:
    #         raise RuntimeError("**time** must be in this format > `hh:mm`")
    #     if len(time[0]) != 2 or len(time[1]) != 2:
    #         raise RuntimeError("**time** must be in this format > `hh:mm`")
    #     if len(content) > 1000:
    #         raise RuntimeError("**message** is a maximum of 1000 characters.")
        
    #     embed = discord.Embed(
    #         color=self.bot.theme,
    #         description=f'**Reminder**\n*time:* {time[0]}:{time[1]}\n*message:* {content}'
    #     )
    #     embed.set_footer(text=f'{member.display_name}', icon_url=member.display_avatar)        
    #     await interaction.response.send_message(embed=embed)
    #     await asyncio.sleep(int(time[0])*60 + int(time[1]))
    #     await interaction.response.send_message(embed=embed)

    # @reminder.command(name='list')
    # async def reminder_list(self, interaction: Interaction) -> None:
    #     """List all reminders."""

    #     member = interaction.user
    #     guild = interaction.guild

async def setup(bot) -> None:
    await bot.add_cog(Utility(bot))