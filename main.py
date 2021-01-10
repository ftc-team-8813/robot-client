import client
import atexit
import time

IP_ADDR = '192.168.43.1' # Control Hub address (usually fixed to this)
PORT = 23456 # Port number, set by the server

def main():
    conn = client.Connection(IP_ADDR, PORT)
    conn.connect()
    atexit.register(conn.close)
    while True:
        start = time.perf_counter()
        resp = conn.send_recv(0x00, b'Hello World!') # echo
        if resp is None:
            break
        elapsed = time.perf_counter() - start
        print("[%.3f] %s" % (elapsed, resp))
        time.sleep(1)

if __name__ == '__main__':
    main()
