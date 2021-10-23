from client.client import Connection
from plot import Plot


if __name__ == '__main__':
    localhost = '127.0.0.1' # Used for TestServer.java
    robot = '192.168.43.1'

    conn = Connection(robot, 18888)

    # Label related to color and scale factor on graph
    labels = {
        'Arm Pos': ['green', 1.0],
        'P Term': ['blue', 1000.0],
        'I Term': ['red', 1000.0],
        'D Term': ['purple', 1000.0]
    }

    graph = Plot(conn, labels, (-3000, 3000))
    graph.generate_lines() # Creates x and y arrays for line axises
    graph.update_lines() # Updates y arrays with incoming server data
    
