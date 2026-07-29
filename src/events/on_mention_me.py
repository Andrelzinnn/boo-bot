from src.bot import bot
from src.config import GIF_URL
from src.types.Env import settings


@bot.event
async def on_message(message) -> None:
  if message.author == bot.user:
    return
  for user in message.mentions:
    if user.id == settings.user_id:
      await message.channel.send(GIF_URL)
      break
