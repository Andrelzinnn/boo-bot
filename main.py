from sys import exit

from discord import Permissions, errors, utils

import src.events.on_mention_me
from src.bot import bot
from src.config.settings import settings
from src.utils.logger import logger


@bot.event
async def on_ready() -> None:
    logger.info("Boo bot está online")


if __name__ == "__main__":
    if not (settings.client_id and settings.token):
        logger.error("client_id e token são necessários")
        exit(1)
    url = utils.oauth_url(
        client_id=settings.client_id,
        permissions=Permissions(send_messages=True, attach_files=True),
    )
    logger.info(f"Link do convite: {url}")
    try:
        bot.run(settings.token)

    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except errors.PrivilegedIntentsRequired:
        logger.critical(
            "Privileged Intents não estão ativadas! "
            "Acesse https://discord.com/developers/applications -> Seu Bot -> "
            "'Bot' e ative 'Presence Intent', 'Server Members Intent' e 'Message Content Intent'."
          )
    except errors.LoginFailure:
        logger.critical("Token do bot inválido. Verifique a variável TOKEN no arquivo .env.")
    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar o bot: {e}")
