from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from UM.Logger import Logger
import os

class PrintWorker(QObject):
    progress_layer = pyqtSignal(int)
    progress_updated = pyqtSignal(int, int)  # current_layer, total_layers
    finished = pyqtSignal()
    error = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, pipeline, gcode, output_dir):
        super().__init__()
        self.pipeline = pipeline
        self.gcode = gcode
        self.output_dir = output_dir
        self._stop_requested = False
        Logger.log("d", "[PrintWorker] Initialized")

    @pyqtSlot()
    def run(self):
        Logger.log("d", "[PrintWorker] Run method started")
        try:
            # Process gcode
            Logger.log("d", "[PrintWorker] Processing gcode")
            raw_coords = self.pipeline.process_gcode(self.gcode, self.output_dir)
            
            if not raw_coords:
                Logger.log("e", "[PrintWorker] No valid coordinates found")
                self.error.emit("No valid coordinates found.")
                return

            if self._stop_requested:
                Logger.log("d", "[PrintWorker] Stop requested after gcode processing")
                self.cancelled.emit()
                return
            
            Logger.log("d", f"[PrintWorker] Gcode processed, checking output directory: {self.output_dir}")

            # Check if directory exists
            if not os.path.exists(self.output_dir):
                Logger.log("e", f"[PrintWorker] Output directory does not exist: {self.output_dir}")
                self.error.emit(f"Output directory does not exist: {self.output_dir}")
                return

            # Get sorted layer files
            layer_files = []
            for filename in os.listdir(self.output_dir):
                if filename.startswith("layer_") and filename.endswith(".txt"):
                    layer_files.append(filename)
            
            layer_files.sort()
            total_layers = len(layer_files)
            Logger.log("d", f"[PrintWorker] Found {total_layers} layer files")

            if not layer_files:
                Logger.log("e", "[PrintWorker] No layer files found")
                self.error.emit("No layer files found in output directory.")
                return

            # Process each layer
            for i, filename in enumerate(layer_files, start=1):
                if self._stop_requested:
                    Logger.log("d", f"[PrintWorker] Stop requested at layer {i}")
                    self.cancelled.emit()
                    return  # Exit cleanly

                Logger.log("d", f"[PrintWorker] Processing layer {i}: {filename}")
                filepath = os.path.join(self.output_dir, filename)
                
                try:
                    # Check before payload generation
                    if self._stop_requested:
                        Logger.log("d", f"[PrintWorker] Stop requested before layer {i}")
                        self.cancelled.emit()
                        return  # Exit cleanly
                    
                    payload = self.pipeline.generate_payloads(filepath, i)
                    
                    if self._stop_requested:
                        Logger.log("d", f"[PrintWorker] Stop requested after payload generation for layer {i}")
                        self.cancelled.emit()
                        return  # Exit cleanly
                    
                    # Pass the stop flag checker to udp_send if possible
                    result = self.pipeline.udp_send(payload, stop_check=lambda: self._stop_requested)
                    
                    # Check if UDP send was interrupted
                    if self._stop_requested or result == False:
                        Logger.log("d", f"[PrintWorker] Stop requested after UDP send for layer {i}")
                        self.cancelled.emit()
                        return  # Exit cleanly
                    
                    Logger.log("d", f"[PrintWorker] Layer {i} sent via UDP")
                    
                    # Emit progress signals
                    self.progress_layer.emit(i - 1)  # 0-based index for layer preview
                    self.progress_updated.emit(i, total_layers)  # 1-based for progress bar
                    
                except Exception as layer_error:
                    Logger.log("e", f"[PrintWorker] Error processing layer {i}: {layer_error}")
                    self.error.emit(f"Error processing layer {i}: {str(layer_error)}")
                    return

            Logger.log("d", "[PrintWorker] All layers processed successfully")
            self.finished.emit()

        except Exception as e:
            Logger.logException("e", "[PrintWorker] Unexpected error in run()")
            self.error.emit(str(e))

    def stop(self):
        Logger.log("d", "[PrintWorker] Stop requested")
        self._stop_requested = True