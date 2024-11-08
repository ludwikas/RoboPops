import socket
import rtde_receive
import time
import logging
import re
import math

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to send a .txt file (URscript) to the robot controller
def send_urscript(file_path_1f: str, robot_ip: str, port: int = 30002):
    try:
        with open(file_path_1f, "r") as file:
            urscript = file.read()

        with socket.create_connection((robot_ip, port), timeout=10) as s:
            logging.info("Sending URscript to the robot controller")
            s.sendall(urscript.encode("utf-8"))
            logging.info("URscript sent successfully.")

    except FileNotFoundError:
        logging.error(f"File not found: {file_path_1f}")
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Function for total move extraction based on strings we implement in the format with the Format_TCP script
# This is important for the monitoring process that follows, so we know beforehand the number of indices. 

def extract_total_moves(file_path_1f: str) -> int:
    try:
        with open(file_path_1f, 'r') as file:
            content = file.read()

        # Use regex to find all occurrences of "Move start n" 
        move_markers = re.findall(r"Move start \d+", content)
        total_moves = len(move_markers)

        logging.info(f"Total number of moves extracted: {total_moves}")
        return total_moves
    except FileNotFoundError:
        logging.error(f"File not found: {file_path_1f}")
        return 0
    except Exception as e:
        logging.error(f"Unexpected error while reading file: {e}")
        return 0
    
# Function to monitor TCP pose and speed based on both markers and intervals
# Here we monitor based on two factors, a set interval and the main TCP
# Main TCPs are recognised beacuase of the previous format that has taken place 
# Every main TCP is enclosed between two socket_strings that we are waiting to recieve
# Based on the indices of the moves that we extract with the previous function, we can recognise when to start and stop
#the monitoring process because not all positions are important for the calculations that we are going to run next. 

def monitor_tcp_pose_and_speed_combined(robot_ip: str, notification_port: int = 30004, interval: float = 0.5, total_moves: int = None):
    rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)

    # Ensure RTDE interface is connected
    if not rtde_r.isConnected():
        logging.error("RTDE connection failed.")
        return [], []

    logging.info("Connected to RTDE.")

    # Set up a socket to listen for move notifications from URScript
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', notification_port))                                                  # Bind to any available network interface on this port
    s.listen(1)
    s.settimeout(30)                                                                        # Set a timeout if connection is not established
    logging.info(f"Listening for move notifications on port {notification_port}...")

    conn = None
    tcp_data = []
    marker_tcp_data = []                                                                   # List to store TCP data after markers
    monitoring_started = False
    move_counter = 0                                                                       
    try:
        conn, addr = s.accept()
        logging.info(f"Connected by {addr}")

        # Start monitoring using both URScript markers and intervals
        monitoring = True
        while monitoring:
            # Check for any move start/end markers
            try:
                conn.setblocking(0)
                data = conn.recv(1024).decode("utf-8").strip()
                if not data:
                    logging.info("Socket closed by robot. Stopping data collection.")
                    break

                # Start monitoring after receiving "Move end" markers
                if "Move end" in data:
                    # Extract the move index from the marker
                    move_counter += 1
                    logging.info(f"Received: {data}. Move count: {move_counter}")

                    # Start monitoring at "Move end 2" (no need to be dynamic)
                    # Here we assume that monitoring will always be starting after the end of the first two moves
                    # that is based on the FIRST programable move that is always going to be a movej (moving the robot from
                    #a random starting position to the start of the program and the SECOND that is going to be the aproach/test line of the print)
                    # For the monitoring to function properly those moves should be accounted while programming the robot in the early stages

                    if not monitoring_started and "Move end 2" in data:
                        logging.info("Move end 2 marker received. Starting monitoring.")
                        monitoring_started = True

                # If "Move start" marker is received during monitoring
                if monitoring_started and "Move start" in data:
                    logging.info(f"Received: {data}. Movement ended.")
                    tcp_pose = rtde_r.getActualTCPPose()
                    tcp_speed = rtde_r.getActualTCPSpeed()                                                              # Collect speed for the marker pose
                    marker_tcp_data.append(tcp_pose)
                    tcp_data.append((tcp_pose, tcp_speed, "Marker"))                                                    # Include speed for the marker pose
                    logging.info(f"TCP Pose collected immediately after Move end (for marker list): {tcp_pose}")

                    # Stop monitoring before the last move
                    # Stop monitoring before reaching the last move
                    # The last move is going to be the retraction move where extrusion is not wanted. For that reason we take this out of the 
                    #data that we need to calculate
                    if total_moves and move_counter == total_moves -1:
                        logging.info("Reached one move before the last move. Stopping monitoring.")
                        monitoring = False
                    continue

            except socket.error:
                pass
            finally:
                conn.setblocking(1)

            # Collect interval data based on previous if statements
            if monitoring_started:
                tcp_pose = rtde_r.getActualTCPPose()
                tcp_speed = rtde_r.getActualTCPSpeed()
                tcp_data.append((tcp_pose, tcp_speed, "Interval"))
                logging.info(f"Interval - TCP Pose: {tcp_pose}, TCP Speed: {tcp_speed}")
                time.sleep(interval)

    except socket.timeout:
        logging.warning("Socket accept timed out. No connection established.")
    except KeyboardInterrupt:
        logging.info("Monitoring interrupted by user.")
    except Exception as e:
        logging.error(f"Error during TCP pose and speed monitoring: {e}")
    finally:
        if conn:
            conn.close()
        s.close()
        return tcp_data, marker_tcp_data

