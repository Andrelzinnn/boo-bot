import json
from datetime import datetime, timezone
from pathlib import Path

from src.types.kingshot import GuildData, KingshotConfig, KingshotStoreData, PlayerRecord
from src.utils.logger import logger

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "kingshot_data.json"


class KingshotStore:
    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path: Path = data_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_path.exists():
            initial_data: KingshotStoreData = {"guilds": {}}
            self._write_file(initial_data)

    def _read_file(self) -> KingshotStoreData:
        try:
            with open(self.data_path, encoding="utf-8") as f:
                raw_data = json.load(f)

                # Migração automática caso exista o formato antigo (mono-servidor)
                if "guilds" not in raw_data:
                    old_config = raw_data.get(
                        "config", {"redeem_channel_id": None, "admin_role_id": None}
                    )
                    old_players = raw_data.get("players", [])
                    return {
                        "guilds": {
                          "default": {
                              "config": old_config,
                              "players": old_players,
                          }
                        }
                    }

                return {"guilds": raw_data.get("guilds", {})}
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Erro ao ler banco de dados Kingshot ({self.data_path}): {e}")
            return {"guilds": {}}

    def _write_file(self, data: KingshotStoreData) -> None:
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (OSError, TypeError) as e:
            logger.error(f"Erro ao salvar banco de dados Kingshot ({self.data_path}): {e}")

    def _get_or_create_guild(self, data: KingshotStoreData, guild_id: int | str) -> GuildData:
        gid = str(guild_id)
        if gid not in data["guilds"]:
            default_config: KingshotConfig = {
                "redeem_channel_id": None,
                "admin_role_id": None,
            }
            data["guilds"][gid] = {
                "config": default_config,
                "players": [],
            }
        return data["guilds"][gid]

    def get_config(self, guild_id: int | str) -> KingshotConfig:
        data = self._read_file()
        guild_data = self._get_or_create_guild(data, guild_id)
        return guild_data["config"]

    def set_config(
        self,
        guild_id: int | str,
        redeem_channel_id: int | None = None,
        admin_role_id: int | None = None,
    ) -> None:
        data = self._read_file()
        guild_data = self._get_or_create_guild(data, guild_id)
        if redeem_channel_id is not None:
            guild_data["config"]["redeem_channel_id"] = redeem_channel_id
        if admin_role_id is not None:
            guild_data["config"]["admin_role_id"] = admin_role_id
        self._write_file(data)

    def get_players(self, guild_id: int | str) -> list[PlayerRecord]:
        data = self._read_file()
        guild_data = self._get_or_create_guild(data, guild_id)
        return guild_data["players"]

    def add_player(
        self,
        guild_id: int | str,
        player_id: str,
        kingdom: str,
        nickname: str,
        added_by: int,
    ) -> bool:
        data = self._read_file()
        guild_data = self._get_or_create_guild(data, guild_id)
        pid_str = str(player_id).strip()
        kid_str = str(kingdom).strip()

        for p in guild_data["players"]:
            if p["player_id"] == pid_str:
                p["kingdom"] = kid_str
                p["nickname"] = nickname
                self._write_file(data)
                return False  # Já existia, apenas atualizou

        guild_data["players"].append(
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

    def remove_player(self, guild_id: int | str, query: str) -> PlayerRecord | None:
        data = self._read_file()
        guild_data = self._get_or_create_guild(data, guild_id)
        query_clean = query.strip().lower()

        for idx, p in enumerate(guild_data["players"]):
            if p["player_id"].lower() == query_clean or p["nickname"].lower() == query_clean:
                removed = guild_data["players"].pop(idx)
                self._write_file(data)
                return removed
        return None

    def update_player(
        self,
        guild_id: int | str,
        player_id: str,
        nickname: str | None = None,
        kingdom: str | None = None,
    ) -> None:
        data = self._read_file()
        guild_data = self._get_or_create_guild(data, guild_id)
        updated = False
        for p in guild_data["players"]:
            if p["player_id"] == str(player_id):
                if nickname:
                    p["nickname"] = nickname
                if kingdom:
                    p["kingdom"] = str(kingdom)
                updated = True
                break
        if updated:
            self._write_file(data)

    def find_player(self, guild_id: int | str, query: str) -> PlayerRecord | None:
        players = self.get_players(guild_id)
        query_clean = query.strip().lower()
        for p in players:
            if p["player_id"].lower() == query_clean or p["nickname"].lower() == query_clean:
                return p
        return None


kingshot_store = KingshotStore()
