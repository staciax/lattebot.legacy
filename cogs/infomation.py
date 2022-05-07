import discord
from discord import Interaction
from discord.ext import commands
from discord import app_commands
from discord import ui
from typing import Union, Optional, Literal
from discord import Asset, Member, User

from utils import Cog
from utils.view import AvatarView
from utils.utils import Banner, get_dominant_color
from utils.formats import deltaconv
from utils.checks import cooldown_for_everyone_but_me
from utils.emojis import LATTE_EMOJI

deafult_guild = discord.Object(id=840379510704046151)
            
class Infomation(Cog):
    """Infomation commands"""

    @property
    def display_emoji(self) -> discord.Emoji:
        return str(LATTE_EMOJI.LOVE_NOTE)
        # return self.bot.get_emoji(909498501799505930)
    
    @app_commands.command()
    @app_commands.describe(member='The member you want to get the avatar of.')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def avatar(self, interaction: Interaction, member: Union[discord.Member, discord.User] = None):
        """Shows the user avatar of the specified member."""

        member = member or interaction.user
    
        if member.avatar is not None:
            view = AvatarView(interaction, member)
            return await view.start()

        raise RuntimeError(f'**{member.display_name}** must have a avatar.')

    @app_commands.command()
    @app_commands.describe(member='The member you want to get the avatar of.')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def banner(self, interaction: Interaction, member:Union[discord.Member, discord.User] = None):
        """Shows the banner of the specified member."""
        member = member or interaction.user
        banner: Banner = await self.bot.fetch_banner(member)

        embed = discord.Embed(title=f"{member.name}'s Banner:")

        if banner.url is not None:
            embed.set_image(url=banner.url)
            return await interaction.response.send_message(embed=embed)
            
        elif banner.color is not None:
            embed.title = f"{member.name}'s color:"
            embed.set_image(url="attachment://color.png")
            embed.set_footer(text=f'HEX: #{hex(banner.color)[2:]}')
            file = banner.dominant_color
            return await interaction.response.send_message(embed=embed, file=file)

        raise RuntimeError("this user don't have a banner.")

        # try:
        #     file_2 = banner.color_from_avatar
        #     embed.title = f"{member.name}'s color:"
        #     embed.color = banner.color_avatar
        #     embed.set_image(url="attachment://color.png")
        #     await interaction.response.send_message(embed=embed, file=file_2)
        # except Exception as e:
        #     print(e)

    @app_commands.command()
    @app_commands.describe(choose='Choose the option you want to get.')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def server(self, interaction: Interaction, choose: Literal['Icon', 'Banner', 'Splash']):
        """Get server icon, banner or splash."""
        guild = interaction.guild
        embed = discord.Embed(title=f"{guild.name}'s {choose.lower()}:")

        if choose == 'Icon' and guild.icon is not None:
            embed.set_image(url=guild.icon.url)
        elif choose == 'Banner' and guild.banner is not None:
            embed.set_image(url=guild.banner.url)
        elif choose == 'Splash' and guild.splash is not None:
            embed.set_image(url=guild.splash.url)

        if embed.image:
            return await interaction.response.send_message(embed=embed)
        raise RuntimeError(f'{guild.name} has no {choose}.')
    
    @app_commands.command()
    @app_commands.describe(channel='The channel you want to get the first message')
    @app_commands.checks.bot_has_permissions(read_message_history=True)
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def first_message(self, interaction: Interaction, channel: discord.TextChannel = None):
        """Shows the first message of the specified channel."""
        channel = channel or interaction.channel
        try:
            async for message in channel.history(limit=1, oldest_first=True):
                content = message.content
                if len(content) > 25:
                    content = f"`Please click button 'Go to message'`"

                embed = discord.Embed(color=self.bot.theme)
                embed.title = f"First message in #{channel.name}"
                embed.url = message.jump_url
                embed.description = f"**Content:** {content}\n**Author:** {message.author.mention}\n**Sent at:** {discord.utils.format_dt(message.created_at, style='F')} ({discord.utils.format_dt(message.created_at, style='R')})"
                embed.set_footer(text=f"Message ID : {message.author.id}")
                
                view = ui.View()
                view.add_item(ui.Button(label='ɢᴏ ᴛᴏ ᴏʀɪɢɪɴᴀʟ ᴍᴇꜱꜱᴀɢᴇ', url=message.jump_url))

                return await interaction.response.send_message(embed=embed, view=view)
        
        except discord.Forbidden as e:
            raise RuntimeError(f'Bot missing permissions `read_message_history`')
        except Exception as e:
            print(e)
            raise RuntimeError(f'Not found message in {channel}')

    # @app_commands.context_menu(name='avatar')
    # @app_commands.guilds(deafult_guild)
    # async def avatar_context(interaction: discord.Interaction, member: Union[discord.Member, discord.User]):
    #     await interaction.response.send_message(f"{member.mention}'s avatar:")
    
    # @app_commands.command()
    # @app_commands.guilds(discord.Object(id=840379510704046151))
    # async def spotify(self, interaction: Interaction, member:Union[discord.Member, discord.User] = None):
    #     member = member or interaction.user
    #     spotify = discord.utils.find(lambda act: isinstance(act, discord.Spotify), member.activities)

    #     if spotify:
    #         duration = f"Duration: {deltaconv((interaction.created_at - spotify.start).total_seconds())} / {deltaconv(spotify.duration.total_seconds())}"
    #         embed = discord.Embed()
    #         embed.title = f"{member.name} is listening to {spotify.title}"
    #         embed.description = f"Title: [{spotify.title}]({spotify.track_url})\n{duration}\nArtists: {', '.join(spotify.artists)}"
    #         embed.color = spotify.color
    #         embed.set_image(url=spotify.album_cover_url)
    #         embed.set_footer(text=f'Track ID: {spotify.track_id}')
    #         speac = '\u2001'*6
    #         view = ui.View()
    #         view.add_item(ui.Button(emoji=f"{bot_emoji('spotify')}",label=f"Listen on spoify{speac}",url=spotify.track_url))
    #         view.add_item(ui.Button(label="≡"))
    #         for x in view.children:
    #             if x.label == '≡':
    #                 x.disabled = True

    #         return await interaction.response.send_message(embed=embed, view=view)

    #     raise RuntimeError("That member doesn't have a spotify status!")

async def setup(bot):
    await bot.add_cog(Infomation(bot))


