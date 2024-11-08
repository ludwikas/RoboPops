# The functions in this script are structured to 
# Read the output files TCP_main.txt, tcp_intervals.txt, linear_speed.txt
# Sort through the speeds
# Detect constant speed patterns 
# Collect start and end of constant segments based on the interval_TCP
# Write speeds and TCPs into .txt

# Reading MAIN TCP poses from the file
def read_TCP_main(file_path_TCP_main):
    main_tcp_poses = []

    with open(file_path_TCP_main, 'r') as file:
        for line in file:
            main_pose = line.strip()

            if '[' in line:
                line = line.split('[', 1)[1]

            line = line.replace(']', '').split(',')

            try:
                #Convert each item to float:
                main_pose = [float(value) for value in line]
                main_tcp_poses.append(main_pose)

            except ValueError:
                print(f"Could not convert line to float: {line}")
      
    return main_tcp_poses

# Reading ALL TCP poses from the file 
def read_tcp_intervals(file_path_intTCP):
    tcp_poses = []

    with open(file_path_intTCP, 'r') as file:
        for line in file:  # Add a loop to iterate over each line
            pose = line.strip()

            if '[' in line:
                line = line.split('[', 1)[1]

            line = line.replace(']', '').split(',')

            try:
                #Convert each item to float:
                pose = [float(value) for value in line]
                tcp_poses.append(pose)

            except ValueError:
                print(f"Could not convert line to float: {line}")
      
    return tcp_poses

# Reading speed data from the file
def read_lspeed_data(file_path_lspeed):

    speed_data = []
    with open(file_path_lspeed, 'r') as file:
        for line in file:
            line = line.strip()
            # Extract the numeric speed part after the colon
            if ':' in line:
                speed_str = line.split(':')[1].strip().replace(' m/s', '')
            else:
                speed_str = line.replace(' m/s', '')  # In case there's no colon formatting

            try:
                # Convert the extracted speed value to float
                speed = float(speed_str)
                speed_data.append(speed)
            except ValueError:
                print(f"Could not convert line to float: {line}")

    return speed_data

# Searching for the main TCPs' indices in the list of all the TCPs:
def find_main_in_all(tcp_poses, main_tcp_poses):

    main_indices = []  #list of tuples
    not_found_indices = []

    for main_index, main_pose in enumerate(main_tcp_poses, start = 1):
        try:
            all_index = tcp_poses.index(main_pose) + 1                                        #Finds the index of a specific main pose in the list tcp_poses                         
            main_indices.append((main_index, all_index))                                      #Collects the indices if found, otherwise appends it in not_found_indices
        except ValueError:
            not_found_indices.append(main_index)
            print(f"Pose from main TCPs list is not found in all TCPs list: {main_pose}")

    return main_indices, not_found_indices

# Search for constant speed segments
def detect_speed_pattern(speed_data, tolerance = 0.005, min_constant_points=5):

    """
    Detect speed increases, decreases, and constant speed segments.
    
    Args:
    speed_data (list of floats)
    tolerance (float)
    min_constant_points (int): Minimum number of points to consider a constant speed segment.

    """
    
    increases = []                                                                                      # Poses where speed increases
    decreases = []                                                                                      # Poses where speed decreases
    constant_start = []                                                                                 # Poses of the start of constant speed segments
    constant_end = []                                                                                   # Poses of the end of constant speed segments

    # Variable to track constant speed segments
    in_constant_segment = False
    constant_segment_count = 0
    constant_segment_start = None                                                                       # Track start index of constant segment

    for i in range(1, len(speed_data)):
        speed_change = speed_data[i] - speed_data[i - 1]
        
        # Check for speed increase
        if speed_change > tolerance:
            increases.append(i)

            if in_constant_segment:
                # End of a constant speed segment
                if constant_segment_count >= min_constant_points:
                    constant_end.append(i - 1)
                in_constant_segment = False
                constant_segment_count = 0

        # Check for speed decrease
        elif speed_change < -tolerance:
            decreases.append(i)

            if in_constant_segment:
                # End of a constant speed segment
                if constant_segment_count >= min_constant_points:
                    constant_end.append(i - 1)
                in_constant_segment = False
                constant_segment_count = 0

        # Check for constant speed (within tolerance)
        else:
            if not in_constant_segment:
                # Start a new constant speed segment
                constant_segment_start = i - 1
                constant_start.append(constant_segment_start)
                in_constant_segment = True

            # Increment the count for the constant speed segment
            constant_segment_count += 1

        # If we are in a constant speed segment and reach the last data point, close it
        if in_constant_segment and i == len(speed_data) - 1:
            if constant_segment_count >= min_constant_points:
                constant_end.append(i)

    return increases, decreases, constant_start, constant_end

# Get main TCPs with corresponding indices in ALL
def get_main_with_indices(main_tcp_poses, main_indices, tcp_poses):

    main_with_indices = []
    for _, all_index in main_indices:
        pose = tcp_poses[all_index - 1]  # Use the index to get the pose from tcp_poses
        main_with_indices.append((all_index, pose))

    return main_with_indices

# Combine main TCPs and enriched TCPs
def combine_main_and_enriched(main_with_indices, tcp_poses, constant_start, constant_end):
    combined_tcp_poses = main_with_indices[:] # a copy of the list main_with_indices is being created and assigned to the variable combined_tcp_poses

    # Convert to a set of unique indices to avoid duplicates
    combined_indices_set = {index for index, _ in main_with_indices}  

    # Adding the enriched points based on constant speed segments
    enriched_indices = [
        (start + 1, tcp_poses[start]) for start in constant_start if (start + 1) not in combined_indices_set
    ] + [
        (end + 1, tcp_poses[end]) for end in constant_end if (end + 1) not in combined_indices_set
    ]
    combined_tcp_poses.extend(enriched_indices)
    combined_indices_set.update(index for index, _ in enriched_indices)

    # Sort the combined list by indices
    combined_tcp_poses = sorted(combined_tcp_poses, key=lambda x: x[0])

    return combined_tcp_poses

