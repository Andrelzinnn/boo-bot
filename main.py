from discord import Permissions, utils

import src.events.on_mention_me
from src.bot import bot
from src.config.settings import settings
from src.utils.logger import logger


@bot.event
async def on_ready() -> None:
    logger.info("Boo bot está online")


if __name__ == "__main__":
    if settings.client_id and settings.token:
        url = utils.oauth_url(
            client_id=settings.client_id,
            permissions=Permissions(send_messages=True, attach_files=True),
        )
        logger.info(url)
        bot.run(settings.token)
    else:
        logger.error("client_id e token são necessários")
