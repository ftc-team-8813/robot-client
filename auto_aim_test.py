import math
import struct

import tkinter as tk

import client
import widgets

class MainWindow(tk.Frame):
    def __init__(self, parent, conn):
        tk.Frame.__init__(self, parent)
        self.conn = conn

        self.field_plot = widgets.Plot2D(self, 500, 500, -72, 72, -72, 72)
        self.field_plot.grid(row=0, column=0, rowspan=2)
        self.setup_grids()
        self.odo_channel = self.field_plot.add_channel((0xFF, 0x00, 0x00))
        self.sprite_heading = self.field_plot.add_sprite((0x00, 0x00, 0xFF),
                (( (0, 0),  (10, 0) ),
                 ( (10, 0), (9,  1) ),
                 ( (10, 0), (9, -1) ),
                )
        )
        self.sprite_target = self.field_plot.add_sprite((0x00, 0xFF, 0xFF),
                (( (0, 0), (5, 0) ),
                )
        )
        self.sprite_pt = self.field_plot.add_sprite((0x00, 0x00, 0x00),
                (( (-1,  1), ( 1, -1) ),
                 ( ( 1,  1), (-1, -1) ),
                )
        )

        pt_x, pt_y, heading_off = struct.unpack('>fff', self.conn.send_recv(0x02))
        self.heading_off = heading_off
        self.field_plot.put_sprite(self.sprite_pt, pt_x, pt_y)

    def update(self, root):
        data = self.conn.send_recv(0x01)
        if data is None:
            return
        values = struct.unpack('>ffff', data)
        # Plot the robot's XY location (does nothing if the value is the same)
        odo_x = values[0]
        odo_y = values[1]
        heading = values[2]
        target_heading = values[3]
        self.field_plot.put(self.odo_channel, odo_x, odo_y)
        self.field_plot.put_sprite(self.sprite_heading, odo_x, odo_y,
                math.radians(heading))
        self.field_plot.put_sprite(self.sprite_target, odo_x, odo_y,
                math.radians(target_heading + heading))

        root.after(16, self.update, root)

    def setup_grids(self):
        ylines = self.field_plot.add_channel((0xcc, 0xcc, 0xcc))
        y0 = 75
        for x in range(-11, 12):
            self.field_plot.put(ylines, x*6, y0)
            y0 = -y0
            self.field_plot.put(ylines, x*6, y0)

        xlines = self.field_plot.add_channel((0xcc, 0xcc, 0xcc))
        x0 = 75
        for y in range(-11, 12):
            self.field_plot.put(xlines, x0, y*6)
            x0 = -x0
            self.field_plot.put(xlines, x0, y*6)

        x_zero_line = self.field_plot.add_channel((0x80, 0x80, 0x80))
        self.field_plot.put(x_zero_line, -75, 0)
        self.field_plot.put(x_zero_line,  75, 0)
        y_zero_line = self.field_plot.add_channel((0x80, 0x80, 0x80))
        self.field_plot.put(y_zero_line, 0, -75)
        self.field_plot.put(y_zero_line, 0,  75)

if __name__ == '__main__':
    conn = client.Connection('192.168.43.1', 19997)
    conn.connect()

    root = tk.Tk()
    win = MainWindow(root, conn)
    win.grid(column=0, row=0)

    root.after(0, win.update, root)
    root.mainloop()
