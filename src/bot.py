from discord import Intents, Permissions, utils
from discord.ext import commands
from typing_extensions import override

from src.config.settings import settings
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
        await self.load_extension("src.cogs.general")
        await self.load_extension("src.cogs.kingshot")

        _ = await self.tree.sync()
        logger.info("Cogs carregados")

    async def on_ready(self) -> None:
        client_id = settings.client_id or (self.user.id if self.user else None)
        if client_id:
            url = utils.oauth_url(
                client_id=client_id,
                permissions=Permissions(send_messages=True, attach_files=True),
            )
            logger.info(f"Link do convite: {url}")
            logger.info(f"{self.user} está online e pronto")
        else:
            logger.warning("Client ID não encontrado")


bot = BooBot()
