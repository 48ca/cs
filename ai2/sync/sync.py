#!/usr/bin/env python3

from random import random
import tkinter as tk

height = 900
width = 1600

root = tk.Tk()
canvas = tk.Canvas(root, width=width,height=height, background="black", bd=0, highlightthickness=0, relief='ridge')
canvas.pack()

# I didn't write this
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle
#

N = 2000
THRES = .8

BUMP_FACTOR = .01
DELTA_X = .01
RADIUS = 3
DECAY_AMP = 5
DELAY = 20

MARGIN_X = 0
MARGIN_Y = 0

MOVE = True
MOVE_X_OFFSET = 0
MOVE_X_SCALE = 5
MOVE_Y_OFFSET = 0
MOVE_Y_SCALE = 3

GREY = 50

class Fly:
    def __init__(self):
        self.x = MARGIN_X + random()*(width-2*MARGIN_X)
        self.y = MARGIN_Y + random()*(height-2*MARGIN_Y)
        self.rad = RADIUS
        #
        self.bf = BUMP_FACTOR
        self.dx = DELTA_X

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
    try:
        canvas.delete("all")
        bumped = False
        for f in flies:
            if f.tick() and not bumped:
                bumped = True
                for mf in flies:
                    mf.bump()
                f.inten = 0
        if MOVE:
            for f in flies:
                f.x += (1+MOVE_X_OFFSET - random() - random())*MOVE_X_SCALE
                if f.x < 0: f.x = width
                if f.x > width: f.x = 0
                f.y += (1+MOVE_Y_OFFSET - random() - random())*MOVE_Y_SCALE
                if f.y < 0: f.y = height
                if f.y > height: f.y = 0
        for f in flies:
            i = int(255*f.inten)
            # colors = [i,i,i]
            colors = [GREY,GREY,GREY]
            if f.inten < .15: # Just fired
                colors = [GREY+30, int(255-i*DECAY_AMP), GREY+10]
            canvas.create_circle(f.x,f.y,f.rad,fill="#{:02X}{:02X}{:02X}".format(*colors))
        root.after(DELAY,tick)
    except KeyboardInterrupt:
        closing()
        print()

tick()

def closing(s=None):
    root.destroy()

root.configure(background="black")
root.wm_title("Fireflies")
root.protocol("WM_DELETE_WINDOW",closing)
keys = ['<Control-c>','<Control-backslash>','q','Escape']
for k in keys: root.bind(k,closing)
try:
    root.mainloop()
except KeyboardInterrupt:
    closing()
    print()
