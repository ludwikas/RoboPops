import socket
import rtde_receive
import time
import logging
import re

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to send a .txt file (URscript as it is) to the robot controller
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

def extract_total_moves(file_path_1f: str) -> int:
    try:
        with open(file_path_1f, 'r') as file:
            content = file.read()

        # Use regex to find all occurrences of "Move start n" where n is an integer
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
# Function to monitor TCP pose and speed based on both markers and intervals
def monitor_tcp_pose_and_speed_combined(robot_ip: str, notification_port: int = 30004, interval: float = 0.1, total_moves: int = None):
    rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)

    # Ensure RTDE interface is connected
    if not rtde_r.isConnected():
        logging.error("RTDE connection failed.")
        return [], []

    logging.info("Connected to RTDE.")

    # Set up a socket to listen for move notifications from URScript
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', notification_port))  # Bind to any available network interface on this port
    s.listen(1)
    s.settimeout(30)  # Set a timeout for accept
    logging.info(f"Listening for move notifications on port {notification_port}...")

    conn = None
    tcp_data = []
    marker_tcp_data = []  # List to store TCP data after markers (e.g., Move start)
    monitoring_started = False
    move_counter = 0  # Tracks the number of "Move start" markers received

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

                # Start monitoring after receiving "Move start n" markers
                if "Move start" in data:
                    # Extract the move index from the marker
                    move_counter += 1
                    logging.info(f"Received: {data}. Move count: {move_counter}")

                    # Start monitoring at "Move start 3"
                    if not monitoring_started and "Move start 3" in data:
                        logging.info("Move start 3 marker received. Starting monitoring.")
                        monitoring_started = True

                    # Stop monitoring one move before the last move if total_moves is known
                    if total_moves and monitoring_started and move_counter == total_moves:
                        logging.info("One move before the last move reached. Stopping monitoring.")
                        monitoring = False
                        continue

                # If "Move end" marker is received during monitoring
                if monitoring_started and "Move end" in data:
                    logging.info(f"Received: {data}. Movement ended.")
                    tcp_pose = rtde_r.getActualTCPPose()
                    marker_tcp_data.append(tcp_pose)
                    logging.info(f"TCP Pose collected immediately after Move end (for marker list): {tcp_pose}")
                    continue

            except socket.error:
                pass
            finally:
                conn.setblocking(1)

            # Collect interval data only after monitoring has started
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

# Function to write TCP poses after markers to a separate file
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
    tcp_data, marker_tcp_data = monitor_tcp_pose_and_speed_combined(robot_ip, notification_port=notification_port, interval=0.01, total_moves=total_moves)

    # Step 4: Write the collected TCP poses and speeds to separate .txt files
    write_tcp_positions_to_file(tcp_data)
    write_tcp_speeds_to_file(tcp_data)  # Ensuring speeds are written

    # Step 5: Write TCP poses collected after markers to a separate file
    write_marker_tcp_positions_to_file(marker_tcp_data)

    # Output the collected TCP data to the console
    logging.info("\nCollected Marker TCP Data:")
    for i, pose in enumerate(marker_tcp_data):  # No need to unpack more than 1 value for marker data
        logging.info(f"Marker Pose {i + 1}: {pose}")

if __name__ == "__main__":
    main()