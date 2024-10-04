import re
import numpy as np

# Function to extract TCP positions from the URScript output
def extract_tcp_positions(file_path):
    tcp_positions = []
    tcp_pattern = r'TCP Pose: ([-0-9., ]+), ([-0-9., ]+), ([-0-9., ]+), ([-0-9., ]+), ([-0-9., ]+), ([-0-9., ]+)'  # Updated regex to match TCP Pose outputs

    # Open and read the URScript output file line by line
    with open(file_path, 'r') as file:
        for line in file:
            print(f"Reading line: {line.strip()}")  # Debug: Print each line to check the actual content
            match = re.search(tcp_pattern, line)
            if match:
                # Extract the TCP positions as a list of floats
                positions = list(map(float, match.groups()))  # Extract all matched groups as floats
                # Only take the first three values (x, y, z) for 3D Cartesian arc length
                tcp_positions.append(positions[:3])
                print(f"Extracted TCP Position: {positions[:3]}")  # Debug: Check extracted positions
    print(f"Total TCP Positions Extracted: {len(tcp_positions)}")  # Debug: Total positions extracted
    return tcp_positions


# Function to calculate the Euclidean distance between consecutive TCP positions (arc length)
def calculate_tcp_arc_lengths(tcp_positions):
    arc_lengths = []
    for i in range(1, len(tcp_positions)):
        pos1 = np.array(tcp_positions[i-1])
        pos2 = np.array(tcp_positions[i])
        # Calculate Euclidean distance in 3D space (x, y, z)
        arc_length = np.linalg.norm(pos2 - pos1)
        arc_lengths.append(arc_length)
        print(f"Calculated Arc Length {i}: {arc_length:.6f}")  # Debug: Check calculated arc length
    return arc_lengths

# Function to write the calculated arc lengths to a new file
def write_arc_lengths_to_file(arc_lengths, output_file):
    with open(output_file, 'w') as file:
        for i, arc_length in enumerate(arc_lengths):             
            file.write(f"Arc Length {i+1}: {arc_length:.6f}\n")  # 6 decimal places for precision
    print(f"Arc lengths written to {output_file}")

# Main function
def process_tcp_and_calculate_arcs(tcp_file, output_file):
    tcp_positions = extract_tcp_positions(tcp_file)  # Step 1: Extract TCP positions
    if not tcp_positions:
        print("No TCP positions found! Please check the input file.")
        return
    arc_lengths = calculate_tcp_arc_lengths(tcp_positions)  # Step 2: Calculate arc lengths
    write_arc_lengths_to_file(arc_lengths, output_file)  # Step 3: Write arc lengths to file

# Example usage:
tcp_file = 'URscript.txt'   # Input file containing TCP poses
output_file = 'arc_lengths.txt'  # Output file for arc lengths

process_tcp_and_calculate_arcs(tcp_file, output_file)
