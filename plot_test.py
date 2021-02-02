import widgets
import tkinter as tk

from math import sin
import time

def update(root, plot, chan, x):
    plot.put(chan, x % 1)
    x += 0.2
    root.after(100, update, root, plot, chan, x)

def main():
    root = tk.Tk()
    plot = widgets.Plot1D(root, 300, 150, 100, -1, 1)
    plot.grid(column=0, row=0)

    chan = plot.add_channel((255, 0, 0))
    x = 0

    root.after(0, update, root, plot, chan, x)
    root.mainloop()

if __name__ == '__main__':
    main()
