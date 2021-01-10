import client
import atexit
import time

import numpy as np
import cv2

IP_ADDR = '192.168.43.1' # Control Hub address (usually fixed to this)
PORT = 23456 # Port number, set by the server

def main():
    conn = client.Connection(IP_ADDR, PORT)
    conn.connect()
    atexit.register(conn.close)
    resp = conn.send_recv(0x00, b'testing')
    if resp is None: return
    print(resp)
    cams = conn.send_recv(0x01, b'')
    if cams is None: return
    print(cams)
    sn = cams.split(b',')[0]
    print("Opening camera %s" % sn)
    result = conn.send_recv(0x02, sn)
    if result is None: return
    print(result)
    # if result.startswith(b'!'): return
    frame = b''
    while True:
        while len(frame) == 0:
            frame = conn.send_recv(0x03, b'')
            if frame is None: return
            time.sleep(0.01)
        # print("Got frame")
        frame_data = np.frombuffer(frame, dtype='uint8')
        img = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
        cv2.imshow('Stream test', img)
        cv2.waitKey(5)
        frame = b''

    # with open('frame.jpg', 'wb') as of:
    #     of.write(frame)


if __name__ == '__main__':
    main()
