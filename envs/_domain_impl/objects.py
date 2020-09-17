class Rect:
    def __init__(self, x1, z1, x2, z2):
        self.x1 = min(x1, x2)
        self.z1 = min(z1, z2)
        self.x2 = max(x1, x2)
        self.z2 = max(z1, z2)

    def __iter__(self):
        for x in [self.x1, self.z1, self.x2, self.z2]:
            yield x

    def __contains__(self, item):
        return self.x1 <= item[0] <= self.x2 and self.z1 <= item[1] <= self.z2


class Object:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self._look_at = None
        self.dirty = True
        self.id = 0
        self.attackable = False
        self.in_front = False

    def set_look_at(self, x, y, z, pitch, yaw):
        self._look_at = (x, y, z, pitch, yaw)

    def look_at(self):
        return self._look_at


class Item(Object):
    def __init__(self, x, y, z, type, reachable=None, pickup=None):
        super().__init__(x, y, z)
        self.type = type
        self.reachable = reachable  # a rectangle
        self.picked = False
        self.pickup = pickup
        self.attacked = False

    def can_reach(self, x, z):
        if self.reachable is None or self.picked or self.in_front:  # if we're in front of it already, don't bother!
            return False
        return (x, z) in self.reachable

    def can_pick(self, x, z):
        if self.picked:
            return False
        return abs(x - self.x) + abs(z - self.z) <= 3.5

    def can_attack(self, x, z):
        return False

    def __str__(self):
        return '<DrawItem x="{}" y="{}" z="{}" type="{}"/>'.format(self.x, self.y, self.z, self.type)


class Block(Item):
    def __init__(self, x, y, z, type, reachable=None, pickup=None, attackable=True):
        super().__init__(x, y, z, type, reachable, pickup)
        self.attackable = attackable

    def can_pick(self, x, z):
        if not self.attacked:
            return False
        return super().can_pick(x, z)

    def can_attack(self, x, z):
        if self.attacked:
            return False
        if not self.in_front:
            return False
        if abs(x - self.x) > 1:
            return False
        return abs(x - self.x) + abs(z - self.z) <= 3.5

    def __str__(self):
        return '<DrawBlock x="{}" y="{}" z="{}" type="{}"/>'.format(self.x, self.y, self.z, self.type)


class Door(Object):
    def __init__(self, x, z, north_rect, south_rect, puzzle=False):
        super().__init__(x, None, z)
        self.north_rect = north_rect
        self.south_rect = south_rect
        self.puzzle = puzzle
        self.closed = True

    def can_reach(self, env, moving_north=True):
        pos = env.get_x(), env.get_z()

        sign = -1 if moving_north else 1
        if self.close(self.z + sign * 2.5, pos[1]) and self.close(self.x + 0.5, pos[0]):
        # if self.z + sign * 1.5 == pos[1] and self.x + 0.5 == pos[0]:
            # can't walk to a door if we're already at it!
            return False
        if moving_north:
            return pos in self.south_rect
        return pos in self.north_rect

    def close(self, x, y):
        return abs(x-y) < 0.1

    def can_walk_through(self, env, moving_north=True):
        if self.closed:
            return False

        if not self.in_front:
            return False

        if moving_north and not env.is_facing_north():
            return False

        if not moving_north and env.is_facing_north():
            return False

        pos = env.get_x(), env.get_z()
        if moving_north:
            return pos in self.south_rect
        return pos in self.north_rect

    def can_toggle(self, env, moving_north=True):

        if self.puzzle and not moving_north:
            return False

        if not self.in_front:
            return False

        if moving_north and not env.is_facing_north():
            return False

        if not moving_north and env.is_facing_north():
            return False

        sign = -1 if moving_north else 1
        # rectangle = Rect(self.x - 1, self.z + sign * 3, self.x + 1, self.z + sign * 1.5)
        rectangle = Rect(self.x - 1, self.z + sign * 3, self.x + 1, self.z + sign * 2)

        pos = env.get_x(), env.get_z()
        return pos in rectangle

    def is_close(self, env, moving_north=True):

        sign = -1 if moving_north else 1
        # rectangle = Rect(self.x - 1, self.z + sign * 3, self.x + 1, self.z + sign * 1.5)
        rectangle = Rect(self.x - 1, self.z + sign * 3, self.x + 1, self.z + sign * 2)

        pos = env.get_x(), env.get_z()
        return pos in rectangle
