import urx
import time

# Connect to the robot
robot = urx.Robot("192.168.177.128")  # Replace with the robot's actual IP address

try:
    # Move the arm to a specific joint position (radians)
    joint_positions = [-1.0, -1.5, 1.5, -1.0, 1.5, 0.0]
    robot.movej(joint_positions, acc=5, vel=5)
    time.sleep(2)  # Wait for 2 seconds

    # Move the arm in Cartesian space (meters and radians)
    tcp_position = [0.3, 0.1, 0.2, 0, 3.14, 0]  # x, y, z, rx, ry, rz
    robot.movel(tcp_position, acc=5, vel=5)
    time.sleep(2)  # Wait for 2 seconds

    # Return to home position (all zeros for joints)
    home_position = [0, 0, 0, 0, 0, 0]
    robot.movej(home_position, acc=5, vel=5)

finally:
    # Close the connection to the robot
    robot.close()
