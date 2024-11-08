import logging
import rtde_control
import rtde_receive
import socket

# READ TCPs
# Function to read TCP poses from text file
def read_tcp_poses_from_file(file_path_TCP_seq):
    tcp_poses = {}
    try:
        with open(file_path_TCP_seq, "r") as file:
            for line in file:
                # Check for the presence of ':' and '[' to validate the format of the line
                if ":" in line and "[" in line:
                    # Split the line to get the index and pose part separately
                    index_part, pose_str = line.split(":", 1)
                    
                    # Take only the first value before any text as the index
                    index = int(index_part.split()[0].strip())
                    
                    # Extract the values inside the brackets as pose
                    pose_str = pose_str[pose_str.index("[")+1:pose_str.index("]")]
                    pose = [float(val) for val in pose_str.split(",")]
                    
                    if len(pose) == 6:  # Ensure there are 6 values for TCP pose (x, y, z, rx, ry, rz)
                        tcp_poses[index] = pose
    except Exception as e:
        print(f"Error reading file: {e}")
    return tcp_poses

# SEND TCP TO RC
# Function to send TCP poses and receive joint positions via RTDE
def get_joint_positions_from_tcp(tcp_poses, robot_ip):
    joint_positions = []
    
    # Initialize RTDE interfaces
    rtde_c = rtde_control.RTDEControlInterface(robot_ip)
    rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)

    logging.info("Connected to the robot controller via RTDE")
    
    try:
        for idx, pose in tcp_poses.items():
            try:
                # Move the robot to each TCP pose using RTDE
                logging.info(f"Moving to pose {idx}: {pose}")
                rtde_c.moveL(pose)  # Linear move to the specified TCP pose

                # Get the joint positions after moving to the pose
                joint_data = rtde_r.getActualQ()  # Get current joint positions (list of 6 values)
                joint_positions.append(joint_data)
                
                logging.info(f"Received joint positions for pose {idx}: {joint_data}")

            except Exception as move_error:
                logging.error(f"Error processing pose {idx}: {move_error}")
    
    except Exception as conn_error:
        logging.error(f"Error in RTDE communication: {conn_error}")
    
    finally:
        # stop RTDE control
        rtde_c.stopScript()
        logging.info("RTDE control stopped")
    
    return joint_positions

# FORMAT NEW MOVE L LINES
# Function to create an indexed list of the new joint positions obtained from the previous step
def create_joint_position_list(joint_positions):
    # Add an index to each joint position
    return {i + 1: pos for i, pos in enumerate(joint_positions)}

# Function to read the original URScript and strip movel and movep commands while retaining the first and last move commands
def read_and_strip_urscript(file_path_unf):
    stripped_script = []
    first_move_command_found = False
    last_move_command = None
    movej_retained = False

    try:
        with open(file_path_unf, "r") as file:
            for line in file:
                # Check for movej command and retain the first one
                if "movej" in line and not movej_retained:
                    stripped_script.append(line)
                    movej_retained = True
                    continue
                
                # Check for movel or movep commands
                if "movel" in line or "movep" in line:
                    if not first_move_command_found:
                        # Retain the first movel or movep command
                        stripped_script.append(line)
                        first_move_command_found = True
                    # Update last_move_command with the current line
                    last_move_command = line
                    continue  # Skip the remaining movel/movep lines

                # Exclude lines with "end" as they will be replaced
                if "end" not in line:
                    stripped_script.append(line)

    except Exception as e:
        logging.error(f"Error reading and stripping URScript file: {e}")
    
    # If a last move command was found, add it to the end
    if last_move_command:
        stripped_script.append(last_move_command)

    return stripped_script

# create pose types dictionary
def create_pose_types_dict(file_path_TCP_seq):
    pose_types = {}
    try:
        with open(file_path_TCP_seq, "r") as file:
            for line in file:
                if ":" in line:
                    # Split line to get index and description part
                    index_part, _ = line.split(":", 1)

                    # Extract the index from the start of the line
                    index = int(index_part.split()[0].strip())

                    # Determine the type based on keywords in the line
                    if "Marker pose" in line:
                        pose_types[index] = "Marker pose"
                    elif "Interval" in line:
                        pose_types[index] = "Interval"

    except Exception as e:
        logging.error(f"Error creating pose types dictionary: {e}")
    
    return pose_types

