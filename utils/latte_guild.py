from __future__ import annotations

import discord
import traceback
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

class DeveloperContributorRequest(ui.Modal, title='Developer/Contributor'):
    role_request = discord.ui.TextInput(
        label="Role Request",
        placeholder='What role are you requesting?',
        style=discord.TextStyle.short,
        max_length=20,
    )
    name = discord.ui.TextInput(
        label="Request exclusive role",
        placeholder='Please describe your request',
        style=discord.TextStyle.paragraph,
        max_length=300,
    )
    github = discord.ui.TextInput(
        label="Github",
        placeholder='if you have a github account, please enter it here',
        required=False
    )
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        channel = guild.get_channel(934041100048535563)
        embed = discord.Embed(
            title="Developer Request",
            description=f"**Role:**{self.role_request.value}\n**Request:** {self.name.value}\n**Github:** {self.github.value}\nUser: {interaction.user.mention}",
            color=0xffffff
        )
        await channel.send(content='<@240059262297047041>', embed=embed)
        await interaction.response.send_message(embed=discord.Embed(description=f"Thank you for your request. We will get back to you as soon as possible.", color=0xffffff), ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)

# class ContributorRequest(ui.Modal, title='Contributor role'):
#     name = discord.ui.TextInput(
#         label="Request contributor role",
#         placeholder='Please describe your request',
#     )
#     github = discord.ui.TextInput(
#         label="Github",
#         placeholder='if you have a github account, please enter it here',
#     )

#     async def on_submit(self, interaction: discord.Interaction):
#         await interaction.response.defer(ephemeral=True)
#         guild = interaction.guild
#         channel = guild.get_channel(934041100048535563)
#         embed = discord.Embed(
#             title="Contributor Request",
#             description=f"Request: {self.name.value}\nGithub: {self.github.value}\nUser: {interaction.user.mention}",
#             color=0xffffff
#         )
#         await channel.send(embed=embed)
#         await interaction.response.send_message(embed=discord.Embed(description=f"Thank you for your request. We will get back to you as soon as possible.", color=0xffffff), ephemeral=True)
    
#     async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
#         await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
#         # Make sure we know what the error actually is
#         traceback.print_tb(error.__traceback__)

class LatteSupportVerifyView(ui.View):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__(timeout=None)

    @ui.button(
        label='valorant-bot ♡ ₊˚',
        emoji='<:VALORANT:685247196979134495>',
        style=discord.ButtonStyle.primary,
        custom_id='lattebot_support_view_verify_vlr_role',
        row=0
    )
    async def valorantbot_verify_role(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        user = interaction.user
        guild = interaction.guild
        role = guild.get_role(982374900813680711)

        if role not in user.roles:
            embed = discord.Embed(
                description="Let's check out . . .\n\n﹒<#966721494531067974> \n﹒<#980296252245815376>",
                color=0xfa4c5b
            )
            await user.add_roles(role)
            return await interaction.followup.send(embed=embed, ephemeral=True)
        await user.remove_roles(role)
        await interaction.followup.send(embed=discord.Embed(description=f"You have been removed **{role.name}**", color=0xfa4c5b), ephemeral=True)
    
    @ui.button(
        label='latte-bot ♡ ₊˚',
        emoji='<:latte_icon_new:907030425011109888>',
        style=discord.ButtonStyle.primary,
        custom_id='lattebot_support_view_verify_lattebot_role',
        row=0
    )
    async def lattebot_verify_role(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        user = interaction.user
        guild = interaction.guild
        role = guild.get_role(982375169215574027)

        if role not in user.roles:
            embed = discord.Embed(
                description="Let's check out . . .\n\n﹒<#971285884169248848> \n﹒<#971581397854715915>",
                color=0xffffff
            )
            await user.add_roles(role)
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        await user.remove_roles(role)
        await interaction.followup.send(embed=discord.Embed(description=f"You have been removed **{role.name}**", color=0xffffff), ephemeral=True)

    @ui.button(
        label='member ♡ ₊˚',
        emoji='<:latte_:902674566655139881>',
        style=discord.ButtonStyle.primary,
        custom_id='lattebot_support_view_member_role',
        row=0
    )
    async def member_verify_role(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)

        user = interaction.user
        guild = interaction.guild
        role = guild.get_role(892907635467235399)

        if role not in user.roles:
            embed = discord.Embed(
                description="Let's check out . . .\n\n﹒<#939100705120198686> \n﹒<#939101273649729567>",
                color=0xffffff
            )
            await user.add_roles(role)
            return await interaction.followup.send(embed=embed, ephemeral=True)

        await user.remove_roles(role)
        await interaction.followup.send(embed=discord.Embed(description=f"You have been removed **{role.name}**", color=0xffffff), ephemeral=True)

    @ui.button(
        label='developer/contributor ♡ ₊˚',
        emoji='<:github:903376103345913907>',
        style=discord.ButtonStyle.primary,
        custom_id='lattebot_support_view_contributor_role',
        row=1
    )
    async def dcontributor_verify_role(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(DeveloperContributorRequest())

    # @ui.button(
    #     label='developer ♡ ₊˚',
    #     emoji='<:latte_:902674566655139881>',
    #     style=discord.ButtonStyle.green,
    #     custom_id='lattebot_support_view_developer_role',
    #     row=1
    # )
    # async def developer_verify_role(self, interaction: Interaction, button: ui.Button):
    #     await interaction.response.send_modal(DeveloperRequest())