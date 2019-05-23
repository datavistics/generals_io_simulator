import json
import logging.config
from logging import getLogger

from common.proj_paths import dirs
from hand_crafted.game import create_from_replay

logging.config.fileConfig(dirs['common'] / 'logging.ini')
module_logger = getLogger(__name__)

with open(dirs['hand_crafted'] / 'example.gioreplay', encoding='UTF-8') as json_file:
    replay = json.load(json_file)

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
        afk = replay.afks[current_afk_index]
        current_afk_index += 1
        index = afk['index']

        # If already dead, mark as dead general and neutralize if needed.
        if game.deaths.index(game.sockets[index]) >= 0:
            game.try_neutralize_player(index)

        # Mark as AFK if not already dead.
        else:
            game.deaths.append(game.sockets[index])
            game.alivePlayers -= 1

    game.update()
    return current_move_index, current_afk_index


# Simulate the game!

while not game.isOver() and game.turn < 2000:
    current_move_index, current_afk_index = next_turn(current_move_index, current_afk_index)
    module_logger.info(
        'Simulated turn ' + game.turn + '. ' + game.alivePlayers + ' players left alive. ' +
        'Leader has ' + game.scores[0].total + ' army.')

    # Do whatever you want with the current game state. Some useful fields are:
    # game.turn: The current turn.
    # game.sockets: The array of players. Player game.sockets[i] has playerIndex i.
    # game.map: A Map object representing the current game state. See Map.js.
    # game.scores: An ordered (decreasing) array of scores. Each score object can be tied to a player by its .i field.
    # game.alivePlayers: The number of players left alive.
    # game.deaths: Dead players in chronological order: game.deaths[0] is the first player to die.

module_logger.info('Simulation ended.')