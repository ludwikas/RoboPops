with open(r'D:\TU Delft\_CORE\RoboPops\URscript.txt', "r") as file:
    urscript_code = file.readlines()  #Reads lines into a list

def urscript_to_python(urscript_code):  #Input: a list of strings - each string being a line from the URscript
    python_lines = []
    python_lines.append("import urx")
    python_lines.append("import socket")
    python_lines.append("robot_id = '192.168.177.128'")
    python_lines.append("robot = urx.Robot(robot_id)")

    for line in urscript_code:
        line = line.strip()
        if not line:
            continue

        if "def" in line:
            python_lines.append("# Start of the program")
        elif "set_tcp" in line and "=" in line:  #Extract TCP values
            tcp_values = line.split('=')[1].strip()
            python_lines.append(f"robot.set_tcp({tcp_values})")
        elif "set_payload" in line and "=" in line:  #Extract payload value
            payload_v = line.split('=')[1].strip()
            python_lines.append(f"robot.set_payload({payload_v})")
        elif "movej" in line:
            move_params = line.split('(', 1)[1].rstrip(')')
            move_params = move_params.replace("a=", "acc==").replace("v=", "vel==").replace("r=", "radius==")
            python_lines.append(f"robot.movej([{move_params}])")
        elif "movel" in line:
            move_params = line.split('(', 1)[1].rstrip(')')
            move_params = move_params.replace("a=", "acc==").replace("v=", "vel==").replace("r=", "radius==")
            python_lines.append(f"robot.movel([{move_params}])")
        elif "end" in line:
            python_lines.append("# End of the program")
    
    python_lines.append("robot.close()")

    return python_lines

#Convert URScript to Python
python_lines = urscript_to_python(urscript_code)

#Output the Python code
for line in python_lines:
    print(line)

newfile = r"D:\TU Delft\_CORE\RoboPops\L_python_translation.py" #Add an r before the string to treat it as a raw string, which tells Python not to interpret backslashes as escape sequences
with open(newfile, "w") as file:    
    for i in python_lines:
        file.write(i +"\n")