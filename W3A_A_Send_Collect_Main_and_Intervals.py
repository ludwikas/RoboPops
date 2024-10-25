import socket
import rtde_receive
import time
import logging

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

# Function to monitor TCP pose and speed based on both markers and intervals
def monitor_tcp_pose_and_speed_combined(robot_ip: str, notification_port: int = 30004, interval: float = 0.1):
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

                if "Move end" in data:
                    logging.info(f"Received: {data}. Movement ended.")
                    # Immediately collect TCP pose after Move end
                    tcp_pose = rtde_r.getActualTCPPose()
                    marker_tcp_data.append(tcp_pose)
                    logging.info(f"TCP Pose collected immediately after Move end (for marker list): {tcp_pose}")
                    continue  # Skip to next iteration after Move end.

            except socket.error:
                pass
            finally:
                conn.setblocking(1)

            # Monitor TCP pose and speed based on interval timing
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

    # Step 1: Send URscript to the robot
    send_urscript(file_path_1f, robot_ip)

    # Step 2: Monitor the TCP poses and speeds using both markers and intervals
    tcp_data, marker_tcp_data = monitor_tcp_pose_and_speed_combined(robot_ip, notification_port=notification_port, interval=0.01)

    # Step 3: Write the collected TCP poses and speeds to separate .txt files
    write_tcp_positions_to_file(tcp_data)
    write_tcp_speeds_to_file(tcp_data)  # Ensuring speeds are written

    # Step 4: Write TCP poses collected after markers to a separate file
    write_marker_tcp_positions_to_file(marker_tcp_data)

    # Output the collected TCP data to the console
    logging.info("\nCollected Marker TCP Data:")
    for i, pose in enumerate(marker_tcp_data):  # No need to unpack more than 1 value for marker data
        logging.info(f"Marker Pose {i + 1}: {pose}")

if __name__ == "__main__":
    main()
