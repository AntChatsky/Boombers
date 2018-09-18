from abc import ABC, abstractmethod
from time import sleep
from random import choice
from copy import copy


class GameObject(ABC):
    def __init__(self):
        self.health = False
        self.passage = True
        self.destroyable = True
        self.status = True
        self.image = None

    def change(self):
        self.status = not self.status


class Ground(GameObject):
    def __init__(self):
        super(Ground, self).__init__()
        self.destroyable = False


class Sandstone(GameObject):
    def __init__(self):
        super(Sandstone, self).__init__()
        self.health = 1
        self.passage = False


class Rock(GameObject):
    def __init__(self):
        super(Rock, self).__init__()
        self.health = 3
        self.passage = False


class ActiveGameObject(GameObject):
    def __init__(self, x=None, y=None):
        super(ActiveGameObject, self).__init__()
        self.possible = [(0, 1), (0, -1), (-1, 0), (1, 0), (0, 0)]
        self.x = x
        self.y = y
        self.passage = False
        self.destroyable = False

    def get_coords(self):
        return self.x, self.y

    def set_coords(self, x, y):
        self.x = x
        self.y = y


class Player(ActiveGameObject):
    def __init__(self, x=None, y=None):
        super(Player, self).__init__(x, y)
        self.health = 100
        self.health_limit = copy(self.health)

    def near(self, x, y):
        x_area = self.x - x
        y_area = self.y - y

        if -3 < x_area < 3 and -3 < y_area < 3:
            return True

        else:
            return False


class Monster(ActiveGameObject):
    def __init__(self, health, x=None, y=None):
        super(Monster, self).__init__(x, y)
        self.health = health
        self.health_limit = copy(health)
        self.damage = 10


class Bomb(ActiveGameObject):
    def __init__(self, x=None, y=None):
        super(Bomb, self).__init__(x, y)
        self.destroyable = True
        self.explosion = False
        self.status = False
        self.health = 2
        self.damage = 1

        self.area = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0),  # FIXME
                     (1, 1), (1, -1), (-1, 1), (-1, -1),
                     (0, 2), (0, -2), (2, 0), (-2, 0)]

    def explode(self):
        self.explosion = not self.explosion


class Nukes(Bomb):
    def __init__(self, x=None, y=None):
        super().__init__(x, y)

        self.health = 3
        self.damage = 3

        self.area = []
        for i in range(-4, 4):
            for ii in range(-4, 4):
                self.area.append((i, ii))


class Treasure(ABC):
    def __init__(self, gold):
        self.gold = gold
        self.status = True
        self.image = "gold_bars" if self.gold > 50 else "gold_coins"

    def change(self):
        self.status = not self.status
