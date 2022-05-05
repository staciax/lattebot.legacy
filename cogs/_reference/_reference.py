from discord.ext import commands
from ._base import ReferenceBase

class reference_(ReferenceBase): 
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__)