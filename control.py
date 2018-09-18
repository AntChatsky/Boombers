from objects import *
from random import shuffle


def valid(x, y, size):
    if x < 0 or y < 0:
        return False
    if x >= size[0] or y >= size[1]:
        return False
    return True


def find_path(area, start, target_coords):
    """
    Gets area - 2D list with 1 or 0 inside it, mean is cell passage or not.
    Also start and target_coords point
    """
    possible = ((0, 1), (0, -1), (-1, 0), (1, 0))
    path = [[0 for elem in line] for line in area]
    step = 1
    path[start[0]][start[1]] = 1
    flag = False

    while path[target_coords[0]][target_coords[1]] == 0:
        flag = False

        for i in range(len(path)):
            for ii in range(len(path[i])):
                if area[i][ii] == 0 and path[i][ii] == step:
                    flag = True

                    for situation in possible:
                        dy = i + situation[0]
                        dx = ii + situation[1]

                        if valid(dx, dy, (len(path[i]), len(path))) and \
                                path[dy][dx] == 0 and area[dy][dx] == 0:
                            path[dy][dx] = step + 1

        if not flag:
            return False

        step += 1

    cell_coords = target_coords
    way = []
    while start not in way:
        for i in range(len(path)):
            for ii in range(len(path[i])):
                if cell_coords == (i, ii):
                    temp = -1

                    for situation in possible:
                        dy = i + situation[0]
                        dx = ii + situation[1]

                        if valid(dx, dy, (len(path[i]), len(path))):
                            if path[dy][dx] != 0:
                                if temp > path[dy][dx] or temp == -1:
                                    temp = path[dy][dx]
                                    cell_coords = (dy, dx)

                    way.append(cell_coords)

    return way


class Bot(object):
    def __init__(self, bot, game_canvas, land, img_size):
        self.possible = ((0, 1), (0, -1), (-1, 0), (1, 0))
        self.x, self.y = bot.get_coords()
        self.bot = bot
        self.path = []
        self.median = None
        self.target_coords = None
        self.health = bot.health
        self.land = land
        self.game_canvas = game_canvas
        self.img_size = img_size

    def move(self, area, target_coords):
        bot_x, bot_y = self.bot.get_coords()
        self.land[bot_x][bot_y] = Ground()

        if not self.path or not self.target_coords != target_coords:
            self.path = find_path(area, self.bot.get_coords(), target_coords)

            if not self.path:
                possible = self.bot.possible
                shuffle(possible)

                for direction in possible:
                    bot_dx = bot_x - direction[0]
                    bot_dy = bot_y - direction[1]

                    if self.land.valid(bot_dx, bot_dy) and self.land[bot_dx][bot_dy].passage:
                        self.bot.set_coords(bot_dx, bot_dy)
                        break

                else:
                    self.bot.set_coords(bot_x, bot_y)

            else:
                self.path.pop()
                self.bot.set_coords(*self.path.pop())

        else:
            self.bot.set_coords(*self.path.pop())

        bot_dx, bot_dy = self.bot.get_coords()
        self.target_coords = copy(self.bot.get_coords())

        self.land[bot_dx][bot_dy] = self.bot

        bot_dx -= bot_x
        bot_dy -= bot_y

        self.game_canvas.move(self.bot.image, bot_dy * self.img_size,
                              bot_dx * self.img_size)


class BotMonster(Bot):
    def __init__(self, bot, game_canvas, land, player, img_size):
        super(BotMonster, self).__init__(bot, game_canvas, land, img_size)
        self.player = player

    def update(self):
        x, y = self.bot.get_coords()
        for situation in self.possible:
            # if player is near
            if (x + situation[0], y + situation[1]) == self.player.get_coords():
                self.player.health -= self.bot.damage
                break

        else:
            area = [[1 if elem.__class__.__name__.lower() == "rock" else 0
                     for elem in line] for line in self.land]

            self.move(area, self.player.get_coords())