# function to write URscript with new move commands
def write_ur_script(stripped_script, joint_poses_idx, pose_types, output_file_urscript_newl):
    try:
        with open(output_file_urscript_newl, "w") as file:
            # Write the retained portion of the original URScript up to the first retained movel command
            for line in stripped_script:
                file.write(line)
                # Insert the new movel commands after the first non-movej command
                if "movel" in line or "movep" in line:
                    break

            # Iterate through the joint_poses_idx dictionary and write movel commands based on position type
            for idx, joint_pos in joint_poses_idx.items():
                # Check the type in pose_types dictionary for current index
                if pose_types.get(idx) == "Marker pose":
                    movel_command = f"  movel({joint_pos}, a=1, v=Speed000, r=Zone000)\n"
                elif pose_types.get(idx) == "Interval":
                    movel_command = f"  movel({joint_pos}, a=1, v=Speed000, r=Zone001)\n"
                else:
                    continue  # Skip if the type is undefined

                file.write(movel_command)

            # Resume writing remaining original lines after the inserted movel commands
            for line in stripped_script[len(stripped_script) - 1:]:
                file.write(line)

            # Write the end of the URScript after the last movel command
            file.write("end\n")

    except Exception as e:
        logging.error(f"Error writing URScript file: {e}")

# Function to send the URScript to the robot controller using socket
def send_ur_script_to_robot(output_file_urscript_newl, robot_ip, port=30002):
    try:
        # Open the URScript file and read the content
        with open(output_file_urscript_newl, "r") as file:
            script_content = file.read()

        # Create a socket and connect to the robot controller
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as robot_socket:
            robot_socket.connect((robot_ip, port))
            robot_socket.sendall(script_content.encode('utf-8'))  # Send the URScript content

        logging.info(f"URScript sent to the robot controller at {robot_ip}:{port}")
    except Exception as e:
        logging.error(f"Error sending URScript to the robot controller: {e}")    


# Main function to execute the script
def main():

    logging.basicConfig(level=logging.INFO)

# PART 1: GET JOINT POSITIONS FROM ENRICHED TCPS

    # Path to the file containing enriched TCP poses
    file_path_TCP_seq = r"C:\Users\emily\OneDrive\2.school\build tech\CORE\project\emilyscode\TCPs_with_markers.txt"
    
    # Read TCP poses from the file
    tcp_poses = read_tcp_poses_from_file(file_path_TCP_seq)

    # test print TCPs, ensure file is being read
    print("TCPposes from file:", tcp_poses)

    # Robot IP
    robot_ip = "192.168.60.128"  # UR5 simulator IP

    # Get joint positions for the TCP poses using RTDE
    if tcp_poses:
        joint_positions = get_joint_positions_from_tcp(tcp_poses, robot_ip)
    else:
        logging.error("No valid TCP poses found.")
        joint_positions = []

# PART 2: FORMAT UR SCRIPT WITH JOINT POSITIONS

    # Define the input file path for the original URscript
    file_path_unf = r"C:\Users\emily\OneDrive\2.school\build tech\CORE\project\emilyscode\URscript.txt"

    # Create the indexed list of joint positions
    joint_poses_idx = create_joint_position_list(joint_positions)

    # test print joint list
    print("Indexed joint pose list:", joint_poses_idx)

    # Read and strip movel commands from the original script
    stripped_script = read_and_strip_urscript(file_path_unf)

    # Print the final positions and speeds (for debugging)
    print("New Joint Positions:", joint_poses_idx)

    # Define the output file paths for the new URscript with the added move commands
    output_file_urscript_newl = "C:/Users/emily/OneDrive/2.school/build tech/CORE/project/emilyscode/URscript_newmovel.txt"

    # define pose types
    pose_types = create_pose_types_dict(file_path_TCP_seq)

    # Write the URScript by combining the stripped original script with the new movel commands
    write_ur_script(stripped_script, joint_poses_idx, pose_types, output_file_urscript_newl)

# PART 3: SEND UR SCRIPT. this is for testing.

    # Send the URScript to the robot controller
    send_ur_script_to_robot(output_file_urscript_newl, robot_ip)

if __name__ == "__main__":
    main()