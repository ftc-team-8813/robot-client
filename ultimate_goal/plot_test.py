import widgets
import tkinter as tk

from math import *
import time

def update(root, plot, chan, t):
    plot.put(chan, sin(t), cos(3*t))
    t += 0.1
    if t % 6 > 5.9:
        plot.clear(chan)
    root.after(10, update, root, plot, chan, t)

def main():
    root = tk.Tk()
    plot = widgets.Plot2D(root, 300, 300, -1, 1, -1, 1)
    plot.grid(column=0, row=0)

    chan = plot.add_channel((255, 0, 0))
    t = 0

    root.after(0, update, root, plot, chan, t)
    root.mainloop()

if __name__ == '__main__':
    main()
