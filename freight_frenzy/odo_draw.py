import math
import struct
import turtle
from time import sleep
from math import pi


class OdoDraw:
    def __init__(self, conn) -> None:
        self.conn = conn
        self.conn.connect()
        turtle.color('blue')

    def draw(self) -> None:
        scale_factor = 2
        while 1:
            y, x, heading = self.grab_data(0x2, '3')
            print(
                'Y: ' + str(y),
                'X: ' + str(x),
                'Heading (Degrees): ' + str(heading),
                
            )
            turtle.setposition(-y * scale_factor, x * scale_factor) # Flipped X and Y because coordinated system is offset in SDK
            turtle.setheading(heading + 90)
            sleep(0.01)
    
    def grab_data(self, command, bytes):
        data_raw = self.conn.send_recv(command)

        if data_raw is None:
            print('Empty')
            pass

        try:
            nums = struct.unpack('>' + bytes + 'd', data_raw)
        except TypeError:
            nums = [0, 0, 0]

        return nums