import random
import time
from abc import abstractmethod, ABC

from envs._domain_impl.actions import Teleport, Yaw, Turn, Pitch, Attack, Craft, Use
from envs._domain_impl.inventory import Inventory
from envs._domain_impl.levels import Task

from envs._domain_impl.objects import Object

N_OPTIONS = 9

SLEEP = False

def sleep(duration):

    if SLEEP:
        time.sleep(duration)

def go_to(env, x, y, z):
    return env.step(Teleport(x, y, z))

class Option(ABC):

    @abstractmethod
    def execute(self, env):
        pass

class WalkToItem(Option):
    def __init__(self, item):
        self.id = 0
        self.target_x = item.x
        self.target_z = item.z
        self.item = item
        self.object = item

    def execute(self, env):
        x, z = env.get_x(), env.get_z()
        env.step(Yaw(0))
        sleep(0.2)
        obs, reward, done, info = go_to(env, self.target_x + 0.5, env.get_y(), self.target_z - 1.5)
        sleep(0.2)
        obs, _, _, info = env.step(Turn(0.0001))
        sleep(0.2)
        self.object.in_front = True
        return obs, reward, done, info

    def __str__(self):
        return "Walk to " + str(self.item.type)


class AttackItem(Option):
    def __init__(self, item):
        self.id = 1
        self.target_x = item.x
        self.target_z = item.z
        self.item = item
        self.object = item

    def execute(self, env):

        change_pitch = env.get_y() >= self.item.y

        if change_pitch:
            env.step(Pitch(15))
            sleep(0.2)
        for _ in range(30):
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
        return obs, reward, done, info

    def __str__(self):
        return "Attack " + str(self.item.type)


class PickupItem(Option):
    def __init__(self, item, early_stop=False):
        self.id = 2
        self.target_x = item.x
        self.target_z = item.z
        self.item = item
        self.object = item
        self.early_stop = early_stop

    def execute(self, env):
        obs, reward, done, info = go_to(env, self.target_x, env.get_y(), self.target_z)
        sleep(0.2)
        obs, _, _, info = env.step(Turn(0.0001))
        sleep(0.2)

        if Inventory.contains(env.env.get_observation(), self.object.type):
            self.item.picked = True
            self.item.dirty = True
            obs = env.redraw()
        else:
            print("FAIL PICK!!")
            if self.early_stop:
                done = True
        return obs, reward, done, info

    def __str__(self):
        return "Pickup " + str(self.item.type)


class WalkDoor(Option):
    def __init__(self, door, moving_north=True):
        door_x, door_z = door.x, door.z
        self.target_x = door_x + 0.5
        sign = -1 if moving_north else 1
        self.target_z = door_z + sign * 1.5
        self.yaw = 0 if moving_north else 180
        self.object = door

    def execute(self, env):
        env.step(Yaw(self.yaw))
        sleep(0.2)
        obs, reward, done, info = go_to(env, self.target_x, env.get_y(), self.target_z)
        sleep(0.2)
        obs, _, _, info = env.step(Turn(0.0001))
        sleep(0.2)
        self.object.in_front = True
        return obs, reward, done, info

    def __str__(self):
        return "Walk to door"


class WalkNorthDoor(WalkDoor):
    def __init__(self, door):
        super().__init__(door, True)
        self.id = 3

    def __str__(self):
        return "Walk north to door"


class WalkSouthDoor(WalkDoor):
    def __init__(self, door):
        super().__init__(door, False)
        self.id = 4

    def __str__(self):
        return "Walk south to door"


class WalkThroughDoor(Option):
    def __init__(self, door, moving_north=True):
        self.id = 5
        door_x, door_z = door.x, door.z
        self.target_x = door_x + 0.5
        sign = 1 if moving_north else -1
        self.target_z = door_z + sign * 4.5
        self.yaw = 0 if moving_north else 180
        self.object = door

    def execute(self, env):
        env.step(Yaw(self.yaw))
        sleep(0.2)
        obs, reward, done, info = go_to(env, self.target_x, env.get_y(), self.target_z)
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
        reward += 10
        info['goal_achieved'] = True
        return obs, reward, True, info


class ToggleDoor(Option):
    def __str__(self):
        return "Toggle Door "

    def __init__(self, door):
        self.door = door
        self.id = 8
        self.object = door

    def execute(self, env):
        if self.door.puzzle:
            curr = env.get_yaw()
            yaw = -35

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
            return obs, reward, done, info
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
        return obs, reward, done, info

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
        return obs, reward, done, info


def admissable_actions(env, doors, objects, early_stop=False):
    actions = []

    for i, door in enumerate(doors):

        if door.can_reach(env, moving_north=True):
            #   print("Can walk north to door {}".format(i + 1))
            actions.append(WalkSouthDoor(door))
        # else:
        #     print("Cannot walk north to door {}".format(i + 1))

        if door.can_reach(env, moving_north=False):
            #  print("Can walk south to door {}".format(i + 1))
            actions.append(WalkNorthDoor(door))
        # else:
        #     print("Cannot walk south to door {}".format(i + 1))

        if door.can_toggle(env, moving_north=True):
            actions.append(ToggleDoor(door))
            # print("Can toggle north door {}".format(i + 1))
        # else:
        #     print("Cannot open north door {}".format(i + 1))

        if door.can_toggle(env, moving_north=False):
            actions.append(ToggleDoor(door))
            #   print("Can toggle south door {}".format(i + 1))
        # else:
        #     print("Cannot open south door {}".format(i + 1))

        # TODO can only walk through door if standing AT door!!

        if door.is_close(env, moving_north=True) and door.can_walk_through(env, moving_north=True):
            #  print("Can walk north through door {}".format(i + 1))
            actions.append(WalkThroughDoor(door, moving_north=True))
        # else:
        #     print("Cannot walk north through door {}".format(i + 1))

        if door.is_close(env, moving_north=False) and door.can_walk_through(env, moving_north=False):
            #  print("Can walk south through door {}".format(i + 1))
            actions.append(WalkThroughDoor(door, moving_north=False))
            # else:
            #     print("Cannot walk south through door {}".format(i + 1))

    x, z = env.get_x(), env.get_z()
    for i, object in enumerate(objects):

        if object.can_reach(x, z):
            #  print("Can walk to {}".format(object.type))
            actions.append(WalkToItem(object))

        if object.can_pick(x, z):
            #   print("Can pick up {}".format(object.type))
            actions.append(PickupItem(object, early_stop=early_stop))

        if env.has_item("diamond_pickaxe") and object.can_attack(x, z):
            #  print("Can attack {}".format(object.type))
            if object.attackable:
                actions.append(AttackItem(object))

        if object.type == 'crafting_table' and object.can_attack(x, z):

            if env.has_item('gold_block'):
                actions.append(CraftItem([(1, 'gold_block')], 'gold_ingot'))

            if env.has_item('gold_ingot', 9) and env.has_item('redstone'):
                actions.append(CraftItem([(4, 'gold_ingot'), (1, 'redstone')], 'clock'))

        #if object.can_attack(x, z) and object.type == 'chest':
        if env.has_item('clock') and object.can_attack(x, z) and object.type == 'chest':
            actions.append(OpenChest(object))

    return actions


if __name__ == '__main__':
    env, _, _ = Task.generate(31)
    observation, doors, items, = env.reset(seed=31)

    for x in range(100):
        admissible_actions, disallowed = Task.admissable_actions(env, doors, items)
        action = random.choice(admissible_actions)
        print(action)
        next_observation, reward, done, _ = action.execute(env)
        if done:
            break


