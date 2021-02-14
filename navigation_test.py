import math

import tkinter as tk

import client
import widgets

class MainWindow(tk.Frame):
    def __init__(self, parent, conn):
        tk.Frame.__init__(self, parent)
        self.conn = conn

        # Widgets:
        # * Field graph (data from telemetry)
        # * Telemetry widget (receives all data and displays it)
        #   * X,Y position from odometry (f32, f32)
        #   * IMU heading, degrees (f32)
        #   * Odometry calculated heading, degrees (f32)
        #   * Left drive wheel encoder (int32)
        #   * Right drive wheel encoder (int32)
        #   * Left odometry wheel encoder (f32)
        #   * Right odometry wheel encoder (f32)
        #   * X, Y target position (f32, f32)
        #   * Target heading, degrees (f32)
        #   * Target distance (f32)
        #   * Forward power (f32)
        #   * Turn power (f32)
        # * Settings widgets (adjust things)
        # * 1D plot of distance error (-1 to 1 range or something)
        # * 1D plot of angle error (-10 to 10 range)
        # * 1D plot of forward and turn power (-1 to 1 range)

        self.field_plot = widgets.Plot2D(self, 500, 500, -72, 72, -72, 72)
        self.field_plot.grid(row=0, column=0, rowspan=2)
        self.setup_grids()
        self.odo_channel = self.field_plot.add_channel((0xFF, 0x00, 0x00))
        self.sprite_heading = self.field_plot.add_sprite((0x00, 0x00, 0xFF),
                (( (0, 0),  (10, 0) ),
                 ( (10, 0), (7,  3) ),
                 ( (10, 0), (7, -3) ))
        )
        self.power_plot = widgets.Plot1D(self, 200, 100, 400, -1, 1)
        self.power_chan_fwd  = self.power_plot.add_channel((0xFF, 0x00, 0x00))
        self.power_chan_turn = self.power_plot.add_channel((0x00, 0x00, 0xFF))

        self.telem_widget = widgets.TelemetryWidget(self, conn, 0x01, (
            "Odometry X ",         # 0
            "Odometry Y ",         # 1
            "IMU heading",         # 2
            "Odo heading",         # 3
            "Left wheel encoder ", # 4
            "Right wheel encoder", # 5
            "Left odo encoder ",   # 6
            "Right odo encoder",   # 7
            "Target X ......",     # 8
            "Target Y ......",     # 9
            "Target heading ",     # 10
            "Target forward distance", # 11
            "Forward power",       # 12
            "Turn power ..",       # 13
            "OpMode Status"        # 14
        ), ('%.2f', '%.2f', '%.2f', '%.2f', '%d', '%d', '%.2f', '%.2f', '%.2f', '%.2f',
            '%.2f', '%.2f', '%.3f', '%.3f', '%d'), '>ffffiiffffffffB')
        self.telem_widget.grid(row=0, column=1)

        self.button_frame = tk.Frame(self)

        self.btn_stop = tk.Button(self.button_frame, text='Stop Motors', command=self.start_stop)
        self.btn_stop.grid(row=0, column=0)
        self.slider_fwdSpeed = tk.Scale(self.button_frame, label='Forward Speed',
            from_=0, to=1, resolution=0.01, orient='horizontal', length=100, command=self.send_settings)
        self.slider_fwdSpeed.grid(row=1, column=0)
        self.slider_turnSpeed = tk.Scale(self.button_frame, label='Turn Speed',
            from_=0, to=1, resolution=0.01, orient='horizontal', length=100, command=self.send_settings)
        self.slider_turnSpeed.grid(row=2, column=0)
        self.slider_fwdKp = tk.Scale(self.button_frame, label='Forward kP',
            from_=0, to=0.5, resolution=0.01, orient='horizontal', length=100, command=self.send_settings)
        self.slider_fwdKp.grid(row=3, column=0)
        self.slider_turnKp = tk.Scale(self.button_frame, label='Turn kP',
            from_=0, to=0.5, resolution=0.01, orient='horizontal', length=100, command=self.send_settings)
        self.slider_turnKp.grid(row=4, column=0)
        self.button_frame.grid(row=0, column=2)


    def update(self, root):
        connected = self.telem_widget.update()
        if not connected:
            return
        # Plot the robot's XY location (does nothing if the value is the same)
        odo_x = self.telem_widget.values[0]
        odo_y = self.telem_widget.values[1]
        self.field_plot.put(self.odo_channel, odo_x, odo_y)
        self.field_plot.put_sprite(self.sprite_heading, odo_x, odo_y,
                math.radians(self.telem_widget.values[2]))

        if self.telem_widget.values[14] == 1:
            self.power_plot.put(self.power_chan_fwd, self.telem_widget.values[12])
            self.power_plot.put(self.power_chan_turn, self.telem_widget.values[13])

        root.after(16, self.update, root)

    def start_stop(self, ev):
        pass

    def send_settings(self, val):

        pass

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
    conn = client.Connection('192.168.43.1', 19998)
    conn.connect()

    root = tk.Tk()
    win = MainWindow(root, conn)
    win.grid(column=0, row=0)

    root.after(0, win.update, root)
    root.mainloop()
