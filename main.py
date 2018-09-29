from random import randint, randrange
from tkinter import *
from PIL import Image, ImageTk
from objects import *
from control import *
from gui import HpBar, Clock, ScoreCounter, Weapon
from threading import Timer
import time
import copy


required_font = "OptimusPrinceps "


def load_image(name):
    pillimage = Image.open(name)
    pillimage.thumbnail((Game.img_size, Game.img_size), Image.ANTIALIAS)
    return ImageTk.PhotoImage(pillimage)


def valid(x, y, size):
    if x < 0 or y < 0:
        return False
    if x >= size[0] or y >= size[1]:
        return False
    return True


class Land(object):

    def __init__(self, WORLD_WIDTH, WORLD_HEIGH):
        self.WORLD_SIZE = (WORLD_HEIGH, WORLD_WIDTH)
        self._data = [[Sandstone() for cell in range(self.WORLD_SIZE[1])]
                      for line in range(self.WORLD_SIZE[0])]

        self.timer = False

    def __getitem__(self, i):
        return self._data[i]

    def out(self):
        for line in range(self.WORLD_SIZE):
            for cell in range(self.WORLD_SIZE):
                print(self._data[line][cell], end='')
            print()

    def valid(self, x, y=1):
        return valid(x, y, self.WORLD_SIZE)

    def add_rock(self):
        direction = [0, 1]

        for point in range(self.WORLD_SIZE[1]):
            x = randint(0, self.WORLD_SIZE[0] - 1)
            y = randint(0, self.WORLD_SIZE[1] - 1)
            shuffle(direction)
            length = choice((1, 2, 3, 3))
            for p in range(length):
                self._data[x][y] = Rock()
                x += direction[0]
                y += direction[1]
                wigth = choice((1, 2, 3))
                x1, y1 = x, y
                for g in range(wigth):
                    x1 += direction[1]
                    y1 += direction[0]
                    if not self.valid(x1, y1):
                        break
                    self._data[x1][y1] = Rock()

                wigth = choice((1, 2, 3))
                x1, y1 = x, y
                for g in range(wigth):
                    x1 -= direction[1]
                    y1 -= direction[0]
                    if not self.valid(x1, y1):
                        break
                    self._data[x1][y1] = Rock()

                if not self.valid(x, y):
                    break

    def roun(self):
        delta = ((-1, 0), (0, -1), (1, 0), (0, 1))
        for x in range(self.WORLD_SIZE[0]):
            for y in range(self.WORLD_SIZE[1]):
                # Проверяем что клетка не проходима
                if self._data[x][y].title != 0:
                    # Переменная для сохранения проходимости соседних ячеек
                    pozition = ''
                    for dx, dy in delta:
                        if self.valid(x + dx, y + dy) and self._data[x + dx][y + dy].passage:
                            pozition += '1'

                        else:
                            pozition += '0'
                    # print(pozition)
                    if pozition == '1100':
                        self._data[x][y].title = 2  # левая верхняя
                    elif pozition == '0011':
                        self._data[x][y].title = 3
                    elif pozition == '1001':
                        self._data[x][y].title = 4  # правая нижняя
                    elif pozition == '0110':
                        self._data[x][y].title = 5

        for x in range(self.WORLD_SIZE):
            for y in range(self.WORLD_SIZE):
                if (self._data[x][y].title == 2) and self.valid(x, y + 1) and self._data[x][y + 1].title == 5:
                    self._data[x][y + 1].title == 1
                    self._data[x][y + 2].title == 5

    def add_spawn(self):
        for i in range(4):
            for ii in range(4):
                self._data[i][ii] = Ground()
                self._data[i][-(ii+1)] = Ground()
                self._data[-(i+1)][ii] = Ground()
                self._data[-(i+1)][-(ii+1)] = Ground()


