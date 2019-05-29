from dataclasses import dataclass
from generals_io_replay_utils.map import Map


@dataclass
class Player:
    map: Map
    name: str

    def __post_init__(self):
        pass
