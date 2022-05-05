import discord
from discord.ext import commands
from utils import Latte_Bot

class EventsBase(commands.Cog):
    def __init__(self, bot: Latte_Bot):
        self.bot = bot

        # latte guild stuff
        # self.bot = bot
        # self.total_ = 0
        # self.member_ = 0
        # self.bot_ = 0
        # self.role_ = 0
        # self.channel_ = 0
        # self.text_ = 0
        # self.voice_ = 0
        # self.boost_ = 0
        # self.counted.start()
    
    # def cog_unload(self):
    #     self.counted.cancel()

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{PERSONAL COMPUTER}')

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print(self.__class__.__name__)
