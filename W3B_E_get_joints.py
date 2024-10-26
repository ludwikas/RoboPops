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
                if ":" in line:
                    # Split the line into index and pose part
                    idx, pose_str = line.split(":")
                    idx = int(idx.strip())  # Get the index (integer)

                    # Convert pose string to list of floats
                    pose = [float(val) for val in pose_str.strip(' []\n').split(',')]
                    
                    if len(pose) == 6:  # Ensure there are 6 values for TCP pose (x, y, z, rx, ry, rz)
                        tcp_poses[idx] = pose
                    else:
                        logging.error(f"Invalid pose format at line: {line.strip()}")
    except Exception as e:
        logging.error(f"Error reading TCP positions from file: {e}")
    
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

# Function to create an indexed list of the new joint positions obtianed from previous step
def create_joint_position_list(joint_positions):
      # Add an index to each joint position
    return {i + 1: pos for i, pos in enumerate(joint_positions)}

# Function to read the original URScript and strip movel commands
def read_and_strip_urscript(file_path_unf):
    stripped_script = []
    try:
        with open(file_path_unf, "r") as file:
            for line in file:
                # Exclude lines with "movel" or "end" as they will be replaced
                if "movel" not in line and "end" not in line:
                    stripped_script.append(line)
    except Exception as e:
        logging.error(f"Error reading and stripping URScript file: {e}")
    return stripped_script

# Function to write the URScript based on the joint positions
def write_ur_script(stripped_script, joint_poses_idx, output_file_urscript_newl):
    try:
        with open(output_file_urscript_newl, "w") as file:
            # Write the retained portion of the original URScript
            for line in stripped_script:
                file.write(line)

            # Append the new movel commands based on joint positions and TCP speeds
            for idx in joint_poses_idx:
                joint_pos = joint_poses_idx[idx]
                
                movel_command = f"  movel({joint_pos}, a=1, v=Speed000, r=Zone000)\n"
                file.write(movel_command)

            # Write the end of the URScript **after** the last movel command
            file.write("end\n")   
        
        logging.info(f"URScript successfully written to {output_file_urscript_newl}")
    except Exception as e:
        logging.error(f"Error writing URScript to file: {e}")
    

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
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # PART 1: GET JOINT POSITIONS FROM ENRICHED TCPS

    # Path to the file containing enriched TCP poses
    file_path_TCP_seq = r"C:\Users\emily\OneDrive\2.school\build tech\CORE\project\emilyscode\TCP_poses_idx.txt"
    
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

# PART 2: FOMRAT UR SCRIPT WITH JOINT POSITIONS

    # Define the input file paths
    file_path_unf = r"C:\Users\emily\OneDrive\2.school\build tech\CORE\project\emilyscode\Input_UR_script.txt"

    # Create the indexed list of joint positions
    joint_poses_idx = create_joint_position_list(joint_positions)

    # Read and strip movel commands from the original script
    stripped_script = read_and_strip_urscript(file_path_unf)

    # Print the final positions and speeds (for debugging)
    print("New Joint Positions:", joint_poses_idx)

    # Define the output file paths
    output_file_urscript_newl = "C:/Users/emily/OneDrive/2.school/build tech/CORE/project/emilyscode/output_program.txt"

    # Write the URScript by combining the stripped original script with the new movel commands
    write_ur_script(stripped_script, joint_poses_idx, output_file_urscript_newl)


# PART 3: SEND UR SCRIPT

    # Send the URScript to the robot controller
    send_ur_script_to_robot(output_file_urscript_newl, robot_ip)
