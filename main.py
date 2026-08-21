from discord import Permissions, utils

import src.events.on_mention_me
from src.bot import bot
from src.types.Env import settings


@bot.event
async def on_ready() -> None:
    print("Boo bot está online")


if __name__ == "__main__":
    if settings.client_id and settings.token:
        url = utils.oauth_url(
            client_id=settings.client_id,
            permissions=Permissions(send_messages=True, attach_files=True),
        )
        print(url)
        bot.run(settings.token)
    else:
        print("client_id e token são necessários")
