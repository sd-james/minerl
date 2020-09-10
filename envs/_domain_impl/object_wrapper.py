from collections import OrderedDict

import gym

import numpy as np
import time

from envs._domain_impl.actions import Craft, Turn, Noop
from envs._domain_impl.inventory import Inventory


class ObjectWrapper(gym.ObservationWrapper):
    def __init__(self, env, doors, objects, agent_only=False):
        super().__init__(env)
        self.doors = doors
        self.objects = objects
        self.object_views = OrderedDict()
        self.agent_only = agent_only
        if not self.agent_only:
            for door in doors:
                self.object_views[door] = None
            for object in objects:
                if object.type != 'crafting_table':  # ignore crafting table. Not manipulable
                    self.object_views[object] = None

    def step(self, action):
        for object in self.objects:
            if object.type == 'crafting_table' and (isinstance(action, Craft) or isinstance(action, Turn)):
                pass
            else:
                object.in_front = False
        for door in self.doors:
            door.in_front = True
        observation, reward, done, info = super().step(action)
        return observation, reward, done, info

    def reset(self, seed=None):


        if seed is not None:
            from envs._domain_impl.levels import Task
            doors, objects = Task.create_objects(seed)
            self.doors = doors
            self.objects = objects
            self.object_views = OrderedDict()
            if not self.agent_only:
                for door in doors:
                    self.object_views[door] = None
                for object in objects:
                    if object.type != 'crafting_table':  # ignore crafting table. Not manipulable
                        self.object_views[object] = None
            return super().reset(), doors, objects
        return super().reset()

    def get_index(self, object_id):
        """"
        Get the index in the state space corresponding to the object with the given ID
        """
        if object_id == 0:  # this is the crafting table, so ignore
            return 0
        for i, object in enumerate(self.object_views.keys()):
            if object.id == object_id:
                return i + 1  # plus 1 because first is always agent view
        raise ValueError

    def observation(self, observation):
        # return observation

        _, info = self.unwrapped._peek_obs()
        observation = observation['pov']
        x, y, z, yaw, pitch = info['XPos'], info['YPos'], info['ZPos'], info['Yaw'], info['Pitch']
        facing_forward = -20 <= yaw <= 20
        obs = [observation]

        moved = False
        if not self.agent_only:
            # observation is the agent's view
            for object, view in self.object_views.items():

                if self.object_views[object] is None:
                    print("Drawing " + str(object))
                    new_view = self._redraw_object(object)
                    obs.append(new_view)
                    self.object_views[object] = new_view
                    object.dirty = False
                    self.env.set(x, y, z, yaw, pitch)

                elif object.dirty:
                    _, _, _, n_pitch, _ = object.look_at()
                    if abs(pitch - n_pitch) < 15:
                        new_view = observation
                        # print("Saving " + str(object))
                    else:
                        # print((pitch, n_pitch))
                        # print("Redrawing " + str(object))
                        new_view = self._redraw_object(object, True)
                        self.env.set_pitch(pitch)

                    obs.append(new_view)
                    self.object_views[object] = new_view
                    object.dirty = False
                else:
                    obs.append(self.object_views[object])

        # time.sleep(0.2)
        obs.append(Inventory.to_vector(info))
        obs.append(np.array([x, z, int(facing_forward)]))
        return obs

    def _redraw_object(self, object, pitch_only=False):

        n_x, n_y, n_z, n_pitch, n_yaw = object.look_at()
        if pitch_only:
            self.env.set_pitch(n_pitch)
        else:
            self.env.set(n_x + 0.5, n_y, n_z, n_yaw, n_pitch)
        time.sleep(0.2)
        return self.env.get_image()

    def get_x(self):
        return self.env.get_x()

    def get_y(self):
        return self.env.get_y()

    def get_z(self):
        return self.env.get_z()

    def get_pitch(self):
        return self.env.get_pitch()

    def get_yaw(self):
        return self.env.get_yaw()

    def is_facing_north(self):
        return -10 <= self.get_yaw() <= 10

    def has_item(self, item, amount=1):
        return self.env.has_item(item, amount)

    def redraw(self):
        obs, _, _, _ = self.step(Noop())
        return obs
