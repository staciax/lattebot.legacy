import discord
from discord.ext import commands

from ._base import EventsBase
from utils.formats import format_dt

class PrivateEvents(EventsBase):

    # @commands.Cog.listener('on_pool_create')
    # async def on_pool_create(self, pool: discord.VoicePool):
    #     await self.bot.log_channel.send(f'New Voice Pool Created: {pool.name}')

    # @commands.Cog.listener('on_cache_ready')
    # async def on_cache_ready(self):
    #     await self.bot.log_channel.send('Cache Ready')
    
    @commands.Cog.listener('on_guild_join')
    async def server_join_message(self, guild: discord.Guild):
        channel = self.bot.get_channel(966722528410226709)
        
        embed = discord.Embed(title='ᴊᴏɪɴᴇᴅ ꜱᴇʀᴠᴇʀ', color=0xffffff, timestamp=discord.utils.utcnow(),
                            description=f'**ɴᴀᴍᴇ:** {discord.utils.escape_markdown(guild.name)} • {guild.id}'
                            f'\n**ᴏᴡɴᴇʀ:** {guild.owner} • {guild.owner_id}')
                                   
        embed.add_field(name='ᴍᴇᴍʙᴇʀ ᴄᴏᴜɴᴛ', value=f'{guild.member_count}', inline=True)
        embed.add_field(name='ᴄʀᴇᴀᴛɪᴏɴ ᴅᴀᴛᴇ', value=f'{format_dt(guild.created_at)}', inline=True)
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon)

        await channel.send(embed=embed)

    @commands.Cog.listener('on_guild_remove')
    async def server_leave_message(self, guild: discord.Guild):
        channel = self.bot.get_channel(966722615928561695)
        
        embed = discord.Embed(title='ʟᴇꜰᴛ ꜱᴇʀᴠᴇʀ', color=0xffffff, timestamp=discord.utils.utcnow(),
                            description=f'**ɴᴀᴍᴇ:** {discord.utils.escape_markdown(guild.name)} • {guild.id}'
                            f'\n**ᴏᴡɴᴇʀ:** {guild.owner} • {guild.owner_id}')
                                   
        embed.add_field(name='ᴍᴇᴍʙᴇʀ ᴄᴏᴜɴᴛ', value=f'{guild.member_count}', inline=True)
        embed.add_field(name='ᴄʀᴇᴀᴛɪᴏɴ ᴅᴀᴛᴇ', value=f'{format_dt(guild.created_at)}', inline=True)
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon)

        await channel.send(embed=embed)
                
    # @commands.Cog.listener('on_message')
    # async def nsfw_protector(self, message: discord.Message):
    #     if self.bot.user.id != ID:
    #         return
    #     if message.channel.id != ID or message.author.bot:
    #         return
    #     if not all([a.is_spoiler() for a in message.attachments]):
    #         await message.reply('Please mark **all** your images as spoiler.', allowed_mentions=discord.AllowedMentions.all(), delete_after=10)
    #         await message.delete()
    