import time
from collections import defaultdict

COOLDOWN_SECONDS = 10
_last_triggered: defaultdict[int, float] = defaultdict(float)


def is_on_cooldown(channel_id: int) -> bool:
    now = time.time()
    if now - _last_triggered[channel_id] < COOLDOWN_SECONDS:
        return True
    _last_triggered[channel_id] = now
    return False