# Results console output
def output_results(increases, decreases, constant_start, constant_end, tcp_poses, main_tcp_poses, main_indices, not_found_indices, combined_tcp_poses, speed_data, main_with_indices):

    print("\nMain TCP poses:")                                                                  #Main TCPs
    for idx, point in enumerate(main_tcp_poses, start = 1):
        print(f"Pose {idx}: {point}\n")

    print("\nIndices of main TCPs in all TCPs list:")
    for main_index, all_index in main_indices:
        print(f"Pose {main_index} from MAIN is at index {all_index} in ALL")

    if not_found_indices:
        print("\nThe following poses from MAIN were not found in ALL:")
        for not_found in not_found_indices:
            print(f"Pose {not_found} from MAIN")


    #Main TCPs with corresponding indices in ALL                                        #Main TCPs with corresponding indices in ALL
    print("\nMain TCP poses with corresponding indices in ALL:")
    for _, all_index in main_indices:
        pose = tcp_poses[all_index - 1]  # Use the index to get the pose from tcp_poses
        print(f"{all_index}:{pose}")

    print("\nSpeed increases at these points:")                                                 #Increases

    print(increases)

    #decreases:                                                                                 #Decreases
    print("\nSpeed decreases at these points:")

    print(decreases)

    #constant segments:                                                                         #Constant segments
    print("\nConstant speed segments start and end at these points:")
    for start, end in zip(constant_start, constant_end):
        print(f"Pose {start+1} to Pose {end+1}")

    #Where should TCPs be added?                                                                #Where TCPs should be added?
    print("\nAdd TCPs in the following points:")
    for start, end in zip(constant_start, constant_end):
        print(f"{start+1}:{tcp_poses[start]}")
        print(f"{end+1}:{tcp_poses[end]}")


    #Output the combined list                                                                   #combined list: main + enriched
    print("\nCombined TCP Poses (Main and Enriched):")
    for index, pose in combined_tcp_poses:
        indicator = "(MAIN)" if index in [original_index for original_index, _ in main_with_indices] else "(ENRICHED)"
        print(f"{indicator} {index}: {pose}")

    # Output TCPs and corresponding speed
    print("\nTCP Poses and corresponding speed:")
    for index, pose in combined_tcp_poses:
        speed = speed_data[index - 1] if index - 1 < len(speed_data) else 'N/A'
        print(f"{index}: Pose: {pose}\nSpeed: {speed}\n")

# Save all the needed files:                                                                    
def save_combined_tcp_to_file(combined_tcp_poses, speed_data, main_with_indices, output_file_path_speed_seq, output_file_path_TCP_seq):

     # a) speeds with sequential indices
    with open(output_file_path_speed_seq, 'w') as file:
        for idx, (original_index, _) in enumerate(combined_tcp_poses, start=1):
            speed = speed_data[original_index - 1] if original_index - 1 < len(speed_data) else 'N/A'
            file.write(f"{idx}: {speed}\n")

     # b) New file for TCPs with main/enriched marker and sequential index
    with open(output_file_path_TCP_seq, 'w') as file:
        main_indices_set = {index for index, _ in main_with_indices}  

        for seq_index, (original_index, pose) in enumerate(combined_tcp_poses, start=1):
            if original_index in main_indices_set:
                # This TCP is a main pose
                main_list_index = next((idx for idx, main in enumerate(main_with_indices, start=1) if main[0] == original_index), None)
                file.write(f"{seq_index} Marker pose {main_list_index}: {pose}\n")
            else:
                # This TCP is an enriched pose
                file.write(f"{seq_index} Interval {original_index}: {pose}\n")

def main():

    #1:Load data from files:
    file_path_intTCP = "Interval_TCP.txt"
    file_path_lspeed = "Linear_speeds.txt"
    file_path_TCP_main = "TCP_main.txt"
    tcp_poses = read_tcp_intervals(file_path_intTCP)
    speed_data = read_lspeed_data(file_path_lspeed)
    main_tcp_poses = read_TCP_main(file_path_TCP_main)
    output_file_path_speed_seq = "Speeds_sequential_idx.txt"
    output_file_path_TCP_seq = "TCPs_with_markers.txt"

    # Find indices of MAIN poses in ALL poses
    #outputs main indices from the list of all TCPs and main indices that were not found in the list of all TCPs
    main_indices, not_found_indices = find_main_in_all(tcp_poses, main_tcp_poses)

    # Find speed pattern:
    increases, decreases, constant_start, constant_end = detect_speed_pattern(speed_data, tolerance = 0.005, min_constant_points=5)

    # Collect main TCP poses with their indices from the list of all TCPs
    main_with_indices = get_main_with_indices(main_tcp_poses, main_indices, tcp_poses)
    
    # Combine the main TCPs with TCPs found in the detection part
    combined_tcp_poses = combine_main_and_enriched(main_with_indices, tcp_poses, constant_start, constant_end)

    # Output the results
    output_results(increases, decreases, constant_start, constant_end, tcp_poses, main_tcp_poses, main_indices, not_found_indices, combined_tcp_poses, speed_data, main_with_indices)

    # Save the .txt files:
    save_combined_tcp_to_file(combined_tcp_poses, speed_data, main_with_indices, output_file_path_speed_seq, output_file_path_TCP_seq)

if __name__ == "__main__":
    main()