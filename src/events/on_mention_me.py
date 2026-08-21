from discord import Message, Status

from src.bot import bot
from src.config import GIF_URL, VIOLIN_GIF_URL, YAY_CAT_GIF_URL
from src.types.Env import settings


@bot.event
async def on_message(message: Message) -> None:

  if not message.guild:
    return

  if message.author == bot.user:
    return

  if message.content.lower() == "violin" or message.content.lower() == "violino":
    await message.reply(VIOLIN_GIF_URL)
    return

  if "yay" in message.content.lower():
    await message.reply(YAY_CAT_GIF_URL)
    return

  for user in message.mentions:
    if user.id == settings.user_id:
      member = message.guild.get_member(settings.user_id)
      if member and member.status in [Status.dnd, Status.invisible, Status.offline]:
        await message.channel.send(GIF_URL)
      break
