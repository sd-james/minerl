import numpy as np
from PIL import Image

AIR = 0
GOLD = 1
REDSTONE = 2
PICKAXE = 3

ITEMS = {"gold_ingot": 0, "redstone": 1, "diamond_pickaxe": 2, 'clock': 3, 'gold_block': 4}


class Inventory:

    @staticmethod
    def size():
        return len(ITEMS)

    @staticmethod
    def to_vector(obs):
        rep = np.zeros(len(ITEMS))
        for i in range(9):
            val = obs["Hotbar_{}_item".format(i)]
            if val in ITEMS and obs["Hotbar_{}_size".format(i)] > 0:
                rep[ITEMS[val]] = 1
        return rep

    @staticmethod
    def contains(obs, item):
        for i in range(9):
            val = obs["Hotbar_{}_item".format(i)]
            if val in item and obs["Hotbar_{}_size".format(i)] > 0:
                return True
        return False

    @staticmethod
    def to_image(vec):
        name = list()

        is_masked = any(np.isnan(vec))
        for item, idx in ITEMS.items():
            if not np.isnan(vec[idx]):
                if vec[idx] > 0:
                    name.append(item)
                elif is_masked:
                    name.append('no_{}'.format(item))

        name = 'empty' if len(name) == 0 else ','.join(name)
        im = Image.open('env/images/{}.png'.format(name))
        size = (160, 20)
        im.thumbnail(size, Image.ANTIALIAS)
        return im
