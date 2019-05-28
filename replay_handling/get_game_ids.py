import pickle
from datetime import datetime
from pprint import pprint
from time import sleep
from tqdm import trange

import requests

from common.proj_paths import dirs


def get_game_ids(username, count):
    """
    You can get count as a multiple of 20. Fn will round up: 39-> 40
    :param username:
    :param count:
    :return:
    """
    page_size = 20
    ids = []
    for offset in trange(0, count, page_size):
        url = f"http://generals.io/api/replaysForUsername?u={username}&offset={offset}&count={page_size}"
        r = requests.get(url)
        response_json = r.json()
        response_json_subset = [
            {'started': datetime.utcfromtimestamp(js['started'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
             'id': js['id']}
            for js in response_json]
        ids.extend(response_json_subset)
        sleep(2)
        print(f'Retrieved {offset + 20} total game ids')

    pprint(ids)
    return ids


if __name__ == '__main__':
    username = 'Spraget'
    ids = get_game_ids(username, 2000)
    with open(dirs['replays.game_ids']/f'{username}_games.pkl', 'wb') as f:
        pickle.dump(ids, f)
