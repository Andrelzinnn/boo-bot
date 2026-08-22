from typing import TypedDict


class PlayerRecord(TypedDict):
    player_id: str
    kingdom: str
    nickname: str
    added_by: int
    added_at: str


class KingshotConfig(TypedDict):
    redeem_channel_id: int | None
    admin_role_id: int | None


class KingshotData(TypedDict):
    config: KingshotConfig
    players: list[PlayerRecord]


class RedeemResult(TypedDict):
    player_id: str
    kingdom: str
    nickname: str
    success: bool
    status: str
    message: str
