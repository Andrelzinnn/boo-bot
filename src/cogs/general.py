import discord
from discord import Embed, Interaction, app_commands
from discord.ext import commands

from src.utils.logger import logger


class GeneralCog(commands.Cog, name="general"):
    """Comandos gerais e utilidades do bot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        logger.info("General cog carregado.")

    @app_commands.command(name="ping", description="Verifica a latência do bot.")
    async def ping(self, interaction: Interaction) -> None:
        latency = round(self.bot.latency * 1000)
        embed = Embed(
            title="🏓 Pong!",
            description=f"Latência do Gateway: `{latency}ms`",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))
