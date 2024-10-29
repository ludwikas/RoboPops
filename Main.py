#First Phase
import W3A_A_Format_TCP
import W3A_A_Send_Collect_Main_and_Intervals
import W3A_A_Calculate_speed
#Second Phase
import W3B_L_Detect_Speed_Pattern_and_Find_TCPs
import W3B_E_get_joints
import logging
#Third Phase
import W3C_A_Calculate_StepDelay_Interpolate
import W3C_A_Format_dynamic_voltage_values
import W3CNEW_A_SendNewL_ExtractSpeeds

file_path_unf = "URscript.txt"                                        ## Need to have this in the directory in order for the script to run
output_file_path_1f = "Formatted_URscript.txt"                        ## Name of the 1st format (socketopen() and socketstring())
ip_address = "145.94.133.95"                                          ###### Use "ipconfig" in your terminal to colelect your personal IPV4 (changes every time you close your pc)
message_prefix = "Move"                                               ## Important for formatting 
file_path_1f = "Formatted_URscript.txt"                               ## File name
robot_ip = "192.168.40.128"                                           ## Robot ip
notification_port = 30004                                             ## Receive port                
output_file_path_intTCP = "Interval_TCP.txt"                          ## File name 
output_file_path_intspeeds="Interval_speeds.txt"                      ## File name 
output_file_path_mTCP="TCP_main.txt"                                  ## File name 
interval = 0.007                                                      ####### NOT LESS than 0.06
file_path_speed = "Interval_speeds.txt"                               ## File name
output_file_path_l1speed = "Linear_speeds.txt"                        ## File name

file_path_intTCP = "Interval_TCP.txt"                                 ## File name
file_path_l1speed = "Linear_speeds.txt"                               ## File name

file_path_TCP_main = "TCP_main.txt"                                   ## File name
output_file_urscript_newl = "URscript_newmovel.txt"                   ## File name
output_file_path_speed_seq = "Speeds_sequential_idx.txt"              ## File name
output_file_path_TCP_seq = "TCPs_with_markers.txt"                    ## File name
file_path_TCP_seq = "TCPs_with_markers.txt"                           ## File name
file_path_speed_seq = "Speeds_sequential_idx.txt"                     ## File name

ρ = 0.002015                                                          # g/mm^3                      ### Calculated through testing
m = 6.7                                                               # g                           ### Calculated through testing
V_p = W3C_A_Calculate_StepDelay_Interpolate.calculate_Vp(ρ, m)        # mm^3 per 1 revolution       ### Calculated through testing
w_target = 3.5                                                        # mm                          ### Target print settings
h_target = 3.4                                                        # mm                          ### Target print settings
Ns = 1035                                                             # unit                        ### Calculated through testing 

new_min = 0.475
new_max = 0

file_path_urscript_newl = "URscript_newmovel.txt"
output_file_path_2f = "Formatted_URscript2.txt"
file_path_2f = "Formatted_URscript2.txt"
output_file_path_jspeeds = "Joint_Speeds.txt"
input_file_path_jspeeds = "Joint_Speeds.txt"
output_file_path_l2speed = "Linear_speeds_2.txt"
output_file_path_FinalFormat = "FinalFormat_URscript.txt"

robot_ip_actual = "192.168.1.198"
file_path_FinalFormat = "FinalFormat_URscript.txt"

### First phase
W3A_A_Format_TCP.format_urscript(file_path_unf, output_file_path_1f, ip_address, message_prefix)
total_moves = W3A_A_Send_Collect_Main_and_Intervals.extract_total_moves(file_path_1f)
W3A_A_Send_Collect_Main_and_Intervals.send_urscript(file_path_1f, robot_ip, 30002)
tcp_data, marker_tcp_data = W3A_A_Send_Collect_Main_and_Intervals.monitor_tcp_pose_and_speed_combined(robot_ip, notification_port, interval, total_moves)
W3A_A_Send_Collect_Main_and_Intervals.write_tcp_positions_to_file(tcp_data, output_file_path_intTCP)
W3A_A_Send_Collect_Main_and_Intervals.write_tcp_speeds_to_file(tcp_data, output_file_path_intspeeds)
W3A_A_Send_Collect_Main_and_Intervals.write_marker_tcp_positions_to_file(marker_tcp_data, output_file_path_mTCP)
cartesian_speeds = W3A_A_Calculate_speed.extract_cartesian_speeds(file_path_speed)
v_linear = W3A_A_Calculate_speed.calculate_linear_speeds(cartesian_speeds)
W3A_A_Calculate_speed.write_speeds_in_file(v_linear, output_file_path_l1speed)

