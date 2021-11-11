import struct
from typing import List
from matplotlib import pyplot, animation


class Plot:
    def __init__(self, conn, labels: dict, y_range: tuple) -> None:
        self.conn = conn
        self.conn.connect()
        self.fig, self.ax = pyplot.subplots()
        self.ax.set_ylim(y_range[0], y_range[1])
        self.size = abs(y_range[0]) + y_range[1]
        self.num_lines = len(labels)
        self.labels = labels
        self.line_ranges = []
        self.lines = []
        self.paused = False
    
    def generate_lines(self):
        x = [i for i in range(self.size)]
        for line_num in range(self.num_lines):
            self.line_ranges.append([0 for i in range(self.size)])
            line = self.line_ranges[line_num]
            label = list(self.labels.keys())[line_num]
            color = list(self.labels.values())[line_num][0]
            self.lines.append(self.ax.plot(x, line, label=label, color=color))

    def animate(self, frame):
        nums = self.grab_data(0x1, str(self.num_lines))
        for line_num in range(self.num_lines):
            for i in range(int(0.01 * self.size)):
                self.line_ranges[line_num].pop(0)
                scalar = list(self.labels.values())[line_num][1]
                self.line_ranges[line_num].append(nums[line_num] * scalar)
            self.lines[line_num][0].set_ydata(self.line_ranges[line_num])
        return self.lines
    
    def update_lines(self):
        self.ax.legend()
        self.fig.canvas.mpl_connect('button_press_event', self.change_state) # Callback for pausing with left-click
        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=1, frames=6000) # Runs for around 2 minutes (updates line every 1 ms)
        pyplot.show()
    
    def grab_data(self, command, bytes):
        data_raw = self.conn.send_recv(command)
        if data_raw is None:
            print('Empty')
            pass
        nums = struct.unpack('>' + bytes + 'd', data_raw)
        for index, num in enumerate(nums):
            if num == 0:
                continue
            label = tuple(self.labels.keys())[index]
            print(label + ': ' + str(num), end='   ')
        print()
        return nums
    
    def change_state(self, *args, **kwargs):
        if self.paused:
            self.ani.resume()
        else:
            self.ani.pause()
        self.paused = not self.paused