import WA_Format_TCP
import WA_Send_Collect_Main_and_Intervals
import WA_Calculate_speed

file_path_unf = "URscript.txt"                          ## Need to have this in the directory in order for the script to run
output_file_path_1f = "Formatted_URscript.txt"          ## Name of the 1st format (socketopen() and socketstring())
ip_address = "145.94.142.88"                            ###### Use "ipconfig" in your terminal to collect your personal IPV4 (changes every time you close your pc)
message_prefix = "Move"                                 ## Important for formatting 
file_path_1f = "Formatted_URscript.txt"                 ## File name
robot_ip = "192.168.177.128"                            ###### Robot ip
notification_port = 30004                               ## Receive port          
output_file_path_intTCP = "Interval_TCP.txt"            ## File name
output_file_path_intspeeds="Interval_speeds.txt"        ## File name
output_file_path_mTCP="TCP_main.txt"                    ## File name
interval = 0.01                                         ###### NOT more than 0.05
file_path_speed = "Interval_speeds.txt"                 ## File name
output_file_path_lspeed = "Linear_speeds.txt"           ## File name

WA_Format_TCP.format_urscript(file_path_unf, output_file_path_1f, ip_address, message_prefix)
WA_Send_Collect_Main_and_Intervals.send_urscript(file_path_1f, robot_ip, 30002)
tcp_data, marker_tcp_data = WA_Send_Collect_Main_and_Intervals.monitor_tcp_pose_and_speed_combined(robot_ip, notification_port, interval)
WA_Send_Collect_Main_and_Intervals.write_tcp_positions_to_file(tcp_data, output_file_path_intTCP)
WA_Send_Collect_Main_and_Intervals.write_tcp_speeds_to_file(tcp_data, output_file_path_intspeeds)
WA_Send_Collect_Main_and_Intervals.write_marker_tcp_positions_to_file(marker_tcp_data, output_file_path_mTCP)
cartesian_speeds = WA_Calculate_speed.extract_cartesian_speeds(file_path_speed)
v_linear = WA_Calculate_speed.calculate_linear_speeds(cartesian_speeds)
WA_Calculate_speed.write_speeds_in_file(v_linear, output_file_path_lspeed)