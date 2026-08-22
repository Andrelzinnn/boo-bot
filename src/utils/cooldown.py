import time
from collections import defaultdict

_cooldowns: defaultdict[tuple[int, str], float] = defaultdict(float)

def is_on_cooldown(channel_id: int, command: str = "default", cooldown_seconds: int = 10) -> bool:
    now = time.time()
    key = (channel_id, command)
    if now - _cooldowns[key] < cooldown_seconds:
        return True
    _cooldowns[key] = now
    return False
