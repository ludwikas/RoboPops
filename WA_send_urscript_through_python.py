import socket

# function to send a .txt file (urscript as it is) straight to the robot controller
def send_urscript(file_path: str, robot_ip: str, port: int = 30002):
    

    with open(file_path, "r") as file:
        urscript = file.read()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((robot_ip, port))


    try:
        print("Sending URscript to the robot controller")
        s.sendall(urscript.encode("utf-8"))

        response = s.recv(1024).decode("utf-8")
        print("Respose fromm robot:", response)
    finally:
        s.close()
        print("Connection closed.")


file_path = "URscript.txt"
robot_ip = "192.168.177.128"

send_urscript(file_path, robot_ip)