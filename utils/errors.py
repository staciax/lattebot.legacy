from discord.ext import commands
from typing import Any

class ArgumentBaseError(commands.UserInputError):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

class UserBlacklisted(commands.CheckFailure):
    pass

class BotTesting(commands.CheckFailure):
    pass

class UserLocked(ArgumentBaseError):
    pass
