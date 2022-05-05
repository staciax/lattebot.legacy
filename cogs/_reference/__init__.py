
from ._reference import reference_

class Reference(reference_):
    '''
    This class is reference for the bot.
    '''
    pass

def setup(bot):
    bot.add_cog(Reference(bot))