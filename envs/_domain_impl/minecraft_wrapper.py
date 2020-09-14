import logging
import time

import gym
import numpy as np
from gym.spaces import Discrete

from envs._domain_impl.actions import Turn, Teleport, Yaw, Pitch
from envs._domain_impl.options import N_OPTIONS

logger = logging.getLogger(__name__)


class TeleportWrapper(gym.Wrapper):

    def _desc(self, x):
        if x == 0:
            return "WalkToItem"
        if x == 1:
            return "AttackItem"
        if x == 2:
            return "PickupItem"
        if x == 3:
            return "WalkNorthDoor"
        if x == 4:
            return "WalkSouthDoor"
        if x == 5:
            return "WalkThroughDoor"
        if x == 6:
            return "Craft"
        if x == 7:
            return "OpenChest"
        if x == 8:
            return "ToggleDoor"

    def __init__(self, env):
        super().__init__(env)
        self.action_space = Discrete(N_OPTIONS)


    def reset(self):
        self.env.reset()
        # add tiny rotation because minecraft doesn't redraw on teleport without movement :/
        obs, _, _, _ = self.step(Turn(0.0001))
        return obs

    def get_observation(self):

        obs, info = self.unwrapped._peek_obs()
        return info

    def get_image(self):
        obs, info = self.unwrapped._peek_obs()
        return obs['pov']

    def get_x(self):
        obs, info = self.unwrapped._peek_obs()
        return info['XPos']

    def get_y(self):
        obs, info = self.unwrapped._peek_obs()
        return info['YPos']

    def get_z(self):
        obs, info = self.unwrapped._peek_obs()
        return info['ZPos']

    def get_yaw(self):
        obs, info = self.unwrapped._peek_obs()
        return info['Yaw']

    def get_pitch(self):
        obs, info = self.unwrapped._peek_obs()
        return info['Pitch']

    def has_item(self, item, amount=1):
        obs, info = self.unwrapped._peek_obs()
        for i in range(9):
            val = info["Hotbar_{}_item".format(i)]
            if val == item and info["Hotbar_{}_size".format(i)] >= amount:
                return True
        return False


    def perturb(self):
  #      time.sleep(0.2)
        x, y, z, yaw, pitch = self.get_x(), self.get_y(), self.get_z(), self.get_yaw(), self.get_pitch()
        obs = self.set(x, y, z, yaw, pitch, noise=0.7)
        self.set(x, y, z, yaw, pitch, noise=0)
        return obs

    def noisy(self, x, noise):
        return np.random.normal(x, noise)

    def set(self, x, y, z, yaw, pitch, noise=0.01):

        actions = [Teleport(self.noisy(x, noise), self.noisy(y, 0), self.noisy(z, noise)),
                   Yaw(self.noisy(yaw, noise)), Pitch(self.noisy(pitch, noise)), Turn(0.0001)]
        obs = None
        for action in actions:
            obs, _, _, _ = self.step(action)
            #time.sleep(0.01)
        # time.sleep(0.2)
        return obs

    def set_pitch(self, pitch, noise=0.01):

        actions = [Pitch(self.noisy(pitch, noise)), Turn(0.0001)]
        obs = None
        for action in actions:
            obs, _, _, _ = self.step(action)
           # time.sleep(0.01)
        # time.sleep(0.2)
        return obs

