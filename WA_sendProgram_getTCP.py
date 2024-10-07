import socket
import rtde_receive
import time
import re

# Function to send a .txt file (URscript as it is) to the robot controller
def send_urscript(file_path: str, robot_ip: str, port: int = 30002):
    with open(file_path, "r") as file:
        urscript = file.read()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((robot_ip, port))

    try:
        print("Sending URscript to the robot controller")
        s.sendall(urscript.encode("utf-8"))
        print("URscript sent successfully.")
    except Exception as e:
        print(f"Error during sending URscript: {e}")
    finally:
        s.close()
        print("Connection closed.")

# Function to monitor TCP pose using RTDE
def monitor_tcp_pose(robot_ip: str, expected_moves: int, polling_interval: float = 0.05):
    rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
    
    # Ensure RTDE interface is connected
    if not rtde_r.isConnected():
        print("Error: RTDE connection failed.")
        return []

    print("Connected to RTDE.")

    # List to store the TCP poses after each move
    tcp_poses = []

    try:
        print("Monitoring TCP poses...")
        move_count = 0
        prev_tcp_pose = None

        # Poll for the TCP pose until we have collected all expected moves
        while move_count < expected_moves:
            tcp_pose = rtde_r.getActualTCPPose()

            # If the pose is different from the previous one (significant change)
            if tcp_pose != prev_tcp_pose:
                prev_tcp_pose = tcp_pose
                move_count += 1
                tcp_poses.append(tcp_pose)

                print(f"TCP Pose after move {move_count}: X: {tcp_pose[0]:.3f}, Y: {tcp_pose[1]:.3f}, Z: {tcp_pose[2]:.3f}, RX: {tcp_pose[3]:.3f}, RY: {tcp_pose[4]:.3f}, RZ: {tcp_pose[5]:.3f}")

            # Poll every 50 milliseconds or custom interval
            time.sleep(polling_interval)

    except KeyboardInterrupt:
        print("Monitoring interrupted.")
    except Exception as e:
        print(f"Error during TCP pose monitoring: {e}")
    finally:
        return tcp_poses

# Function to count movement commands in the URScript
def count_movement_commands(file_path: str):
    with open(file_path, "r") as file:
        script_content = file.read()
    
    # Regular expression to match motion commands like movej, movel, movep, etc.
    move_commands = re.findall(r'\bmove[jlp]\b', script_content, re.IGNORECASE)
    
    # Return the number of movement commands found
    return len(move_commands)

def main():
    file_path = "URscript.txt"
    robot_ip = "192.168.177.128"

    # Count the number of movement commands in the URscript
    expected_moves = count_movement_commands(file_path)
    print(f"Number of movement commands detected in URscript: {expected_moves}")

    if expected_moves == 0:
        print("No movement commands detected. Exiting.")
        return

    # Step 1: Send URscript to the robot
    send_urscript(file_path, robot_ip)

    # Step 2: Monitor the TCP poses dynamically based on detected move commands
    tcp_poses = monitor_tcp_pose(robot_ip, expected_moves=expected_moves, polling_interval=0.05)

    # Output the collected TCP poses
    print("\nCollected TCP Poses:")
    for i, pose in enumerate(tcp_poses):
        print(f"Pose {i + 1}: {pose}")

if __name__ == "__main__":
    main()
