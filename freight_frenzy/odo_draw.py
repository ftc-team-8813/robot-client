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
            x, y, heading = self.grab_data(0x2, '3')
            heading = heading * (180/pi) + 90 # Convert to degrees and adjust by 90 for turtle
            print(
                'X: ' + str(x),
                'Y: ' + str(y),
                'Heading (Degrees): ' + str(heading),
                
            )
            turtle.setposition(y * scale_factor, x * scale_factor) # Flipped X and Y because coordinated system is offset in SDK
            turtle.setheading(heading)
            sleep(0.01)
    
    def grab_data(self, command, bytes):
        data_raw = self.conn.send_recv(command)
        if data_raw is None:
            print('Empty')
            pass
        nums = struct.unpack('>' + bytes + 'd', data_raw)
        return nums