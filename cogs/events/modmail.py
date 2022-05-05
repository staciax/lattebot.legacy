import discord
import contextlib
from discord.ext import commands
from discord.errors import HTTPException
from discord.ext.commands.errors import UserNotFound
from collections import defaultdict

from ._base import EventsBase

# thanks duckbot
async def get_webhook(channel: discord.TextChannel) -> discord.Webhook:
    webhook_list = await channel.webhooks()
    if webhook_list:
        for hook in webhook_list:
            if hook.token:
                return hook
            else:
                continue
    hook = await channel.create_webhook(name="LatteBot ModMail")
    return 

class ModMail(EventsBase):

    modmail_category_id = 966401400575758397
    modmail_channel_id = 966401459312807966
    
    dm_webhooks = defaultdict(str)
    
    """LATTE MOD MAIL"""

    async def get_dm_hook(self, channel: discord.TextChannel) -> discord.Webhook:
        if url := self.dm_webhooks.get(channel.id, None):
            return discord.Webhook.from_url(url, session=self.bot.session, bot_token=self.bot.http.token)
        with contextlib.suppress(Exception):
            wh = await get_webhook(channel)
            self.dm_webhooks[channel.id] = wh.url
            return wh

    @commands.Cog.listener('on_message')
    async def on_mail(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            if message.author == self.bot.user or self.bot.dev_mode is True:
                return

            if self.bot.blacklist.get(message.author.id, None):
                return
                # return await message.channel.send("Sorry but that message wasn't delivered! You are blacklisted.")
        
            category = self.bot.get_guild(965942839563386910).get_channel(966401400575758397)
            channel = discord.utils.get(category.channels, id=self.modmail_channel_id)
            
            thread = discord.utils.get(channel.threads, name=f"{message.author.id}")
            if thread is None:
                mod_message = await channel.send(f'**ᴍᴏᴅᴍᴀɪʟ**')
                thread = await mod_message.create_thread(name=f'{message.author.id}')
                if not thread:
                    if not message.reference:
                        return await message.author.send("there was an issue delivering the message.")

            files = [await attachment.to_file(spoiler=attachment.is_spoiler()) for attachment in message.attachments if
                    attachment.size < 8388600]
            
            if not files and message.attachments:
                await message.author.send(
                    embed=discord.Embed(description="Some files couldn't be sent because they were over 8mb",
                                        color=discord.Colour.red()))

            weebhook = await self.get_dm_hook(channel)
            try:
                
                await weebhook.send(content=message.content,
                            username=str(message.author),
                            avatar_url=message.author.display_avatar.url,
                            files=files, thread=thread)
            except AttributeError:
                pass
            except (discord.Forbidden, discord.HTTPException):
                return await message.add_reaction('⚠')

    @commands.Cog.listener('on_message')
    async def on_mail_reply(self, message: discord.Message):
        if not message.guild and not isinstance(message.channel, discord.Thread):
            return

        if any((message.author.bot,self.bot.dev_mode is True, message.channel.category_id != self.modmail_category_id)):
            return
        
        category = self.bot.get_guild(965942839563386910).get_channel(966401400575758397)
        channel = discord.utils.get(category.channels, id=self.modmail_channel_id)
        
        thread = message.channel

        try:
            user = self.bot.get_user(int(thread.name)) or  await self.bot.fetch_user(int(thread.name))
        except (HTTPException, UserNotFound):
            return await channel.send("could not find user.")

        files = [await attachment.to_file(spoiler=attachment.is_spoiler()) for attachment in message.attachments if
                 attachment.size < 8388600]
        if not files and message.attachments:
            await message.author.send("Some files couldn't be sent because they were over 8mb")

        try:
            await user.send(content=message.content, files=files)
        except (discord.Forbidden, discord.HTTPException):
            return await message.add_reaction('⚠')
