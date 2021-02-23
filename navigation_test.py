import math
import struct

import tkinter as tk

import client
import widgets

def verify_numeric(v):
    try:
        float(v + '0')
        return True
    except ValueError:
        return False

class MainWindow(tk.Frame):
    def __init__(self, parent, conn):
        tk.Frame.__init__(self, parent)
        self.parent = parent
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

        self.btn_conn = tk.Button(self, text='Reconnect', command=self.reconnect)
        self.btn_conn.grid(row=0, column=0, columnspan=3, sticky='EW')

        self.field_plot = widgets.Plot2D(self, 500, 250, -48, 48, -24, 24)
        self.field_plot.grid(row=1, column=0, rowspan=2)
        self.setup_grids()
        self.odo_channel = self.field_plot.add_channel((0xFF, 0x00, 0x00))
        self.sprite_heading = self.field_plot.add_sprite((0x00, 0x00, 0xFF),
                (( (0, 0),  (10, 0) ),
                 ( (10, 0), (7,  3) ),
                 ( (10, 0), (7, -3) ))
        )
        self.sprite_target = self.field_plot.add_sprite((0x00, 0x00, 0x00),
                (( (-1, 1), ( 1, -1) ),
                 ( ( 1, 1), (-1, -1) ),
                )
        )
        self.power_plot = widgets.Plot1D(self, 200, 100, 400, -1, 1)
        self.power_chan_fwd  = self.power_plot.add_channel((0xFF, 0x00, 0x00))
        self.power_chan_turn = self.power_plot.add_channel((0x00, 0x00, 0xFF))
        self.field_plot.set_click_listener(self.plot_onclick)

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
        self.telem_widget.grid(row=1, column=1)

        self.button_frame = tk.Frame(self)

        vcmd = (self.register(verify_numeric), '%P')

        self.btn_stop = tk.Button(self.button_frame, text='Stop Program', command=self.start_stop)
        self.btn_stop.grid(row=0, column=0, columnspan=2, sticky='EW')

        self.label_fwdSpeed = tk.Label(self.button_frame, text='Forward Speed')
        self.label_fwdSpeed.grid(row=1, column=0)
        self.slider_fwdSpeed = tk.Scale(self.button_frame, from_=0, to=1, resolution=0.01, orient='horizontal', length=100)
        self.slider_fwdSpeed.grid(row=1, column=1)

        self.label_turnSpeed = tk.Label(self.button_frame, text='Turn Speed')
        self.label_turnSpeed.grid(row=2, column=0)
        self.slider_turnSpeed = tk.Scale(self.button_frame, from_=0, to=1, resolution=0.01, orient='horizontal', length=150)
        self.slider_turnSpeed.grid(row=2, column=1)

        self.label_fwdKp = tk.Label(self.button_frame, text='Forward kP')
        self.label_fwdKp.grid(row=3, column=0)
        self.input_fwdKp = tk.Entry(self.button_frame, validate='key', vcmd=vcmd)
        self.input_fwdKp.insert("end", '0.15')
        self.input_fwdKp.grid(row=3, column=1)

        self.label_fwdKi = tk.Label(self.button_frame, text='Forward kI')
        self.label_fwdKi.grid(row=4, column=0)
        self.input_fwdKi = tk.Entry(self.button_frame, validate='key', vcmd=vcmd)
        self.input_fwdKi.insert("end", '0.001')
        self.input_fwdKi.grid(row=4, column=1)

        self.label_turnKp = tk.Label(self.button_frame, text='Turn kP')
        self.label_turnKp.grid(row=5, column=0)
        self.input_turnKp = tk.Entry(self.button_frame, validate='key', vcmd=vcmd)
        self.input_turnKp.insert("end", '0.01')
        self.input_turnKp.grid(row=5, column=1)

        self.label_turnKi = tk.Label(self.button_frame, text='Forward kI')
        self.label_turnKi.grid(row=6, column=0)
        self.input_turnKi = tk.Entry(self.button_frame, validate='key', vcmd=vcmd)
        self.input_turnKi.insert("end", '0.001')
        self.input_turnKi.grid(row=6, column=1)

        self.submit_btn = tk.Button(self.button_frame, text='Update', command=self.send_settings)
        self.submit_btn.grid(row=7, column=0, columnspan=2, sticky='EW')

        self.clear_btn = tk.Button(self.button_frame, text='Clear Plot', command=self.clear_plot)
        self.clear_btn.grid(row=8, column=0, columnspan=2)

        self.button_frame.grid(row=1, column=2)

    def update(self, root):
        connected = self.telem_widget.update()
        if not connected:
            return
        # Plot the robot's XY location (does nothing if the value is the same)
        odo_x = self.telem_widget.values[0]
        odo_y = self.telem_widget.values[1]
        target_x = self.telem_widget.values[8]
        target_y = self.telem_widget.values[9]
        self.field_plot.put(self.odo_channel, odo_x, odo_y)
        self.field_plot.put_sprite(self.sprite_heading, odo_x, odo_y,
                math.radians(self.telem_widget.values[2]))
        self.field_plot.put_sprite(self.sprite_target, target_x, target_y)

        if self.telem_widget.values[14] == 1:
            self.power_plot.put(self.power_chan_fwd, self.telem_widget.values[12])
            self.power_plot.put(self.power_chan_turn, self.telem_widget.values[13])

        root.after(16, self.update, root)

    def reconnect(self):
        if not self.conn.connected:
            self.conn.connect()
            self.clear_plot()
            self.parent.after(0, self.update, self.parent)

    def plot_onclick(self, pos):
        plot_x = self.field_plot.get_plot_x(pos.x)
        plot_y = -self.field_plot.get_plot_y(pos.y)
        self.send_settings()
        res = self.conn.send_recv(0x02, struct.pack('>ff', plot_x, plot_y))
        if res is None: return
        print("(%.3f, %.3f) -> %d" % (plot_x, plot_y, res[0]))

    def clear_plot(self):
        self.field_plot.clear(self.odo_channel)

    def start_stop(self):
        self.conn.send_recv(0x04) # Emergency stop

    def send_settings(self):
        fspeed = self.slider_fwdSpeed.get()
        tspeed = self.slider_turnSpeed.get()
        try:
            fkp = float(self.input_fwdKp.get())
            fki = float(self.input_fwdKi.get())
            tkp = float(self.input_turnKp.get())
            tki = float(self.input_turnKi.get())
        except ValueError:
            return

        res = self.conn.send_recv(0x03, struct.pack('>ffffff',
            fspeed, tspeed, fkp, fki, tkp, tki))
        if res is None: return
        print('-> %d' % res[0])

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
    # conn.connect()

    root = tk.Tk()
    win = MainWindow(root, conn)
    win.grid(column=0, row=0)

    root.after(0, win.update, root)
    root.mainloop()
