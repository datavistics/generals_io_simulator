from dataclasses import dataclass
from functools import cmp_to_key, partial
from logging import getLogger
from typing import List

from hand_crafted.constants import *
from hand_crafted.map import Map

module_logger = getLogger(__name__)


@dataclass
class Socket:
    gio_username: str
    gio_stars: int


@dataclass
class Score:
    total: int = None
    tiles: int = None
    i: int = None
    dead: bool = None


# @param teams Optional. Defaults to FFA.
@dataclass
class Game:
    sockets: List[Socket]
    teams: List[int] = None

    def __post_init__(self):

        # if no teams, make it a free for all
        if self.teams is None:
            self.teams = list(range(len(self.sockets)))
        self.turn = 0
        self.alive_players = len(self.sockets)
        self.left_sockets = []
        self.input_buffer = []
        self.scores = []
        self.deaths = []
        self.map = None
        self.generals = []
        self.cities = []
        self.city_regen = None

        for i in range(len(self.sockets)):
            self.input_buffer.append([])
            self.scores.append(Score(total=1, tiles=1))

    def add_mountain(self, index):
        self.map.set_tile(index, TILE_MOUNTAIN)

    def add_city(self, index, army):
        self.cities.append(index)
        self.map.set_army(index, army)

    def add_general(self, index):
        self.generals.append(index)
        self.map.set_tile(index, len(self.generals) - 1)
        self.map.set_army(index, 1)

    # Returns true when the game is over.
    def update(self):
        # Handle buffered attacks.
        for sock in range(len(self.sockets)):
            # Flip priorities every other turn.
            if self.turn % 2 == 0:
                i = sock
            else:
                i = len(self.sockets) - 1 - sock

            while len(self.input_buffer[i]):
                attack = self.input_buffer[i].splice(0, 1)[0]
                if self.handle_attack(i, attack[0], attack[1], attack[2], attack[3]):
                    # self attack wasn't useless.
                    break
        self.turn += 1

        # Increment armies at generals and cities.
        if self.turn % RECRUIT_RATE == 0:
            for general in self.generals:
                self.map.increment_army_at(general)

            for city in self.cities:
                # Increment owned cities + unowned cities below the min threshold if city_regen is enabled.
                if self.map.tile_at(city) >= 0 or (self.city_regen and self.map.army_at(city) < MIN_CITY_ARMY):
                    self.map.increment_army_at(city)

        # Give farm to all owned tiles for all players.
        if self.turn % FARM_RATE == 0:
            for i in range(self.map.size()):
                if self.map.tile_at(i) >= 0:
                    self.map.increment_army_at(i)
        self.recalculate_scores()

    # Returns true if the game is over.
    def is_over(self):
        # Game with no teams - ends when one player is left.
        if not self.teams and self.alive_players == 1:
            return True

        # Game with teams - ends when everyone left alive is on the same team.
        elif self.teams:
            winning_team = None
            for i in range(len(self.generals)):
                if self.sockets[i] not in self.deaths:
                    # Player is alive!
                    if winning_team is None:
                        winning_team = self.teams[i]
                    elif self.teams[i] != winning_team:
                        return
            return True

    def recalculate_scores(self):
        # Recalculate scores (totals, tiles).
        for i in range(len(self.sockets)):
            self.scores[i].i = i
            self.scores[i].total = 0
            self.scores[i].tiles = 0
            self.scores[i].dead = self.sockets[i] in self.deaths

        for i in range(self.map.size()):
            tile = self.map.tile_at(i)
            if tile >= 0:
                self.scores[tile].total += self.map.army_at(i)
                self.scores[tile].tiles += 1

        def scores_sort(game, a, b):
            if a.dead and not b.dead:
                return 1
            if b.dead and not a.dead:
                return -1
            if a.dead and b.dead:
                return game.deaths.index(game.sockets[b.i]) - game.deaths.index(game.sockets[a.i])
            if b.total == a.total:
                return b.tiles - a.tiles
            return b.total - a.total

        self.scores.sort(key=cmp_to_key(partial(scores_sort, self)))

    def index_of_socket_id(self, socket_id):
        index = -1
        for i, socket in enumerate(self.sockets):
            if socket.id == socket_id:
                index = i
                break
        return index

    # Returns false if the attack was useless, i.e. had no effect or failed.
    def handle_attack(self, index, start, end, is50):
        # Verify that the attack starts from an owned tile.
        if self.map.tile_at(start) != index:
            return False

        # Store the value of the end tile pre-attack.
        end_tile = self.map.tile_at(end)

        # Handle the attack.
        succeeded = self.map.attack(start, end, is50, self.generals)
        if not succeeded:
            return False

        # Check if self attack toppled a general.
        new_end_tile = self.map.tile_at(end)
        general_index = end in self.generals
        if new_end_tile != end_tile and general_index:
            # General captured! Give the capturer command of the captured's army.
            self.map.replace_all(end_tile, new_end_tile, 0.5)

            # Only count as a death if self player has not died before (i.e. rage quitting)
            dead_socket = self.sockets[end_tile]
            if dead_socket not in self.deaths:
                self.deaths.append(dead_socket)
                self.alive_players -= 1
                # This seems close enough
                module_logger.info(f'Game Lost, killer is {new_end_tile}')
                # dead_socket.emit('game_lost',
                #     killer: new_end_tile,
                # )

            # Turn the general into a city.
            self.cities.append(end)
            self.generals[general_index] = DEAD_GENERAL

    # Returns the index of an alive teammate of the given player, if any.
    def alive_teammate(self, index):
        if self.teams:
            for i, socket, team in enumerate(zip(self.sockets, self.teams)):
                if team == self.teams[index] and socket not in self.deaths:
                    return i

    # If the player hasn't been captured yet, either gives their land to a teammate
    # or turns it gray (neutral).
    def try_neutralize_player(self, player_index):
        dead_general_index = self.generals[player_index]
        self.generals[player_index] = DEAD_GENERAL

        # Check if the player has an alive teammate who can take their land.
        alive_teammate_index = self.alive_teammate(player_index)
        if isinstance(alive_teammate_index, int):
            new_index = alive_teammate_index
        else:
            new_index = TILE_EMPTY

        # Check if the player hasn't been captured yet.
        if self.map.tile_at(dead_general_index) == player_index:
            self.map.replace_all(player_index, new_index)
            self.cities.append(dead_general_index)


def create_from_replay(game_replay):
    sockets = []
    for i, g in enumerate(game_replay['generals']):
        sockets.append(Socket(gio_username=game_replay['usernames'][i], gio_stars=(game_replay['stars'][i] or 0)))

    game = Game(sockets=sockets, teams=game_replay['teams'])

    # Init the game map from the replay.
    game.map = Map(game_replay['mapWidth'], game_replay["mapHeight"], game_replay["teams"])
    for i in range(len(game_replay['mountains'])):
        game.add_mountain(game_replay['mountains'][i])

    for i in range(len(game_replay['cities'])):
        game.add_city(game_replay['cities'][i], game_replay['cityArmies'][i])

    for i in range(len(game_replay['generals'])):
        game.add_general(game_replay['generals'][i])

    # For replay versions < 6, city regeneration is enabled.
    # City regeneration is when cities "heal" themselves back to 40 after
    # dropping below 40 army.
    if game_replay['version'] < 6:
        game.city_regen = True

    return game
