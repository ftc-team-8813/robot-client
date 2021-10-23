from PIL import ImageDraw
import struct

def draw(img, packet, scale=1):
    # draw data sent as a list of opcodes followed by some parameters:
    # 0x00: Arc      <x0=uint16> <y0=uint16> <x1=uint16> <y1=uint16> <start=float> <end=float> <stroke=uint32> <width=uint8>
    # 0x01: Chord    <x0=uint16> <y0=uint16> <x1=uint16> <y1=uint16> <start=float> <end=float> <stroke=uint32> <fill=uint32> <width=uint8>
    # 0x02: Ellipse  <x0=uint16> <y0=uint16> <x1=uint16> <y1=uint16> <stroke=uint32> <fill=uint32> <width=uint8>
    # 0x03: Line     <fill=uint32> <width=uint8> <join=uint8> <segments=uint16> <x0=uint16 y0=uint16> <x1=uint16 y1=uint16>...
    # 0x04: Pieslice <x0=uint16> <y0=uint16> <x1=uint16> <y1=uint16> <start=float> <end=float> <stroke=uint32> <fill=uint32> <width=uint8>
    # 0x05: Point    <x=uint16> <y=uint16> <color=uint32>
    # 0x06: Polygon  <fill=uint32> <stroke=uint32> <segments=uint8> <x0=uint16 y0=uint16> <x1=uint16 y1=uint16>...
    # 0x07: RegPoly  <cx=uint16> <cy=uint16> <radius=uint16> <sides=uint8> <rotation=float> <fill=uint32> <stroke=uint32>
    # 0x08: Rect     <x0=uint16> <y0=uint16> <x1=uint16> <y1=uint16> <fill=uint32> <stroke=uint32> <width=uint8>
    # 0x09: Text     <x=uint16> <y=uint16> <textlen=uint32> <text=char[]> <fill=uint32> <anchor=uint8> <spacing=uint16> <align=uint8> <direction=uint8> <width=uint8> <stroke_fill=uint32>
    d = ImageDraw.Draw(img, "RGBA") # allow semi-transparent drawing

    anchors_h_msb = ['l', 'm', 'r']
    anchors_h_lsb = ['a', 't', 'm', 's', 'b', 'd']

    anchors_v_msb = ['l', 's', 'm', 'r']
    anchors_v_lsb = ['t', 'm', 'b']

    directions = ['ltr', 'rtl', 'ttb']
    aligns = ['left', 'center', 'right']

    ptr = 0
    while ptr < len(packet):
        cmd = packet[ptr]
        ptr+=1
        if cmd == 0x00:
            x0, y0, x1, y1, start, end, stroke, width = struct.unpack('>hhhhffIB', packet[ptr:ptr+0x15])
            ptr += 0x15
            d.arc((x0*scale, y0*scale, x1*scale, y1*scale), start, end, stroke, width)
        elif cmd == 0x01:
            x0, y0, x1, y1, start, end, stroke, fill, width = struct.unpack('>hhhhffIIB', packet[ptr:ptr+0x19])
            ptr += 0x19
            d.chord((x0*scale, y0*scale, x1*scale, y1*scale), start, end, fill, stroke, width)
        elif cmd == 0x02:
            x0, y0, x1, y1, stroke, fill, width = struct.unpack('>hhhhIIB', packet[ptr:ptr+0x11])
            ptr += 0x11
            d.ellipse((x0*scale, y0*scale, x1*scale, y1*scale), fill, stroke, width)
        elif cmd == 0x03:
            fill, width, join, segment_ct = struct.unpack('>IBBH', packet[ptr:ptr+0x08])
            ptr += 0x08
            segments = []
            for i in range(2 + segment_ct):
                pt = struct.unpack('>hh', packet[ptr:ptr+0x04])
                pt = (pt[0] * scale, pt[1] * scale)
                segments.append(pt)
                ptr += 0x04
            joinval = None if join == 0 else "curve"
            d.line(segments, fill, width, joinval)
        elif cmd == 0x04:
            x0, y0, x1, y1, start, end, stroke, fill, width = struct.unpack('>hhhhffIIB', packet[ptr:ptr+0x19])
            ptr += 0x19
            d.pieslice((x0*scale, y0*scale, x1*scale, y1*scale), start, end, fill, stroke, width)
        elif cmd == 0x05:
            x, y, color = struct.unpack('>hhI', packet[ptr:ptr+0x08])
            ptr += 0x08
            d.point((x*scale, y*scale), color)
        elif cmd == 0x06:
            fill, stroke, segment_ct = struct.unpack('>IIB', packet[ptr:ptr+0x09])
            ptr += 0x09
            segments = []
            for i in range(2 + segment_ct):
                point = struct.unpack('>hh', packet[ptr:ptr+0x04])
                ptr += 0x4
                point = (point[0] * scale, point[1] * scale)
                segments.append(point)
            d.polygon(segments, fill, stroke)
        elif cmd == 0x07:
            x, y, r, sides, rotation, fill, stroke = struct.unpack('>hhHBfII', packet[ptr:ptr+0x13])
            ptr += 0x13
            d.regular_polygon((x*scale, y*scale, r*scale), sides, rotation, fill, stroke)
        elif cmd == 0x08:
            x0, y0, x1, y1, fill, stroke, width = struct.unpack('>hhhhIIB', packet[ptr:ptr+0x11])
            ptr += 0x11
            d.rectangle((x0*scale, y0*scale, x1*scale, y1*scale), fill, stroke, width)
        elif cmd == 0x09:
            x, y, textlen = struct.unpack('>hhI', packet[ptr:ptr+0x0C])
            x *= scale
            y *= scale
            ptr += 0x0C
            text = packet[ptr:ptr+textlen].decode('utf-8')
            ptr += textlen
            fill, anchor, spacing, align, direction, width, stroke_fill, bg = struct.unpack('>IBHBBBII', packet[ptr:ptr+0x12])
            ptr += 0x12

            dirtype = directions[direction]
            if direction == 2: # top-to-bottom
                anch = anchors_v_msb[(direction & 0xF0) >> 4] + anchors_v_lsb[(direction & 0x0F)]
            else:
                anch = anchors_h_msb[(direction & 0xF0) >> 4] + anchors_h_lsb[(direction & 0x0F)]
            aligntype = aligns[align]

            font = d.getfont()
            if bg & 0xff000000: # alpha != 0
                bbox = d.textbbox((x, y), text, font, anch, spacing, aligntype, dirtype, None, None, True)
                d.rectangle(bbox, bg, 0x00000000, 0)
            d.text((x, y), text, fill, font, anch, spacing, aligntype, dirtype, None, None, width, stroke_fill, True)
