from discord import Message, NotFound, Status

from src.bot import bot
from src.config.constants import GIF_URL, VIOLIN_GIF_URL, YAY_CAT_GIF_URL
from src.config.settings import settings
from src.utils.cooldown import is_on_cooldown


@bot.event
async def on_message(message: Message) -> None:

    if not message.guild or message.author.bot:
        return

    content_lower = message.content.lower()

    if content_lower in ["violin", "violino"]:
        if is_on_cooldown(message.channel.id):
            return
        _ = await message.reply(VIOLIN_GIF_URL)
        return

    if "yay" in content_lower:
        if is_on_cooldown(message.channel.id):
            return
        _ = await message.reply(YAY_CAT_GIF_URL)
        return

    for user in message.mentions:
        if user.id == settings.user_id:
            if is_on_cooldown(message.channel.id):
                return
            member = message.guild.get_member(settings.user_id)
            if member is None:
                try:
                    member = await message.guild.fetch_member(settings.user_id)
                except NotFound:
                    member = None
            if member and member.status in [
                Status.dnd,
                Status.invisible,
                Status.offline,
            ]:
                _ = await message.channel.send(GIF_URL)
            break
    await bot.process_commands(message)
