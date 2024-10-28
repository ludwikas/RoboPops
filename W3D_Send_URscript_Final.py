# SEND FINAL FORMATTED URSCRIPT TO ROBOT CONTROLLER

import W3A_A_Send_Collect_Main_and_Intervals

robot_ip = "192.168.40.128"
file_path_FinalFormat = "FinalFormat_URscript.txt"

W3A_A_Send_Collect_Main_and_Intervals.send_urscript(file_path_FinalFormat, robot_ip, 30002)

