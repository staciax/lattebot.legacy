import discord
from discord import Interaction
from discord.ext import commands
from discord import app_commands
from discord.app_commands.checks import dynamic_cooldown
from discord.app_commands import Choice

from typing import List, Literal

from utils import Latte_Bot
from utils.emojis import LATTE_EMOJI
from utils.anime_api import *
from utils.checks import is_nsfw, cooldown_5s

SFW1 = Literal['Awoo', 'Bite', 'Blush', 'Bonk', 'Breast', 'Bully', 'Cringe', 'Cry', 'Cuddle', 'Dance', 'Glomp', 'Handhold', 'Happy', 'Highfive', 'Hug', 'Kick', 'Kill', 'Kiss', 'Lick', 'Maid']
SFW2 = Literal['Marin-kitagawa', 'Megumin', 'Mori-calliope', 'Neko', 'Nom', 'Oppai', 'Pat', 'Poke', 'Raiden-shogun', 'Selfies', 'Shinobu', 'Slap', 'Smile', 'Smug', 'Uniform', 'Waifu.im', 'Waifu.pisc', 'Wave', 'Wink', 'Yeet']
NSFW = ['Ass', 'Blowjob', 'Ecchi', 'Ero', 'Hentai', 'Milf', 'Neko', 'Oral', 'Paizuri', 'Trap', 'Waifu']

