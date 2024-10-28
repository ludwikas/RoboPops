import socket
import rtde_receive
import time
import logging
import re
import W3A_A_Format_TCP

# Setting up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to send a .txt file (URscript as it is) to the robot controller
def send_urscript(file_path: str, robot_ip: str, port: int = 30002):
    try:
        with open(file_path, "r") as file:
            urscript = file.read()

        logging.debug(f"URScript content:\n{urscript}")

        with socket.create_connection((robot_ip, port), timeout=10) as s:
            logging.info("Sending URscript to the robot controller")
            s.sendall(urscript.encode("utf-8"))
            logging.info("URscript sent successfully.")

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Function to extract total moves from the URScript file
def extract_total_moves(file_path: str) -> int:
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Use regex to find all occurrences of "Move start n" where n is an integer
        move_markers = re.findall(r"Move start \d+", content)
        total_moves = len(move_markers)

        logging.info(f"Total number of moves extracted: {total_moves}")
        return total_moves
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return 0
    except Exception as e:
        logging.error(f"Unexpected error while reading file: {e}")
        return 0

# Function to monitor joint speeds based on URScript move markers
def monitor_joint_speeds(robot_ip: str, notification_port: int = 30004, total_moves: int = None):
    rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)

    # Ensure RTDE interface is connected
    if not rtde_r.isConnected():
        logging.error("RTDE connection failed.")
        return []

    logging.info("Connected to RTDE.")

    # Set up a socket to listen for move notifications from URScript
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', notification_port))  # Bind to any available network interface on this port
        s.listen(1)
        s.settimeout(60)  # Increase timeout to allow more time for connections
        logging.info(f"Listening for move notifications on port {notification_port}...")

        conn, addr = s.accept()
        logging.info(f"Connected by {addr}")

        conn.setblocking(1)
        joint_speeds_data = []
        move_counter = 0

        while True:
            try:
                data = conn.recv(1024).decode("utf-8").strip()
                if not data:
                    logging.info("Socket closed by robot. Stopping data collection.")
                    break

                logging.debug(f"Received data: {data}")

                if "Move end" in data:
                    move_counter += 1
                    logging.info(f"Received: {data}. Move count: {move_counter}")

                    # Collect joint speeds at the end of each move
                    joint_speeds = rtde_r.getActualQd()
                    joint_speeds_data.append((joint_speeds, f"Move end {move_counter}"))
                    logging.info(f"Joint Speeds collected at move end {move_counter}: {joint_speeds}")

                    if total_moves and move_counter == total_moves:
                        logging.info("All moves completed. Stopping monitoring.")
                        break

            except socket.error as e:
                logging.error(f"Socket error during data reception: {e}")
                break
            except Exception as e:
                logging.error(f"Error during joint speed monitoring: {e}")
                break

    except socket.timeout:
        logging.warning("Socket accept timed out. No connection established.")
    except Exception as e:
        logging.error(f"Error setting up socket: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
        s.close()
        return joint_speeds_data

# Function to write joint speeds to a .txt file
def write_joint_speeds_to_file(joint_speeds_data, output_file_path="Joint_speeds.txt"):
    try:
        with open(output_file_path, "w") as file:
            for i, (joint_speeds, source) in enumerate(joint_speeds_data):
                file.write(f"Data {i + 1}: Source: {source}, Joint Speeds: {joint_speeds}\n")
        logging.info(f"Joint speeds successfully written to {output_file_path}")
    except Exception as e:
        logging.error(f"Error writing joint speeds to file: {e}")

import numpy as np
import re

# Function to extract Cartesian speeds from the file
def extract_cartesian_speeds(file_path_speed):
    pattern = r'Joint Speeds: \[([\d\.\-e]+), ([\d\.\-e]+), ([\d\.\-e]+),'
    cartesian_speeds = []
    
    with open(file_path_speed, "r") as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                x, y, z = map(float, match.groups())
                cartesian_speeds.append((x, y, z))
    return cartesian_speeds

# Function to calculate linear speeds from Cartesian speeds
def calculate_linear_speeds(cartesian_speeds):
    linear_speeds = []
    for x, y, z in cartesian_speeds:
        v_linear = np.sqrt(x**2 + y**2 + z**2)
        linear_speeds.append(v_linear)
    return linear_speeds

# Function to write linear speeds to a file
def write_speeds_in_file(linear_speeds, output_file_path_lspeed: str):
    with open(output_file_path_lspeed, "w") as file:
        for speed in linear_speeds:  # Iterate over each individual speed
            file.write(f"{speed}\n")  # Write each speed on a new lin



def main():
    try:
        file_path_unf = "URscript_newmovel.txt"
        output_file_path_1f = "WFormatted_URscript.txt"
        ip_address = "145.94.133.95"
        W3A_A_Format_TCP.format_urscript(file_path_unf, output_file_path_1f, ip_address, message_prefix="Move")
        file_path = "WFormatted_URscript.txt"
        robot_ip = "192.168.40.128"
        notification_port = 30004

        # Step 1: Extract total moves from the URScript file
        total_moves = extract_total_moves(file_path)

        # Step 2: Send URscript to the robot
        send_urscript(file_path, robot_ip)

        # Step 3: Monitor the joint speeds based on move markers
        joint_speeds_data = monitor_joint_speeds(robot_ip, notification_port=notification_port, total_moves=total_moves)

        # Step 4: Write the collected joint speeds to a .txt file
        write_joint_speeds_to_file(joint_speeds_data)

    except Exception as e:
        logging.error(f"Error in main function: {e}")

    file_path_speed = "Joint_speeds.txt"
    output_file_path_lspeed = "Linear_speeds_2.txt"
        
    # Extract Cartesian speeds from the file
    cartesian_speeds = extract_cartesian_speeds(file_path_speed)
        
    # Calculate linear speeds from the Cartesian speeds
    v_linear = calculate_linear_speeds(cartesian_speeds)
        
    # Write the calculated linear speeds to the output file
    write_speeds_in_file(v_linear, output_file_path_lspeed)
    print(cartesian_speeds)

if __name__ == "__main__":
    main()
