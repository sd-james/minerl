import enum
from abc import abstractmethod
from typing import Any, Dict, Tuple

import numpy as np
import gym


class View(enum.Enum):
    PROBLEM = 1,
    AGENT = 2,
    OBJECT = 3,


class MultiViewEnv(gym.Env):

    @abstractmethod
    def n_dims(self, view: View) -> int:
        """
        The dimensionality of the state space, depending on the view
        """
        pass

    @property
    @abstractmethod
    def agent_space(self) -> gym.Space:
        """
        The agent space size
        """
        pass

    @property
    @abstractmethod
    def object_space(self) -> gym.Space:
        """
        The object space size
        """
        pass

    @abstractmethod
    def split_observation(self, state: np.ndarray):
        pass

    def reset(self) -> Tuple[Any, Any]:
        state = super().reset()
        return self.split_observation(state)

    def step(self, action) -> Tuple[Any, Any, float, bool, Dict]:
        """
        Take a step in the environment
        :param action: the action to execute
        :return: the state, agent's observation, reward, done flag and info
        """
        state, reward, done, info = super().step(action)
        state, observation = self.split_observation(state)
        return state, observation, reward, done, info
