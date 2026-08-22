import re
from typing import Optional

import discord
from discord import Embed, Interaction, Message, Role, TextChannel, app_commands
from discord.ext import commands

from src.services.kingshot_service import kingshot_service
from src.services.kingshot_store import kingshot_store
from src.utils.logger import logger


def build_results_embed(gift_code: str, results: list[dict]) -> Embed:
    """Constrói um Embed visualmente organizado com o relatório do resgate."""
    success_count = sum(1 for r in results if r.get("success"))
    total_count = len(results)

    embed = Embed(
        title="🎁 Relatório de Resgate — Kingshot",
        description=f"**Código:** `{gift_code}`\n**Sucesso:** `{success_count}/{total_count}` contas",
        color=discord.Color.green() if success_count > 0 else discord.Color.orange(),
    )

    for r in results:
        nick = r.get("nickname", "Desconhecido")
        pid = r.get("player_id", "")
        kid = r.get("kingdom", "")
        status = r.get("status", "Erro")
        msg = r.get("message", "")
        detail = f"{status}" + (f" — *{msg}*" if msg and msg != status else "")
        _ = embed.add_field(
            name=f"👑 {nick} (`ID: {pid}` | `Reino: {kid}`)",
            value=detail,
            inline=False,
        )

    _ = embed.set_footer(text="Boo Bot • Kingshot Auto-Redeemer")
    return embed


