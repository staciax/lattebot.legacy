import discord
from discord import app_commands, Interaction
from typing import Optional

def owner_only() -> app_commands.check:
    # the check
    async def actual_check(interaction: Interaction):
        return await interaction.client.is_owner(interaction.user)
    # returning the check
    return app_commands.check(actual_check)

def is_nsfw() -> app_commands.check:
    async def predicate(interaction: Interaction):
        return interaction.channel.is_nsfw()
    return app_commands.check(predicate)

def cooldown_for_everyone_but_me(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if interaction.user.id == 894088743475101697:
        return None
    return app_commands.Cooldown(1, 5)

def only_latte_guild() -> app_commands.check:
    async def predicate(interaction: Interaction):
        if interaction.guild.id == 840379510704046151:
            return True
        return False
    return app_commands.check(predicate)