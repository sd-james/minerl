# import time
#
# import math
# import numpy as np
# from domain.actions import Yaw, Teleport, Turn, Use, Craft, Attack, Pitch, Noop, Forward, WalkForward, Action, Strafe
# from domain.inventory import Inventory
# from domain.levels import Task
# from domain.objects import Object
#
# N_OPTIONS = 9
#
#
# class TurnTo:
#
#     def __init__(self, target_yaw):
#         self.target_yaw = target_yaw
#
#     def execute(self, env):
#         yaw = env.get_yaw()
#         while abs(yaw - self.target_yaw) > 0.2:
#             sign = 1 if self.target_yaw > yaw else -1
#             env.step(Turn(sign * 0.02))
#             yaw = env.get_yaw()
#         return env.step(Turn(0))
#
# class WalkTo:
#     def __init__(self, target_x, target_z):
#         self.target_x = target_x + 0.5
#         self.target_z = target_z + 0.5
#         self.last_emit = None
#         self.current_x, self.current_z = None, None
#
#     def __step(self, env, action, sleep=0.2):
#         self.last_emit = env.step(action) if isinstance(action, Action) else action.execute(env)
#         time.sleep(sleep)
#         self.current_x, self.current_z = env.get_x(), env.get_z()
#         return self.last_emit
#
#     def _is_close(self):
#         return int(self.current_x) == int(self.target_x) and int(self.current_z) == int(self.target_z)
#
#
#     def execute(self, env):
#         x, z, yaw = env.get_x(), env.get_z(), env.get_yaw()
#         # self.__step(env, TurnTo(0))
#         facing_forward = -50 <= yaw <= 50
#
#         if not facing_forward and self.target_z > z:
#             self.__step(env, TurnTo(0))
#         elif facing_forward and self.target_z < z:
#             self.__step(env, TurnTo(180))
#
#         dx = env.get_x() - self.target_x
#         while abs(dx) > 0.2:
#             sign = 1 if dx > 0 else -1
#             self.__step(env, Strafe(sign * 0.1))
#             x = env.get_x()
#             dx = x - self.target_x
#             print('{} {} {}'.format(x, dx, self.target_x))
#         self.__step(env, Strafe(0))
#
#         dz = z - self.target_z
#         while abs(dz) > 0.2:
#             self.__step(env, WalkForward(0.1))
#             z = env.get_z()
#             dz = z - self.target_z
#             print('{} {} {}'.format(x, dx, self.target_x))
#         return self.__step(env, WalkForward(0))
#
#         # req_pitch = math.atan2(math.sqrt(dz * dz + dx * dx), 0) + math.pi
#         # req_yaw = self._get_yaw(x, z, self.target_x, self.target_z)
#         # self.__step(env, TurnTo(req_yaw))
#         #
#         # while not self._is_close():
#         #     self.__step(env, WalkForward(0.1))
#         # self.__step(env, TurnTo(yaw))
#
#     def _get_yaw(self, x1, z1, x2, z2):
#         dz = z1 - z2
#         dx = x1 - x2
#         return (math.atan2(dz, dx) + math.pi / 2) * 57.2957795130823209
#
#
# # class RealWalkToItem:
# #     def __init__(self, item):
# #         self.id = 0
# #         self.target_x = item.x
# #         self.target_z = item.z
# #         self.item = item
# #         self.object = item
# #
# #     def execute(self, env):
# #         x, z = env.get_x(), env.get_z()
# #         env.step(Yaw(0))
# #         time.sleep(0.2)
# #         obs, reward, done, info = env.step(Teleport(self.target_x + 0.5, env.get_y(), self.target_z - 2.5))
# #         time.sleep(0.2)
# #         obs, _, _, info = env.step(Turn(0.0001))
# #         time.sleep(0.2)
# #         self.object.in_front = True
# #         return obs, reward, done, info
#
#
# if __name__ == '__main__':
#     env, doors, objects = Task.generate(31)
#     env.reset()
#     time.sleep(1)
#     action = WalkTo((4, 5))
#     action.execute(env)
#
#
#     # if z < self.target_z:
#     #     # go north
#     #     yaw = 0
#     #     x = self.target_x + 0.5
#     #     z = self.target_z - 2
#     # elif z > self.target_z:
#     #     # go south
#     #     yaw = 180
#     #     x = self.target_x + 0.5
#     #     z = self.target_z + 2
#     # elif x < self.target_x:
#     #     # go west
#     #     yaw = -90
#     #     x = self.target_x - 2
#     #     z = self.target_z + 0.5
#     # else:
#     #     # go east
#     #     yaw = 90
#     #     x = self.target_x + 2
#     #     z = self.target_z + 0.5
#     #
#     # env.step(Yaw(yaw))
#     # time.sleep(0.2)
#     # obs, reward, done, info = env.step(Teleport(x, env.get_y(), z))
#     # time.sleep(0.2)
#     # obs, _, _, info = env.step(Turn(0.0001))
#     # time.sleep(0.2)
#     # return obs, reward, done, info
#
#     def __str__(self):
#         return "Walk to " + str(self.item.type)
#
# #
# # class AttackItem:
# #     def __init__(self, item):
# #         self.id = 1
# #         self.target_x = item.x
# #         self.target_z = item.z
# #         self.item = item
# #         self.object = item
# #
# #     def execute(self, env):
# #
# #         change_pitch = env.get_y() >= self.item.y
# #
# #         if change_pitch:
# #             env.step(Pitch(30))
# #             time.sleep(0.2)
# #         obs, reward, done, info = env.step(Attack(1))
# #         time.sleep(0.2)
# #         obs, _, _, info = env.step(Attack(0))
# #         time.sleep(0.2)
# #         if change_pitch:
# #             env.step(Pitch(0))
# #             time.sleep(0.2)
# #         obs, _, _, info = env.step(Turn(0.0001))
# #         self.item.attacked = True
# #         self.item.dirty = True
# #         obs = env.redraw()
# #         return obs, reward, done, info
# #
# #     def __str__(self):
# #         return "Attack " + str(self.item.type)
# #
# #
# # class PickupItem:
# #     def __init__(self, item):
# #         self.id = 2
# #         self.target_x = item.x
# #         self.target_z = item.z
# #         self.item = item
# #         self.object = item
# #
# #     def execute(self, env):
# #         obs, reward, done, info = env.step(Teleport(self.target_x, env.get_y(), self.target_z))
# #         time.sleep(0.2)
# #         obs, _, _, info = env.step(Turn(0.0001))
# #         time.sleep(0.2)
# #
# #         if Inventory.contains(env.env.get_observation(), self.object.type):
# #             self.item.picked = True
# #             self.item.dirty = True
# #             obs = env.redraw()
# #         else:
# #             print("FAIL PICK!!")
# #             done = True
# #         return obs, reward, done, info
# #
# #     def __str__(self):
# #         return "Pickup " + str(self.item.type)
# #
# #
# # class WalkDoor:
# #     def __init__(self, door, moving_north=True):
# #         door_x, door_z = door.x, door.z
# #         self.target_x = door_x + 0.5
# #         sign = -1 if moving_north else 1
# #         self.target_z = door_z + sign * 2.5
# #         self.yaw = 0 if moving_north else 180
# #         self.object = door
# #
# #     def execute(self, env):
# #         env.step(Yaw(self.yaw))
# #         time.sleep(0.2)
# #         obs, reward, done, info = env.step(Teleport(self.target_x, env.get_y(), self.target_z))
# #         time.sleep(0.2)
# #         obs, _, _, info = env.step(Turn(0.0001))
# #         time.sleep(0.2)
# #         self.object.in_front = True
# #         return obs, reward, done, info
# #
# #     def __str__(self):
# #         return "Walk to door"
# #
# #
# # class WalkNorthDoor(WalkDoor):
# #     def __init__(self, door):
# #         super().__init__(door, True)
# #         self.id = 3
# #
# #     def __str__(self):
# #         return "Walk north to door"
# #
# #
# # class WalkSouthDoor(WalkDoor):
# #     def __init__(self, door):
# #         super().__init__(door, False)
# #         self.id = 4
# #
# #     def __str__(self):
# #         return "Walk south to door"
# #
# #
# # class WalkThroughDoor:
# #     def __init__(self, door, moving_north=True):
# #         self.id = 5
# #         door_x, door_z = door.x, door.z
# #         self.target_x = door_x + 0.5
# #         sign = 1 if moving_north else -1
# #         self.target_z = door_z + sign * 4.5
# #         self.yaw = 0 if moving_north else 180
# #         self.object = door
# #
# #     def execute(self, env):
# #         env.step(Yaw(self.yaw))
# #         time.sleep(0.2)
# #         obs, reward, done, info = env.step(Teleport(self.target_x, env.get_y(), self.target_z))
# #         time.sleep(0.2)
# #         obs, _, _, info = env.step(Turn(0.0001))
# #         time.sleep(0.2)
# #         return obs, reward, done, info
# #
# #     def __str__(self):
# #         return "Walk through door"
# #
# #
# # class CraftItem:
# #     def __init__(self, ingredients, item):
# #         self.id = 6
# #         self.ingredients = ingredients  # list of tuples (kind, amount)
# #         self.item = item
# #
# #         # just need a dummy id
# #         self.object = Object(-1, -1, -1)
# #         self.object.id = 0
# #
# #     def __str__(self):
# #         return "Craft " + str(self.item)
# #
# #     def can_craft(self, env):
# #         for (type, amount) in self.ingredients:
# #             if not env.has_item(type, amount):
# #                 return False
# #         return True
# #
# #     def execute(self, env):
# #         obs, reward, done, info = env.step(Craft(self.item))
# #         obs, _, _, info = env.step(Turn(0.0001))
# #         time.sleep(0.2)
# #         return obs, reward, done, info
# #
# #
# # class OpenChest:
# #     def __init__(self, chest):
# #         self.id = 7
# #         self.chest = chest
# #         self.object = chest
# #
# #     def __str__(self):
# #         return "OpenChest"
# #
# #     def execute(self, env):
# #         actions = [Pitch(25), 0.2, Use(True), Use(False), 0.1, Pitch(0), 0.1, Turn(0.0001)]
# #         obs = None
# #         reward = 0
# #         info = {}
# #         for action in actions:
# #
# #             if isinstance(action, float):
# #                 time.sleep(action)
# #             else:
# #                 obs, r, done, info = env.step(action)
# #                 reward += r
# #         self.chest.dirty = True
# #         obs = env.redraw()
# #         reward += 10
# #         return obs, reward, True, info
# #
# #
# # class ToggleDoor:
# #     def __str__(self):
# #         return "Toggle Door "
# #
# #     def __init__(self, door):
# #         self.door = door
# #         self.id = 8
# #         self.object = door
# #
# #     def execute(self, env):
# #         if self.door.puzzle:
# #             curr = env.get_yaw()
# #             yaw = -25
# #             actions = [Yaw(yaw), 0.2, Use(True), Use(False), 0.1, Yaw(curr), 0.1, Turn(0.0001)]
# #             obs = None
# #             reward = 0
# #             done = False
# #             for action in actions:
# #
# #                 if isinstance(action, float):
# #                     time.sleep(action)
# #                 else:
# #                     obs, r, done, info = env.step(action)
# #                     reward += r
# #
# #             temp = info['observation']['LineOfSight']
# #             if 'type' in temp and 'iron_door' in temp['type'] and temp['inRange']:
# #                 self.door.closed = True
# #                 print("Door closed")
# #             else:
# #                 self.door.closed = False
# #                 print("Door open")
# #             self.door.dirty = True
# #             obs = env.redraw()
# #             # TODO FIX
# #             # return obs, reward, True, info
# #             return obs, reward, done, info
# #         else:
# #             if self.door.closed:
# #                 return self.open_door(env)
# #             return self.close_door(env)
# #
# #     def open_door(self, env):
# #         actions = [Use(True), Use(False)]
# #         reward = 0
# #         done = False
# #         for action in actions:
# #             obs, r, done, _ = env.step(action)
# #             reward += r
# #
# #         time.sleep(0.2)
# #         obs, _, _, info = env.step(Turn(0.0001))
# #         time.sleep(0.2)
# #
# #         temp = info['observation']['LineOfSight']
# #         if 'type' in temp and 'wooden_door' in temp['type'] and temp['inRange']:
# #             self.door.closed = True
# #             print("Door closed")
# #         else:
# #             self.door.closed = False
# #             print("Door open")
# #         self.door.dirty = True
# #         obs = env.redraw()
# #         # TODO FIX
# #         return obs, reward, done, info
# #
# #     def close_door(self, env):
# #         curr = env.get_yaw()
# #         if curr < 50:
# #             yaw = 10
# #         else:
# #             yaw = 170
# #         actions = [Yaw(yaw), 0.2, Use(True), Use(False), 0.1, Yaw(curr), 0.1, Turn(0.0001)]
# #
# #         obs = None
# #         reward = 0
# #         done = False
# #         for action in actions:
# #             if isinstance(action, float):
# #                 time.sleep(action)
# #             else:
# #                 obs, r, done, info = env.step(action)
# #                 reward += r
# #
# #         temp = info['observation']['LineOfSight']
# #         if 'type' in temp and 'wooden_door' in temp['type']:
# #             self.door.closed = True
# #             print("Door closed")
# #         else:
# #             self.door.closed = False
# #             print("Door open")
# #         self.door.dirty = True
# #         obs = env.redraw()
# #         return obs, reward, done, info
#
#
# # def admissable_actions(env, doors, objects):
# #     actions = []
# #
# #     for i, door in enumerate(doors):
# #
# #         if door.can_reach(env, moving_north=True):
# #             #   print("Can walk north to door {}".format(i + 1))
# #             actions.append(WalkSouthDoor(door))
# #         # else:
# #         #     print("Cannot walk north to door {}".format(i + 1))
# #
# #         if door.can_reach(env, moving_north=False):
# #             #  print("Can walk south to door {}".format(i + 1))
# #             actions.append(WalkNorthDoor(door))
# #         # else:
# #         #     print("Cannot walk south to door {}".format(i + 1))
# #
# #         if door.can_toggle(env, moving_north=True):
# #             actions.append(ToggleDoor(door))
# #             # print("Can toggle north door {}".format(i + 1))
# #         # else:
# #         #     print("Cannot open north door {}".format(i + 1))
# #
# #         if door.can_toggle(env, moving_north=False):
# #             actions.append(ToggleDoor(door))
# #             #   print("Can toggle south door {}".format(i + 1))
# #         # else:
# #         #     print("Cannot open south door {}".format(i + 1))
# #
# #         # TODO can only walk through door if standing AT door!!
# #
# #         if door.is_close(env, moving_north=True) and door.can_walk_through(env, moving_north=True):
# #             #  print("Can walk north through door {}".format(i + 1))
# #             actions.append(WalkThroughDoor(door, moving_north=True))
# #         # else:
# #         #     print("Cannot walk north through door {}".format(i + 1))
# #
# #         if door.is_close(env, moving_north=False) and door.can_walk_through(env, moving_north=False):
# #             #  print("Can walk south through door {}".format(i + 1))
# #             actions.append(WalkThroughDoor(door, moving_north=False))
# #             # else:
# #             #     print("Cannot walk south through door {}".format(i + 1))
# #
# #     x, z = env.get_x(), env.get_z()
# #     for i, object in enumerate(objects):
# #
# #         if object.can_reach(x, z):
# #             #  print("Can walk to {}".format(object.type))
# #             actions.append(WalkToItem(object))
# #
# #         if object.can_pick(x, z):
# #             #   print("Can pick up {}".format(object.type))
# #             actions.append(PickupItem(object))
# #
# #         if env.has_item("diamond_pickaxe") and object.can_attack(x, z):
# #             #  print("Can attack {}".format(object.type))
# #             if object.attackable:
# #                 actions.append(AttackItem(object))
# #
# #         if object.type == 'crafting_table' and object.can_attack(x, z):
# #
# #             if env.has_item('gold_block'):
# #                 actions.append(CraftItem([(1, 'gold_block')], 'gold_ingot'))
# #
# #             if env.has_item('gold_ingot', 9) and env.has_item('redstone'):
# #                 actions.append(CraftItem([(4, 'gold_ingot'), (1, 'redstone')], 'clock'))
# #
# #         if env.has_item('clock') and object.can_attack(x, z) and object.type == 'chest':
# #             actions.append(OpenChest(object))
# #
# #     return actions
