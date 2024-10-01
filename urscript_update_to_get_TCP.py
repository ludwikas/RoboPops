import re

# Function to modify the URScript file by adding TCP pose extraction after each movej command
def modify_urscript_for_tcp_pose(file_path):
    movej_pattern = r'(movej\([^\)]+\))'  # Regex to match movej commands
    tcp_pose_code = '''  
  tcp_pose = get_actual_tcp_pose()
  textmsg("TCP Pose: ", to_str(tcp_pose[0]), ", ", to_str(tcp_pose[1]), ", ", to_str(tcp_pose[2]), ", ", to_str(tcp_pose[3]), ", ", to_str(tcp_pose[4]), ", ", to_str(tcp_pose[5]))
    '''.strip()  # Strip any extra newlines or spaces

    # Read the URScript file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []

    # Iterate through each line in the file
    for line in lines:
        modified_lines.append(line.rstrip())  # Strip trailing whitespace, including newlines
        # If the line contains a movej command, append the TCP pose code
        if re.search(movej_pattern, line):
            modified_lines.append(tcp_pose_code)  # Append TCP pose code immediately after movej command

    # Save the modified URScript with correct formatting
    with open(file_path, 'w') as file:
        for line in modified_lines:
            file.write(line + '\n')  # Write each line with a single newline character

    print(f"Modified URScript saved back to {file_path}")

# Example usage:
urscript_file = 'URscript.txt'   # Path to your URScript file
modify_urscript_for_tcp_pose(urscript_file)
