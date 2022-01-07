from client import Connection
from freight_frenzy.plot import Plot
from freight_frenzy.odo_draw import OdoDraw
from freight_frenzy.captsone_detector import CapstoneDetector


def capstone_detector():
    directory = './freight_frenzy/test_imgs/'
    filename = 'competition2.jpg'

    detector = CapstoneDetector(directory + filename)
    detector.image_prep()
    detector.masked()
    # detector.find_color_ranges()


def odo_drawer():
    localhost = '127.0.0.1' # Used for TestServer.java
    robot = '192.168.43.1'

    conn = Connection(robot, 18888)

    odo_draw = OdoDraw(conn)
    odo_draw.draw()

def plotter():
    localhost = '127.0.0.1' # Used for TestServer.java
    robot = '192.168.43.1'

    conn = Connection(robot, 18888)

    # Label related to color and scale factor on graph
    labels = {
        'Lift Pos': ['black', 0],
        'Lift Power': ['orange', 0],

        'P Term': ['red', 0],
        'I Term': ['green', 0],
        'D Term': ['blue', 0],
    }

    plot = Plot(conn, labels, (-1, 1))
    plot.generate_lines() # Creates x and y arrays for line axises
    plot.update_lines() # Updates y arrays with incoming server data

if __name__ == '__main__':
    capstone_detector()
    # plotter()
    # odo_drawer()
