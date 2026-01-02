import struct
import re
import os 

class Packetizer:
    def __init__(self):
        pass

    def extract_coordinates(self,gcode_text):
        coords = []
        current_x, current_y = None, None
        for line in gcode_text.splitlines():
            x_match = re.search(r'X([-+]?\d*\.?\d+)', line)
            y_match = re.search(r'Y([-+]?\d*\.?\d+)', line)

            if x_match:
                current_x = float(x_match.group(1))
            if y_match:
                current_y = float(y_match.group(1))

            if current_x is not None and current_y is not None:
                coords.append((current_x, current_y))
                current_x, current_y = None, None
        return coords



    def no_normalize_and_scale(self, coords, max_x_val = 1, max_y_val = 1):
        scaled = []
        for x, y in coords:
            norm_x = x / max_x_val
            norm_y = y / max_y_val
            scaled_x = round(norm_x * 1)
            scaled_y = round(norm_y * 1)
            scaled.append((scaled_x, scaled_y))                        ### Interchange (X,Y) for better viewing
        return scaled


    def get_verilog_file(self, max_len, left_scaled_wrapped, right_scaled_wrapped):
        # Format output
        lines = []
        x1_list = []
        x2_list = []
        y1_list = []
        y2_list = []
        for i in range(max_len):
            x1, y1 = left_scaled_wrapped[i]
            x2, y2 = right_scaled_wrapped[i]
            x1_hex = f"{x1 & 0xFFFF:04X}"
            y1_hex = f"{y1 & 0xFFFF:04X}"
            x2_hex = f"{x2 & 0xFFFF:04X}"
            y2_hex = f"{y2 & 0xFFFF:04X}"
            lines.append(f"X1_rom[{i:4}] <= 16'h{x1_hex}; Y1_rom[{i:4}] <= 16'h{y1_hex}; "f"X2_rom[{i:4}] <= 16'h{x2_hex}; Y2_rom[{i:4}] <= 16'h{y2_hex};")
            x1_list.append(x1)
            x2_list.append(x2)
            y1_list.append(y1)
            y2_list.append(y2)

    #   Save to file
        current_dir = os.path.dirname(__file__)
        output_file_path = os.path.join(current_dir, "output", "verilog_rom_format.txt")
        print(f"[DEBUG] Saving to file: {output_file_path}")
        with open(output_file_path, "w") as f:
            print(f"[DEBUG] Writing {len(lines)} lines to file.")
            f.write("\n".join(lines))
        
        return (x1_list, y1_list, x2_list, y2_list)

    # takes a list and converts its elements into 16 bit int data
    def convert_to_16bit(self,input_list):
        packed_list = []

        for x in input_list:
            packed = struct.pack('>H', x)  # 16-bit unsigned int
            packed_list.append(packed)
        return packed_list


    # takes: 2-byte packet and converts it into 21 bits
    def insert_zero_bits_16_to_21(self,packed_2bytes):
        value_16bit = int.from_bytes(packed_2bytes, byteorder='big', signed=False)
        bin_str = format(value_16bit, '016b')  # 16-bit binary string
        new_string = "00000"


        result = new_string + bin_str
        extended_val = int(result, 2)
        
        return extended_val


    # takes coordinate data and header and combines them into one packet
    def build_packet(self,header_11bit, payload_21bit):
        packet_32bit = (header_11bit << 21) | payload_21bit
        return packet_32bit.to_bytes(4, byteorder='little')


    # takes 4 packets and combines them into one payload
    def combine_packets(self,packets):
        if len(packets) != 4:
            raise ValueError("You must pass exactly 4 packets.")
    
    # Concatenate the 4 packets into one large byte object
        combined = b''.join(packets)

        # add tail 
        # Append 0xAA followed by two zero bytes
        combined += b'\xAA\x00\x00'
        return combined

    def convert_to_payload(self, x1, y1, x2, y2):
    
        header_left = 0b00000000000  #laser1
        header_right = 0b00000000000  #laser2

        x1_16 = self.convert_to_16bit(x1)
        y1_16 = self.convert_to_16bit(y1)
        x2_16 = self.convert_to_16bit(x2)
        y2_16 = self.convert_to_16bit(y2)


        x1_21 = [self.insert_zero_bits_16_to_21(val) for val in x1_16]
        y1_21 = [self.insert_zero_bits_16_to_21(val) for val in y1_16]
        x2_21 = [self.insert_zero_bits_16_to_21(val) for val in x2_16]
        y2_21 = [self.insert_zero_bits_16_to_21(val) for val in y2_16]

        x_left_packet = []
        x_right_packet = []
        y_left_packet = []
        y_right_packet = []

        x_left_packet = [self.build_packet(header_left, val) for val in x1_21]
        y_left_packet = [self.build_packet(header_left, val) for val in y1_21]
        x_right_packet = [self.build_packet(header_right, val) for val in x2_21]
        y_right_packet = [self.build_packet(header_right, val) for val in y2_21]

        payload = []

        for i in range(len(x_left_packet)):
            payload.append(self.combine_packets([x_left_packet[i], y_left_packet[i], x_right_packet[i],y_right_packet[i]]))

        return payload







