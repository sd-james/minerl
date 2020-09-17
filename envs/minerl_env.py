import os
import pickle

import cv2
import gym
import numpy as np
from gym.envs.classic_control import rendering
from gym.spaces import Discrete
from tqdm.auto import trange

from envs._domain_impl.levels import Task
from envs._domain_impl.options import Option


def make_env(id: str, **kwargs):
    """
    Convenience function for calling gym.make
    """
    return gym.make(id, **kwargs)


def make_path(root,
              *args):
    """
    Creates a path from the given parameters
    :param root: the root of the path
    :param args: the elements of the path
    :return: a string, each element separated by a forward slash.
    """
    path = root
    if path.endswith('/'):
        path = path[0:-1]
    for element in args:
        if not isinstance(element, str):
            element = str(element)
        if element[0] != '/':
            path += '/'
        path += element
    return path


def get_dir_name(file):
    """
    Get the directory of the given file
    :param file: the file
    :return: the file's directory
    """
    return os.path.dirname(os.path.realpath(file))


class MineRLEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array', 'human']}

    """
    TODO: add description
    """

    def __init__(self, version=0, **kwargs):
        """
        Create a new instantiation of the Minecraft task
        """
        seeds = [31, 33, 76, 82, 92]
        self._seed = seeds[version]
        self.viewer = None
        self.early_stop = kwargs.get('early_stop', False)
        self.noisy = kwargs.get('noisy', True)
        self.version = version
        self._env, self._doors, self._objects = Task.generate(version, self.early_stop, self.noisy)

        self.option_names = ["WalkToItem",
                             "AttackItem",
                             "PickupItem",
                             "WalkNorthDoor",
                             "WalkSouthDoor",
                             "WalkThroughDoor",
                             "Craft",
                             "OpenChest",
                             "ToggleDoor",
                             ]
        self.action_space = Discrete(len(self.option_names))
        # self.observation_space = Box(np.float32(0.0), np.float32(1.0), shape=(len(s),))  # TODO

    def reset(self):
        observation, self._doors, self._objects, = self._env.reset(seed=self._seed)
        return observation

    def get_indexer(self):
        return self._env.object_views

    @property
    def available_mask(self):
        """
        Get a binary-encoded array of the options that can be run at the current state
        :return: a binary array specifying which options can be run
        """
        raise NotImplementedError

    def admissable_actions(self, positive_only=True):
        x = Task.admissable_actions(self._env, self._doors, self._objects, early_stop=self.early_stop, noisy=self.noisy)
        if positive_only:
            return x[0]
        return x


    def step(self, action):
        if isinstance(action, Option):
            return action.execute(self._env)
        return self._env.step(action)

    def render(self, mode='rgb_array'):

        rgb = self._env.render(mode='rgb_array')
        if mode == 'human':
            return
        elif mode == 'rgb_array':
            # draw it like gym
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(rgb)
            return rgb

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
        self._env.close()
