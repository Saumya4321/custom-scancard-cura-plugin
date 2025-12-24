from .gcode_parser import GCodeParser
from .galvo_transformer import GalvoTransformer
from .packetisation import Packetizer
from .udp_sender import UDPSender
from .interpolation_module import PathPlanner
from .packetisation import Packetizer

class PrintPipeline:
    def __init__(self):
        self.gcode_parser = GCodeParser()
        self.transformer = GalvoTransformer()
        self.interpolator = PathPlanner()
        self.packetizer = Packetizer()

    def process_gcode(self, gcode_text, output_dir):
        raw_coords = self.gcode_parser.extract_layers_as_segments(gcode_text)
        self.interpolator.save_layers_to_txt(raw_coords, output_dir)
        x1,x2 = self.transformer.compute_global_bounds(raw_coords)
        return raw_coords

    def generate_payloads(self, filepath, layer_idx):
        
        coords = self.transformer.load_coords_from_file(filepath)
        transformed = self.transformer.transforming(coords, layer_idx)
        formatted = self.transformer.convert_to_string(transformed)
        coords = self.packetizer.extract_coordinates(formatted)
        scaled = self.packetizer.no_normalize_and_scale(coords)
        x1, y1, x2, y2 = self.packetizer.get_verilog_file(len(scaled), scaled, scaled)
        return self.packetizer.convert_to_payload(x1, y1, x2, y2)


    def udp_send(self, payload_list):
        udp_socket = UDPSender()
        udp_socket.send_loop(payload_list)
        udp_socket.close()