class Manager(object):

    def __init__(self, game):
        self.game = game
        self.root = self.game.root
        self.land = self.game.land
        self.game_canvas = self.game.game_canvas

        global required_font

        self.hp_bar = self.game.hp_bar
        self.player = self.game.player
        self.player_coords = None
        self.hp_temp = copy.copy(self.player.health)

        self.monster = BotMonster(self.game.monster, self.game_canvas,
                                  self.land, self.player, Game.img_size)

        self.player_is_achievable = True

        self.timer = self.game.timer
        self.clock = self.game.clock

        self.bombs = self.game.bombs

        self.period = 1000

    def update(self):
        if len(self.bombs) > 0:
            for bomb in self.bombs:
                if bomb.health == 0:
                    x, y = bomb.get_coords()

                    self.game.explode_bomb(bomb)

                    bomb.explode()

                else:
                    bomb.health = bomb.health - 1

        for i in range(len(self.bombs)):
            if self.bombs[i].explosion:
                self.bombs[i] = 0

        if 0 in self.bombs:
            while 0 in self.bombs:
                self.bombs.pop(self.bombs.index(0))

        if self.player.health != self.hp_temp:
            self.hp_bar.update(self.hp_temp - self.player.health)
            self.hp_temp = copy.copy(self.player.health)

        if self.player.health <= 0:
            self.game.game_canvas.destroy()
            self.game.gui_canvas.destroy()
            self.root.configure(background="black")
            Label(self.root, text="YOU DIED", font=required_font + "92",
                  foreground="black").place(relx=0.5, rely=0.5, anchor=CENTER)

        if self.monster.health <= 0:
            x, y = self.monster.get_coords()
            self.land[x][y] = Ground()
            self.game_canvas.delete(self.monster)

        else:
            self.monster.update()

        if self.timer <= 0:
            self.game.game_canvas.destroy()
            self.game.gui_canvas.destroy()
            self.root.configyure(background="black")
            Label(self.root, text="TIME HAS GONE", font=required_font + "92",
                  foreground="black").place(relx=0.5, rely=0.5, anchor=CENTER)

        self.timer -= 1
        self.clock.update(1)

        self.game.game_canvas.after(self.period, self.update)


