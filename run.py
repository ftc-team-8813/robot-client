from client import Connection
from freight_frenzy.plot import Plot
from freight_frenzy.odo_draw import OdoDraw


def odo_drawer():
    localhost = '127.0.0.1' # Used for TestServer.java
    robot = '192.168.43.1'

    conn = Connection(localhost, 18888)

    odo_draw = OdoDraw(conn)
    odo_draw.draw()
    

def plotter():
    localhost = '127.0.0.1' # Used for TestServer.java
    robot = '192.168.43.1'

    conn = Connection(localhost, 18888)

    # Label related to color and scale factor on graph
    labels = {
        'Arm Pos': ['green', 1.0],
        'P Term': ['blue', 1.0],
        'I Term': ['red', 1.0],
        'D Term': ['purple', 1.0]
    }

    plot = Plot(conn, labels, (-5000, 5000))
    plot.generate_lines() # Creates x and y arrays for line axises
    plot.update_lines() # Updates y arrays with incoming server data

if __name__ == '__main__':
    # plotter()
    odo_drawer()
