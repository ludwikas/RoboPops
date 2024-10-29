import matplotlib.pyplot as plt
import re

# Function to parse a line and extract the first two coordinates after ':['
def extract_coordinates(line):
    # Find the part after ':[' and extract the first two numbers
    values = re.findall(r'\[([-+]?\d*\.\d+), ([-+]?\d*\.\d+), ([-+]?\d*\.\d+)', line)
    if values:
        # Convert the first match to floats (ignore the z value)
        return [float(values[0][0]), float(values[0][1])]
    else:
        return None  # Return None if the pattern is not found

# Read and process the file
filename = 'TCPs_sequential_idx.txt'  # Update with your file path if needed
marker_poses = []

with open(filename, 'r') as file:
    for line in file:
        coords = extract_coordinates(line)
        if coords:  # Only add if coordinates were extracted correctly
            marker_poses.append(coords)
            print(f"Read coordinates: {coords}")  # Output the coordinates as they are read

# Extracting x and y coordinates
x_coords = [pose[0] for pose in marker_poses]
y_coords = [pose[1] for pose in marker_poses]

# Creating a 2D plot
fig, ax = plt.subplots()

# Plotting the points and adding lines between each successive point
ax.scatter(x_coords, y_coords, c='b', marker='o')
ax.plot(x_coords, y_coords, color='black', linestyle='-', linewidth=1)

# Adding labels to each point
for i, (x, y) in enumerate(marker_poses, start=1):
    ax.text(x, y, f'{i}', color='red')

# Setting labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Plot of the points in 2D (X, Y)')

plt.show()
