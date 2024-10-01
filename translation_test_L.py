import socket 
import math 
import time
import urx


# 0. def Program():
# 1.   extruder_clayTcp = p[0, 0, 0.2535, 0, 0, 1.5708]
# 2.   extruder_clayWeight = 0
# 3.   extruder_clayCog = [0, 0, 0.2535]
# 4.   Speed000 = 0.1
# 5.   DefaultZone = 0
# 6.   set_tcp(extruder_clayTcp)
#   set_payload(extruder_clayWeight, extruder_clayCog)
# 7.   movej([1.4265, -0.8756, 1.0797, -1.7749, -1.5708, -0.1443], a=3.1416, v=0.3142, r=DefaultZone)
# 8.   movel(p[0, -0.31366, 0.00052, 2.22144, 2.22144, 0], a=1, v=Speed000, r=DefaultZone)
# 9. end

robot_ip = "192.168.177.128"  # Replace with your robot's actual IP
robot = urx.Robot(robot_ip)
home_position = [1.4265, -0.8756, 1.0797, -1.7749, -1.5708, -0.1443]  # Example joint angles for a UR robot

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
    initial_joint_position = [1.4265, -0.8756, 1.0797, -1.7749, -1.5708, -0.1443]
    robot.movej(initial_joint_position, acc=5, vel=5, wait=True)
    print("Moved to initial joint position:", initial_joint_position)

    # Step 4: Draw the line using movel to the target Cartesian position
    # Note: In urx, p[] values are given in meters and radians, similar to URScript
    target_position = [0, -0.31366, 0.00052, 2.22144, 2.22144, 0]
    robot.movel(target_position, acc=5, vel=5, wait=True)
    print("Moved linearly to target position:", target_position)

# Return to the home position after completing the task
    print("Returning to home position...")
    robot.movej(home_position, acc=5, vel=5, wait=True)
    print("Robot returned to home position")

finally:
    # Close the connection properly
    robot.close()
    print("Connection to the robot closed")

#this is working - how do I reset the robot without Grasshopper though? 
