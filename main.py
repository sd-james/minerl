import pickle
import time
from collections import deque

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

    data = list()
    for version in trange(0, 5, desc='Task'):
        found = False

        env = MineRLEnv(version=version)
        for episode in trange(5, desc='Episode'):
            state = env.reset()
            for _ in range(1000):
                allowed = env.admissable_actions()
                action = np.random.choice(allowed)
                print(allowed)
                print(action)
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
        else:
            print("Finished level {}".format(version))
