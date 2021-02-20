import tkinter as tk
import widgets
import client
import struct

def update(conn, root, plot, ch0, ch1, prev_init):
    data = conn.send_recv(0x01)
    if data is None: return
    fields = struct.unpack('>ffB', data)
    print(fields)
    if fields[2]:
        if not prev_init:
            plot.clear()
        plot.put(ch0, fields[0])
        plot.put(ch1, fields[1])

    root.after(100, update, conn, root, plot, ch0, ch1, fields[2])


def main():
    conn = client.Connection('192.168.43.1', 17777)
    conn.connect()

    root = tk.Tk()
    plot = widgets.Plot1D(root, 700, 300, 500, 0, 10)
    plot.grid(column=0, row=0)
    ch0 = plot.add_channel((255, 0, 0))
    ch1 = plot.add_channel((0, 255, 0))

    root.after(0, update, conn, root, plot, ch0, ch1, 0)
    root.mainloop()

if __name__ == '__main__':
    main()
