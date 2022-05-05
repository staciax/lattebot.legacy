from .guild import GuildEvents
from .latte_guild import LatteGuild
from .error_handler import Error_handler
from .private_events import PrivateEvents
from .modmail import ModMail
class Events(GuildEvents, LatteGuild, Error_handler, PrivateEvents, ModMail):
    pass
    '''
    This class is the event handler for the bot.
    '''

async def setup(bot):
    await bot.add_cog(Events(bot))