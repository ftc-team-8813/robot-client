import math

import tkinter as tk

import client
import draw
import widgets

import struct
import io

from PIL import Image, ImageTk

class MainWindow(tk.Frame):
    def __init__(self, parent, conn):
        tk.Frame.__init__(self, parent)
        self.conn = conn

        self.field_plot = widgets.Plot2D(self, 500, 500, -144, 0, -72, 72)
        self.field_plot.grid(row=0, column=0, rowspan=3)
        self.setup_grids()
        self.odo_channel = self.field_plot.add_channel((0xFF, 0x00, 0x00))
        self.sprite_heading = self.field_plot.add_sprite((0x00, 0x00, 0xFF),
                (( (0, 0),  (10, 0) ),
                 ( (10, 0), (9,  1) ),
                 ( (10, 0), (9, -1) ),
                )
        )
        self.sprite_target = self.field_plot.add_sprite((0x00, 0x00, 0x00),
                (( (-1, 1), ( 1, -1) ),
                 ( ( 1, 1), (-1, -1) ),
                )
        )
        self.power_plot = widgets.Plot1D(self, 600, 100, 1000, -0.5, 0.5)
        self.power_plot.grid(row=0, column=1, columnspan=2)
        self.power_chan_fwd  = self.power_plot.add_channel((0xFF, 0x00, 0x00))
        self.power_chan_turn = self.power_plot.add_channel((0x00, 0x00, 0xFF))

        power_zero = self.power_plot.add_channel((0xcc, 0xcc, 0xcc))
        for i in range(1000):
            self.power_plot.put(power_zero, 0)

        self.dist_plot = widgets.Plot1D(self, 300, 100, 500, 0, 10)
        self.dist_plot.grid(row=1, column=1)
        self.dist_chan = self.dist_plot.add_channel((0x00, 0x00, 0x00))

        self.rate_plot = widgets.Plot1D(self, 300, 100, 500, 0, 10)
        self.rate_plot.grid(row=1, column=2)
        self.rate_chan = self.rate_plot.add_channel((0x00, 0x00, 0x00))

        self.heading_plot = widgets.Plot1D(self, 600, 100, 1000, -7, 7)
        self.heading_plot.grid(row=2, column=1, columnspan=2)
        self.heading_chan = self.heading_plot.add_channel((0xFF, 0x00, 0x00))
        self.htarget_chan = self.heading_plot.add_channel((0x00, 0xFF, 0x00))

        self.log_widget = widgets.LogWidget(self, self.conn, 0x01, 150, 10)
        self.log_widget.grid(row=3, column=0, columnspan=3)

        self.img_canvas = tk.Canvas(root, width=800, height=448)
        self.img_canvas.grid(row=0, column=3, rowspan=4)
        self.canvas_img = self.img_canvas.create_image(0, 0, image=None, anchor='nw')
        self.frame = None

    def update(self, root):
        data_raw = self.conn.send_recv(0x05)
        if data_raw is None: return
        data2_raw = self.conn.send_recv(0x04)
        if data2_raw is None: return
        frame_raw = self.conn.send_recv(0x02)
        if frame_raw is None: return

        data = struct.unpack('>10f', data_raw)
        if len(data2_raw) == 40:
            data2 = struct.unpack('>5d', data2_raw)
        else:
            data2 = [0] * 5

        if len(frame_raw) > 0:
            lines_raw = self.conn.send_recv(0x03)
            if lines_raw is None: return

            img = Image.open(io.BytesIO(frame_raw))
            draw.draw(img, lines_raw)
            self.frame = ImageTk.PhotoImage(img)
            self.img_canvas.itemconfigure(self.canvas_img, image=self.frame)

        # 0: Odo X
        # 1: Odo Y
        # 2: Heading
        # 3: Target X
        # 4: Target Y
        # 5: Target heading
        # 6: Target distance
        # 7: Forward power
        # 8: Turn power
        # 9: Distance change
        self.field_plot.put(self.odo_channel, data[0], data[1])
        self.field_plot.put_sprite(self.sprite_heading, data[0], data[1], data[2])
        self.field_plot.put_sprite(self.sprite_target, data[3], data[4])

        self.dist_plot.put(self.dist_chan, data[6])
        self.power_plot.put(self.power_chan_fwd, data[7])
        self.power_plot.put(self.power_chan_turn, data[8])
        self.rate_plot.put(self.rate_chan, data2[3])

        self.heading_plot.put(self.heading_chan, data[2])
        self.heading_plot.put(self.htarget_chan, data[5])

        self.log_widget.update()

        root.after(10, self.update, root)

    def setup_grids(self):
        ylines = self.field_plot.add_channel((0xcc, 0xcc, 0xcc))
        y0 = 75
        x = -144
        for i in range(24):
            self.field_plot.put(ylines, x+i*6, y0)
            y0 = -y0
            self.field_plot.put(ylines, x+i*6, y0)

        xlines = self.field_plot.add_channel((0xcc, 0xcc, 0xcc))
        x0 = 144
        y = -72
        for i in range(24):
            self.field_plot.put(xlines, x0, y+i*6)
            x0 = -x0
            self.field_plot.put(xlines, x0, y+i*6)

        x_zero_line = self.field_plot.add_channel((0x80, 0x80, 0x80))
        self.field_plot.put(x_zero_line, -144, 0)
        self.field_plot.put(x_zero_line,  144, 0)
        y_zero_line = self.field_plot.add_channel((0x80, 0x80, 0x80))
        self.field_plot.put(y_zero_line, 0, -75)
        self.field_plot.put(y_zero_line, 0,  75)


if __name__ == '__main__':
    conn = client.Connection('192.168.43.1', 8814)
    conn.connect()

    root = tk.Tk()
    win = MainWindow(root, conn)
    win.grid(column=0, row=0)

    root.after(0, win.update, root)
    root.mainloop()
