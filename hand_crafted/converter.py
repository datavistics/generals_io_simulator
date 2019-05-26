import json
from pprint import pprint

from lzstring import LZString, _decompress

from common.proj_paths import dirs


def decompressFromUint8Array(compressed):
    lz = LZString()
    if compressed is None:
        return ""
    if compressed == "":
        return None
    buf = [None for _ in range(int(len(compressed) / 2))]
    for i in range(len(buf)):
        buf[i] = compressed[i * 2] * 256 + compressed[i * 2 + 1]

    r = _decompress(len(buf), 32768, lambda index: buf[index])
    return r


def deserialize(serialized):
    print(len(serialized))
    lz = decompressFromUint8Array(serialized)
    return lz


def deserialize_afk(afks):
    ret_afks = []
    keys = ['index', 'turn']
    for afk in afks:
        ret_afks.append(dict(zip(keys, afk)))
    return ret_afks


def deserialize_move(moves):
    ret_move = []
    keys = ['index', 'start', 'end', 'is50', 'turn']
    for move in moves:
        ret_move.append(dict(zip(keys, move)))
    return ret_move


def convert_dense_to_sparse(obj):
    replay = {}
    replay['version'] = obj[0]
    replay['id'] = obj[1]
    replay['mapWidth'] = obj[2]
    replay['mapHeight'] = obj[3]
    replay['usernames'] = obj[4]
    replay['stars'] = obj[5]
    replay['cities'] = obj[6]
    replay['cityArmies'] = obj[7]
    replay['generals'] = obj[8]
    replay['mountains'] = obj[9]
    replay['moves'] = deserialize_move(obj[10])
    replay['afks'] = deserialize_afk(obj[11])
    replay['teams'] = obj[12]
    replay['map_title'] = obj[13]  # only available when version >= 7
    return replay


def gior_to_replay(file):
    with open(file, 'rb') as f:
        ser = f.read()

    des = deserialize(ser)
    replay = convert_dense_to_sparse(json.loads(des))
    return replay


if __name__ == '__main__':
    file = dirs['replays'] / 'BeKdahWa4.gior'
    replay = gior_to_replay(file)
    pprint(replay)
