import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from numpy.lib.npyio import save
from client import Connection
from time import sleep
import struct

fig, ax = plt.subplots()

x = np.arange(0, 60, 0.01)
y1 = np.arange(-3000, 3000, 1)
y2 = np.arange(-3000, 3000, 1)
y3 = np.arange(-3000, 3000, 1)
arm_line, = ax.plot(y1, color='green', label='Arm Pos')
p_line, = ax.plot(y2, color='blue', label='P Term')
i_line, = ax.plot(y3, color='red', label='I Term')
ax.legend()


arm_poses = [0 for i in range(6000)]
p_poses = [0 for i in range(6000)]
i_poses = [0 for i in range(6000)]


def grab_data(command, bytes):
    data_raw = conn.send_recv(command)
    if data_raw is None:
        return
    nums = struct.unpack('>' + bytes + 'd', data_raw)
    return nums

def update_line(line, poses, num):
    for i in range(100):
        poses.pop(0)
        poses.append(num)
    line.set_ydata(poses)

def animate(frame): 
    nums = grab_data(0x1, '3')

    update_line(arm_line, arm_poses, nums[0])
    update_line(p_line, p_poses, nums[1])
    update_line(i_line, i_poses, nums[2])
    return arm_line,

def main():
    ani = animation.FuncAnimation(fig, animate, interval=1, frames=6000) # Runs for around 2 minutes (updates line every 20 ms)
    plt.show()


if __name__ == '__main__':
    conn = Connection('127.0.0.1', 18888)
    conn.connect()
    main()
