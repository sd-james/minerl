import random
from typing import Tuple, Any

import numpy as np
from gym import Space

from envs.minerl_env import MineRLEnv
from envs.multiview_env import MultiViewEnv, View


class MultiMineRLEnv(MultiViewEnv, MineRLEnv):

    def __init__(self, version_number: int, **kwargs):
        super().__init__(version=version_number, **kwargs)
        self._version_number = version_number

    @property
    def object_space(self) -> Space:
        raise NotImplementedError

    def n_dims(self, view: View) -> int:
        """
        The dimensionality of the state space, depending on the view
        """
        if view == View.PROBLEM:
            return self.observation_space.shape[-1]
        elif view == View.AGENT:
            raise NotImplementedError
            # return len(self.agent_space.nvec)
        elif view == View.OBJECT:
            return len(self._env.object_views) + 1 + 1  # one for agent POV, one for inventory!
            # return len(self._env.object_views) + Inventory.size() + 1  # one for agent POV

    def split_observation(self, obs: np.ndarray) -> Tuple[Any, Any]:

        # objects = list(obs[0: -2])
        # inventory = obs[-2]
        # for x in inventory:
        #     objects.append(np.ones(shape=(1)) * x)
        objects = list(obs[0: -1])

        observation = np.array(objects)
        state = obs[-1]
        return state, observation

    def __str__(self):
        return "MineRL-v{}".format(self._version_number)

    def describe_option(self, option: int) -> str:
        return self.option_names[option]

    @property
    def task_id(self):
        return self._version_number


if __name__ == '__main__':

    random.seed(0)
    np.random.seed(0)

    for i in range(0, 5):
        env = MultiMineRLEnv(i)
        solved = False
        while not solved:
            state, obs = env.reset()
            for N in range(1000):
                action = np.random.choice(env.admissable_actions())
                print(action)
                next_state, next_obs, reward, done, info = env.step(action)
                env.render('human')
                if done:
                    print("WIN: {}".format(N))
                    print(info)
                    solved = True
                    env.close()
                    break
                # time.sleep(0.5)
