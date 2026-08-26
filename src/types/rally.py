from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

ZoneType = Literal["forbidden", "normal"]

class ConstructionType(str, Enum):
    TILE = "tile"
    CITY = "city"
    TERROR = "terror"
    FACILITY = "facility"
    CASTLE = "castle"
    TURRET = "turret"

    @property
    def size(self) -> int:
        match self:
            case ConstructionType.TILE:
                return 1
            case ConstructionType.CITY | ConstructionType.TURRET | ConstructionType.TERROR:
                return 2
            case ConstructionType.CASTLE:
                return 4
            case ConstructionType.FACILITY:
                return 3
    @property
    def offset(self) -> float:
        return (self.size - 1) / 2.0

    @property
    def default_zone(self) -> ZoneType:
        match self:
            case ConstructionType.CASTLE | ConstructionType.TURRET:
                return "forbidden"
            case _:
                return "normal"

    @property
    def display_name(self) -> str:
        return self.value


class Coordinate(BaseModel):
    x: float = Field(ge=0, le=1199, description="Coordinate X")
    y: float = Field(ge=0, le=1199, description="Coordinate Y")

class Construction(BaseModel):
    coordinate: Coordinate
    type: ConstructionType = Field(description="Construction type")

    @property
    def centroid(self) -> tuple[float, float]:
        return (self.coordinate.x + self.type.offset, self.coordinate.y + self.type.offset)

class Player(BaseModel):
    name: str
    msu: float = Field(default=0.0,description="MSU (MARCH SPEED UP) in percentage")

    @property
    def speed_increase(self) -> float:
        return 1 + self.msu / 100.0
