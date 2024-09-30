import socket 
import math 
import time
import urx

# 0. def Program():
# 1.   extruder_clayTcp = p[0, 0, 0.2535, 0, 0, 1.5708] - sets the tool to the given point: [x, y, z, rx, ry, rz] : 
# 2.   extruder_clayWeight = 0 - Sets the payload weight to 0
# 3.   extruder_clayCog = [0, 0, 0.2535] - Sets the center of gravity (COG) to [0, 0, 0.2535]
# 4.   Speed000 = 0.007
# 5.   DefaultZone = 0
# 6.   set_tcp(extruder_clayTcp)
#      set_payload(extruder_clayWeight, extruder_clayCog)
# 7.   movej([1.3224, -1.6028, 2.0734, -2.0415, -1.5708, -0.2484], a=3.1416, v=0.022, r=DefaultZone)
# 8.   movel(p[0, -0.36801, 0.00052, 2.22144, 2.22144, 0], a=1, v=Speed000, r=DefaultZone)
# 9. end


robot_ip = "192.168.0.10"  # Replace with your robot's actual IP
robot = urx.Robot(robot_ip)

try:
    # Step 1: Set the Tool Center Point (TCP); robot.set_tcp(extruder_clayTcp) sets the TCP similar to set_tcp in URScript.
    extruder_clayTcp = [0, 0, 0.2535, 0, 0, math.pi / 2]
    robot.set_tcp(extruder_clayTcp)
    print("TCP set to:", extruder_clayTcp)

    # Step 2: Set Payload and Center of Gravity (COG):
    extruder_clayWeight = 0  # Payload weight in kg
    extruder_clayCog = [0, 0, 0.2535]  # Center of gravity
    robot.set_payload(extruder_clayWeight, extruder_clayCog)
    print("Payload set to:", extruder_clayWeight, "with COG:", extruder_clayCog)

    # Step 3: Move to initial joint position using movej; 
    # moves the robot to the initial joint position. 
    # The acc and vel parameters correspond to acceleration and velocity, just like in URScript.
    initial_joint_position = [1.3224, -1.6028, 2.0734, -2.0415, -1.5708, -0.2484]
    robot.movej(initial_joint_position, acc=3.1416, vel=0.022, wait=True)
    print("Moved to initial joint position:", initial_joint_position)

    # Step 4: Draw the line using movel to the target Cartesian position
    # Note: In urx, p[] values are given in meters and radians, similar to URScript
    target_position = [0, -0.36801, 0.00052, 2.22144, 2.22144, 0]
    robot.movel(target_position, acc=1, vel=0.007, wait=True)
    print("Moved linearly to target position:", target_position)

finally:
    robot.close()
    print("Connection closed")