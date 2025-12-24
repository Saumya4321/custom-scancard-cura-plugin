import matplotlib.pyplot as plt

# Read your .txt file
with open('output/transformed_coords.txt', 'r') as f:
    lines = f.readlines()

# Parse coordinates
points = []
for line in lines:
    line = line.strip()
    if line.startswith('(') and line.endswith(')'):
        coords = line[1:-1].split(',')
        x = int(coords[0].strip())
        y = int(coords[1].strip())
        points.append((x, y))

# Plot segments (pairs of consecutive points)
plt.figure(figsize=(10, 10))

# Draw each segment separately
for i in range(0, len(points) - 1, 2):  # Step by 2 to get pairs
    if i + 1 < len(points):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        plt.plot([x1, x2], [y1, y2], 'b-', linewidth=0.5)

plt.axhline(y=32768, color='r', linestyle='--', alpha=0.3, label='Center Y=32768')
plt.axvline(x=32768, color='r', linestyle='--', alpha=0.3, label='Center X=32768')
plt.gca().set_aspect('equal')
plt.grid(True, alpha=0.3)
plt.title('Galvo Coordinates')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.show()

print(f"Total points: {len(points)}")
print(f"Total segments: {len(points) // 2}")
xs = [p[0] for p in points]
ys = [p[1] for p in points]
print(f"X: {min(xs)} to {max(xs)}")
print(f"Y: {min(ys)} to {max(ys)}")