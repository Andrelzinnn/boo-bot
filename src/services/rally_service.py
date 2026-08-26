import math

from src.types.rally import Construction, Player, ZoneType


def calculate_distance(attacker: Construction, target: Construction) -> float:
    ax, ay = attacker.centroid
    tx, ty = target.centroid
    return math.hypot(ax - tx, ay - ty)


def calculate_speed(player: Player, zone: ZoneType) -> float:
    speed_coeficiente: float = 0.360 if zone == "normal" else 0.185
    return speed_coeficiente * player.speed_increase

def calculate_march_time(distance: float, player: Player, zone: ZoneType) -> float:
    speed = calculate_speed(player, zone)
    if zone == "forbidden":
        return math.ceil((distance / speed) + 5.0)
    return round((distance / speed) + 3.2)