class Game(object):

    img_size = 40
    size = [0, 0]

    WIDTH = 0
    HEIGHT = 0

    def __init__(self):
        self.root = Tk()

        Game.size = ((self.root.winfo_screenwidth()-50)//Game.img_size,
                     (self.root.winfo_screenheight() - 120)//Game.img_size)

        Game.WIDTH = Game.img_size * Game.size[0]
        Game.HEIGHT = Game.img_size * Game.size[1]

        self.root.configure(background="black")
        self.root.attributes("-fullscreen", True)
        self.root.title("Blow it!")
        self.root.config(width=Game.WIDTH + 100, height=Game.HEIGHT + 100)
        self.root.minsize(width=Game.WIDTH + 100, height=Game.HEIGHT + 100)

        self.spawn = (1, 1)
        self.player = Player(self.spawn[0], self.spawn[1])

        self.game_frame = Frame(self.root)
        self.game_frame.pack(side=TOP)

        self.game_canvas = Canvas(self.game_frame, highlightthickness=0,
                                  width=Game.WIDTH, height=Game.HEIGHT)
        self.game_canvas.configure(bg="black")
        self.game_canvas.pack(anchor=CENTER)

        self.gui_frame = Frame(self.root)
        self.gui_frame.pack(side=BOTTOM)

        self.gui_canvas = Canvas(self.gui_frame, highlightthickness=0,
                                 width=Game.WIDTH)
        self.gui_canvas.configure(bg="black")
        self.gui_canvas.pack()

        self.hp_bar = HpBar(self.gui_canvas, 0, 10, self.player.health)

        self.counter = ScoreCounter(self.gui_canvas, 400, 10)

        self.weapon_indicator = Weapon(self.gui_canvas, 600, 10)

        self.timer = 150
        self.clock = Clock(self.gui_canvas, 930, 20, self.timer)

        self.movement = {"Left": (0, -1), "Right": (0, 1), "Up": (-1, 0), "Down": (1, 0)}
        self.time_start = time.time()
        self.time_limit = 0.2
        self.bombs = []

        adress = {"sandstone": r'sources/textures/land/sandstone.jpg',
                  "rock": r'sources/textures/land/rock.jpg',
                  "ground": r'sources/textures/land/ground.png',
                  "darkness": r'sources/textures/land/darkness.jpg',
                  "bomb": r'sources/textures/bombs/bomb.png',
                  "nukes": r'sources/textures/bombs/nukes.png',
                  "flash": r'sources/textures/bombs/flash.png',
                  "smoke": r'sources/textures/bombs/smoke.png',
                  "player": r'sources/textures/characters/player.png',
                  "monster": r'sources/textures/characters/monster.png',
                  "gold_bars": r'sources/textures/treasure/bars.png',
                  "gold_coins": r'sources/textures/treasure/coins.png'}

        self.weapons = [adress["bomb"], adress["nukes"]]
        self.weapon_types = {"bomb": Bomb, "nukes": Nukes}
        self.weapon_indicator.update(self.weapons[0], [0, 1])
        self.weapon_iterator = 0

        self.land_textures = ["sandstone", "rock", "ground", "darkness"]
        self.textures = {}
        for name in adress:
            self.textures[name] = load_image(adress[name])

        self.land = Land(*Game.size)
        self.landMap = []

        self.playerBudget = 0
        self.treasures = [[0 for elem in range(Game.size[0])]
                          for line in range(Game.size[1])]
        self.treasureMap = []
        for i in range(len(self.treasures)):
            for ii in range(len(self.treasures[i])):
                chance = randint(0, 10)

                if chance == 10:
                    gold = randrange(10, 100, 5)
                    self.treasures[i][ii] = Treasure(gold)

        self.monster_spawn = (1, Game.size[0]-2)
        # self.monster_spawn = (1, 6)
        self.monster_health = 100
        self.monster = Monster(self.monster_health, *self.monster_spawn)
        self.land[self.monster_spawn[0]][self.monster_spawn[1]] = Ground()
        self.manager = Manager(self)

    def start(self):
        self.land.add_rock()
        self.land.add_spawn()
        self.show_world()
        self.refresh()

        self.land[self.monster_spawn[0]][self.monster_spawn[1]] = self.monster

        # FIXME self.land.roun()
        self.player.image = self.game_canvas.create_image(
            self.spawn[1] * Game.img_size + 25,
            self.spawn[0] * Game.img_size + 25,
            image=self.textures["player"])

        self.monster.image = self.game_canvas.create_image(
            self.monster_spawn[1] * Game.img_size + 25,
            self.monster_spawn[0] * Game.img_size + 25,
            image=self.textures["monster"])

        self.root.bind("<Key>", self.action)

        self.manager.update()

        self.root.mainloop()

    def action(self, event):
        # here game actions, which are limited in using per second
        if time.time() - self.time_start > self.time_limit:
            if event.keysym in self.movement:
                self.move(event.keysym)

            elif event.keysym == "space":
                bomb = self.weapon_types[self.weapons[self.weapon_iterator][:-4].split("/")[-1]]()
                self.set_bomb(bomb, *self.player.get_coords())

            elif event.keycode == 88:  # Letter "x"
                self.set_bomb(Nukes(), *self.player.get_coords())

            self.time_start = time.time()

        # everything else
        if event.keysym == "1" or event.keysym == "2":
            self.change_weapon(event)

        elif event.keysym == "Escape":
            self.root.destroy()
            menu = Menu()

    def move(self, key):
        dx, dy = self.movement[key]

        x, y = self.player.get_coords()
        dx += x
        dy += y

        if self.land.valid(dx, dy) and self.land[dx][dy].passage:
            if isinstance(self.treasures[dx][dy], Treasure):
                self.clean(self.treasureMap[dx][dy])

                self.playerBudget += self.treasures[dx][dy].gold
                self.counter.update(self.treasures[dx][dy].gold)

                self.treasures[dx][dy] = 0

            self.land[x][y] = Ground()
            self.land[dx][dy] = self.player
            self.player.set_coords(dx, dy)
            dx -= x
            dy -= y
            self.game_canvas.move(self.player.image, dy * Game.img_size,
                                  dx * Game.img_size)

    def change_weapon(self, event):
        if event.keysym == "1" and self.check_leftover(self.weapons,
                                                       self.weapon_iterator)[0]:
            self.weapon_iterator -= 1
            self.weapon_indicator.update(self.weapons[self.weapon_iterator],
                                         self.check_leftover(self.weapons,
                                                             self.weapon_iterator))

        elif event.keysym == "2" and self.check_leftover(self.weapons,
                                                         self.weapon_iterator)[1]:
            self.weapon_iterator += 1
            self.weapon_indicator.update(self.weapons[self.weapon_iterator],
                                         self.check_leftover(self.weapons,
                                                             self.weapon_iterator))

    def set_bomb(self, bomb, x, y):
        for a_bomb in self.bombs:
            dx, dy = a_bomb.get_coords()
            if dx == x and dy == y:
                break

        else:
            self.bombs.append(bomb)

            bomb.set_coords(x, y)
            bomb.change()
            bomb.image = self.game_canvas.create_image(y * Game.img_size + 25,
                                                       x * Game.img_size + 25,
                                                       image=self.textures[
                                                           bomb.__class__.__name__.lower()])

    def explode_bomb(self, bomb):
        self.game_canvas.delete(bomb.image)

        area = bomb.area
        x, y = bomb.get_coords()

        effects = []

        for pos in area:
            dx = pos[0] + x
            dy = pos[1] + y

            if self.land.valid(dx, dy):
                player_x, player_y = self.player.get_coords()
                monster_x, monster_y = self.monster.get_coords()

                if dx == player_x and dy == player_y:
                    self.player.health -= self.player.health_limit/2

                if dx == monster_x and dy == monster_y:
                    self.monster_health -= 50

                else:
                    if self.land[dx][dy].destroyable:
                        self.land[dx][dy].health = self.land[dx][dy].health - bomb.damage
                        if self.land[dx][dy].health <= 0:
                            self.land[dx][dy] = Ground()

                effects.append(self.game_canvas.create_image(
                    dy * Game.img_size + 25, dx * Game.img_size + 25,
                    image=self.textures["flash"]
                ))

        Timer(0.2, self.change, [effects, self.textures["smoke"]]).start()
        Timer(0.3, self.clean, [effects]).start()

    def change(self, storage, obj_im):
        if type(storage) == list or type(storage) == tuple:
            for elem in storage:
                self.game_canvas.itemconfig(elem, image=obj_im)

        else:
            self.game_canvas.itemconfig(storage, image=obj_im)

    def clean(self, storage):
        if type(storage) == list or type(storage) == tuple:
            for elem in storage:
                self.game_canvas.delete(elem)

        else:
            self.game_canvas.delete(storage)

    def show_world(self):
        for x in range(Game.size[1]):
            self.landMap.append([])
            self.treasureMap.append([])
            for y in range(Game.size[0]):
                if self.land[x][y].__class__.__name__.lower() in self.land_textures:
                    self.landMap[-1].append(self.game_canvas.create_image(
                        y * Game.img_size + 25, x * Game.img_size + 25,
                        image=self.textures[self.land[x][y].__class__.__name__.lower()]))

                    self.land[x][y].change()

                if self.land[x][y].passage and isinstance(self.treasures[x][y], Treasure):
                    self.treasureMap[-1].append(self.game_canvas.create_image(
                        y * Game.img_size + 25, x * Game.img_size + 25,
                        image=self.textures[self.treasures[x][y].image]))

                    self.treasures[x][y].change()

                elif self.treasures[x][y] == 0:
                    self.treasureMap[-1].append(0)

    def refresh(self):
        for x in range(Game.size[1]):
            for y in range(Game.size[0]):
                if self.land[x][y].__class__.__name__.lower() in\
                        self.land_textures and self.land[x][y].status:
                    self.game_canvas.itemconfig(self.landMap[x][y],
                                                image=self.textures[self.land[x][y].__class__.__name__.lower()])

                    self.land[x][y].change()

                if self.land[x][y].passage and isinstance(self.treasures[x][y], Treasure) and\
                        self.treasures[x][y].status:
                    self.treasureMap[x][y] = (self.game_canvas.create_image(y * Game.img_size + 25,
                                                                            x * Game.img_size + 25,
                                              image=self.textures[self.treasures[x][y].image]))

                    self.treasures[x][y].change()

        self.root.after(200, self.refresh)

    @staticmethod
    def check_leftover(mas, i):
        result = []

        if i <= 0:
            result.append(0)
        else:
            result.append(1)

        if i >= len(mas)-1:
            result.append(0)
        else:
            result.append(1)

        return result


class Menu(object):
    def __init__(self):
        self.menu = Tk()
        self.menu.configure(bg="black")
        self.menu.title("Blow it!")
        self.menu.window_size = (200, 200)
        self.menu.minsize(*self.menu.window_size)
        self.menu.maxsize(*self.menu.window_size)

        screen_widht = self.menu.winfo_screenwidth()
        screen_height = self.menu.winfo_screenheight()
        x = (screen_widht//2) - (self.menu.window_size[0]//2)
        y = (screen_height//2) - (self.menu.window_size[1]//2)
        self.menu.geometry("{}x{}+{}+{}".format(self.menu.window_size[0],
                                                self.menu.window_size[1], x, y))

        self.texts = {"Start": self.start_game, "Exit": self.menu.destroy}
        global required_font
        self.buttons = []

        for text in self.texts:
            self.buttons.append(Button(self.menu, text=text,
                                       font=required_font + "25", width=5,
                                       fg="red", command=self.texts[text]))
            self.buttons[-1].pack(pady=15)

        self.menu.mainloop()

    def start_game(self):
        self.menu.destroy()

        g = Game()
        g.start()


menu = Menu()

