from discord import Forbidden, HTTPException, Message, NotFound, Status

from src.bot import bot
from src.config.settings import settings
from src.utils.cooldown import is_on_cooldown
from src.utils.logger import logger


@bot.event
async def on_message(message: Message) -> None:
    if not message.guild or message.author.bot:
        return

    content_lower = message.content.lower()
    if content_lower in ["violin", "violino"] and not is_on_cooldown(message.channel.id, cooldown_seconds=settings.cooldown_seconds, command="violin"):
        try:
            _ = await message.reply(settings.violin_gif_url)
        except (Forbidden, HTTPException) as e:
            logger.warning(f"Falha ao enviar resposta de violino: {e}")
        return

    if "yay" in content_lower and not is_on_cooldown(message.channel.id, cooldown_seconds=settings.cooldown_seconds, command="yay"):
        try:
            _ = await message.reply(settings.yay_gif_url)
        except (Forbidden, HTTPException) as e:
            logger.warning(f"Falha ao enviar resposta yay: {e}")
        return


    if settings.user_id:
        for user in message.mentions:
            if user.id == settings.user_id:
                member = message.guild.get_member(settings.user_id)
                if member is None:
                    try:
                        member = await message.guild.fetch_member(settings.user_id)
                    except (NotFound, Forbidden, HTTPException) as e:
                        logger.debug(f"Não foi possível obter o membro {settings.user_id}: {e}")
                        member = None

                if member and member.status not in [Status.online, Status.idle] and not is_on_cooldown(message.channel.id, cooldown_seconds=settings.cooldown_seconds, command="unpresence"):
                    try:
                        _ = await message.channel.send(settings.gif_unpresence_url)
                        logger.info(f"GIF de ausência enviado para #{message.channel.id}")
                    except (Forbidden, HTTPException) as e:
                        logger.warning(f"Falha ao enviar GIF de ausência: {e}")
                break

    await bot.process_commands(message)