### Second phase
tcp_poses = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.read_tcp_intervals(file_path_intTCP)
speed_data = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.read_lspeed_data(file_path_l1speed)
main_tcp_poses =W3B_L_Detect_Speed_Pattern_and_Find_TCPs.read_TCP_main(file_path_TCP_main)
main_indices, not_found_indices = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.find_main_in_all(tcp_poses, main_tcp_poses)
increases, decreases, constant_start, constant_end = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.detect_speed_pattern(speed_data, min_constant_points=5)
main_with_indices = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.get_main_with_indices(main_tcp_poses, main_indices, tcp_poses)
combined_tcp_poses = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.combine_main_and_enriched(main_with_indices, tcp_poses, constant_start, constant_end)
W3B_L_Detect_Speed_Pattern_and_Find_TCPs.output_results(increases, decreases, constant_start, constant_end, tcp_poses, main_tcp_poses, main_indices, not_found_indices, combined_tcp_poses, speed_data, main_with_indices)
W3B_L_Detect_Speed_Pattern_and_Find_TCPs.save_combined_tcp_to_file(combined_tcp_poses, speed_data, main_with_indices, output_file_path_speed_seq, output_file_path_TCP_seq)
W3B_E_get_joints.read_tcp_poses_from_file(file_path_TCP_seq)
tcp_poses = W3B_E_get_joints.read_tcp_poses_from_file(file_path_TCP_seq)
if tcp_poses:
    joint_positions = W3B_E_get_joints.get_joint_positions_from_tcp(tcp_poses, robot_ip)
else:
    logging.error("No valid TCP poses found.")
    joint_positions = []
pose_types = W3B_E_get_joints.create_pose_types_dict(file_path_TCP_seq)
joint_poses_idx = W3B_E_get_joints.create_joint_position_list(joint_positions)
stripped_script = W3B_E_get_joints.read_and_strip_urscript(file_path_unf)
W3B_E_get_joints.write_ur_script(stripped_script, joint_poses_idx, pose_types, output_file_urscript_newl)

### Third Phase
W3A_A_Format_TCP.format_urscript(file_path_urscript_newl, output_file_path_2f, ip_address, message_prefix="Move")
total_moves = W3CNEW_A_SendNewL_ExtractSpeeds.extract_total_moves(file_path_2f)
W3CNEW_A_SendNewL_ExtractSpeeds.send_urscript(file_path_2f, robot_ip)
joint_speeds_data = W3CNEW_A_SendNewL_ExtractSpeeds.monitor_joint_speeds(robot_ip, notification_port=notification_port, total_moves=total_moves)
W3CNEW_A_SendNewL_ExtractSpeeds.write_joint_speeds_to_file(joint_speeds_data, output_file_path_jspeeds)
cartesian_speeds = W3CNEW_A_SendNewL_ExtractSpeeds.extract_cartesian_speeds(input_file_path_jspeeds)
v_linear = W3CNEW_A_SendNewL_ExtractSpeeds.calculate_linear_speeds(cartesian_speeds)
W3CNEW_A_SendNewL_ExtractSpeeds.write_speeds_in_file(v_linear, output_file_path_l2speed)
v_new = W3C_A_Calculate_StepDelay_Interpolate.read_v_values(output_file_path_l2speed)
step_delay_values = W3C_A_Calculate_StepDelay_Interpolate.calculate_step_delay(Ns, V_p, w_target, h_target, v_new)
old_max = W3C_A_Calculate_StepDelay_Interpolate.sort_max_delay(step_delay_values)
old_min = W3C_A_Calculate_StepDelay_Interpolate.sort_min_delay(step_delay_values)
voltage_values = W3C_A_Calculate_StepDelay_Interpolate.map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max)
W3C_A_Format_dynamic_voltage_values.format_urscript_voltages(file_path_urscript_newl, output_file_path_FinalFormat, voltage_values)

### Fourth Phase
W3A_A_Send_Collect_Main_and_Intervals.send_urscript(file_path_FinalFormat, robot_ip, 30002)