#!/usr/bin/env python3

import math
from random import random
import tkinter as tk

height = 600
width = 800

root = tk.Tk()
canvas = tk.Canvas(root, width=width,height=height)
canvas.pack()

# I didn't write these two methods
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

def _create_circle_arc(self, x, y, r, **kwargs):
    if "start" in kwargs and "end" in kwargs:
        kwargs["extent"] = kwargs["end"] - kwargs["start"]
    del kwargs["end"]
    return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle_arc = _create_circle_arc
#

N = 100
THRES = .8

class Fly:
    def __init__(self):
        self.x = 20 + random()*(width-40)
        self.y = 20 + random()*(height-40)
        self.rad = 4  # Radius
        #
        self.bf = .01 # Bump factor
        self.dx = .01 # Delta x

        self.inten = random()

    def tick(self):
        self.inten = self.inten + (1 - self.inten) * self.dx
        if self.inten > THRES:
            self.inten = 0
            return True
        return False

    def bump(self):
        self.inten += self.bf
        if self.inten > THRES:
            self.inten = 0

    def __str__(self):
        return "<Fly (br:{0:.4f}) at ({1:.4f},{2:.4f})>".format(self.inten,self.x,self.y)
    def __repr__(self):
        return "<Fly (br:{0:.4f}) at ({1:.4f},{2:.4f})>".format(self.inten,self.x,self.y)

flies = []
for i in range(N):
    flies.append(Fly())
def tick():
    canvas.delete("all")
    bumped = False
    for f in flies:
        if f.tick() and not bumped:
            bumped = True
            for mf in flies:
                mf.bump()
            f.inten = 0
    for f in flies:
        i = int(255*f.inten)
        canvas.create_circle(f.x,f.y,f.rad,fill="#{:02X}{:02X}{:02X}".format(i,i,i))
    root.after(1,tick)

tick()

root.wm_title("Fireflies")
root.mainloop()
