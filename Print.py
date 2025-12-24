from UM.Extension import Extension
from UM.Logger import Logger
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import os
from UM.Application import Application
from .extract_coords import *
from .transform import Transform
from .verilog_converter import VerilogConverter
from .parser import Parser
from .udp_sender import UDPSender

class Print(Extension):
    def __init__(self):
        super().__init__()
        self.addMenuItem("Send to scancard", self.print_process)
        self.addMenuItem("Test Layer Slider", self.test_layer_slider) 
        Logger.log("d", "[PrintPlugin] Initialized successfully")
        self.Logger = Logger
        self.transform_function = Transform()

    def test_layer_slider(self):
        """Test layer slider access"""
        Logger.log("d", "[FinalPlugin] Testing layer slider access...")
        
        results = []
        
        try:
        
            app = Application.getInstance()
            controller = app.getController()
            
            # Test 1: Get active view
            active_view = controller.getActiveView()
            view_name = active_view.getPluginId() if active_view else "None"
            results.append(f"Active View: {view_name}")
            Logger.log("d", f"Active view: {view_name}")
            
            # Test 2: Get the actual SimulationView object
            simulation_view = controller.getActiveView()
            results.append(f"Got active view object: {type(simulation_view)}")
            
            # Test 3: Check SimulationView attributes and methods
            if simulation_view and view_name == "SimulationView":
                # List all methods with 'layer' in the name
                layer_attrs = [attr for attr in dir(simulation_view) 
                            if 'layer' in attr.lower() and not attr.startswith('_')]
                results.append(f"Layer-related attributes: {', '.join(layer_attrs)}")
                Logger.log("d", f"Layer attributes: {layer_attrs}")
                
                # Test getting current layer
                get_methods = ['getCurrentLayer', 'currentLayer', 'getLayer', 
                            'current_layer', 'getMinimumLayer', 'getMaximumLayer']
                for method_name in get_methods:
                    if hasattr(simulation_view, method_name):
                        try:
                            attr = getattr(simulation_view, method_name)
                            if callable(attr):
                                value = attr()
                            else:
                                value = attr
                            results.append(f"✓ {method_name}: {value}")
                            Logger.log("d", f"{method_name} = {value}")
                        except Exception as e:
                            results.append(f"✗ {method_name} error: {e}")
                
                # Test setting layer
                set_methods = ['setLayer', 'setCurrentLayer', 'set_current_layer']
                for method_name in set_methods:
                    if hasattr(simulation_view, method_name):
                        try:
                            method = getattr(simulation_view, method_name)
                            method(10)
                            results.append(f"✓ {method_name}(10) SUCCESS!")
                            Logger.log("d", f"{method_name}(10) worked!")
                        except Exception as e:
                            results.append(f"✗ {method_name}(10) error: {e}")
                            Logger.log("w", f"{method_name} error: {e}")
            
            # Test 4: Find sliders in UI
            from PyQt6.QtWidgets import QSlider
            main_window = app.getMainWindow()
            if main_window:
                sliders = main_window.findChildren(QSlider)
                results.append(f"\nFound {len(sliders)} QSlider widgets")
                
                for i, slider in enumerate(sliders[:5]):  # First 5 sliders
                    obj_name = slider.objectName() or "unnamed"
                    results.append(f"  Slider {i} ({obj_name}): {slider.minimum()}-{slider.maximum()}, value={slider.value()}")
                    Logger.log("d", f"Slider {i}: {obj_name}, range=[{slider.minimum()},{slider.maximum()}], value={slider.value()}")
        
        except Exception as e:
            results.append(f"ERROR: {e}")
            Logger.logException("e", "[FinalPlugin] Test error")
            import traceback
            results.append(f"Traceback: {traceback.format_exc()}")
        
        # Show results
        result_text = "\n".join(results)
        QMessageBox.information(None, "Layer Slider Test", result_text)
        Logger.log("d", f"Test results:\n{result_text}")
       
    def update_layer_preview(self, layer_number):
        """Update Cura's preview to show the layer that was just printed"""
        try:
            app = Application.getInstance()
            controller = app.getController()
            
            # Get the active view
            active_view = controller.getActiveView()
            
            if active_view and hasattr(active_view, 'setLayer'):
                # Set the layer in the preview
                active_view.setLayer(layer_number)
                
                # Force UI to update immediately
                app.processEvents()
                
                Logger.log("d", f"[PrintPlugin] Preview updated to show layer {layer_number}")
            else:
                Logger.log("w", "[PrintPlugin] Preview not available - user may not be in Preview mode")
                
        except Exception as e:
            Logger.log("w", f"[PrintPlugin] Could not update preview: {e}")

               
    def print_process(self):
        try:
            app = Application.getInstance()
            controller = app.getController()
            scene = controller.getScene()

            # Cura stores G-code here after slicing
            gcode_dict = getattr(scene, "gcode_dict", None)

            if not gcode_dict:
                QMessageBox.warning(None, "Print Plugin",
                                    "Please slice the model first.")
                return
            
            # Usually extruder 0
            gcode_text = gcode_dict.get(0, "")

            if not gcode_text:
                QMessageBox.warning(None, "Print Plugin",
                                    "No G-code found after slicing.")
                return
            
            if isinstance(gcode_text, list):
                gcode_text = "".join(gcode_text)
            
            plugin_dir = os.path.dirname(__file__)
            output_path = os.path.join(plugin_dir, "gcode.txt")
            with open(output_path, "w") as debug_file:
                debug_file.write(gcode_text)
            

            Logger.log("d", f"{gcode_text[:100]}")  # Log first 100 characters for debugging

            raw_coords = extract_layers_as_segments(gcode_text)
            if not raw_coords:
                QMessageBox.warning(None, "Print Plugin",
                                    "No valid coordinates found in G-code.")
                return
            x1,x2 = self.transform_function.compute_global_bounds(raw_coords)
            Logger.log("d", f"[PrintPlugin] Canvas_width: {x1} || Canvas_height: {x2}]]")

            # Ask for save location
            save_path, _ = QFileDialog.getSaveFileName(
                None, "Save Geometry", "", "Text Files (*.txt)"
            )
            if not save_path:
                return
            
            output_dir=os.path.dirname(save_path)
            save_layers_to_txt(raw_coords, output_dir)

            i = 0
            for filename in sorted(os.listdir(output_dir)):
                if filename.startswith("layer_") and filename.endswith(".txt"):
                    filepath = os.path.join(output_dir, filename)
                    i += 1
                    coords = load_coords_from_file(filepath)
                    transformed_coords = self.transform_function.transforming(coords, layer_num = i)
                    # Logger.log("d", f"[HERE] {transformed_coords}")
                    formatted = self.transform_function.convert_to_string(transformed_coords)

                    Logger.log("d", f"[PrintPlugin] Parsed {len(coords)} coordinates of layer {i}")

                    # Step 2. Convert to Verilog format
                    verilog_converter = VerilogConverter()
                    coords = verilog_converter.extract_coordinates(formatted)
                    scaled = verilog_converter.no_normalize_and_scale(coords)

                    plugin_dir = os.path.dirname(__file__)
                    output_path = os.path.join(plugin_dir, "output", "verilog_layer_1.txt")
                    verilog_converter.get_verilog_file(
                        len(scaled), scaled, scaled, output_path
                    )

                    # Step 3. Build and send UDP payloads
                    parser = Parser()
                    x1, y1, x2, y2 = parser.extract_coordinates_dual(output_path)
                    payload_list = parser.convert_to_payload(x1, y1, x2, y2)

                    udp_socket = UDPSender(self)
                    udp_socket.send_loop(payload_list)
                    udp_socket.close()

                    Logger.log("d", f"[PrintPlugin] Sent {len(payload_list)} UDP payloads of layer {i} to scan card")
                
                    self.update_layer_preview(i)
                    
                    reply = QMessageBox.question(
                        None,
                        "Print Plugin",
                        f"Sent {len(payload_list)} UDP payloads of layer {i} to scan card. \nContinue to next layer?"
                    )
            

                    if reply == 65536:
                        Logger.log("d", f"[PrintPlugin] User cancelled the print job.")
                        QMessageBox.information(None, "Print Plugin", "Print job cancelled by user.")
                        return  # User cancelled
        

            QMessageBox.information(None, "Print Plugin",
                                    "Print job finished!")

        

        except Exception as e:
            Logger.logException("e", "[PrintPlugin] Error while printing file")
            QMessageBox.critical(None, "Print Plugin", str(e))

