import urx
import socket
robot = urx.Robot('IP')
# Start of the program
robot.movej([[1.4265, -0.8758, 1.0793, -1.7743, -1.5708, -0.1443], acc=3.1416, vel=0.3142, radius=DefaultZone])
robot.movel([p[0, -0.31366, 0.00052, 2.22144, 2.22144, 0], acc=1, vel=Speed000, radius=DefaultZone])
# End of the program
robot.close()
