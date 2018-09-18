from tkinter import *
from PIL import Image, ImageTk
from copy import copy


def load_image(name, x_size, y_size):
    pillimage = Image.open(name)
    pillimage.thumbnail((x_size, y_size), Image.ANTIALIAS)
    return ImageTk.PhotoImage(pillimage)


class GuiCell(object):
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y


class HpBar(GuiCell):
    def __init__(self, canvas, x, y, health, colour="dark green"):
        super(HpBar, self).__init__(canvas, x, y)

        self.tool_im = load_image('sources/textures/hp_bar/tool.png', 300, 300)

        self.bar_size = {"x": 291, "y": 80}
        self.borders = {"x": 90, "y": 15}

        self.bar_coords = [self.x + self.borders["x"], self.y + self.borders["y"],
                           self.x + self.bar_size["x"], self.y + self.bar_size["y"]]

        self.health = health
        self.full = copy(health)
        self.step = (self.bar_size["x"]-self.borders["x"])//self.full

        self.bar = self.canvas.create_rectangle(*self.bar_coords, fill=colour)

        self.tool = self.canvas.create_image(self.x, self.y, image=self.tool_im, anchor=NW)

    def update(self, damage):
        if self.health - damage >= self.full:
            self.bar_coords[2] = self.x + self.bar_size["x"]

        else:
            self.bar_coords[2] = self.bar_coords[2] - damage*self.step
        self.canvas.coords(self.bar, *self.bar_coords)


class Clock(GuiCell):
    def __init__(self, canvas, x, y, time, colour="dark red"):
        super(Clock, self).__init__(canvas, x, y)

        self.tool_im = load_image('sources/textures/timer/timer_bar.png', 900, 100)

        self.bar_size = {"x": 825, "y": 70}
        self.borders = {"x": 70, "y": 15}

        self.bar_coords = [self.x + self.borders["x"], self.y + self.borders["y"],
                           self.x + self.bar_size["x"], self.y + self.bar_size["y"]]

        self.time = time
        self.full = copy(time)
        self.step = (self.bar_size["x"] - self.borders["x"]) // self.full

        self.bar = self.canvas.create_rectangle(*self.bar_coords, fill=colour)

        self.tool = self.canvas.create_image(self.x, self.y, image=self.tool_im, anchor=NW)

    def update(self, time_gone):
        if self.time - time_gone >= self.full:
            self.bar_coords[2] = self.x + self.bar_size["x"]

        else:
            self.bar_coords[2] = self.bar_coords[2] - time_gone*self.step
        self.canvas.coords(self.bar, *self.bar_coords)


class ScoreCounter(GuiCell):
    def __init__(self, canvas, x, y):
        super(ScoreCounter, self).__init__(canvas, x, y)

        self.gold = 0
        self.counter = self.canvas.create_text(self.x, self.y, text=str(self.gold), anchor=NW,
                                               fill="yellow", font="OptimusPrinceps 72")

    def update(self, gold):
        self.gold += gold
        self.canvas.itemconfig(self.counter, text=str(self.gold))


class Weapon(GuiCell):
    def __init__(self, canvas, x, y):
        super(Weapon, self).__init__(canvas, x, y)

        self.weapon_img = 0
        self.weapon = 0

        self.points = [100+x, 0+y, 100+x, 100+y, 30+x, 50+y]
        self.points2 = [200+x, 0+y, 200+x, 100+y, 270+x, 50+y]

        self.triangleL = self.canvas.create_polygon(self.points, fill="green")
        self.triangleR = self.canvas.create_polygon(self.points2, fill="green")

    def update(self, path, leftover):
        self.weapon_img = load_image(path, 200, 200)

        self.weapon = self.canvas.create_image(200+self.x, 0+self.y,
                                               image=self.weapon_img,
                                               anchor="ne")

        if not leftover[0]:
            self.canvas.itemconfig(self.triangleL, fill="#003319")
        else:
            self.canvas.itemconfig(self.triangleL, fill="green")

        if not leftover[1]:
            self.canvas.itemconfig(self.triangleR, fill="#003319")
        else:
            self.canvas.itemconfig(self.triangleR, fill="green")
