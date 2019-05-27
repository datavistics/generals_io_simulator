from pickle import load
import time

import requests
from tqdm import tqdm

from common.proj_paths import dirs


def download_giors(username, ids):
    assert isinstance(ids, list), f"Make ids a list, not a string"
    dir = dirs['replays.giors'] / username
    dir.mkdir(parents=True, exist_ok=True)  # Make dir if doesnt exist
    print(f"Adding {len(ids)} files to {str(dir)}")
    for id in tqdm(ids):
        gior_url = f'https://generalsio-replays-bot.s3.amazonaws.com/{id}.gior'
        r = requests.get(gior_url)
        with open(dir / f'{id}.gior', 'wb') as f:
            f.write(r.content)
        time.sleep(.1)


if __name__ == '__main__':
    user = 'Spraget'
    id = 'ruJMRCOa4'
    game_ids = load(open(dirs['replays.game_ids'] / f'{user}.pkl', 'rb'))
    game_ids_cleaned = [el['id'] for el in game_ids]
    download_giors(user, game_ids_cleaned)
