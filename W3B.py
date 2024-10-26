import W3B_L_Detect_Speed_Pattern_and_Find_TCPs
import W3B_E_get_joints
import logging

robot_ip = "192.168.40.128" 
#File paths
file_path_intTCP = "Interval_TCP.txt"
file_path_lspeed = "Linear_speeds.txt"
file_path_TCP_main = "TCP_main.txt"

output_file_path_TCP_orig = "TCPs_original_idx.txt"
output_file_path_TCP_seq = "TCPs_sequential_idx.txt"
output_file_path_Tspeed_orig = "Speeds_original_idx.txt"
output_file_path_speed_seq = "Speeds_sequential_idx.txt"
output_file_urscript_newl = "URscript_newmovel.txt"

file_path_unf = "URscript.txt" 
file_path_TCP_seq = "TCPs_sequential_idx.txt"
file_path_speed_seq = "Speeds_sequential_idx.txt"

tcp_poses = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.read_tcp_intervals(file_path_intTCP)
speed_data = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.read_lspeed_data(file_path_lspeed)
main_tcp_poses =W3B_L_Detect_Speed_Pattern_and_Find_TCPs.read_TCP_main(file_path_TCP_main)
main_indices, not_found_indices = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.find_main_in_all(tcp_poses, main_tcp_poses)
increases, decreases, constant_start, constant_end= W3B_L_Detect_Speed_Pattern_and_Find_TCPs.detect_speed_pattern(speed_data, tolerance=0.0015, min_constant_points=5)
main_with_indices = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.get_main_with_indices(main_tcp_poses, main_indices, tcp_poses)
combined_tcp_poses = W3B_L_Detect_Speed_Pattern_and_Find_TCPs.combine_main_and_enriched(main_with_indices, tcp_poses, constant_start, constant_end)
W3B_L_Detect_Speed_Pattern_and_Find_TCPs.output_results(increases, decreases, constant_start, constant_end, tcp_poses, main_tcp_poses, main_indices, not_found_indices, combined_tcp_poses, speed_data, main_with_indices)
W3B_L_Detect_Speed_Pattern_and_Find_TCPs.save_combined_tcp_to_file(combined_tcp_poses, speed_data)

W3B_E_get_joints.read_tcp_poses_from_file(file_path_TCP_seq)
tcp_poses = W3B_E_get_joints.read_tcp_poses_from_file(file_path_TCP_seq)
if tcp_poses:
    joint_positions = W3B_E_get_joints.get_joint_positions_from_tcp(tcp_poses, robot_ip)
else:
    logging.error("No valid TCP poses found.")
    joint_positions = []
joint_poses_idx = W3B_E_get_joints.create_joint_position_list(joint_positions)
actual_TCP_speeds = W3B_E_get_joints.read_tcp_speeds(file_path_speed_seq)
stripped_script = W3B_E_get_joints.read_and_strip_urscript(file_path_unf)
W3B_E_get_joints.write_ur_script(stripped_script, joint_poses_idx, actual_TCP_speeds, output_file_urscript_newl)