class KingshotCog(commands.GroupCog, name="kingshot"):
    """Comandos e automação de resgate de códigos para o jogo Kingshot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        logger.info("Kingshot cog carregado.")

    def _check_permission(self, interaction: Interaction) -> bool:
        """Verifica se o usuário é administrador ou possui o cargo configurado."""
        if not interaction.guild:
            return True
        if interaction.user.guild_permissions.administrator:  # type: ignore[union-attr]
            return True

        config = kingshot_store.get_config()
        admin_role_id = config.get("admin_role_id")
        if admin_role_id and isinstance(interaction.user, discord.Member):
            return any(role.id == admin_role_id for role in interaction.user.roles)

        return False

    # 1. Comando: Setup
    @app_commands.command(
        name="setup", description="Configura o canal de auto-redeem e cargo de permissão."
    )
    @app_commands.describe(
        channel="Canal onde códigos de presente serão monitorados para auto-redeem",
        admin_role="Cargo opcional com permissão para adicionar e remover contas",
    )
    async def setup_cmd(
        self,
        interaction: Interaction,
        channel: TextChannel,
        admin_role: Optional[Role] = None,
    ) -> None:
        if not self._check_permission(interaction):
            _ = await interaction.response.send_message(
                "❌ Você não tem permissão para configurar o Kingshot.", ephemeral=True
            )
            return

        kingshot_store.set_config(
            redeem_channel_id=channel.id,
            admin_role_id=admin_role.id if admin_role else None,
        )

        role_info = f" Cargo permitido: {admin_role.mention}." if admin_role else ""
        _ = await interaction.response.send_message(
            f"✅ Configuração concluída! Monitorando códigos no canal {channel.mention}.{role_info}",
            ephemeral=True,
        )

    # 2. Comando: Add Player
    @app_commands.command(
        name="add", description="Adiciona uma conta de jogador para resgate automático."
    )
    @app_commands.describe(
        player_id="O Player ID numérico do jogo Kingshot (visível no Avatar)",
        kingdom="O número/código do Reino (Kingdom) da conta (ex: 1, 10, 100)",
        nickname="Apelido ou nome da conta para identificação no relatório",
    )
    async def add_cmd(
        self,
        interaction: Interaction,
        player_id: str,
        kingdom: str,
        nickname: Optional[str] = None,
    ) -> None:
        if not self._check_permission(interaction):
            _ = await interaction.response.send_message(
                "❌ Você não tem permissão para adicionar contas.", ephemeral=True
            )
            return

        clean_id = player_id.strip()
        clean_kid = kingdom.strip()
        display_name = nickname.strip() if nickname else f"Player_{clean_id}"

        _ = await interaction.response.defer(thinking=True)

        # Valida a conta no portal oficial do Kingshot
        is_valid, val_msg = await kingshot_service.validate_player(clean_id, clean_kid)
        if not is_valid:
            await interaction.followup.send(
                f"❌ **Falha na validação:** Não foi possível validar o Player ID `{clean_id}` no Reino `{clean_kid}`.\n"
                f"Detalhe do site: *{val_msg}*\n"
                "Verifique se o Player ID e o Reino foram digitados corretamente no jogo."
            )
            return

        is_new = kingshot_store.add_player(clean_id, clean_kid, display_name, interaction.user.id)
        action_msg = "adicionada com sucesso" if is_new else "atualizada"
        await interaction.followup.send(
            f"✅ Conta **{display_name}** (`ID: {clean_id}` | `Reino: {clean_kid}`) {action_msg} para resgate automático!"
        )

    # 3. Comando: Remove Player
    @app_commands.command(
        name="remove", description="Remove uma conta de jogador pelo ID ou apelido."
    )
    @app_commands.describe(query="Player ID ou apelido da conta a remover")
    async def remove_cmd(self, interaction: Interaction, query: str) -> None:
        if not self._check_permission(interaction):
            _ = await interaction.response.send_message(
                "❌ Você não tem permissão para remover contas.", ephemeral=True
            )
            return

        removed = kingshot_store.remove_player(query)
        if removed:
            _ = await interaction.response.send_message(
                f"🗑️ Conta **{removed.get('nickname')}** (`ID: {removed.get('player_id')}` | `Reino: {removed.get('kingdom', '1')}`) removida da lista."
            )
        else:
            _ = await interaction.response.send_message(
                f"❌ Conta `{query}` não foi encontrada na base de dados.", ephemeral=True
            )

    # 4. Comando: List Players
    @app_commands.command(
        name="list", description="Lista todas as contas registradas para resgate automático."
    )
    async def list_cmd(self, interaction: Interaction) -> None:
        players = kingshot_store.get_players()
        if not players:
            _ = await interaction.response.send_message(
                "ℹ️ Nenhuma conta cadastrada no momento. Use `/kingshot add <player_id> <kingdom>`.",
                ephemeral=True,
            )
            return

        embed = Embed(
            title="📋 Contas Registradas — Kingshot",
            description=f"Total de contas cadastradas: **{len(players)}**",
            color=discord.Color.blue(),
        )

        for p in players:
            pid = p.get("player_id", "")
            kid = p.get("kingdom", "1")
            nick = p.get("nickname", pid)
            embed.add_field(name=f"👑 {nick}", value=f"ID: `{pid}`\nReino: `{kid}`", inline=True)

        _ = embed.set_footer(text="Boo Bot • Kingshot Redeemer")
        _ = await interaction.response.send_message(embed=embed)

    # 5. Comando: Redeem Manual
    @app_commands.command(
        name="redeem", description="Resgata manualmente um código de presente para todas as contas."
    )
    @app_commands.describe(
        gift_code="O código de presente para resgatar",
        player_id="Opcional: Resgatar apenas para este Player ID",
    )
    async def redeem_cmd(
        self,
        interaction: Interaction,
        gift_code: str,
        player_id: Optional[str] = None,
    ) -> None:
        clean_code = gift_code.strip()
        _ = await interaction.response.defer(thinking=True)

        target_ids = [player_id.strip()] if player_id else None
        results = await kingshot_service.redeem_all(clean_code, target_player_ids=target_ids)

        if not results:
            _ = await interaction.followup.send(
                "⚠️ Nenhuma conta cadastrada para resgatar. Use `/kingshot add <player_id> <kingdom>` primeiro."
            )
            return

        embed = build_results_embed(clean_code, results)
        await interaction.followup.send(embed=embed)

    # 6. Listener: Auto-Redeem em canal configurado
    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if not message.guild or message.author.bot:
            return

        config = kingshot_store.get_config()
        redeem_channel_id = config.get("redeem_channel_id")

        # Só monitora mensagens no canal configurado
        if not redeem_channel_id or message.channel.id != redeem_channel_id:
            return

        ctx = await self.bot.get_context(message)
        if ctx.prefix is not None:
            return

        # Regex para identificar potenciais gift codes (ex: KS15K, KINGSHOT2026, etc)
        matches = re.findall(r"\b[A-Za-z0-9]{4,25}\b", message.content)
        if not matches:
            return

        candidate_code = matches[0]
        players = kingshot_store.get_players()
        if not players:
            return

        status_msg = await message.reply(
            f"🎁 Código `{candidate_code}` detectado! Iniciando resgate automático para **{len(players)}** contas..."
        )

        results = await kingshot_service.redeem_all(candidate_code)
        if results:
            embed = build_results_embed(candidate_code, results)
            _ = await status_msg.edit(content=None, embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(KingshotCog(bot))