class Anime(commands.Cog):
    """Anime Commands"""

    def __init__(self, bot: Latte_Bot):
        self.bot = bot

    @property
    def display_emoji(self) -> discord.Emoji:
        return str(LATTE_EMOJI.RAIDEN)
        # return self.bot.get_emoji(840678426867793921)

    waifu = app_commands.Group(name='waifu', description='Waifu pictures')

    @waifu.command(name='sfw')
    @app_commands.describe(tags='pick tags')
    @dynamic_cooldown(cooldown_5s)
    async def waifu_sfw(self, interaction: Interaction, tags: SFW1) -> None:
        """Display waifu sfw."""

        url = PISC_URL('sfw', tags)
        view = WAIFU_PISC_VIEW(interaction, tags, url)
        await view.start()

    @waifu.command(name='sfw2')
    @dynamic_cooldown(cooldown_5s)
    @app_commands.describe(tags='pick tags')
    async def waifu_sfw2(self, interaction: Interaction, tags: SFW2) -> None:
        """Display waifu sfw."""

        IM_SFW = ['Uniform', 'Maid', 'Waifu', 'Marin-kitagawa', 'Mori-calliope', 'Raiden-shogun', 'Selfies', 'Oppai']

        if tags in IM_SFW or tags == 'Waifu.im':
            url = IM_URL(tags)
            view = WAIFU_IM_VIEW(interaction, url)
            return await view.start()

        url = PISC_URL('sfw', tags)
        view = WAIFU_PISC_VIEW(interaction, tags, url)
        await view.start()

    @waifu.command(name='nsfw')
    @app_commands.describe(tags='pick tags')
    @is_nsfw()
    async def waifu_nsfw(self, interaction: Interaction, tags: str) -> None:
        """Display waifu nsfw."""

        IM_NSFW = ['Ass', 'Hentai', 'Milf', 'Oral', 'Paizuri', 'Ecchi', 'Ero']

        if tags in IM_NSFW:
            url = IM_URL(tags)
            view = WAIFU_IM_VIEW(interaction, url)
            return await view.start()

        url = PISC_URL(interaction.command.name, tags)
        view = WAIFU_PISC_VIEW(interaction, tags, url)
        await view.start()

    @waifu_nsfw.autocomplete('tags')
    async def tags_autocomplete(self, interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
        if interaction.channel.is_nsfw():
            return [Choice(name=tag, value=tag) for tag in NSFW]
        return [Choice(name='NSFW', value='The optional will not be displayed if it is not an NSFW channel.')]

    # @waifu.command(name='pisc')
    # @app_commands.describe(type='Choose type of waifu', tags='pick tags')
    # async def waifu_pisc(self, interaction: Interaction, type: Literal['sfw', 'nsfw'], tags: str):
    #     """Display waifu pisc."""
    #     if type == "nsfw" and not interaction.channel.is_nsfw():
    #         channel = interaction.channel.mention
    #         raise RuntimeError(f"{channel} is not a nsfw channel.")
    #         # return await interaction.response.send_message(f"{channel} needs to be NSFW for this command to work.", ephemeral=True)
    #         # # raise commands.NSFWChannelRequired(interaction.channel.mention)

    #     url = PISC_URL(type, tags)
    #     view = WAIFU_PISC_VIEW(interaction, tags, url)
    #     await view.start()
    
    # @waifu_pisc.autocomplete('tags')
    # async def tags_autocomplete(
    #     self,
    #     interaction: Interaction,
    #     current: str
    # ) -> List[app_commands.Choice[str]]:
    #     if interaction.namespace.type == 'sfw':
    #         return [
    #             app_commands.Choice(name=tag, value=tag)
    #             for tag in PISC_SFW if current.lower() in tag.lower()
    #         ][:25]
    #     elif interaction.namespace.type == 'nsfw':
    #         return [
    #             app_commands.Choice(name=tag, value=tag)
    #             for tag in PISC_NSFW if current.lower() in tag.lower()
    #         ][:25]
    #     else:
    #         return [app_commands.Choice(name='waifu', value='waifu')]

    # @waifu.command(name='im')
    # @app_commands.describe(
    #     type='Choose type of waifu',
    #     tags='pick tags'
    # )
    # async def waifu_im(self, interaction: Interaction, type: Literal['sfw', 'nsfw'], tags: str):
    #     """Display waifu im."""
    #     if type == "nsfw" and not interaction.channel.is_nsfw():
    #         channel = interaction.channel.mention
    #         raise RuntimeError(f"{channel} is not a nsfw channel.")
    #         # return await interaction.response.send_message(f"{channel} needs to be NSFW for this command to work.", ephemeral=True)
    #         # raise commands.NSFWChannelRequired(channel)

    #     url = IM_URL(tags)
    #     view = WAIFU_IM_VIEW(interaction, url)
    #     await view.start()
    
    # @waifu_im.autocomplete('tags')
    # async def tags_autocomplete(
    #     self,
    #     interaction: Interaction,
    #     current: str
    # ) -> List[app_commands.Choice[str]]:
    #     if interaction.namespace.type == 'sfw':
    #         return [
    #             app_commands.Choice(name=tag, value=tag)
    #             for tag in IM_SFW if current.lower() in tag.lower()
    #         ][:25]
    #     elif interaction.namespace.type == 'nsfw':
    #         return [
    #             app_commands.Choice(name=tag, value=tag)
    #             for tag in IM_NSFW if current.lower() in tag.lower()
    #         ][:25]
    #     else:
    #         return [app_commands.Choice(name='waifu', value='waifu')]

# class Waifu(app_commands.Group):
#     """Fetch tags by their name"""
    
#     def __init__(self, bot: Latte_Bot):
#         super().__init__(name='waifu', guild_ids=[840379510704046151])
#         self.bot = bot

#     @app_commands.command(name='pisc')
#     @app_commands.describe(
#         type='Choose type of waifu',
#         tags='pick tags'
#     )
#     # @app_commands.choices(type=[
#     #     Choice(name='sfw', value=1),
#     #     Choice(name='nsfw', value=2)
#     # ])
#     async def waifu_pisc(self, interaction: Interaction, type: Literal['sfw', 'nsfw'], tags: str):
#         """Display waifu pisc."""
#         if type == "nsfw" and not interaction.channel.is_nsfw():
#             channel = interaction.channel.mention
#             return await interaction.response.send_message(f"{channel} needs to be NSFW for this command to work.", ephemeral=True)
#             # raise commands.NSFWChannelRequired(interaction.channel.mention)

#         url = PISC_URL(type, tags)
#         view = WAIFU_PISC_VIEW(self.bot, interaction, tags, url)
#         await view.start()
        
#     @waifu_pisc.autocomplete('tags')
#     async def tags_autocomplete(
#         self,
#         interaction: Interaction,
#         current: str
#     ) -> List[app_commands.Choice[str]]:
#         if interaction.namespace.type == 'sfw':
#             return [
#                 app_commands.Choice(name=tag, value=tag)
#                 for tag in PISC_SFW if current.lower() in tag.lower()
#             ][:25]
#         elif interaction.namespace.type == 'nsfw':
#             return [
#                 app_commands.Choice(name=tag, value=tag)
#                 for tag in PISC_NSFW if current.lower() in tag.lower()
#             ][:25]
#         else:
#             return [app_commands.Choice(name='waifu', value='waifu')]
            
#     @app_commands.command(name='im')
#     @app_commands.describe(
#         type='Choose type of waifu',
#         tags='pick tags'
#     )
#     async def waifu_im(self, interaction: Interaction, type: Literal['sfw', 'nsfw'], tags: str):
#         """Display waifu im."""
#         if type == "nsfw" and not interaction.channel.is_nsfw():
#             channel = interaction.channel.mention
#             return await interaction.response.send_message(f"{channel} needs to be NSFW for this command to work.", ephemeral=True)
#             # raise commands.NSFWChannelRequired(channel)

#         url = IM_URL(tags)
#         view = WAIFU_IM_VIEW(self.bot, interaction, url)
#         await view.start()
    
#     @waifu_im.autocomplete('tags')
#     async def tags_autocomplete(
#         self,
#         interaction: Interaction,
#         current: str
#     ) -> List[app_commands.Choice[str]]:
#         if interaction.namespace.type == 'sfw':
#             return [
#                 app_commands.Choice(name=tag, value=tag)
#                 for tag in IM_SFW if current.lower() in tag.lower()
#             ][:25]
#         elif interaction.namespace.type == 'nsfw':
#             return [
#                 app_commands.Choice(name=tag, value=tag)
#                 for tag in IM_NSFW if current.lower() in tag.lower()
#             ][:25]
#         else:
#             return [app_commands.Choice(name='waifu', value='waifu')]

async def setup(bot):
    await bot.add_cog(Anime(bot))
    # bot.tree.add_command(Waifu(bot))