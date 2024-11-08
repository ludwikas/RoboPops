import matplotlib.pyplot as plt
import re
from mpl_toolkits.mplot3d import Axes3D

# Function to parse a line and extract the first three coordinates after ':['
def extract_coordinates(line):
    # Find the part after ':[' and extract the first three numbers
    values = re.findall(r'\[([-+]?\d*\.\d+), ([-+]?\d*\.\d+), ([-+]?\d*\.\d+)', line)
    if values:
        # Convert the match to floats (including z value)
        return [float(values[0][0]), float(values[0][1]), float(values[0][2])]
    else:
        return None  # Return None if the pattern is not found

# Read and process the file
filename = 'TCPs_with_markers.txt'  # Update with your file path if needed
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
    ax.text(x, y, z, f'{i}', color='red')

# Setting labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Perspective Plot of the Points (X, Y, Z)')

# Set a perspective view angle
ax.view_init(elev=30, azim=45)  # Adjust elevation and azimuth for a better perspective view

# Set the scale for the z-axis
ax.set_zlim(min(z_coords) + 0, max(z_coords) + 0.025)  # Adjust limits as needed

plt.show()
