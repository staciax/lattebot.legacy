import discord
import asyncio
from typing import Union
from utils.errors import UserLocked

class UserLock:
    def __init__(self, user: Union[discord.Member, discord.User, discord.Object], error_message: str):
        self.user = user
        self.error_message = error_message
        self.lock = asyncio.Lock()

    def __call__(self, bot):
        bot.add_user_lock(self)
        return self.lock

    def locked(self):
        return self.lock.locked()

    @property
    def error(self):
        return UserLocked(message=self.error_message)