import random
import gym
from envs._domain_impl.levels.layout import MAPS
from envs._domain_impl.minecraft_wrapper import TeleportWrapper
from envs._domain_impl.object_wrapper import ObjectWrapper
from envs._domain_impl.objects import Rect, Block, Item, Door
from envs._domain_impl.options import WalkSouthDoor, ToggleDoor, WalkThroughDoor, \
    WalkToItem, AttackItem, PickupItem, CraftItem, OpenChest, WalkNorthDoor


def sample(room):
    room = tuple(room)
    buffer = 2

    return [random.randint(room[0] + buffer, room[2] - buffer + 1), 55, random.randint(room[1] + buffer + 2,
                                                                                       room[3] - buffer + 1)]


def make_object(id, object_creator, room):
    pos = sample(room)
    if id == 1:
        x = 1 if random.random() else 8
        pos[0] = x
        # pos[0] = 8

    object = object_creator(pos, room)
    if 'pickaxe' in object.type:
        object.set_look_at(pos[0], pos[1], pos[2] - 1, 45, 0)
    else:
        object.set_look_at(pos[0], pos[1], pos[2] - 2, 30, 0)
    object.id = id
    return object


def _make_block(name, attackable=True):
    return lambda pos, room: Block(*pos, name, room, attackable=attackable)


def _make_item(name):
    return lambda pos, room: Item(*pos, name, room)


def make_door(id, loc, north_room, south_room, puzzle=False):
    door = Door(loc[0], loc[1], north_room, south_room, puzzle)
    door.set_look_at(loc[0], 55, loc[1] - 2, 7, 0)
    door.id = id
    return door


def create_objects(seed):
    layout = MAPS[seed]
    random.seed(seed)

    room1 = Rect(0, 0, 9, 6)
    room2 = Rect(0, 8, 9, 14)
    room3 = Rect(0, 16, 9, 22)
    room4 = Rect(0, 24, 9, 30)
    room5 = Rect(0, 32, 9, 39)

    door1, door2, door3, door4 = layout['door1'], layout['door2'], layout['door3'], layout['door4']
    gold_pos = layout['gold']

    rooms = [room1, room2, room3, room4]

    if random.random():
        p_room = room1
        rooms.pop(0)
    else:
        p_room = room2
        rooms.pop(1)

    random.shuffle(rooms)
    pickaxe = make_object(1, _make_item('diamond_pickaxe'), p_room)
    table = make_object(0, _make_block('crafting_table', False), rooms[0])
    chest = make_object(2, _make_block('chest', False), rooms[1])
    ore = make_object(3, _make_block('redstone_ore'), rooms[2])

    gold = Block(gold_pos[0], gold_pos[1], gold_pos[2], "gold_block", room5)
    gold.set_look_at(gold_pos[0], gold_pos[1], gold_pos[2] - 2, 30, 0)
    gold.id = 4

    objects = [table, pickaxe, chest, ore]  # leave gold out since env creates it!

    objects.append(gold)

    door_1 = make_door(5, door1, room2, room1, layout['puzzles'][0])
    door_2 = make_door(6, door2, room3, room2, layout['puzzles'][1])
    door_3 = make_door(7, door3, room4, room3, layout['puzzles'][2])
    door_4 = make_door(8, door4, room5, room4, layout['puzzles'][3])

    doors = [door_1, door_2, door_3, door_4]

    return doors, objects


def generate(version, early_stop, **kwargs):
    seeds = [31, 33, 76, 82, 92]
    seed = seeds[version]


    layout = MAPS[seed]
    random.seed(seed)

    room1 = Rect(0, 0, 9, 6)
    room2 = Rect(0, 8, 9, 14)
    room3 = Rect(0, 16, 9, 22)
    room4 = Rect(0, 24, 9, 30)
    room5 = Rect(0, 32, 9, 39)

    door1, door2, door3, door4 = layout['door1'], layout['door2'], layout['door3'], layout['door4']
    gold_pos = layout['gold']

    rooms = [room1, room2, room3, room4]

    if random.random():
        p_room = room1
        rooms.pop(0)
    else:
        p_room = room2
        rooms.pop(1)

    random.shuffle(rooms)
    pickaxe = make_object(1, _make_item('diamond_pickaxe'), p_room)
    table = make_object(0, _make_block('crafting_table', False), rooms[0])
    chest = make_object(2, _make_block('chest', False), rooms[1])
    ore = make_object(3, _make_block('redstone_ore'), rooms[2])
    gold = Block(gold_pos[0], gold_pos[1], gold_pos[2], "gold_block", room5)
    gold.set_look_at(gold_pos[0], gold_pos[1], gold_pos[2] - 2, 30, 0)
    gold.id = 4

    objects = [table, pickaxe, chest, ore, gold]
    if early_stop:
        name = 'ChestClockEarlyStop{}-v0'.format(version)
    else:
        name = 'ChestClock{}-v0'.format(version)

    env = TeleportWrapper(gym.make(name))

    door_1 = make_door(5, door1, room2, room1, layout['puzzles'][0])
    door_2 = make_door(6, door2, room3, room2, layout['puzzles'][1])
    door_3 = make_door(7, door3, room4, room3, layout['puzzles'][2])
    door_4 = make_door(8, door4, room5, room4, layout['puzzles'][3])

    doors = [door_1, door_2, door_3, door_4]

    env = ObjectWrapper(env, doors, objects, agent_only=kwargs.get('agent_only', False))

    return env, doors, objects


