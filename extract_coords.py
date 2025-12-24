import re
import numpy as np
import ast
import os


def extract_layers_as_segments(gcode_text):
    """
    Returns layers as flat list of points where consecutive pairs form segments.
    Handles G1 moves without E values (continuous extrusion).
    
    Returns:
        dict: {layer_num: [(x1,y1), (x2,y2), (x3,y3), (x4,y4), ...]}
              Connect consecutive pairs: (x1,y1)→(x2,y2), (x3,y3)→(x4,y4), etc.
              Always even number of points - each pair is one line segment.
    """
    pattern_xy = re.compile(r'X(-?\d+\.?\d*)|Y(-?\d+\.?\d*)')
    pattern_z = re.compile(r'Z(-?\d+\.?\d*)')
    pattern_e = re.compile(r'E(-?\d+\.?\d*)')

    layers = {}
    current_layer = 0
    current_z = 0.0
    last_e = 0.0
    last_pos = None
    is_extruding_mode = False  # Track if we're in extrusion mode
    
    layers[current_layer] = []

    for line in gcode_text.splitlines():
        line = line.strip()

        if line.startswith(";LAYER:"):
            num = int(line.split(":")[1])
            current_layer = num
            layers.setdefault(current_layer, [])
            # Don't reset last_pos - position carries over from previous layer
            is_extruding_mode = False  # But reset extrusion mode
            continue

        z_match = pattern_z.search(line)
        if z_match:
            new_z = float(z_match.group(1))
            if new_z != current_z:
                current_z = new_z
                current_layer = int(round(new_z * 100))
                layers.setdefault(current_layer, [])
                last_pos = None
                is_extruding_mode = False
            continue

        # Track if this is G0 (travel) or G1 (potential extrusion)
        is_g0 = line.startswith("G0")
        is_g1 = line.startswith("G1")
        
        if not (is_g0 or is_g1):
            continue

        x = y = e = None
        for match in pattern_xy.findall(line):
            if match[0]:
                x = float(match[0])
            if match[1]:
                y = float(match[1])
        
        e_match = pattern_e.search(line)
        if e_match:
            e = float(e_match.group(1))

        if x is not None or y is not None:
            if last_pos:
                x = x if x is not None else last_pos[0]
                y = y if y is not None else last_pos[1]
            
            if x is not None and y is not None:
                current_pos = (x, y)
                
                # Determine if this specific move is extruding
                this_move_extrudes = False
                
                if is_g0:
                    # G0 is always travel
                    is_extruding_mode = False
                    this_move_extrudes = False
                elif is_g1:
                    if e is not None and e > last_e:
                        # G1 with E increasing - definitely extruding
                        is_extruding_mode = True
                        this_move_extrudes = True
                    elif e is not None and e <= last_e:
                        # G1 with E not increasing - stop extruding
                        is_extruding_mode = False
                        this_move_extrudes = False
                    else:
                        # G1 with no E value - use current mode
                        this_move_extrudes = is_extruding_mode
                
                # Add segment if this move extrudes
                if this_move_extrudes and last_pos is not None:
                    layers[current_layer].append(last_pos)
                    layers[current_layer].append(current_pos)
                
                last_pos = current_pos
                if e is not None:
                    last_e = e

    return layers

def save_layers_to_txt(layers, output_dir="layers_output"):
    # Create output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Sort layers by layer index
    for layer_num in sorted(layers.keys()):
        coords = layers[layer_num]

        # Skip empty layers
        if not coords:
            continue

        # # DEBUG: Check layer 15 before interpolation
        # if layer_num == 15:
        #     print(f"\nLayer 15 BEFORE interpolation: {len(coords)} points")
        #     # Check if middle diagonal points are there
        #     for i in range(0, len(coords)-1, 2):
        #         if abs(coords[i+1][0] - 40.76) < 0.1 and abs(coords[i+1][1] - 59.239) < 0.1:
        #             return (f"  Found middle diagonal segment: {coords[i]} -> {coords[i+1]}")

        # Build file path
        filename = os.path.join(output_dir, f"layer_{layer_num}.txt")
        
        coords = interpolate_path(coords, resolution=0.3)

        # DEBUG: Check layer 15 after interpolation
        # if layer_num == 15:
        #     print(f"Layer 15 AFTER interpolation: {len(coords)} points")
        #     # Check if middle diagonal points survived
        #     found_diagonal = False
        #     for i in range(0, len(coords)-1, 2):
        #         if abs(coords[i+1][0] - 40.76) < 0.1 and abs(coords[i+1][1] - 59.239) < 0.1:
        #             found_diagonal = True
        #             break
        #     return (f"  Middle diagonal still present: {found_diagonal}")

        # Save only coordinate pairs
        with open(filename, "w") as f:
                f.write(str(coords))

    print("All layers saved successfully!")

def load_coords_from_file(path):
   
    with open(path, "r") as f:
        return ast.literal_eval(f.read().strip())


def save_coords_to_txt(path, coords):
    with open(path, "w") as f:
        f.write(str(coords))

def interpolate_line(x1, y1, x2, y2, resolution=0.3):
    """Same as before - no changes needed"""
    length = np.hypot(x2 - x1, y2 - y1)

    if length == 0:
        return [(x1, y1)]

    num_points = int(length / resolution) + 1
    t = np.linspace(0, 1, num_points)

    x_vals = x1 + t * (x2 - x1)
    y_vals = y1 + t * (y2 - y1)

    return [(float(round(x, 5)), float(round(y, 5)))
            for x, y in zip(x_vals, y_vals)]


def interpolate_path(point_list, resolution=0.3):
    final_segments = []

    for i in range(0, len(point_list) - 1, 2):
        x1, y1 = point_list[i]
        x2, y2 = point_list[i + 1]

        seg = interpolate_line(x1, y1, x2, y2, resolution)
        
        # Convert each segment to pairs
        for j in range(len(seg) - 1):
            final_segments.append(seg[j])      # Start point
            final_segments.append(seg[j + 1])  # End point

    return final_segments