import client
from PIL import Image
import cv2
import draw
import client
import struct
import numpy as np

def main():
    conn = client.Connection('192.168.43.1', 19999)
    conn.connect()

    last_x = 500
    last_y = 500

    img = Image.open('graph.png')
    # overlay = Image.new('RGBA', 1000, 1000, (0, 0, 0, 0))
    while True:
        data_raw = conn.send_recv(0x1)
        if data_raw is None: return
        data = np.frombuffer(data_raw[:-4], dtype='>f8')
        color = struct.unpack('>I', data_raw[-4:])[0]
        print(data)

        x = data[3] * 7
        y = data[4] * 7

        img_x = y + 500
        img_y = 500 - x

        draw_packet = struct.pack('>BIBBHhhhh', 0x03, color, 2, 0, 0, int(last_x), int(last_y), int(img_x), int(img_y))

        last_x = img_x
        last_y = img_y

        draw.draw(img, draw_packet)
        img_array = np.array(img)
        # overlay_array = np.array(overlay)
        # img_array = cv2.addWeighted(img_array, overlay_array[:,:,:3], overlay_array[:,:,3])
        cv2.imshow('path', img_array)
        cv2.waitKey(16)

if __name__ == '__main__':
    main()
