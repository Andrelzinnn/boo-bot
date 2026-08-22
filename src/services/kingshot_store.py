import json
from datetime import datetime, timezone
from pathlib import Path

from src.types.kingshot import KingshotConfig, KingshotData, PlayerRecord
from src.utils.logger import logger

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "kingshot_data.json"


class KingshotStore:
    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path: Path = data_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_path.exists():
            initial_data: KingshotData = {
                "config": {
                    "redeem_channel_id": None,
                    "admin_role_id": None,
                },
                "players": [],
            }
            self._write_file(initial_data)

    def _read_file(self) -> KingshotData:
        try:
            with open(self.data_path, encoding="utf-8") as f:
                data = json.load(f)
                default_config: KingshotConfig = {
                    "redeem_channel_id": None,
                    "admin_role_id": None,
                }
                return {
                    "config": data.get("config", default_config),
                    "players": data.get("players", []),
                }
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Erro ao ler banco de dados Kingshot ({self.data_path}): {e}")
            return {
                "config": {"redeem_channel_id": None, "admin_role_id": None},
                "players": [],
            }

    def _write_file(self, data: KingshotData) -> None:
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (OSError, TypeError) as e:
            logger.error(f"Erro ao salvar banco de dados Kingshot ({self.data_path}): {e}")

    def get_config(self) -> KingshotConfig:
        data = self._read_file()
        return data["config"]

    def set_config(
        self,
        redeem_channel_id: int | None = None,
        admin_role_id: int | None = None,
    ) -> None:
        data = self._read_file()
        if redeem_channel_id is not None:
            data["config"]["redeem_channel_id"] = redeem_channel_id
        if admin_role_id is not None:
            data["config"]["admin_role_id"] = admin_role_id
        self._write_file(data)

    def get_players(self) -> list[PlayerRecord]:
        data = self._read_file()
        return data["players"]

    def add_player(
        self,
        player_id: str,
        kingdom: str,
        nickname: str,
        added_by: int,
    ) -> bool:
        data = self._read_file()
        pid_str = str(player_id).strip()
        kid_str = str(kingdom).strip()

        for p in data["players"]:
            if p["player_id"] == pid_str:
                p["kingdom"] = kid_str
                p["nickname"] = nickname
                self._write_file(data)
                return False  # Já existia, apenas atualizou

        data["players"].append(
            {
                "player_id": pid_str,
                "kingdom": kid_str,
                "nickname": nickname,
                "added_by": added_by,
                "added_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._write_file(data)
        return True

    def remove_player(self, query: str) -> PlayerRecord | None:
        data = self._read_file()
        query_clean = query.strip().lower()

        for idx, p in enumerate(data["players"]):
            if p["player_id"].lower() == query_clean or p["nickname"].lower() == query_clean:
                removed = data["players"].pop(idx)
                self._write_file(data)
                return removed
        return None

    def update_player(
        self,
        player_id: str,
        nickname: str | None = None,
        kingdom: str | None = None,
    ) -> None:
        data = self._read_file()
        updated = False
        for p in data["players"]:
            if p["player_id"] == str(player_id):
                if nickname:
                    p["nickname"] = nickname
                if kingdom:
                    p["kingdom"] = str(kingdom)
                updated = True
                break
        if updated:
            self._write_file(data)

    def find_player(self, query: str) -> PlayerRecord | None:
        players = self.get_players()
        query_clean = query.strip().lower()
        for p in players:
            if p["player_id"].lower() == query_clean or p["nickname"].lower() == query_clean:
                return p
        return None


kingshot_store = KingshotStore()
