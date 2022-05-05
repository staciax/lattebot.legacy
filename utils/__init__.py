from discord.ext import commands
from datetime import timedelta
from typing import Literal
import asyncpg

from .bot_base import Latte_Bot
from .useful import LatteContext

__all__ = (
    "Latte_Bot",
    "Cog",
    "GuildModel",
    "Lowercase",
    "s",
    "humanize_time",
    "cleanup_code",
    "LatteContext"
)

class Cog(commands.Cog):
    """Base class for all cogs"""

    def __init__(self, bot: Latte_Bot) -> None:
        self.bot = bot
        self.db: asyncpg.Pool = self.bot.db

class _Lowercase(commands.Converter):
    async def convert(self, ctx, text):
        return text.lower()

Lowercase = _Lowercase()

def s(data) -> Literal["", "s"]:
    if isinstance(data, str):
        data = int(not data.endswith("s"))
    elif hasattr(data, "__len__"):
        data = len(data)
    check = data != 1
    return "s" if check else ""

def humanize_time(time: timedelta) -> str:
    if time.days > 365:
        years, days = divmod(time.days, 365)
        return f"{years} year{s(years)} and {days} day{s(days)}"
    if time.days > 1:
        return f"{time.days} day{s(time.days)}, {humanize_time(timedelta(seconds=time.seconds))}"
    hours, seconds = divmod(time.seconds, 3600)
    minutes = seconds // 60
    if hours > 0:
        return f"{hours} hour{s(hours)} and {minutes} minute{s(minutes)}"
    return f"{minutes} minute{s(minutes)}"

def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    # remove `foo`
    return content.strip('` \n')