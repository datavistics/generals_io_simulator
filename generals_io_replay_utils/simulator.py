import json
import logging.config
from logging import getLogger

from common.proj_paths import dirs
from replay_handling.converter import gior_to_replay
from generals_io_replay_utils.game import create_from_replay

logging.config.fileConfig(dirs['common'] / 'logging.ini')
module_logger = getLogger(__name__)

replay = gior_to_replay(dirs['replays'] / 'BeKdahWa4.gior')

game = create_from_replay(replay)
current_move_index = 0
current_afk_index = 0


def next_turn(current_move_index, current_afk_index):
    while len(replay['moves']) > current_move_index and replay['moves'][current_move_index]['turn'] <= game.turn:
        move = replay['moves'][current_move_index]
        current_move_index += 1

        game.handle_attack(move['index'], move['start'], move['end'], move['is50'])

    # Check for AFKs.
    while len(replay['afks']) > current_afk_index and replay['afks'][current_afk_index]['turn'] <= game.turn:
        afk = replay['afks'][current_afk_index]
        current_afk_index += 1
        index = afk['index']

        # If already dead, mark as dead general and neutralize if needed.
        if game.sockets[index] in game.deaths:
            game.try_neutralize_player(index)

        # Mark as AFK if not already dead.
        else:
            game.deaths.append(game.sockets[index])
            game.alive_players -= 1

    game.update()
    return current_move_index, current_afk_index


# Simulate the game!
while not game.is_over() and game.turn < 2000:
    module_logger.info(f'Game turn: {game.turn}')
    current_move_index, current_afk_index = next_turn(current_move_index, current_afk_index)
    module_logger.info(f'Simulated turn {game.turn}\t{game.alive_players} players left alive.\tLeader has {game.scores[0].total} army.')

    # Do whatever you want with the current game state. Some useful fields are:
    # game.turn: The current turn.
    # game.sockets: The array of players. Player game.sockets[i] has playerIndex i.
    # game.map: A Map object representing the current game state. See Map.js.
    # game.scores: An ordered (decreasing) array of scores. Each score object can be tied to a player by its .i field.
    # game.alivePlayers: The number of players left alive.
    # game.deaths: Dead players in chronological order: game.deaths[0] is the first player to die.

module_logger.info('Simulation ended.')
