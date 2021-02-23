# Basic robot client widgets to create Tkinter windows
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

import io
import struct

import client
import draw
import math

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
        self.values = values
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
            y1 = self.get_pixel_y(this_pt)
            y2 = self.get_pixel_y(next_pt)
            x1 = self.width - (self.width / self.x_size) * (n+1)
            x2 = self.width - (self.width / self.x_size) * n
            self.canvas.create_line(x1, y1, x2, y2, fill=ch_color, tags=ch_tag, width=2)
            # TODO: filled areas (if necessary)
            n += 1

    def get_pixel_y(self, y):
        margin = 3
        return (y - self.ymin) / (self.ymax - self.ymin) * -(self.height - margin*2) + self.height - margin

    def put(self, channel, value):
        points_list = self.channels[channel]['points']
        points_list.append(value)
        if len(points_list) > self.x_size:
            points_list.pop(0)
        self.redraw(channel)

    def clear(self):
        for i in range(len(self.channels)):
            self.channels[i]['points'] = []
            self.redraw(i)

class Plot2D(tk.Frame):

    def __init__(self, parent, width, height, min_x, max_x, min_y, max_y,
                 bg='#ffffff', bg_img=None, viewport_size=None):
        tk.Frame.__init__(self, parent)
        self.width = width
        self.height = height

        if viewport_size is not None:
            self.scrollx = tk.Scrollbar(self, orient=HORIZONTAL)
            self.scrolly = tk.Scrollbar(self, orient=VERTICAL)
            self.canvas = tk.Canvas(self,
                width=viewport_size[0], height=viewport_size[1], background=bg,
                scrollregion=(0, 0, width, height),
                xscrollcommand=self.scrollx.set, yscrollcommand=self.scrolly.set)
            self.scrollx['command'] = self.canvas.xview
            self.scrolly['command'] = self.canvas.yview
            self.scrollx.grid(column=0, row=1, sticky='ew')
            self.scrolly.grid(column=1, row=0, sticky='ns')
        else:
            self.canvas = tk.Canvas(self, width=width, height=height, background=bg)
        if bg_img is not None:
            self.bg_img = tk.PhotoImage(bg_img)
            self.canvas.create_image(0, 0, image=self.bg_img, anchor='nw', tags='bg-img')
        self.canvas.grid(column=0, row=0)

        self.xmin = min_x
        self.ymin = min_y
        self.xmax = max_x
        self.ymax = max_y

        self.channels = []
        self.sprites = []

    def add_channel(self, color):
        chid = len(self.channels)
        self.channels.append({
            'color': '#%02x%02x%02x' % color,
            'points': [],
            'tag': 'channel-' + str(chid)
        })
        return chid

    def add_sprite(self, color, segments):
        sprite_id = len(self.sprites)
        self.sprites.append({
            'color': '#%02x%02x%02x' % color,
            'segments': segments,
            'tag': 'sprite-' + str(sprite_id),
            'lines': []
        })
        return sprite_id

    def put_sprite(self, sprite, x, y, rotation=0, scale=1):
        spr = self.sprites[sprite]
        # for line_id in self.canvas.find_withtag(spr['tag']):
        #     self.canvas.delete(line_id)
        line_n = 0
        for seg in spr['segments']:
            past_x = None
            past_y = None
            for pt in seg:
                res_x = x + (pt[0] * math.cos(rotation) - pt[1] * math.sin(rotation)) * scale
                res_y = y + (pt[0] * math.sin(rotation) + pt[1] * math.cos(rotation)) * scale
                pix_x = self.get_pixel_x(res_x)
                pix_y = self.get_pixel_y(res_y)
                if past_x is not None:
                    if len(spr['lines']) <= line_n:
                        line_id = self.canvas.create_line(past_x, past_y,
                                pix_x, pix_y, fill=spr['color'], width=2,
                                tags=spr['tag'])
                        spr['lines'].append(line_id)
                    else:
                        line_id = spr['lines'][line_n]
                        self.canvas.coords(line_id, past_x, past_y, pix_x, pix_y)
                    line_n += 1

                past_x = pix_x
                past_y = pix_y

    def get_pixel_x(self, x):
        margin = 3
        return (x - self.xmin) / (self.xmax - self.xmin) * (self.width - 2*margin) + margin

    def get_pixel_y(self, y):
        margin = 3
        return (y - self.ymin) / (self.ymax - self.ymin) * -(self.height - 2*margin) + self.height - margin

    def get_plot_x(self, px):
        margin = 3
        return (px - margin) * (self.xmax - self.xmin) / (self.width - 2*margin) + self.xmin

    def get_plot_y(self, py):
        margin = 3
        return (py - margin) * (self.ymax - self.ymin) / (self.height - 2*margin) + self.ymin

    def set_click_listener(self, func):
        self.canvas.bind("<Button 1>", func)

    def draw_next_point(self, channel, index=-2):
        pts = self.channels[channel]['points']
        if len(pts) < 2: return
        start = pts[index]
        end = pts[index+1]
        x0 = self.get_pixel_x(start[0])
        x1 = self.get_pixel_x(end[0])
        y0 = self.get_pixel_y(start[1])
        y1 = self.get_pixel_y(end[1])
        self.canvas.create_line(x0, y0, x1, y1, fill=self.channels[channel]['color'],
            tags=self.channels[channel]['tag'], width=2)

    def clear(self, channel, delete=True):
        for line in self.canvas.find_withtag(self.channels[channel]['tag']):
            self.canvas.delete(line)
        if delete:
            self.channels[channel]['points'] = []

    def redraw(self):
        for chan in range(len(self.channels)):
            self.clear(chan, delete=False)
            for i in range(len(self.channels[chan]['points']) - 1):
                self.draw_next_point(chan, index=i)

    def set_bounds(self, xmin, xmax, ymin, ymax):
        if (self.xmin, self.xmax, self.ymin, self.ymax) != (xmin, xmax, ymin, ymax):
            self.xmin = xmin
            self.xmax = xmax
            self.ymin = ymin
            self.ymax = ymax
            self.redraw()

    def put(self, channel, x, y):
        pts = self.channels[channel]['points']
        if len(pts) == 0 or pts[-1] != (x, y):
            pts.append((x, y))
            self.draw_next_point(channel)
