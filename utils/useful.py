# Standard
import asyncio
import contextlib
import discord
import datetime

from discord import Interaction
from discord.ext import commands
from typing import Union, Optional, Tuple, Any, Callable, Awaitable, Dict

# thank_stella_bot https://github.com/InterStella0/

class Embed(discord.Embed):
    def __init__(self, color=0xffffff, fields=(), field_inline=False, **kwargs) -> None:
        super().__init__(color=color, **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

class LatteEmbed(discord.Embed):
    """Main purpose is to get the usual setup of Embed for a command or an error embed"""
    def __init__(self, color: Union[discord.Color, int] = 0xffffff, fields: Tuple[Tuple[str, str]] = (), field_inline: Optional[bool] = False, **kwargs):
        super().__init__(color=color, **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def default(cls, **kwargs) -> "LatteEmbed":
        instance = cls(**kwargs)
        # user = interaction.user
        # instance.set_footer(text=f"Requested by {user}")
        # if user.default_avatar is not None:
        #     instance.set_footer(text=f"Requested by {user}", icon_url=user.display_avatar)
        return instance

    @classmethod
    def to_error(cls, color: Union[discord.Color, int] = 0xFF7878, **kwargs) -> "LatteEmbed":
        return cls(color=color, **kwargs)
    
    @classmethod
    def to_success(cls, color: Union[discord.Color, int] = 0xffffff, **kwargs) -> "LatteEmbed":
        return cls(color=color, **kwargs)

def default_date(datetime_var: datetime.datetime) -> str:
    """The default date format that are used across this bot."""
    return datetime_var.strftime('%d %b %Y %I:%M %p %Z')

class LatteContext(commands.Context):  # type: ignore[misc] #FIX THIS

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.sent_messages: Dict[int, discord.Message] = {}
        self.reinvoked = False

    def process_message(self, message: discord.Message) -> discord.Message:
        self.sent_messages.update({message.id: message})
        return message

    async def delete_all(self) -> None:
        if self.channel.permissions_for(self.me).manage_messages:
            with contextlib.suppress(discord.NotFound):
                await self.channel.delete_messages(self.sent_messages.values())
        else:
            for message in self.sent_messages.values():
                await message.delete(delay=0)

        self.sent_messages.clear()

    def get_message(self, message_id: int) -> Optional[discord.Message]:
        return self.sent_messages.get(message_id)

    @property
    def created_at(self) -> datetime.datetime:
        return self.message.created_at

    def remove_message(self, message_id: int) -> Optional[discord.Message]:
        return self.sent_messages.pop(message_id, None)

    async def maybe_reply(self, content: Optional[str] = None, mention_author: bool = False,
                          **kwargs: Any) -> discord.Message:
        """Replies if there is a message in between the command invoker and the bot's message."""
        await asyncio.sleep(0.05)
        with contextlib.suppress(discord.HTTPException):
            if ref := self.message.reference:
                # it is very unlikely for this to not be cached
                author = ref.cached_message.author  # type: ignore
                if not mention_author:
                    mention_author = author in self.message.mentions and author.id not in self.message.raw_mentions
                return await self.send(content, mention_author=mention_author, reference=ref, **kwargs)

            if getattr(self.channel, "last_message", None) != self.message:
                return await self.reply(content, mention_author=mention_author, **kwargs)
        return await self.send(content, **kwargs)

    async def embed(self, content: Optional[str] = None, *, reply: bool = True, mention_author: bool = False,
                    embed: Optional[discord.Embed] = None, **kwargs: Any) -> discord.Message:
        embed_only_kwargs = [
            "colour", "color", "title", "type", "url", "description", "timestamp", "fields", "field_inline"
        ]
        ori_embed = LatteEmbed.default(
            self, **{key: value for key, value in kwargs.items() if key in embed_only_kwargs}
        )
        if embed:
            new_embed = embed.to_dict()
            new_embed.update(ori_embed.to_dict())
            ori_embed = LatteEmbed.from_dict(new_embed)
        to_send = (self.send, self.maybe_reply)[reply]
        if not self.channel.permissions_for(self.me).embed_links:
            raise commands.BotMissingPermissions(["embed_links"])
        send_dict = {'tts': False, 'file': None, 'files': None,
                     'delete_after': None, 'nonce': None}
        for x, v in kwargs.items():
            if x in send_dict:
                send_dict[x] = v

        return await to_send(content, mention_author=mention_author, embed=ori_embed, **send_dict)

    def confirmed(self, message_id: Optional[int] = None) -> Awaitable[None]:
        message = self.message if not message_id else self.channel.get_partial_message(message_id)
        return message.add_reaction("<:checkmark:753619798021373974>") 