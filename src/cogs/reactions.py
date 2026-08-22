from discord import Forbidden, HTTPException, Message
from discord.ext import commands

from src.config.settings import settings
from src.utils.cooldown import is_on_cooldown
from src.utils.logger import logger


class ReactionsCogs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        logger.info("Reactions cog loaded")

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if not message.guild or message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        if ctx.prefix is not None:
            return

        content_lower = message.content.lower()
        if content_lower in ["violin", "violino"] and not is_on_cooldown(
            message.channel.id,
            cooldown_seconds=settings.cooldown_seconds,
            command="violin",
        ):
            try:
                _ = await message.reply(settings.violin_gif_url)
            except (Forbidden, HTTPException) as e:
                logger.warning(f"Falha ao enviar resposta de violino: {e}")
            return

        if "yay" in content_lower and not is_on_cooldown(
            message.channel.id,
            cooldown_seconds=settings.cooldown_seconds,
            command="yay",
        ):
            try:
                _ = await message.reply(settings.yay_gif_url)
            except (Forbidden, HTTPException) as e:
                logger.warning(f"Falha ao enviar resposta yay: {e}")
            return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ReactionsCogs(bot))
