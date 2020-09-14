import pickle
import time

import cv2
import gym
import numpy as np
from tqdm import trange
import minerl
from envs.minerl_env import MineRLEnv


def process(s):
    n = list()
    for x in s:
        if len(x.shape) == 3:
            x = np.uint8(np.dot(x[..., :3], [0.299, 0.587, 0.114]))
            x = cv2.resize(x, (160, 120), interpolation=cv2.INTER_AREA)
        n.append(x)
    return n


def add(data, s, a, s_prime):
    s = process(s)
    s_prime = process(s_prime)
    data.append((a.id, a.object.id, s, s_prime))


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    env = MineRLEnv(version=0)
    for episode in trange(5, desc='Episode'):
        state = env.reset()
        for _ in range(1000):
            action = np.random.choice(env.admissable_actions())
            print(action)
            print(env.admissable_actions())
            next_state, reward, done, info = env.step(action)
            state = next_state
            print(state[9])
            time.sleep(5)
            if done:
                found = True
                break
        env.close()

    exit(0)

    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    # path = deque([1, 1, 0, 0, 1, 2, 2, 3, 1, 1, 2, 1, 1])

    data = list()
    for version in trange(1, 2, desc='Task'):
        found = False
        env = MineRLEnv(version=version)
        for episode in trange(5, desc='Episode'):
            state = env.reset()
            for _ in range(1000):
                action = np.random.choice(env.admissable_actions())
                print(action)
                print(env.admissable_actions())
                next_state, reward, done, info = env.step(action)
                add(data, state, action, next_state)
                state = next_state
                print(state[9])
                if done:
                    found = True
                    break
        env.close()
        if not found:
            print("Didn't finish level {}".format(version))
            exit(0)
        else:
            print("Finished level {}".format(version))
        with open('test_{}.pkl'.format(version), 'wb') as file:
            pickle.dump(data, file)
