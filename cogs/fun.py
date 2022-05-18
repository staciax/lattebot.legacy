import discord
from discord import app_commands, Interaction, Member, User
from discord.app_commands.checks import dynamic_cooldown
from typing import Union

from utils import Cog
from utils.checks import cooldown_5s

class Fun(Cog):
    """Fun commands"""

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='🥳')
    
    @app_commands.command(name='latte_say')
    @app_commands.describe(message='Input message', attachment='The attachment to send')
    @dynamic_cooldown(cooldown_5s)
    async def latte_say(self, interaction: Interaction, message: str, attachment: discord.Attachment = None):
        """Message something you give latte to say."""

        files = []
        if attachment is not None: files.append(await attachment.to_file(spoiler=attachment.is_spoiler()))
        
        await interaction.response.send_message('\u200b', ephemeral=True)
        await interaction.channel.send(f'{message}', allowed_mentions=discord.AllowedMentions.none(), files=files)

    @app_commands.command(name='saybot')
    @app_commands.describe(message='Input message', member="The member to say something to saybot", attachment="The attachment to send")
    @app_commands.checks.bot_has_permissions(manage_webhooks=True)
    @dynamic_cooldown(cooldown_5s)
    async def saybot(self, interaction: Interaction, message: str, attachment: discord.Attachment = None, member: Union[Member, User] = None):

        """Your message to saybot"""

        member = member or interaction.user

        await interaction.response.defer(ephemeral=True)

        files = []
        if attachment is not None: files.append(await attachment.to_file(spoiler=attachment.is_spoiler()))

        webhook = await interaction.channel.create_webhook(name=member.display_name)
        await webhook.send(
            content=message,
            username=member.display_name,
            avatar_url=member.display_avatar,
            files=files,
            allowed_mentions=discord.AllowedMentions.none()
        )
        await webhook.delete()
        await interaction.followup.send('\u200b')

async def setup(bot):
    await bot.add_cog(Fun(bot))