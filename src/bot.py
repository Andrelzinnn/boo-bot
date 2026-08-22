from discord import Intents
from discord.ext import commands
from typing_extensions import override

from src.utils.logger import logger


class BooBot(commands.Bot):
    def __init__(self) -> None:
        intents = Intents.default()
        intents.message_content = True
        intents.presences = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    @override
    async def setup_hook(self) -> None:
        await self.load_extension("src.cogs.mentions")
        await self.load_extension("src.cogs.reactions")
        logger.info("Cogs carregados")


bot = BooBot()
