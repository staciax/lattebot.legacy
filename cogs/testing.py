import discord
from discord import Interaction
from discord import ui
from discord.ext import commands
from discord import app_commands
import mathjspy

from utils import Cog

# These are Calculator Functions
def get_highest(iterable):
    resp = 0
    for i in iterable:
        if i > resp:
            resp = i
    return resp

def get_last_operator(response: str):
    try:
        plus = response.rindex("+")
    except ValueError:
        plus = None
    try:
        minus = response.rindex("-")
    except ValueError:
        minus = None
    try:
        mul = response.rindex("*")
    except ValueError:
        mul = None
    try:
        div = response.rindex("/")
    except ValueError:
        div = None
    valid = [n for n in [plus, minus, mul, div] if n != None]
    indx = get_highest(valid)
    return response[indx:]

async def default_execution_function(view, label, interaction: discord.Interaction):
    view.expression += str(label)
    await interaction.response.edit_message(content=view.expression)

# These are Calculator Buttons
class CalcButton(ui.Button):
    def __init__(
        self, label: str, row: int, execution_function=default_execution_function, style=discord.ButtonStyle.blurple
    ):
        super().__init__(label=label, row=row, style=style)
        self.__func = execution_function

    async def callback(self, interaction: discord.Interaction):
        await self.__func(self.view, self.label, interaction)

async def give_result_operator(view, label, interaction: discord.Interaction):
    parser = view.parser
    if not view.expression:
        return await interaction.response.send_message("You didn't tell me anything to evaluate.", ephemeral=True)
    if view.expression.replace(".", "").isdigit() and view.last_expr:
        view.expression += view.last_expr
    else:
        view.last_expr = get_last_operator(view.expression)
    result = str(float(parser.eval(view.expression)))
    view.expression = result
    await interaction.response.edit_message(content=result)

async def go_back(view, label, interaction: discord.Interaction):
    if not view.expression:
        return
    view.expression = view.expression[:-1]
    await interaction.response.edit_message(content=view.expression)

async def operator_handler(view, label, interaction: discord.Interaction):
    if not view.expression or not view.expression[0].isdigit():
        return await interaction.response.send_message("You cannot use operators at start.", ephemeral=True)
    if not view.expression[-1].isdigit():
        return await interaction.response.send_message("You cannot add operator after operator.", ephemeral=True)
    view.expression += label
    await interaction.response.edit_message(content=view.expression)

async def stop_button(view, label, interaction: discord.Interaction):
    for i in view.children:
        i.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

# Actual Calculator Buttons
class CalcView(ui.View):
    def __init__(self, interaction, **kwargs):
        super().__init__(**kwargs)
        self.interaction = interaction
        self.parser = mathjspy.MathJS()
        self.expression = ""
        self.last_expr = ""
        numb = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        for row in range(len(numb)):
            for i in numb[row]:
                self.add_item(CalcButton(i, row))
        self.add_item(CalcButton("=", 3, give_result_operator, discord.ButtonStyle.gray))
        self.add_item(CalcButton("<==", 3, go_back))
        for label, row in [["+", 0], ["-", 1], ["*", 2], ["/", 3]]:
            self.add_item(CalcButton(label, row, operator_handler, discord.ButtonStyle.green))
        self.add_item(CalcButton(f'{"Stop":⠀^20}', 4, stop_button, discord.ButtonStyle.red))
        self.add_item(CalcButton(".", 4, style=discord.ButtonStyle.green))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message(
                f"This button can only be accessed by {self.interaction.user.name}.", ephemeral=True
            )
            return False
        else:
            return True

    async def on_timeout(self):
        for i in self.children:
            i.disabled = True
        await self.message.edit(content="If you want your calculator to work you need to make a new one.", view=self)
        self.stop()

class Owner(Cog):

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return self.bot.get_emoji(840678426867793921)

    @app_commands.command(name='stacia')
    @app_commands.guilds(discord.Object(id=840379510704046151))
    async def stacia(self, interaction: Interaction) -> None:
        ...
        # embed = discord.Embed(description='testing')

        # channel = interaction.channel

        # await channel.send()
        # await interaction.channel.send(embed=embed)

    # @commands.hybrid_command(name='testing')
    # @app_commands.guilds(discord.Object(id=840379510704046151))
    # async def stacia_test(self, ctx):
    #     await ctx.send('testing')
    
    # @app_commands.command()
    # @app_commands.guilds(discord.Object(id=840379510704046151))
    # async def calculator(self, interaction: Interaction):
    #     view = CalcView(interaction)
    #     await interaction.response.send_message("\u200b", view=view)

async def setup(bot) -> None:
    await bot.add_cog(Owner(bot))