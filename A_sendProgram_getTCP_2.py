import socket
import rtde_receive
import time
import logging

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to send a .txt file (URscript as it is) to the robot controller
def send_urscript(file_path: str, robot_ip: str, port: int = 30002):
    try:
        with open(file_path, "r") as file:
            urscript = file.read()

        with socket.create_connection((robot_ip, port), timeout=5) as s:
            logging.info("Sending URscript to the robot controller")
            s.sendall(urscript.encode("utf-8"))
            logging.info("URscript sent successfully.")

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Function to monitor TCP pose using RTDE
def monitor_tcp_pose_dynamic(robot_ip: str, port: int = 30004):
    rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)

    # Ensure RTDE interface is connected
    if not rtde_r.isConnected():
        logging.error("RTDE connection failed.")
        return []

    logging.info("Connected to RTDE.")

    # Set up a socket to listen for move notifications from URScript
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))  # Bind to any available network interface on this port
    s.listen(1)
    logging.info(f"Listening for move notifications on port {port}...")

    conn = None  # Initialize conn variable
    tcp_poses = []
    try:
        s.settimeout(30)  # Set timeout for accept
        conn, addr = s.accept()
        logging.info(f"Connected by {addr}")

        while True:
            data = conn.recv(1024).decode("utf-8").strip()
            if not data:
                break

            # When move ends, collect the TCP pose
            if "Move end" in data:
                tcp_pose = rtde_r.getActualTCPPose()
                tcp_poses.append(tcp_pose)
                logging.info(f"TCP Pose collected at the end of a move: {tcp_pose}")

            # Optionally handle "Move start" messages if needed
            elif "Move start" in data:
                logging.info(f"Received: {data}")

            time.sleep(0.05)  # Sleep briefly between checks

    except socket.timeout:
        logging.warning("Socket accept timed out. No connection established.")
    except KeyboardInterrupt:
        logging.info("Monitoring interrupted by user.")
    except Exception as e:
        logging.error(f"Error during TCP pose monitoring: {e}")
    finally:
        if conn:
            conn.close()  # Close conn only if it was successfully assigned
        s.close()
        return tcp_poses

def main():
    file_path = "Formated_URscript.txt"
    robot_ip = "192.168.40.128"
    notification_port = 30004  # Port for listening to URScript notifications (different from RTDE)

    # Step 1: Send URscript to the robot
    send_urscript(file_path, robot_ip)

    # Step 2: Monitor the TCP poses dynamically based on URScript move notifications
    tcp_poses = monitor_tcp_pose_dynamic(robot_ip, port=notification_port)

    # Output the collected TCP poses
    logging.info("\nCollected TCP Poses:")
    for i, pose in enumerate(tcp_poses):
        logging.info(f"Pose {i + 1}: {pose}")

if __name__ == "__main__":
    main()
