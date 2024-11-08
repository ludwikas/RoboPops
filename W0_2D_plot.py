import matplotlib.pyplot as plt
import re

def extract_coordinates(line):
    values = re.findall(r'\[([-+]?\d*\.\d+), ([-+]?\d*\.\d+), ([-+]?\d*\.\d+)', line)
    if values:
        # Convert the first match to floats (ignore the z value)
        return [float(values[0][0]), float(values[0][1])]
    else:
        return None  # Return None if the pattern is not found

# Read and process the file
filename = 'TCPs_with_markers.txt'  
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

# Creating a 2D plot with a square aspect ratio
fig, ax = plt.subplots(figsize=(6, 6))  # Set figure size to square

# Plotting the points and adding lines between each successive point
scatter = ax.scatter(x_coords, y_coords, c='b', marker='o', label='TCP points')  # Add label for the legend
ax.plot(x_coords, y_coords, color='black', linestyle='-', linewidth=1)

# Adding labels to each point with smaller font size
for i, (x, y) in enumerate(marker_poses, start=1):
    ax.text(x, y, f'{i}', color='red', fontsize=8)  # Adjust fontsize here

# Adding the legend
ax.legend()

# set labels and title
ax.set_xlabel('X coordinates')
ax.set_ylabel('Y coordinates')
ax.set_title('TCP point coordinates (X, Y)')

# display plot
plt.show()