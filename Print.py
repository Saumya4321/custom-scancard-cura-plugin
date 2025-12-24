from UM.Extension import Extension
from UM.Logger import Logger
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from UM.Application import Application
from .print_pipeline import PrintPipeline
import os

class Print(Extension):
    def __init__(self):
        super().__init__()
        self.addMenuItem("Send to scancard", self.print_process)
        self.Logger = Logger
        self.print_pipeline = PrintPipeline()
        self.app = Application.getInstance()
        self.controller = self.app.getController()
        self.scene = self.controller.getScene()
        self.Logger.log("d", "[PrintPlugin] Initialized successfully")
       
    def update_layer_preview(self, layer_number):
        """Update Cura's preview to show the layer that was just printed"""
        try:
            # Get the active view
            active_view = self.controller.getActiveView()
            
            if active_view and hasattr(active_view, 'setLayer'):
                # Set the layer in the preview
                active_view.setLayer(layer_number)
                
                # Force UI to update immediately
                self.app.processEvents()
                
                Logger.log("d", f"[PrintPlugin] Preview updated to show layer {layer_number}")
            else:
                Logger.log("w", "[PrintPlugin] Preview not available - user may not be in Preview mode")
                
        except Exception as e:
            Logger.log("w", f"[PrintPlugin] Could not update preview: {e}")

    def extract_gcode(self):
        # Cura stores G-code here after slicing
        gcode_dict = getattr(self.scene, "gcode_dict", None)

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
            gcode_list = "".join(gcode_text)
        
        # store gcode text for debugging
        plugin_dir = os.path.dirname(__file__)
        output_path = os.path.join(plugin_dir, "gcode.txt")
        with open(output_path, "w") as debug_file:
            debug_file.write(gcode_list)

        return gcode_list
        
               
    def print_process(self):
        try:
            self.update_layer_preview(0)

            # take user input for saving directory
            save_path, _ = QFileDialog.getSaveFileName(
                None, "Save Geometry", "", "Text Files (*.txt)"
            )
            if not save_path:
                return
            
            output_dir=os.path.dirname(save_path)

            gcode = self.extract_gcode()
      
            raw_coords = self.print_pipeline.process_gcode(gcode, output_dir)
            Logger.log("d", f"{gcode[:100]}")  # Log first 100 characters for debugging

            if not raw_coords:
                QMessageBox.warning(None, "Print Plugin",
                                    "No valid coordinates found in G-code.")
                return
            
            
            i = 0
            for filename in sorted(os.listdir(output_dir)):
                if filename.startswith("layer_") and filename.endswith(".txt"):
                    filepath = os.path.join(output_dir, filename)
                    i += 1
                    payload = self.print_pipeline.generate_payloads(filepath, i)
                    Logger.log("d", f"[PrintPlugin] Payload generated")
                    Logger.log("d", f"[PrintPlugin] Streaming via UDP...")
                    self.print_pipeline.udp_send(payload)

                    Logger.log("d", f"[PrintPlugin] Sent {len(payload)} UDP payloads of layer {i} to scan card")
            
                    self.update_layer_preview(i-1)
                
                    reply = QMessageBox.question(
                    None,
                    "Print Plugin",
                    f"Sent {len(payload)} UDP payloads of layer {i} to scan card. \nContinue to next layer?"
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

