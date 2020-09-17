import math
import random
import time
from abc import abstractmethod, ABC

from envs._domain_impl.actions import Teleport, Yaw, Turn, Pitch, Attack, Craft, Use
from envs._domain_impl.inventory import Inventory
from envs._domain_impl.levels import Task

from envs._domain_impl.objects import Object

N_OPTIONS = 9

SLEEP = False


def get_reward(x, z, target_x, target_z):
    return -math.sqrt((x - target_x) ** 2 + (z - target_z) ** 2)


def sleep(duration):
    if SLEEP:
        time.sleep(duration)


def go_to(env, x, y, z, noisy):
    a, b = env.get_x(), env.get_z()
    obs, _, done, info = env.step(Teleport(x, y, z, noise=noisy))
    env.step(Teleport(x, y, z, noise=False))
    return obs, get_reward(a, b, x, z), done, info


class Option(ABC):

    @abstractmethod
    def execute(self, env):
        pass


class WalkToItem(Option):
    def __init__(self, item, noisy=True):
        self.id = 0
        self.noisy = noisy
        self.target_x = item.x
        self.target_z = item.z
        self.item = item
        self.object = item

    def execute(self, env):
        env.step(Yaw(0))
        sleep(0.2)
        obs, reward, done, info = go_to(env, self.target_x + 0.5, env.get_y(), self.target_z - 2.5, noisy=self.noisy)
        # obs, reward, done, info = go_to(env, self.target_x + 0.5, env.get_y(), self.target_z - 1.5)
        sleep(0.2)
        obs, _, _, info = env.step(Turn(0.0001))
        sleep(0.2)
        self.object.in_front = True
        return obs, reward, done, info

    def __str__(self):
        return "Walk to " + str(self.item.type)


class AttackItem(Option):
    def __init__(self, item, noisy=True):
        self.id = 1
        self.noisy = noisy

        self.target_x = item.x
        self.target_z = item.z
        self.item = item
        self.object = item

    def execute(self, env):

        change_pitch = env.get_y() >= self.item.y

        if change_pitch:
            # env.step(Pitch(15))
            env.step(Pitch(30))
            sleep(0.2)
        for _ in range(20):
            obs, reward, done, info = env.step(Attack(1))
        sleep(0.2)
        obs, _, _, info = env.step(Attack(0))
        sleep(0.2)
        if change_pitch:
            env.step(Pitch(0))
            sleep(0.2)
        obs, _, _, info = env.step(Turn(0.0001))
        self.item.attacked = True
        self.item.dirty = True
        # self.item.in_front = True
        obs = env.redraw()
        reward = -10
        return obs, reward, done, info

    def __str__(self):
        return "Attack " + str(self.item.type)


class PickupItem(Option):
    def __init__(self, item, early_stop=False, noisy=True):
        self.id = 2
        self.noisy = noisy

        self.target_x = item.x
        self.target_z = item.z
        self.item = item
        self.object = item
        self.early_stop = early_stop

    def execute(self, env):
        y = env.get_y()
        for delta_x in [-0.5, 0, 0.5]:
            for delta_z in [-0.5, 0, 0.5]:
                go_to(env, self.target_x + delta_x, y, self.target_z + delta_z, noisy=self.noisy)
        obs, reward, done, info = go_to(env, self.target_x, y, self.target_z, noisy=self.noisy)
        sleep(0.2)
        obs, _, _, info = env.step(Turn(0.0001))
        sleep(0.2)

        if Inventory.contains(env.env.get_observation(), self.object.type):
            self.item.picked = True
            self.item.dirty = True
            obs = env.redraw()
        else:
            self.item.picked = True  # we tried, it failed. Let's move on
            print("FAIL PICK!!")
            if self.early_stop:
                done = True
                reward = -100

        return obs, reward, done, info

    def __str__(self):
        return "Pickup " + str(self.item.type)


class WalkDoor(Option):
    def __init__(self, door, moving_north=True, noisy=True):
        door_x, door_z = door.x, door.z
        self.noisy = noisy
        self.target_x = door_x + 0.5
        sign = -1 if moving_north else 1
        # self.target_z = door_z + sign * 1.5
        self.target_z = door_z + sign * 2.5
        self.yaw = 0 if moving_north else 180
        self.object = door

    def execute(self, env):
        env.step(Yaw(self.yaw))
        sleep(0.2)
        obs, reward, done, info = go_to(env, self.target_x, env.get_y(), self.target_z, noisy=self.noisy)
        sleep(0.2)
        obs, _, _, info = env.step(Turn(0.0001))
        sleep(0.2)
        self.object.in_front = True
        return obs, reward, done, info

    def __str__(self):
        return "Walk to door"


class WalkNorthDoor(WalkDoor):
    def __init__(self, door, noisy=True):
        super().__init__(door, True, noisy=noisy)
        self.id = 3

    def __str__(self):
        return "Walk north to door"


