import discord
import contextlib
from discord.ext import commands, tasks
from utils.formats import get_fancy_text

from ._base import EventsBase

class LatteGuild(EventsBase):

    @commands.Cog.listener('on_voice_state_update')
    async def latte_voice_log(self, member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
        
        channel = self.bot.get_channel(870173863726682112)

        if member.guild.id == 840379510704046151:
            
            embed = discord.Embed(timestamp=discord.utils.utcnow())
            embed.set_footer(text=member, icon_url=member.display_avatar)
        
            if not before.channel and after.channel:
                embed.description = f"**ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ** : `{after.channel.name}`"
                embed.color=0x77dd77            
                await channel.send(embed=embed)
        
            if before.channel and not after.channel:
                embed.description = f"**ʟᴇᴀᴠᴇ ᴄʜᴀɴɴᴇʟ** : `{before.channel.name}`"
                embed.color=0xd34e4e
                await channel.send(embed=embed)
        
            if before.channel and after.channel: #and before.channel != after.channel
                if before.channel.id != after.channel.id:
                    embed.description = f"**ꜱᴡɪᴛᴄʜᴇᴅ ᴄʜᴀɴɴᴇʟꜱ** : `{before.channel.name}` ᴛᴏ `{after.channel.name}`"
                    embed.color=0xfcfc64
                    await channel.send(embed=embed)
                
            if before.self_stream != after.self_stream:
                if after.self_stream:
                    embed.description = f"**ꜱᴛʀᴇᴀᴍɪɴɢ ɪɴ** `{before.channel.name}`"
                    embed.colour=0x8A2BE2
                    await channel.send(embed=embed)
                if before.self_stream:
                    embed.description = f"**ʟᴇᴀᴠᴇ ꜱᴛʀᴇᴀᴍɪɴɢ ɪɴ** `{before.channel.name}`"
                    embed.colour=0x8A2BE2
                    await channel.send(embed=embed)

            if before.deaf != after.deaf:
                if after.deaf:
                    embed.description = f"**ᴍᴇᴍʙᴇʀ ᴅᴇᴀꜰ**"
                    embed.colour=0xFF7878
                    await channel.send(embed=embed)
                if before.deaf:
                    embed.description = f"**ᴍᴇᴍʙᴇʀ ᴜɴᴅᴇᴀꜰ**"
                    embed.colour=0x77dd77
                    await channel.send(embed=embed)

            if before.mute != after.mute:
                if after.mute:
                    embed.description = f"**MEMBER MUTED**"
                    embed.colour=0xFF7878
                    await channel.send(embed=embed)
                if before.mute:
                    embed.description = f"**ᴍᴇᴍʙᴇʀ ᴜɴᴍᴜᴛᴇᴅ**"
                    embed.colour=0x77dd77
                    await channel.send(embed=embed)

            if before.self_deaf != after.self_deaf:
                if after.self_deaf:
                    embed.description = f"**SELF DEAF**"
                    embed.colour=0xFF7878
                    await channel.send(embed=embed)
                if before.self_deaf:
                    embed.description = f"**SELF UNDEAF**"
                    embed.colour=0x77dd77
                    await channel.send(embed=embed)

            if before.self_mute != after.self_mute:
                if after.self_mute:
                    embed.description = f"**SELF MUTED**"
                    embed.colour=0xFF7878
                    await channel.send(embed=embed)
                if before.self_mute:
                    embed.description = f"**SELF UNMUTED**"
                    embed.colour=0x77dd77
                    await channel.send(embed=embed)

            if after.channel is not None:
                temp_channel = {
                    '873677543453126676': 873679362082369546,
                    '875037193196945409': 875038018736644166,
                    '873696566165250099': 883027485455941712,
                    '883025077610876958': 883059509810040884
                }
                with contextlib.suppress(Exception):
                    channel_move = temp_channel[str(after.channel.id)]
                    channel_voice =  member.guild.get_channel(channel_move)
                    return await member.move_to(channel_voice)
   
    # @tasks.loop(seconds=1)
    # async def counted(self):
    #     pass
        # try:
        #     guild = self.bot.latte
        #     total_count = guild.member_count
        #     if self.total_ != total_count:
        #         self.total_ = total_count
        #         total_channel = guild.get_channel(876738880282431489)
        #         total_name = f"ᴛᴏᴛᴀʟ‌・{self.total_}"
        #         await total_channel.edit(name=total_name)
            
        #     member_count = len([member for member in guild.members if not member.bot])
        #     if self.member_ != member_count:
        #         self.member_ = member_count
        #         member_channel = guild.get_channel(876712142160678923)
        #         member_name = f"ᴍᴇᴍʙᴇʀs・{self.member_}"
        #         await member_channel.edit(name=member_name)

        #     bot_count = len([Member for Member in guild.members if Member.bot])
        #     if self.bot_ != bot_count:
        #         self.bot_ = bot_count
        #         bot_channel = guild.get_channel(876724022686150687)
        #         bot_name = f"ʙᴏᴛs‌・{self.bot_}"
        #         await bot_channel.edit(name=bot_name)
            
        #     role_count = len(guild.roles)
        #     if self.role_ != role_count:
        #         self.role_ = role_count
        #         role_channel = guild.get_channel(876712169662742588)
        #         role_name = f"ʀᴏʟᴇs‌・{self.role_}"
        #         await role_channel.edit(name=role_name)
            
        #     channel_count = len(guild.channels)
        #     if self.channel_ != channel_count:
        #         self.channel_ = channel_count
        #         channel_channel = guild.get_channel(876712200214024192)
        #         channel_name = f"ᴄʜᴀɴɴᴇʟs・{self.channel_}"
        #         await channel_channel.edit(name=channel_name)
            
        #     text_channel_count = len(guild.text_channels)
        #     if self.text_ != text_channel_count:
        #         self.text_ = text_channel_count
        #         text_channel = guild.get_channel(876740437505871922)
        #         text_name = f"ᴛᴇxᴛ・{self.text_}"
        #         await text_channel.edit(name=text_name)
            
        #     voice_channel_count = len(guild.voice_channels)
        #     if self.voice_ != voice_channel_count:
        #         self.voice_ = voice_channel_count
        #         voice_channel = guild.get_channel(876740515863879711)
        #         voice_name = f"ᴠᴏɪᴄᴇ・{self.voice_}"
        #         await voice_channel.edit(name=voice_name)
            
        #     boost_count = guild.premium_subscription_count
        #     if self.boost_ != boost_count:
        #         self.boost_ = boost_count
        #         boost_channel = guild.get_channel(876737270051389470)
        #         boost_name = f"ʙᴏᴏꜱᴛꜱ・{self.boost_}"
        #         await boost_channel.edit(name=boost_name)
    
        # except Exception as e:
        #     print(e)

    # @counted.before_loop
    # async def before_counted(self):
    #     await self.bot.wait_until_ready()

    # @commands.Cog.listener('on_presence_update')
    # async def latte_status_log(self, before:discord.Member, after:discord.Member):
        
    #     def status_icon(status):
    #         status = str(status)
    #         icons = {
    #             'online':'https://cdn.discordapp.com/emojis/864171414466592788.png',
    #             'idle':'https://cdn.discordapp.com/emojis/864185381833277501.png',
    #             'dnd':'https://cdn.discordapp.com/emojis/864173608321810452.png',
    #             'offline':'https://cdn.discordapp.com/emojis/864171414750625812.png',
    #         }
    #         output = icons[status]
    #         return output
        
    #     channel = self.bot.get_channel(948885857862029322)
    #     if before.guild.id == 931480707040174100:
    #         if before.status != after.status:
    #             embed = discord.Embed(
    #                 colour=after.colour,
    #                 timestamp=discord.utils.utcnow()
    #             )
    #             if after.avatar is not None:
    #                 embed.set_author(name=after, icon_url=after.avatar.url)
    #             else:
    #                 embed.set_author(name=after)
    #             embed.set_footer(text=f"{get_fancy_text(str(after.status))}", icon_url=status_icon(after.status))
    #             await channel.send(embed=embed)

    # @commands.Cog.listener('on_member_update')
    # async def latte_member_log(self, before:discord.Member, after:discord.Member):

    #     channel = self.bot.get_channel(948885857862029322)
    #     # channel_roles = self.bot.get_channel(873688581682634762)
        
    #     if before.guild.id == 931480707040174100:

    #         if before.display_name != after.display_name:
    #             embed = discord.Embed(title='ɴɪᴄᴋɴᴀᴍᴇ',color=0xfdfd96, timestamp=discord.utils.utcnow())
                
    #             embed.add_field(name="**ʙᴇꜰᴏʀᴇ**", value=f"```{before.display_name}```", inline=False)
    #             embed.add_field(name="**ᴀꜰᴛᴇʀ**", value=f"```{after.display_name}```", inline=False)

    #             embed.set_footer(text=after)
    #             if after.avatar is not None:
    #                 embed.set_footer(text=after, icon_url=after.avatar)

    #             await channel.send(embed=embed)

    #         elif before.display_avatar != after.display_avatar:
    #             embed = discord.Embed(title='ꜱᴇʀᴠᴇʀ ᴀᴠᴀᴛᴀʀ', color=0xf3d4b4, timestamp=discord.utils.utcnow())
    #             embed.description = "ɴᴇᴡ ɪᴍᴀɢᴇ ɪꜱ ʙᴇʟᴏᴡ, ᴏʟᴅ ᴛᴏ ᴛʜᴇ ʀɪɢʜᴛ."
                                
    #             if before.display_avatar is not None:
    #                 embed.set_thumbnail(url=before.display_avatar)
                
    #             if after.display_avatar is not None:
    #                 embed.set_image(url=after.display_avatar.url)
                
    #             embed.set_footer(text=after)
    #             if after.avatar is not None:
    #                 embed.set_footer(text=after, icon_url=after.avatar)
        
    #             await channel.send(embed=embed)
            
    #         elif before.roles != after.roles:

    #             embed = discord.Embed(title='ʀᴏʟᴇ', timestamp=discord.utils.utcnow())
                
    #             ADD_ROLE = [x.mention for x in after.roles if x not in before.roles]                
    #             REMOVE_ROLE = [x.mention for x in before.roles if x not in after.roles]
    #             ROLE = ADD_ROLE or REMOVE_ROLE
    #             UPDATE = 'ᴀᴅᴅ ʀᴏʟᴇ' if ADD_ROLE else 'ʀᴇᴍᴏᴠᴇ ʀᴏʟᴇ'
    #             COLOR =  discord.Colour.green() if ADD_ROLE else discord.Colour.red()
                
    #             embed.color = COLOR
    #             embed.add_field(name=UPDATE,value=''.join(ROLE))
    #             embed.set_footer(text=after)
    #             if after.avatar is not None:
    #                 embed.set_footer(text=after, icon_url=after.avatar)
                
    #             await channel.send(embed=embed)