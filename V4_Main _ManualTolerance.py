#First Phase
import W1_Format_TCP
import W2_Send_Collect_Main_and_Intervals
import W3_Calculate_speed
#Second Phase
import W4_Manual_Detect_Speed_Pattern_and_Find_TCPs
import W5_Get_joints
import logging
#Third Phase
import W6_SendNewL_ExtractSpeeds
import W7_Calculate_StepDelay_Interpolate

# There is a clear distinction between input file paths (file_path...) and output file paths (output_file_path...)
# file_path... arguments are used as input and output_file_path... arguments as output 
# this means that an output file will have to have a second argument with the file_path... format 
# in order to be used as an input argument 
# Even though this makes the changing an argument a 2 step process for certain ones 
# this is by design to make the data structure/flow as clear as possible

# Arguments that are defined through functions are found later 

# Phase 1 arguments
file_path_unf = "URscript.txt"                                        ## Need to have this in the directory in order for the script to run
output_file_path_1f = "01_Formatted_URscript.txt"                     ## Name of the 1st format (socketopen() and socketstring())
ip_address = "145.94.170.171"                                         ###### Use "ipconfig" in your terminal to colelect your personal IPV4 
message_prefix = "Move"                                               ## Important for formatting 
file_path_1f = "01_Formatted_URscript.txt"                            ## File name
robot_ip = "192.168.40.128"                                           ## Robot ip
notification_port = 30004                                             ## Receive port                
output_file_path_intTCP = "02_Interval_TCP.txt"                       ## File name 
output_file_path_intspeeds="03_Interval_speeds.txt"                   ## File name 
output_file_path_mTCP="04_TCP_main.txt"                               ## File name 
interval = 0.005                                                      ## Controls the interval of collection. Lower numbers create bigger "resolutions"
file_path_speed = "03_Interval_speeds.txt"                            ## File name
output_file_path_l1speed = "05_Linear_speeds.txt"                     ## File name

# Phase 2 arguments
file_path_intTCP = "02_Interval_TCP.txt"                               ## File name
file_path_l1speed = "05_Linear_speeds.txt"                             ## File name

file_path_TCP_main = "04_TCP_main.txt"                                 ## File name
output_file_path_speed_seq = "06_Speeds_sequential_idx.txt"            ## File name
output_file_path_TCP_seq = "07_TCPs_with_markers.txt"                  ## File name
file_path_TCP_seq = "07_TCPs_with_markers.txt"                         ## File name
file_path_speed_seq = "06_Speeds_sequential_idx.txt"                   ## File name
output_file_urscript_newl = "08_URscript_newmovel.txt"                 ## File name

# Phase 3 arguments
ρ = 0.002015                                                           # g/mm^3                      ### Calculated through testing
m = 7.5                                                                # g                           ### Calculated through testing
V_p = W7_Calculate_StepDelay_Interpolate.calculate_Vp(ρ, m)            # mm^3 per 1 revolution       ### Calculated through testing
w_target = 3.5                                                         # mm                          ### Target print settings
h_target = 3.4                                                         # mm                          ### Target print settings
Ns = 1035                                                              # unit                        ### Calculated through testing 

# The values bellow represent voltage values that the robot 
#controller is going to output. There are two bottlenecks occuring.
#The first is in regard with the robot controller being able to send 
#a maximum of 10 volts. The second is what the arduino that is goint to 
#receive the values. Since the arduino cannot handle more than 5 volts
#we use that as tha value of the interpolation.

new_min = 0.5                                                         # Volts  The 0.5 value represents 5 volts. UR syntax is working with a 0-1 range for 0 - 10 volts. 
new_max = 0                                                           # Volts

file_path_urscript_newl = "08_URscript_newmovel.txt"
output_file_path_2f = "09_Formatted_URscript2.txt"
file_path_2f = "09_Formatted_URscript2.txt"
output_file_path_jspeeds = "10_Joint_Speeds.txt"
input_file_path_jspeeds = "10_Joint_Speeds.txt"
output_file_path_l2speed = "11_Linear_speeds_2.txt"
output_file_path_FinalFormat = "12_FinalFormat_URscript.txt"

# This controls the actual robot the robot ip variable is set based on the simulated environment,
#robot_ip_actual is made to send the final product of this script to the robot, changing the argument on the 
#last phsae (phase 4) form robot_ip_actual to robot_ip can also work if the goal is to just send the final 
#product for a simulation. Sending the Final Script to the robot_actual without being connected to a robot 
#will just create a time_out error after a while when the script finally cannot be sent anywhere.
robot_ip_actual = "192.168.1.198"
file_path_FinalFormat = "12_FinalFormat_URscript.txt"

