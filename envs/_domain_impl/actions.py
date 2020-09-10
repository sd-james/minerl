import numpy as np

NO_OP = 0
FORWARD = 1
BACKWARD = 2
TURN_RIGHT = 3
TURN_LEFT = 4
USE_A = 5
USE_B = 6

NOISY = True


def noisy(x, scale=0.1) -> float:
    if not NOISY:
        return x

    return x + np.random.normal(0, scale=scale)


class Action:

    @property
    def value(self):
        return None


class Attack(Action):

    def __init__(self, on):
        self.on = on

    @property
    def value(self):
        if self.on:
            return "attack 1"
        return "attack 0"


class Use(Action):

    def __init__(self, on):
        self.on = on

    @property
    def value(self):
        if self.on:
            return "use 1"
        return "use 0"


class WalkForward(Action):

    def __init__(self, speed):
        self.speed = speed

    @property
    def value(self):
        return 'move {}'.format(self.speed)


class Strafe(Action):

    def __init__(self, speed):
        self.speed = speed

    @property
    def value(self):
        return 'strafe {}'.format(self.speed)


class Forward(Action):
    @property
    def value(self):
        return FORWARD


class Backward(Action):
    @property
    def value(self):
        return BACKWARD


class TurnRight(Action):
    @property
    def value(self):
        return TURN_RIGHT


class TurnLeft(Action):
    @property
    def value(self):
        return TURN_LEFT


class Turn(Action):

    def __init__(self, rotation):
        self.rotation = rotation

    @property
    def value(self):
        return 'turn {}'.format(self.rotation)


class Teleport(Action):

    def __init__(self, x=None, y=None, z=None):
        self.x = noisy(x)
        self.y = y
        self.z = noisy(z, scale=0.05)

    @property
    def value(self):
        if self.y is None and self.z is None:
            return "tpx {}".format(self.x)
        if self.x is None and self.z is None:
            return "tpy {}".format(self.y)
        if self.x is None and self.y is None:
            return "tpz {}".format(self.z)
        return "tp {} {} {}".format(self.x, self.y, self.z)


class Yaw(Action):

    def __init__(self, yaw):
        self.yaw = noisy(yaw)

    @property
    def value(self):
        return "setYaw {}".format(self.yaw)


class Craft(Action):

    def __init__(self, item):
        self.item = item

    @property
    def value(self):
        return "craft {}".format(self.item)


class Noop(Action):

    @property
    def value(self):
        return "move 0"


class Pitch(Action):

    def __init__(self, pitch):
        self.pitch = pitch

    @property
    def value(self):
        return "setPitch {}".format(self.pitch)
