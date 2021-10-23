import struct
import turtle
from time import sleep


class OdoDraw:
    def __init__(self, conn) -> None:
        self.conn = conn
        self.conn.connect()
        turtle.color('blue')

    def draw(self) -> None:
        scale_factor = 2
        while 1:
            x, y, heading = self.grab_data(0x2, '3')
            print(x, y, heading)
            turtle.setposition(x * scale_factor, y * scale_factor)
            turtle.setheading(heading)
            sleep(0.01)
    
    def grab_data(self, command, bytes):
        data_raw = self.conn.send_recv(command)
        if data_raw is None:
            print('Empty')
            pass
        nums = struct.unpack('>' + bytes + 'd', data_raw)
        return nums