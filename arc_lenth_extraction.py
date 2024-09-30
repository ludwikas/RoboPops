import socket

def send_urscript(urscript: str, robot_ip: str, port: int = 30002) -> str:
    """
    Sends a URScript to the UR robot controller and listens for a response.
    
    Args:
        urscript (str): The URScript to be sent.
        robot_ip (str): IP address of the robot.
        port (int): The port to connect to the robot controller (default is 30002).

    Returns:
        str: Data received from the robot controller (e.g., calculated arc lengths).
    """
    # Create socket connection to the robot controller
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((robot_ip, port))
    
    try:
        # Send the URScript to the robot controller
        s.sendall(urscript.encode('utf-8'))
        
        # Receive response data from the robot controller
        data = s.recv(1024).decode('utf-8')  # Adjust buffer size if necessary
        
        return data  # Return the received data (arc lengths)
    
    finally:
        s.close()

# Example URScript to send (this will need to be customized based on your needs)
urscript = """
def my_program():
    # Calculate arc length (example values for demonstration)
    arc_length = 2 * 3.14 * 0.5  # Placeholder calculation
    # Print arc length, this can also be sent via socket communication
    textmsg("Calculated Arc Length: ", arc_length)
    # Hold the program before motion (e.g., waiting for response)
    sleep(5)
    # Start moving the robot
    movej([1.57, -1.57, 1.57, -1.57, 1.57, 0])
end
"""

# Send URScript and receive arc length data
robot_ip = "192.168.0.1"  # Replace with your robot's IP
arc_length_data = send_urscript(urscript, robot_ip)
print(f"Received arc length data: {arc_length_data}")
