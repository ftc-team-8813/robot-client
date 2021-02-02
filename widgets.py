# Basic robot client widgets to create Tkinter windows
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

import io
import struct

import client
import draw

class JpegWidget(tk.Frame):
    def __init__(self, parent, conn, cmd_id, width, height, scale_fac=1, draw_cmd=None):
        tk.Frame.__init__(self, parent)
        self.conn = conn
        self.cmd_id = cmd_id
        self.canvas_width = int(width * scale_fac)
        self.canvas_height = int(height * scale_fac)

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(column=0, row=0)
        self.canvas_img = self.canvas.create_image(0, 0, image=None, anchor='nw')
        self.photo_image = None

        self.scale_factor = scale_fac
        self.draw_cmd = draw_cmd

    def update(self, send_data=b''):
        frame = self.conn.send_recv(self.cmd_id, send_data)
        if frame is None: return False
        if len(frame) > 0:
            img = Image.open(io.BytesIO(frame))
            if self.scale_factor != 1:
                img = img.resize((self.canvas_width, self.canvas_height))
            if self.draw_cmd is not None:
                draw_data = self.conn.send_recv(self.draw_cmd)
                if draw_data is None: return False
                draw.draw(img, draw_data, self.scale_factor)
            self.photo_image = ImageTk.PhotoImage(img)
            canvas.itemconfigure(self.canvas_img, self.photo_image)
        return True

class TelemetryWidget(tk.Frame):
    def __init__(self, parent, conn, cmd_id, captions, format_strings, structure):
        tk.Frame.__init__(self, parent)

        self.conn = conn
        self.cmd_id = cmd_id
        self.captions = captions
        self.format_strings = format_strings
        self.struct = struct.Struct(structure)

        self.message = tk.Message(self, text='', anchor='nw', justify='left', font='monospace 9')
        self.message.grid(column=0, row=0)

    def update(self, send_data=b''):
        data = self.conn.send_recv(self.cmd_id, send_data)
        if data is None: return False
        if len(data) != self.struct.size:
            if len(data) > 0:
                print("[TelemetryWidget ERROR -- need %d bytes, got %d bytes]" % (self.struct.size, len(data)))
            return True
        values = self.struct.unpack(data)
        text = ''
        for i in range(len(self.captions)):
            text += ('%s: ' + self.format_strings[i] + '\n') % (self.captions[i], values[i])
        self.message.configure(text=text)
        return True

class LogWidget(tk.Frame):
    def __init__(self, parent, conn, cmd_id, width, height):
        tk.Frame.__init__(self, parent)

        self.conn = conn
        self.cmd_id = cmd_id
        self.textbox = tk.Text(self, width=width, height=height)
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.textbox.yview)

        self.textbox.configure(yscrollcommand=self.scrollbar.set)
        self.textbox.grid(column=0, row=0)
        self.scrollbar.grid(column=1, row=0, sticky='ns')

        self.textbox.configure(state='disabled')

    def update(self, send_data=b''):
        data_raw = self.conn.send_recv(self.cmd_id, send_data)
        if data_raw is None: return False
        log_text = data_raw.decode('utf-8')
        if len(log_text) > 0:
            self.textbox.configure(state='normal')
            self.textbox.insert("end", log_text)
            self.textbox.see("end")
            self.textbox.configure(state='disabled')
        return True

class Plot1D(tk.Frame):
    # Simple 1-D line plot. Each value is separated by the same amount.
    STYLE_NORMAL = 0
    STYLE_FILLED = 1

    def __init__(self, parent, width, height, x_size, ymin, ymax, style=STYLE_NORMAL, bg='#ffffff'):
        tk.Frame.__init__(self, parent)
        self.width = width
        self.height = height

        self.canvas = tk.Canvas(self, width=width, height=height, background=bg)
        self.canvas.grid(column=0, row=0)

        self.x_size = x_size
        self.channels = []

        self.ymin = ymin
        self.ymax = ymax

        self.style = style
        self.bg = bg

    def add_channel(self, color):
        chid = len(self.channels)
        self.channels.append({
            'color': '#%02x%02x%02x' % color,
            'points': [],
            'tag': 'channel-' + str(chid)
        })
        return chid

    def redraw(self, channel):
        ch_tag    = self.channels[channel]['tag']
        old_drawing = self.canvas.find_withtag(ch_tag)
        for shape_id in old_drawing:
            self.canvas.delete(shape_id)

        ch_color  = self.channels[channel]['color']
        ch_points = self.channels[channel]['points']
        n = 0
        for i in reversed(range(len(ch_points)-1)):
            this_pt = ch_points[i]
            next_pt = ch_points[i+1]
            y_margin = 3
            y1 = (this_pt - self.ymin) / (self.ymax - self.ymin) * -(self.height-y_margin*2) + self.height - y_margin
            y2 = (next_pt - self.ymin) / (self.ymax - self.ymin) * -(self.height-y_margin*2) + self.height - y_margin
            x1 = self.width - (self.width / self.x_size) * (n+1)
            x2 = self.width - (self.width / self.x_size) * n
            self.canvas.create_line(x1, y1, x2, y2, fill=ch_color, tags=ch_tag, width=2)
            # TODO: filled areas (if necessary)
            n += 1

    def put(self, channel, value):
        points_list = self.channels[channel]['points']
        points_list.append(value)
        if len(points_list) > self.x_size:
            points_list.pop(0)
        self.redraw(channel)