class WalkSouthDoor(WalkDoor):
    def __init__(self, door, noisy=True):
        super().__init__(door, False, noisy=noisy)
        self.id = 4

    def __str__(self):
        return "Walk south to door"


class WalkThroughDoor(Option):
    def __init__(self, door, moving_north=True, noisy=True):
        self.id = 5
        self.noisy = noisy

        door_x, door_z = door.x, door.z
        self.target_x = door_x + 0.5
        sign = 1 if moving_north else -1
        self.target_z = door_z + sign * 4.5
        self.yaw = 0 if moving_north else 180
        self.object = door

    def execute(self, env):
        env.step(Yaw(self.yaw))
        sleep(0.2)
        obs, reward, done, info = go_to(env, self.target_x, env.get_y(), self.target_z, noisy=self.noisy)
        sleep(0.2)
        obs, _, _, info = env.step(Turn(0.0001))
        sleep(0.2)
        return obs, reward, done, info

    def __str__(self):
        return "Walk through door"


class CraftItem(Option):
    def __init__(self, ingredients, item):
        self.id = 6
        self.ingredients = ingredients  # list of tuples (kind, amount)
        self.item = item

        # just need a dummy id
        self.object = Object(-1, -1, -1)
        self.object.id = 0

    def __str__(self):
        return "Craft " + str(self.item)

    def can_craft(self, env):
        for (type, amount) in self.ingredients:
            if not env.has_item(type, amount):
                return False
        return True

    def execute(self, env):
        obs, reward, done, info = env.step(Craft(self.item))
        obs, _, _, info = env.step(Turn(0.0001))
        sleep(0.2)
        reward = 10
        return obs, reward, done, info


class OpenChest(Option):
    def __init__(self, chest):
        self.id = 7
        self.chest = chest
        self.object = chest

    def __str__(self):
        return "OpenChest"

    def execute(self, env):
        actions = [Pitch(25), 0.2, Use(True), Use(False), 0.1, Pitch(0), 0.1, Turn(0.0001)]
        obs = None
        reward = 0
        info = {}
        for action in actions:

            if isinstance(action, float):
                sleep(action)
            else:
                obs, r, done, info = env.step(action)
                reward += r
        self.chest.dirty = True
        obs = env.redraw()
        reward = 100
        info['goal_achieved'] = True
        return obs, reward, True, info


class ToggleDoor(Option):
    def __str__(self):
        return "Toggle Door "

    def __init__(self, door, noisy=True):
        self.door = door
        self.id = 8
        self.noisy = noisy
        self.object = door

    def execute(self, env):
        if self.door.puzzle:
            curr = env.get_yaw()
            # yaw = -35
            yaw = -25
            actions = [Yaw(yaw), 0.2, Use(True), Use(False), 0.1, Yaw(curr), 0.1, Turn(0.0001)]
            obs = None
            reward = 0
            done = False
            for action in actions:
                if isinstance(action, float):
                    sleep(action)
                else:
                    obs, r, done, info = env.step(action)
                    reward += r

            temp = info['LineOfSight']
            if 'type' in temp and 'iron_door' in temp['type'] and temp['inRange']:
                self.door.closed = True
                # print("Door closed")
            else:
                self.door.closed = False
                # print("Door open")
            self.door.dirty = True
            obs = env.redraw()
            # TODO FIX
            # return obs, reward, True, info
            return obs, -10, done, info
        else:
            if self.door.closed:
                return self.open_door(env)
            return self.close_door(env)

    def open_door(self, env):
        actions = [Use(True), Use(False)]
        reward = 0
        done = False
        for action in actions:
            obs, r, done, _ = env.step(action)
            reward += r

        sleep(0.2)
        obs, _, _, info = env.step(Turn(0.00001))
        sleep(0.2)

        temp = info['LineOfSight']
        if 'type' in temp and 'wooden_door' in temp['type'] and temp['inRange']:
            self.door.closed = True
            # print("Door closed")
        else:
            self.door.closed = False
            # print("Door open")
        self.door.dirty = True
        obs = env.redraw()
        # TODO FIX
        return obs, -10, done, info

    def close_door(self, env):
        curr = env.get_yaw()
        if curr < 50:
            yaw = 10
        else:
            yaw = 170
        actions = [Yaw(yaw), 0.2, Use(True), Use(False), 0.1, Yaw(curr), 0.1, Turn(0.0001)]

        obs = None
        reward = 0
        done = False
        for action in actions:
            if isinstance(action, float):
                sleep(action)
            else:
                obs, r, done, info = env.step(action)
                reward += r

        temp = info['LineOfSight']
        if 'type' in temp and 'wooden_door' in temp['type']:
            self.door.closed = True
            # print("Door closed")
        else:
            self.door.closed = False
            # print("Door open")
        self.door.dirty = True
        obs = env.redraw()
        return obs, -10, done, info

