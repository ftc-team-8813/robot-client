import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
from time import sleep

import client
import draw

import sys
import time
import io

img_ref = None

def update(conn, root, canvas, img_id, textvar):
    global img_ref
    frame = b''
    while len(frame) == 0:
        frame = conn.send_recv(0x01)
        if frame is None: sys.exit(1)
        time.sleep(0.01)
    # print("-> Recv frame: %d bytes" % len(frame))
    img = Image.open(io.BytesIO(frame))
    # img.save("competition.jpg", "JPEG")
    # sys.exit('Saved Image') 
    draw_data = conn.send_recv(0x02)
    if draw_data is None: sys.exit(1)
    draw.draw(img, draw_data)
    img_ref = ImageTk.PhotoImage(img)
    canvas.itemconfigure(img_id, image=img_ref)

    telem_data = conn.send_recv(0x03)
    if telem_data is None: sys.exit(1)
    telem = np.frombuffer(telem_data, dtype='>f8')
    # textvar.set('Contour area: %.3f' % telem[0])

    print("-> Data: %d bytes frame, %d bytes draw, %d bytes telemetry" % (len(frame), len(draw_data), len(telem_data)))

    root.after(16, update, conn, root, canvas, img_id, textvar)

def main():
    conn = client.Connection('192.168.43.1', 20000)
    conn.connect()

    root = tk.Tk()
    img_width = 800
    img_height = 448

    canvas = tk.Canvas(root, width=img_width, height=img_height)
    canvas.grid(column=0, row=0)
    canvas_img = canvas.create_image(0, 0, image=None, anchor='nw')

    textvar = tk.StringVar()
    label = tk.Label(root, textvariable=textvar)
    label.grid(column=0, row=1)

    root.after(16, update, conn, root, canvas, canvas_img, textvar)
    root.mainloop()

if __name__ == '__main__':
    main()