# Function to remove consecutive duplicates from the tcp_data list based on pose values
# There is a possibility that some of the collected poses are going to be the same, in order 
#for that to not create a confusion in the next data processing we eliminate that possibility 
#already by "cleaning" the list before writing the data into a file.
def remove_consecutive_duplicates(tcp_data, tolerance=1e-6):
    if not tcp_data:
        return []

    # Start with the first element in the list
    deduplicated_data = [tcp_data[0]]

    # Iterate over the rest of the data and compare poses for approximate equality
    for i in range(1, len(tcp_data)):
        current_pose = tcp_data[i][0]
        previous_pose = tcp_data[i - 1][0]

        # Check if current pose and previous pose are approximately equal
        if not are_poses_approximately_equal(current_pose, previous_pose, tolerance):
            deduplicated_data.append(tcp_data[i])

    return deduplicated_data

# Compare two poses based on a tolerance
def are_poses_approximately_equal(pose1, pose2, tolerance):
    if len(pose1) != len(pose2):
        return False

    # Compare each element of the poses
    for a, b in zip(pose1, pose2):
        if not math.isclose(a, b, abs_tol=tolerance):
            return False

    return True

# Function to write TCP poses to a .txt file
def write_tcp_positions_to_file(tcp_data, output_file_path="Interval_TCP.txt"):
    try:
        with open(output_file_path, "w") as file:
            for i, (pose, _, source) in enumerate(tcp_data):
                file.write(f"Data {i + 1}: Source: {source}, Pose: {pose}\n")
        logging.info(f"TCP positions successfully written to {output_file_path}")
    except Exception as e:
        logging.error(f"Error writing TCP positions to file: {e}")

# Function to write TCP speeds to a .txt file
def write_tcp_speeds_to_file(tcp_data, output_file_path="Interval_speeds.txt"):
    try:
        with open(output_file_path, "w") as file:
            for i, (_, speed, source) in enumerate(tcp_data):
                file.write(f"Data {i + 1}: Source: {source}, Speed: {speed}\n")
        logging.info(f"TCP speeds successfully written to {output_file_path}")
    except Exception as e:
        logging.error(f"Error writing TCP speeds to file: {e}")

# Function to write TCP poses after markers to a separate file (main TCPs)
def write_marker_tcp_positions_to_file(marker_tcp_data, output_file_path="TCP_main.txt"):
    try:
        with open(output_file_path, "w") as file:
            for i, pose in enumerate(marker_tcp_data):
                file.write(f"Marker Pose {i + 1}: {pose}\n")
        logging.info(f"Marker TCP positions successfully written to {output_file_path}")
    except Exception as e:
        logging.error(f"Error writing Marker TCP positions to file: {e}")

def main():
    file_path_1f = "Formatted_URscript.txt"
    robot_ip = "192.168.40.128"
    notification_port = 30004

    # Step 1: Extract total moves from the URScript file
    total_moves = extract_total_moves(file_path_1f)

    # Step 2: Send URscript to the robot
    send_urscript(file_path_1f, robot_ip)

    # Step 3: Monitor the TCP poses and speeds using both markers and intervals
    tcp_data, marker_tcp_data = monitor_tcp_pose_and_speed_combined(robot_ip, notification_port=notification_port, interval=0.1, total_moves=total_moves)

    # Step 4: Remove consecutive duplicates from the tcp_data list based on pose values
    tcp_data = remove_consecutive_duplicates(tcp_data)

    # Step 5: Write the collected TCP poses and speeds to .txt 
    write_tcp_positions_to_file(tcp_data)
    write_tcp_speeds_to_file(tcp_data)  

    # Step 6: Write TCP poses collected after markers to a separate file
    write_marker_tcp_positions_to_file(marker_tcp_data)

    # Output the collected TCP data to the console
    logging.info("\nCollected Marker TCP Data:")
    for i, pose in enumerate(marker_tcp_data):
        logging.info(f"Marker Pose {i + 1}: {pose}")

if __name__ == "__main__":
    main()
