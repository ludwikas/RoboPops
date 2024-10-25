import numpy as np
import re

# Function to extract Cartesian speeds from the file
def extract_cartesian_speeds(file_path_speed):
    pattern = r'Speed: \[([\d\.\-e]+), ([\d\.\-e]+), ([\d\.\-e]+),'
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
            file.write(f"{speed}\n")  # Write each speed on a new line

### really helpfull for callin the modules properly later(blocks unwanted authorization)
if __name__ == "__main__":
    file_path_speed = "interval_speeds.txt"
    output_file_path_lspeed = "Linear_speeds.txt"
    
    # Extract Cartesian speeds from the file
    cartesian_speeds = extract_cartesian_speeds(file_path_speed)
    
    # Calculate linear speeds from the Cartesian speeds
    v_linear = calculate_linear_speeds(cartesian_speeds)
    
    # Write the calculated linear speeds to the output file
    write_speeds_in_file(v_linear, output_file_path_lspeed)


#speed1 = np.array([0.02393271659621, 0.04554902918299161, -0.09238083703797023])
#v_linear = np.linalg.norm(speed1)
#print(f"Linear speed 1: {round(v_linear, 3)} m/s")