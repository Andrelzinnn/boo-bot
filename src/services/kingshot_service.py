import asyncio
from typing import Any

from playwright.async_api import (
    Browser,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from src.services.kingshot_store import kingshot_store
from src.utils.logger import logger

DEFAULT_KINGSHOT_URL = "https://ks-giftcode.centurygame.com/"


class KingshotService:
    def __init__(self, url: str = DEFAULT_KINGSHOT_URL, timeout_ms: int = 1500) -> None:
        self.url = url
        self.timeout_ms = timeout_ms

    async def _setup_lightweight_page(self, browser: Browser) -> Page:
        """Cria uma página no navegador bloqueando o download de mídias e fontes pesadas."""
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        # Bloqueia apenas mídias pesadas para garantir que scripts e formulários carreguem normalmente
        await page.route(
            "**/*.{png,jpg,jpeg,gif,svg,webp,mp4,mp3}",
            lambda route: route.abort(),
        )
        return page

    async def validate_player(self, player_id: str, kingdom: str) -> tuple[bool, str]:
        """Testa se o Player ID e Reino (Kingdom) são válidos no portal oficial do Kingshot."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--no-zygote",
                ],
            )
            page = await self._setup_lightweight_page(browser)
            try:
                await page.goto(self.url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_selector("input[placeholder*='Player ID']", timeout=10000)

                await page.fill("input[placeholder*='Player ID']", player_id)
                await page.fill("input[placeholder*='Kingdom']", kingdom)
                await page.fill("input[placeholder*='Gift Code']", "VALIDATE_CHECK")

                btn = await page.query_selector(".exchange_btn, .btn")
                if btn:
                    await btn.click()

                modal = await page.wait_for_selector(".message_modal .msg", timeout=8000)
                if modal:
                    msg = (await modal.inner_text()).strip()
                    msg_lower = msg.lower()

                    # Fecha o modal
                    try:
                        confirm_btn = await page.query_selector(".confirm_btn")
                        if confirm_btn:
                            await confirm_btn.click()
                    except Exception:
                        pass

                    if any(w in msg_lower for w in ["character info is incorrect", "user info error", "enter your kingdom"]):
                        return False, msg

                    # Qualquer outra resposta (ex: código inválido, expirado) significa que a conta e o reino são válidos!
                    return True, "Conta e Reino validados com sucesso!"

                return False, "Não foi possível obter resposta do servidor."
            except Exception as e:
                logger.error(f"Erro ao validar Player ID {player_id}: {e}")
                return False, f"Erro de conexão/timeout: {e}"
            finally:
                await browser.close()

    async def _redeem_for_single_player_on_page(
        self,
        page: Page,
        player_id: str,
        kingdom: str,
        gift_code: str,
    ) -> dict[str, Any]:
        """Executa a rotina de resgate para um jogador específico na página aberta."""
        result: dict[str, Any] = {
            "player_id": player_id,
            "kingdom": kingdom,
            "nickname": player_id,
            "success": False,
            "status": "Erro",
            "message": "",
        }

        try:
            # Preenche os 3 campos obrigatórios do formulário
            await page.fill("input[placeholder*='Player ID']", player_id)
            await page.fill("input[placeholder*='Kingdom']", kingdom)
            await page.fill("input[placeholder*='Gift Code']", gift_code)

            # Clica no botão Confirm
            btn = await page.query_selector(".exchange_btn, .btn")
            if btn:
                await btn.click()

            # Aguarda a mensagem do modal de resposta
            try:
                modal = await page.wait_for_selector(".message_modal .msg", timeout=self.timeout_ms * 4)
                if modal:
                    msg_text = (await modal.inner_text()).strip()
                    result["message"] = msg_text

                    # Fecha o modal para liberar a próxima iteração
                    try:
                        confirm_btn = await page.query_selector(".confirm_btn")
                        if confirm_btn:
                            await confirm_btn.click()
                    except Exception:
                        pass

                    msg_lower = msg_text.lower()
                    if any(w in msg_lower for w in ["success", "congratulations", "sucesso", "recompensa"]):
                        result["success"] = True
                        result["status"] = "✅ Sucesso"
                    elif any(w in msg_lower for w in ["used", "already", "resgatado", "repetido", "claimed"]):
                        result["success"] = False
                        result["status"] = "⚠️ Já Resgatado"
                    elif any(w in msg_lower for w in ["expired", "expirado"]):
                        result["success"] = False
                        result["status"] = "⏰ Código Expirado"
                    elif any(w in msg_lower for w in ["character info is incorrect", "user info error"]):
                        result["success"] = False
                        result["status"] = "❌ ID ou Reino Incorreto"
                    elif any(w in msg_lower for w in ["not exist", "invalid", "inválido", "incorreto"]):
                        result["success"] = False
                        result["status"] = "❌ Código Inválido"
                    elif any(w in msg_lower for w in ["server busy", "busy"]):
                        result["success"] = False
                        result["status"] = "⚠️ Servidor Ocupado"
                    else:
                        result["success"] = False
                        result["status"] = "ℹ️ Resposta"
                    return result
            except (PlaywrightTimeoutError, Exception) as e:
                result["message"] = f"Timeout na confirmação: {e}"
                result["status"] = "⚠️ Timeout"
                return result

        except Exception as e:
            logger.error(f"Exceção ao resgatar para {player_id}: {e}")
            result["message"] = str(e)
            result["status"] = "❌ Erro"

        return result

    async def redeem_all(
        self,
        gift_code: str,
        target_player_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Resgata o código de presente para todas as contas registradas."""
        players = kingshot_store.get_players()
        if target_player_ids:
            players = [p for p in players if str(p.get("player_id")) in target_player_ids]

        if not players:
            return []

        results: list[dict[str, Any]] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--no-zygote",
                ],
            )
            page = await self._setup_lightweight_page(browser)

            try:
                await page.goto(self.url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_selector("input[placeholder*='Player ID']", timeout=10000)

                for player in players:
                    pid = str(player.get("player_id"))
                    kid = str(player.get("kingdom", "1"))
                    nick = str(player.get("nickname") or pid)

                    logger.info(f"Tentando resgatar '{gift_code}' para {nick} (ID: {pid}, Reino: {kid})...")
                    res = await self._redeem_for_single_player_on_page(page, pid, kid, gift_code)
                    res["nickname"] = nick
                    results.append(res)
                    await asyncio.sleep(0.4)  # Intervalo de segurança entre envios
            except Exception as e:
                logger.error(f"Erro geral no loop de resgate: {e}")
            finally:
                await browser.close()

        return results


kingshot_service = KingshotService()
