from .udp_sender import UDPSender
import struct


class Parser:
    def __init__(self):
        self.input_file = ""

    # takes in processed file
    # returns x and y coordinate list in integers base 10
    def extract_coordinates_dual(self, input_file):
        x1, y1, x2, y2 = [], [], [], []

        with open(input_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('X1_rom'):
                    parts = line.split(';')
                    x1_val = parts[0].split("16'h")[1]
                    y1_val = parts[1].split("16'h")[1]
                    x2_val = parts[2].split("16'h")[1]
                    y2_val = parts[3].split("16'h")[1].replace(';', '')

                    x1.append(int(x1_val, 16))
                    y1.append(int(y1_val, 16))
                    x2.append(int(x2_val, 16))
                    y2.append(int(y2_val, 16))
        return x1, y1, x2, y2
    

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
        # print(result)
        
        

        extended_val = int(result, 2)
        # print(extended_val)
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


def main():
    parser = Parser()
    x1_list, y1_list, x2_list, y2_list = parser.extract_coordinates_dual("output/v_output.txt")
    payload_list = parser.convert_to_payload(x1_list, y1_list, x2_list, y2_list)
    print(payload_list)
    udp_socket = UDPSender()
    udp_socket.send_loop(payload_list)




if __name__ == "__main__":
    main()