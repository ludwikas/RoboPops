import matplotlib.pyplot as plt
import re

def extract_coordinates(line):
    values = re.findall(r'\[([-+]?\d*\.\d+), ([-+]?\d*\.\d+), ([-+]?\d*\.\d+)', line)
    if values:
        # Convert the first match to floats (ignore the z value)
        return [float(values[0][0]), float(values[0][1])]
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
fig, ax = plt.subplots(figsize=(6, 6)) 
scatter = ax.scatter(x_coords, y_coords, c='b', marker='o', label='TCP points') 
ax.plot(x_coords, y_coords, color='black', linestyle='-', linewidth=1)

for i, (x, y) in enumerate(marker_poses, start=1):
    ax.text(x, y, f'{i}', color='red', fontsize=8)  

ax.legend()
ax.set_xlabel('X coordinates')
ax.set_ylabel('Y coordinates')
ax.set_title('TCP point coordinates (X, Y)')
plt.show()