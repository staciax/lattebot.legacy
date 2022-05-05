import discord
from discord import ui
from discord import Interaction
from discord import ButtonStyle

class LatteVerifyView(ui.View):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__(timeout=None)

    @ui.button(label='Click for verify!', emoji='<:latte_:902674566655139881>', style=ButtonStyle.primary, custom_id='lattebot_view_verifydpy')
    async def latte_view_buttons(self, interaction: Interaction, button: ui.Button):
        
        user = interaction.user

        guild = interaction.client.get_guild(840379510704046151)
        latte_role = guild.get_role(842309176104976387)
        lvl_role = guild.get_role(854503041775566879)
        spacial_role = guild.get_role(926471814757113946)

        if latte_role not in user.roles:
            await user.add_roles(latte_role, lvl_role, spacial_role)

            embed = discord.Embed(
                title='Latte ♡ ₊‧',
                description="Let's check out . . .\n\n﹒<#861883647070437386> \n﹒<#840380566862823425>",
                color=0xffffff
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            channel = interaction.guild.get_channel(861883647070437386)
            await channel.send(f'୨୧・━━⋄✩ ₊ ˚・\nwelcome to our latte . .\n⸝⸝・{interaction.user.mention}', allowed_mentions=discord.AllowedMentions.none())
    
class LatteSupportVerifyView(ui.View):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__(timeout=None)

    @ui.button(label='Click for verify!', emoji='<:latte_:902674566655139881>', style=discord.ButtonStyle.primary, custom_id='lattebot_support_view_verifydpy')
    async def latte_support_view_buttons(self, interaction: Interaction, button: ui.Button):
        
        user = interaction.user
        guild = interaction.client.get_guild(887274968012955679)
        role = guild.get_role(892907635467235399)

        if role not in user.roles:
            embed = discord.Embed(
                description="Let's check out . . .\n\n﹒<#939100705120198686> \n﹒<#939101273649729567>",
                color=0xffffff
            )
            await user.add_roles(role)
            await interaction.response.send_message(embed=embed, ephemeral=True)