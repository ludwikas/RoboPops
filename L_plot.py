import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# Function to parse a line and extract the first three coordinates after ':['
def extract_coordinates(line):
    # Find the part after ':[' and extract numbers
    values = re.findall(r'\[([-+]?\d*\.\d+), ([-+]?\d*\.\d+), ([-+]?\d*\.\d+)', line)
    if values:
        # Convert the first match to floats
        return [float(val) for val in values[0]]
    else:
        return None  # Return None if the pattern is not found

# Read and process the file
filename = 'URscript.txt'  # Update with your file path if needed
marker_poses = []

with open(filename, 'r') as file:
    for line in file:
        coords = extract_coordinates(line)
        if coords:  # Only add if coordinates were extracted correctly
            marker_poses.append(coords)
            print(f"Read coordinates: {coords}")  # Output the coordinates as they are read

# Extracting x, y, and z coordinates
x_coords = [pose[0] for pose in marker_poses]
y_coords = [pose[1] for pose in marker_poses]
z_coords = [pose[2] for pose in marker_poses]

# Creating a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plotting the points and adding lines between each successive point
ax.scatter(x_coords, y_coords, z_coords, c='b', marker='o')
ax.plot(x_coords, y_coords, z_coords, color='black', linestyle='-', linewidth=1)

# Adding labels to each point
for i, (x, y, z) in enumerate(marker_poses, start=1):
    ax.text(x, y, z, f'Pose {i}', color='red')

# Setting labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('PLot of the points')

plt.show()
