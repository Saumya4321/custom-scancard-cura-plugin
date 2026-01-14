
import ast
import math
import os

class GalvoTransformer:
    def __init__(self):
        self.unit = 0 # what about the unit?
        self.coords = None
        self.canvas_width = 0
        self.canvas_height = 0
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0

    def compute_global_bounds(self, layers):
        all_x = []
        all_y = []
        
        for layer_data in layers.values():
            for item in layer_data:
                # Simple (x, y) tuple - no None values in segment format
                all_x.append(item[0])
                all_y.append(item[1])
        
        if not all_x:
            return ((0, 0), (0, 0))

        self.min_x = min(all_x)
        self.max_x = max(all_x)
        self.min_y = min(all_y)
        self.max_y = max(all_y)

        self.canvas_width = math.ceil(abs(self.max_x - self.min_x))
        self.canvas_height = math.ceil(abs(self.max_y - self.min_y))

        return self.canvas_width, self.canvas_height


    def transforming(self, coords, layer_num):
        self.coords = coords
    
        transformed_list = self.transform_points(self.coords, self.canvas_width, self.canvas_height)
       
    
        plugin_dir = os.path.dirname(__file__)
        output_path = os.path.join(plugin_dir, "output", "transformed_coords.txt")
        # save transformed list to a text file
        with open(output_path, "w") as f:
            for point in transformed_list:
                f.write(f"{point}\n")
        
        return transformed_list

    def transform_to_galvo_scaled(self, x, y, scale=2):
            x_offset = x - self.min_x
            y_offset = y - self.min_y

            # Step 1: Shift origin to center
            x_centered = x_offset - (self.canvas_width / 2)
            y_centered = y_offset - (self.canvas_height / 2)  # flip Y-axis

            # Step 2: Normalize to [-1, 1] based on half canvas size (no scale here)
            norm_factor_x = self.canvas_width / 2
            norm_factor_y = self.canvas_height / 2

            x_norm = x_centered / norm_factor_x
            y_norm = y_centered / norm_factor_y

            # y_norm = -y_norm  # ← Uncomment if needed

            # Step 3: Map normalized coords to full galvo range [0, 65536]
            X_full = x_norm * 32768 + 32768
            Y_full = y_norm * 32768 + 32768

            # Step 4: Scale down galvo coords by 'scale' (to reduce output range)
            X = int(32768 + (X_full - 32768) / scale)
            Y = int(32768 + (Y_full - 32768) / scale)

            return X, Y

    
    def transform_points(self,points, canvas_width, canvas_height, scale=2):
        transformed = []
        for x, y in points:
            X, Y = self.transform_to_galvo_scaled(x, y, scale)
            transformed.append((X, Y))
        return transformed

    def convert_to_string(self, transformed_points):
        formatted_string = '\n'.join(f"X{x}Y{y}" for x, y in transformed_points)
        return formatted_string

    def load_coords_from_file(self, path):
   
        with open(path, "r") as f:
            return ast.literal_eval(f.read().strip())
    

