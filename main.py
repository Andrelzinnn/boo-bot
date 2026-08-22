import asyncio
import signal
from sys import exit

from aiohttp import ClientError
from discord import errors

from src.bot import bot
from src.config.settings import settings
from src.utils.logger import logger


async def runner() -> None:
    if not settings.token:
        logger.critical("Token não encontrado.")
        exit(1)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.close()))
        except NotImplementedError:
            pass

    async with bot:
        await bot.start(settings.token)

def main() -> None:
    try:
        asyncio.run(runner())
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Interrompido pelo usuário ou pelo sistema.")
    except errors.PrivilegedIntentsRequired:
        logger.critical(
            "Privileged Intents não estão ativadas! "
            + "Acesse https://discord.com/developers/applications -> Seu Bot -> 'Bot' "
            + "e ative 'Presence Intent', 'Server Members Intent' e 'Message Content Intent'."
        )
        exit(1)
    except errors.LoginFailure:
        logger.critical("Falha ao fazer login. Verifique o token.")
        exit(1)
    except (errors.DiscordException, OSError, ClientError) as e:
        logger.critical(f"Erro de conexão ou comunicação com o Discord: {e}")
        exit(1)

if __name__ == "__main__":
   main()
