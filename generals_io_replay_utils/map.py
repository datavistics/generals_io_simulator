from logging import getLogger
from dataclasses import dataclass
from math import floor, ceil
from typing import List

from generals_io_replay_utils.constants import *

module_logger = getLogger(__name__)


@dataclass
class Map:
    width: int
    height: int
    teams: List[int] = None

    def __post_init__(self):
        self._map = [TILE_EMPTY for _ in range(self.width * self.height)]
        self._armies = [0 for _ in range(self.width * self.height)]

    def size(self):
        return self.width * self.height

    def index_from(self, row, col):
        return row * self.width + col

    def is_adjacent(self, i1, i2):
        r1 = floor(i1 / self.width)
        c1 = floor(i1 % self.width)
        r2 = floor(i2 / self.width)
        c2 = floor(i2 % self.width)
        return abs(r1 - r2) + abs(c1 - c2) == 1

    def is_valid_tile(self, index):
        return 0 <= index < self.size()

    def tile_at(self, index):
        return self._map[index]

    def army_at(self, index):
        return self._armies[index]

    def set_tile(self, index, val):
        self._map[index] = val

    def set_army(self, index, val):
        self._armies[index] = val

    def increment_army_at(self, index):
        self._armies[index] += 1

    def attack(self, start, end, is50, generals):

        if not self.is_valid_tile(start):
            module_logger.error(f"Attack has invalid start position {start}")
            # raise ValueError(f"Attack has invalid start position {start}")
            return False

        if not self.is_valid_tile(end):
            module_logger.error(f"Attack has invalid end position {end}")
            # raise ValueError(f"Attack has invalid end position {end}")
            return False

        if not self.is_adjacent(start, end):
            module_logger.error(f"Attack for non-adjacent tiles {start} , {end}")
            # raise ValueError(f"Attack for non-adjacent tiles {start} , {end}")
            return False

        if self.tile_at(end) == TILE_MOUNTAIN:
            return False

        if is50:
            reserve = ceil(self._armies[start] / 2)
        else:
            reserve = 1

        # Attacking an Enemy
        if not self.teams or self.teams[self.tile_at(start)] != self.teams[self.tile_at(end)]:
            # If the army at the start tile is <= 1, the attack fails.
            if self._armies[start] <= 1:
                return False

            if self.tile_at(end) == self.tile_at(start):
                # player -> player
                self._armies[end] += self._armies[start] - reserve

            else:
                # player -> enemy
                if self._armies[end] >= self._armies[start] - reserve:
                    # Non-takeover
                    self._armies[end] -= self._armies[start] - reserve
                else:
                    # Takeover
                    self._armies[end] = self._armies[start] - reserve - self._armies[end]
                    self.set_tile(end, self.tile_at(start))

        # Attacking an Ally.
        else:
            self._armies[end] += self._armies[start] - reserve
            if generals.index_of(end) < 0:
                # Attacking a non-general allied tile.
                # Steal ownership of the tile.
                self.set_tile(end, self.tile_at(start))

        self._armies[start] = reserve

        return True

    # Replaces all tiles of value val1 with val2.
    # @param scale Optional. If provided, scales replaced armies down using scale as a multiplier.
    def replace_all(self, val1, val2, scale):
        scale = scale or 1
        for i in range(self.size()):
            if self._map[i] == val1:
                self._map[i] = val2
                self._armies[i] = round(self._armies[i] * scale)

    # Returns the Manhattan distance between index1 and index2.
    def distance(self, index1, index2):
        r1 = floor(index1 / self.width)
        c1 = index1 % self.width
        r2 = floor(index2 / self.width)
        c2 = index2 % self.width
        return abs(r1 - r2) + abs(c1 - c2)
