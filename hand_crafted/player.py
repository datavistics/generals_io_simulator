from dataclasses import dataclass
from hand_crafted.map import Map


@dataclass
class Player:
    map: Map
    name: str

    def __post_init__(self):
        pass
