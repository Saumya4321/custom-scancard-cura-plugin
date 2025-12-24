import os
import numpy as np

class PathPlanner:
    def __init__(self):
        pass

    def interpolate_line(self, x1, y1, x2, y2, resolution=0.3):
        
        length = np.hypot(x2 - x1, y2 - y1)
        if length == 0:
            return [(x1, y1)]

        num_points = int(length / resolution) + 1
        t = np.linspace(0, 1, num_points)

        x_vals = x1 + t * (x2 - x1)
        y_vals = y1 + t * (y2 - y1)

        return [(float(round(x, 5)), float(round(y, 5)))
                for x, y in zip(x_vals, y_vals)]


    def interpolate_path(self, point_list, resolution=0.3):
        final_segments = []

        for i in range(0, len(point_list) - 1, 2):
            x1, y1 = point_list[i]
            x2, y2 = point_list[i + 1]

            seg = self.interpolate_line(x1, y1, x2, y2, resolution)
            
            # Convert each segment to pairs
            for j in range(len(seg) - 1):
                final_segments.append(seg[j])      # Start point
                final_segments.append(seg[j + 1])  # End point

        return final_segments


    def save_layers_to_txt(self, layers, output_dir="layers_output"):
        # Create output folder if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Sort layers by layer index
        for layer_num in sorted(layers.keys()):
            coords = layers[layer_num]

            # Skip empty layers
            if not coords:
                continue

            # Build file path
            filename = os.path.join(output_dir, f"layer_{layer_num}.txt")
            
            coords = self.interpolate_path(coords, resolution=0.3)
            # Save only coordinate pairs
            with open(filename, "w") as f:
                    f.write(str(coords))

        print("All layers saved successfully!")