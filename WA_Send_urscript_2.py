### THIS WORKS WITH THE ARDUINO THE FIRST DOESN'T FOR SOME REASON
import socket


# Function to send a .txt file (URScript as it is) straight to the robot controller
def send_urscript(file_path: str, robot_ip: str, port: int = 30002):
    try:
        # Read the URScript from the file
        with open(file_path, "r") as file:
            urscript = file.read()

        # Create a socket connection to the robot controller
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((robot_ip, port))
            print("Sending URScript to the robot controller...")
            s.sendall(urscript.encode("utf-8"))

            # Optionally receive response
            try:
                response = s.recv(1024).decode("utf-8")
                if response:
                    print("Response from robot:", response)
            except socket.timeout:
                print("No response received from the robot.")
        
        print("Connection closed.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except socket.error as e:
        print(f"Socket error: {e}")

# Update the file path and robot IP as per your setup
file_path = "URscript.txt"  # Changed for MOCKUP day
robot_ip = "192.168.1.198"

send_urscript(file_path, robot_ip)

#DynamicVoltScript