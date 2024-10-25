import WL_Detect_Speed_Pattern_and_Find_TCPs

#File paths
file_path_intTCP = "Interval_TCP.txt"
file_path_lspeed = "Linear_speeds.txt"
file_path_TCP_main = "TCP_main.txt"

output_file_path_TCP_orig = "TCPs_original_idx.txt"
output_file_path_TCP_seq = "TCPs_sequential_idx.txt"
output_file_path_Tspeed_orig = "Speeds_original_idx.txt"
output_file_path_speed_seq = "Speeds_sequential_idx.txt"

tcp_poses = WL_Detect_Speed_Pattern_and_Find_TCPs.read_tcp_intervals(file_path_intTCP)
speed_data = WL_Detect_Speed_Pattern_and_Find_TCPs.read_lspeed_data(file_path_lspeed)
main_tcp_poses =WL_Detect_Speed_Pattern_and_Find_TCPs.read_TCP_main(file_path_TCP_main)
main_indices, not_found_indices = WL_Detect_Speed_Pattern_and_Find_TCPs.find_main_in_all(tcp_poses, main_tcp_poses)
increases, decreases, constant_start, constant_end, first_drop_position = WL_Detect_Speed_Pattern_and_Find_TCPs.detect_speed_pattern(speed_data, tolerance=0.0015, min_constant_points=5)
main_with_indices = WL_Detect_Speed_Pattern_and_Find_TCPs.get_main_with_indices(main_tcp_poses, main_indices, tcp_poses)
combined_tcp_poses = WL_Detect_Speed_Pattern_and_Find_TCPs.combine_main_and_enriched(main_with_indices, tcp_poses, constant_start, constant_end)
WL_Detect_Speed_Pattern_and_Find_TCPs.output_results(increases, decreases, constant_start, constant_end, tcp_poses, main_tcp_poses, main_indices, not_found_indices, combined_tcp_poses, speed_data, main_with_indices)
WL_Detect_Speed_Pattern_and_Find_TCPs.save_combined_tcp_to_file(combined_tcp_poses, speed_data)