### First phase
W1_Format_TCP.format_urscript(file_path_unf, output_file_path_1f, ip_address, message_prefix)
total_moves = W2_Send_Collect_Main_and_Intervals.extract_total_moves(file_path_1f)
W2_Send_Collect_Main_and_Intervals.send_urscript(file_path_1f, robot_ip, 30002)
tcp_data, marker_tcp_data = W2_Send_Collect_Main_and_Intervals.monitor_tcp_pose_and_speed_combined(robot_ip, notification_port, interval, total_moves)
tcp_data = W2_Send_Collect_Main_and_Intervals.remove_consecutive_duplicates(tcp_data)
W2_Send_Collect_Main_and_Intervals.write_tcp_positions_to_file(tcp_data, output_file_path_intTCP)
W2_Send_Collect_Main_and_Intervals.write_tcp_speeds_to_file(tcp_data, output_file_path_intspeeds)
W2_Send_Collect_Main_and_Intervals.write_marker_tcp_positions_to_file(marker_tcp_data, output_file_path_mTCP)
cartesian_speeds = W3_Calculate_speed.extract_cartesian_speeds(file_path_speed)
v_linear = W3_Calculate_speed.calculate_linear_speeds(cartesian_speeds)
W3_Calculate_speed.write_speeds_in_file(v_linear, output_file_path_l1speed)

### Second phase
tcp_poses = W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.read_tcp_intervals(file_path_intTCP)
speed_data = W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.read_lspeed_data(file_path_l1speed)
main_tcp_poses = W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.read_TCP_main(file_path_TCP_main)
main_indices, not_found_indices = W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.find_main_in_all(tcp_poses, main_tcp_poses)
increases, decreases, constant_start, constant_end = W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.detect_speed_pattern(speed_data, tolerance = 0.005, min_constant_points=5)
main_with_indices = W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.get_main_with_indices(main_tcp_poses, main_indices, tcp_poses)
combined_tcp_poses = W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.combine_main_and_enriched(main_with_indices, tcp_poses, constant_start, constant_end)
W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.output_results(increases, decreases, constant_start, constant_end, tcp_poses, main_tcp_poses, main_indices, not_found_indices, combined_tcp_poses, speed_data, main_with_indices)
W4_Manual_Detect_Speed_Pattern_and_Find_TCPs.save_combined_tcp_to_file(combined_tcp_poses, speed_data, main_with_indices, output_file_path_speed_seq, output_file_path_TCP_seq)
W5_Get_joints.read_tcp_poses_from_file(file_path_TCP_seq)
tcp_poses = W5_Get_joints.read_tcp_poses_from_file(file_path_TCP_seq)
if tcp_poses:
    joint_positions = W5_Get_joints.get_joint_positions_from_tcp(tcp_poses, robot_ip)
else:
    logging.error("No valid TCP poses found.")
    joint_positions = []
pose_types = W5_Get_joints.create_pose_types_dict(file_path_TCP_seq)
joint_poses_idx = W5_Get_joints.create_joint_position_list(joint_positions)
stripped_script = W5_Get_joints.read_and_strip_urscript(file_path_unf)
W5_Get_joints.write_ur_script(stripped_script, joint_poses_idx, pose_types, output_file_urscript_newl)

### Third Phase
W1_Format_TCP.format_urscript(file_path_urscript_newl, output_file_path_2f, ip_address, message_prefix="Move")
total_moves = W6_SendNewL_ExtractSpeeds.extract_total_moves(file_path_2f)
W6_SendNewL_ExtractSpeeds.send_urscript(file_path_2f, robot_ip)
joint_speeds_data = W6_SendNewL_ExtractSpeeds.monitor_joint_speeds(robot_ip, notification_port=notification_port, total_moves=total_moves)
W6_SendNewL_ExtractSpeeds.write_joint_speeds_to_file(joint_speeds_data, output_file_path_jspeeds)
cartesian_speeds = W6_SendNewL_ExtractSpeeds.extract_cartesian_speeds(input_file_path_jspeeds)
v_linear = W6_SendNewL_ExtractSpeeds.calculate_linear_speeds(cartesian_speeds)
W6_SendNewL_ExtractSpeeds.write_speeds_in_file(v_linear, output_file_path_l2speed)
v_new = W7_Calculate_StepDelay_Interpolate.read_v_values(output_file_path_l2speed)
step_delay_values = W7_Calculate_StepDelay_Interpolate.calculate_step_delay(Ns, V_p, w_target, h_target, v_new)
old_max = W7_Calculate_StepDelay_Interpolate.sort_max_delay(step_delay_values)
old_min = W7_Calculate_StepDelay_Interpolate.sort_min_delay(step_delay_values)
voltage_values = W7_Calculate_StepDelay_Interpolate.map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max)
W7_Calculate_StepDelay_Interpolate.format_urscript_voltages(file_path_urscript_newl, output_file_path_FinalFormat, voltage_values)

### Fourth Phase
W2_Send_Collect_Main_and_Intervals.send_urscript(file_path_FinalFormat, robot_ip_actual, 30002)