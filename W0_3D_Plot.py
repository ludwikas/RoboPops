import matplotlib.pyplot as plt
import re
from mpl_toolkits.mplot3d import Axes3D

def extract_coordinates(line):
    values = re.findall(r'\[([-+]?\d*\.\d+), ([-+]?\d*\.\d+), ([-+]?\d*\.\d+)', line)
    if values:
        # Convert the match to floats (including z value)
        return [float(values[0][0]), float(values[0][1]), float(values[0][2])]
    else:
        return None


filename = 'TCPs_with_markers.txt'
marker_poses = []

with open(filename, 'r') as file:
    for line in file:
        coords = extract_coordinates(line)
        if coords:  
            marker_poses.append(coords)
            print(f"Read coordinates: {coords}")  

x_coords = [pose[0] for pose in marker_poses]
y_coords = [pose[1] for pose in marker_poses]
z_coords = [pose[2] for pose in marker_poses]
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x_coords, y_coords, z_coords, c='b', marker='o')
ax.plot(x_coords, y_coords, z_coords, color='black', linestyle='-', linewidth=1)

for i, (x, y, z) in enumerate(marker_poses, start=1):
    ax.text(x, y, z, f'{i}', color='red')


ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Perspective Plot of the Points (X, Y, Z)')
ax.view_init(elev=30, azim=45) 
ax.set_zlim(min(z_coords) + 0, max(z_coords) + 0.025)  
plt.show()
