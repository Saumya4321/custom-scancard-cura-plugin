import re

class GCodeParser:
    def __init__(self):
        pass

    def extract_layers_as_segments(self, gcode_text):
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