def admissable_actions(env, doors, objects, early_stop=False):
    actions = []

    disallowed = []

    for i, door in enumerate(doors):

        if door.can_reach(env, moving_north=True):
            #   print("Can walk north to door {}".format(i + 1))
            actions.append(WalkNorthDoor(door))
        else:
            disallowed.append(WalkNorthDoor(door))
            # print("Cannot walk north to door {}".format(i + 1))

        if door.can_reach(env, moving_north=False):
            #  print("Can walk south to door {}".format(i + 1))
            actions.append(WalkSouthDoor(door))
        else:
            disallowed.append(WalkSouthDoor(door))
            # print("Cannot walk south to door {}".format(i + 1))

        if door.can_toggle(env, moving_north=True):
            actions.append(ToggleDoor(door))
            # print("Can toggle north door {}".format(i + 1))
        else:
            disallowed.append(ToggleDoor(door))
            # print("Cannot open north door {}".format(i + 1))

        if door.can_toggle(env, moving_north=False):
            actions.append(ToggleDoor(door))
            #   print("Can toggle south door {}".format(i + 1))
        else:
            disallowed.append(ToggleDoor(door))
        # print("Cannot open south door {}".format(i + 1))

        # TODO can only walk through door if standing AT door!!

        if door.is_close(env, moving_north=True) and door.can_walk_through(env, moving_north=True):
            #  print("Can walk north through door {}".format(i + 1))
            actions.append(WalkThroughDoor(door, moving_north=True))
        else:
            disallowed.append(WalkThroughDoor(door, moving_north=True))
        # print("Cannot walk north through door {}".format(i + 1))

        if door.is_close(env, moving_north=False) and door.can_walk_through(env, moving_north=False):
            #  print("Can walk south through door {}".format(i + 1))
            actions.append(WalkThroughDoor(door, moving_north=False))
        else:
            disallowed.append(WalkThroughDoor(door, moving_north=False))
            #     print("Cannot walk south through door {}".format(i + 1))

    x, z = env.get_x(), env.get_z()
    for i, object in enumerate(objects):

        if object.can_reach(x, z):
            #  print("Can walk to {}".format(object.type))
            actions.append(WalkToItem(object))
        else:
            disallowed.append(WalkToItem(object))

        if object.can_pick(x, z):
            #   print("Can pick up {}".format(object.type))
            actions.append(PickupItem(object, early_stop=early_stop))
        else:
            disallowed.append(PickupItem(object, early_stop=early_stop))

        if env.has_item("diamond_pickaxe") and object.can_attack(x, z):
            #  print("Can attack {}".format(object.type))
            if object.attackable:
                actions.append(AttackItem(object))
            else:
                disallowed.append(AttackItem(object))
        else:
            disallowed.append(AttackItem(object))

        if object.type == 'crafting_table' and object.can_attack(x, z):

            if env.has_item('gold_block'):
                actions.append(CraftItem([(1, 'gold_block')], 'gold_ingot'))
            else:
                disallowed.append(CraftItem([(1, 'gold_block')], 'gold_ingot'))

            if env.has_item('gold_ingot', 9) and env.has_item('redstone'):
                actions.append(CraftItem([(4, 'gold_ingot'), (1, 'redstone')], 'clock'))
            else:
                disallowed.append(CraftItem([(4, 'gold_ingot'), (1, 'redstone')], 'clock'))
        else:
            disallowed.append(CraftItem([(1, 'gold_block')], 'gold_ingot'))
            disallowed.append(CraftItem([(4, 'gold_ingot'), (1, 'redstone')], 'clock'))

        if env.has_item('clock') and object.can_attack(x, z) and object.type == 'chest':
            actions.append(OpenChest(object))
        else:
            disallowed.append(OpenChest(object))

    return actions, disallowed
