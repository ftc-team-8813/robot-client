import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

import client
import draw

import sys
import time
import io

img_ref = None

def update(conn, root, canvas, img_id, textvar, logview):
    global img_ref

    # pull new log data
    log_raw = conn.send_recv(0x01)
    if log_raw is None: return
    log_data = log_raw.decode('utf-8')
    if len(log_data) > 0:
        print(log_data)
        logview.configure(state='normal')
        logview.insert("end", log_data)
        logview.see("end")
        logview.configure(state='disabled')

    frame = conn.send_recv(0x02)
    if frame is None: return
    draw_data = b''
    if len(frame) > 0:
        img = Image.open(io.BytesIO(frame))
        draw_data = conn.send_recv(0x03)
        if draw_data is None: return
        draw.draw(img, draw_data)
        img_ref = ImageTk.PhotoImage(img)
        canvas.itemconfigure(img_id, image=img_ref)

    telem_data = conn.send_recv(0x04)
    if telem_data is None: return
    telem = np.frombuffer(telem_data, dtype='>f8')
    if len(telem) > 0:
        textvar.set(
            """
Forward power:    %.3f
Turn power:       %.3f
Forward position: %.1f
Heading:          %.3f
Path index:       %.0f
Speed:            %.3f
Turret position:  %.3f
Turret target:    %.3f
Shooter power:    %.3f
Shooter velocity: %.0f
Rings detected:   %.0f
            """ % tuple(telem)
        )

    if len(log_raw) > 0 or len(frame) > 0 or len(draw_data) > 0 or len(telem_data) > 0:
        print("-> Data: %d bytes log, %d bytes frame, %d bytes draw, %d bytes telemetry" % (len(log_raw), len(frame), len(draw_data), len(telem_data)))

    root.after(16, update, conn, root, canvas, img_id, textvar, logview)

def main():
    conn = client.Connection('192.168.43.1', 8813)
    conn.connect()

    root = tk.Tk()
    img_width = 800
    img_height = 448

    canvas = tk.Canvas(root, width=img_width, height=img_height)
    canvas.grid(column=0, row=0, columnspan=2)
    canvas_img = canvas.create_image(0, 0, image=None, anchor='nw')

    frame = tk.Frame(root)
    logview = tk.Text(frame, width=150, height=13)
    logscroll = tk.Scrollbar(frame, orient='vertical', command=logview.yview)
    logview.configure(yscrollcommand=logscroll.set)
    logview.grid(column=0, row=0)
    logscroll.grid(column=1, row=0, sticky="ns")
    frame.grid(column=0, row=1, sticky="w")
    logview.configure(state='disabled')

    textvar = tk.StringVar()
    textvar.set(
        """
        Forward power:
        Turn power:
        Forward position:
        Heading:
        Path index:
        Speed:
        Turret position:
        Turret target:
        Shooter power:
        Shooter velocity:
        Rings detected:
        """
    )
    telem_message = tk.Message(root, textvariable=textvar, anchor='nw', justify='left', font='monospace 9', bg='#ffffff', width=300)
    telem_message.grid(column=1, row=1, sticky="ew")

    root.resizable(False, False)

    root.after(16, update, conn, root, canvas, canvas_img, textvar, logview)
    root.mainloop()

if __name__ == '__main__':
    main()
