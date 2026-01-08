from UM.Extension import Extension
from UM.Logger import Logger
from UM.Application import Application
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from .print_pipeline import PrintPipeline
from .printView import printView
from .print_job_service import PrintJobService
import os

class PrintController(Extension):
    def __init__(self):
        super().__init__()
        self.addMenuItem("Send to scancard", self.print_process)
        self.Logger = Logger
        self.print_pipeline = PrintPipeline()
        self.printView = printView()
        self.app = Application.getInstance()
        self.controller = self.app.getController()
        self.scene = self.controller.getScene()
        self.active_view = self.controller.getActiveView()
        self.is_printing = False
        self.printView.cancel_requested.connect(self.cancel_print)
        self.job = PrintJobService(self.print_pipeline)
        
        self.job.progress_layer.connect(self.update_layer_preview)
        self.job.finished.connect(self.on_print_finished)
        self.job.error.connect(self.on_print_error)
        self.job.cancelled.connect(self.on_cancelled)
        
        self.Logger.log("d", "[PrintPlugin] Initialized successfully")


    def reset_layers(self):
        self.active_view = self.controller.getActiveView()
        self.active_view.setLayer(0)      
        self.active_view.setMinimumPath(0)
        self.active_view.setPath(0)      

    def cancel_print(self):
        """Request cancellation of the print job"""
        Logger.log("d", "[PrintPlugin] Cancel print called")
        
        self.job.cancel()
    

    def _cleanup_ui(self):
        """Centralized UI cleanup - called after worker has stopped"""
        Logger.log("d", "[PrintPlugin] Starting UI cleanup")
        
        # First restore cursor BEFORE closing dialog
        self.printView.restore_cursor()
        
        # Process events to ensure cursor is updated
        QApplication.processEvents()
        
        # Small delay to ensure cursor change is processed
        QTimer.singleShot(50, self.printView.close_printing_dialog)

        QApplication.processEvents()

        # self.reset_layers()
      
    def update_layer_preview(self, layer_number):
        """Update Cura's preview to show the layer that was just printed"""
        try:
            if self.active_view and hasattr(self.active_view, 'setLayer'):
                max_paths = self.active_view.getMaxPaths()
                self.active_view.setPath(max_paths)
                self.active_view.setLayer(layer_number)
                self.app.processEvents()
                Logger.log("d", f"[PrintPlugin] Preview updated to show layer {layer_number}")
            else:
                Logger.log("w", "[PrintPlugin] Preview not available - user may not be in Preview mode")
        except Exception as e:
            Logger.log("w", f"[PrintPlugin] Could not update preview: {e}")

    def extract_gcode(self):
        gcode_dict = getattr(self.scene, "gcode_dict", None)

        if not gcode_dict:
            self.printView.geometry_processing_error("No G-code found. Please slice the model first.")
            return None
        
        gcode_text = gcode_dict.get(0, "")

        if not gcode_text:
            self.printView.geometry_processing_error("No G-code found after slicing.")
            return None
        
        if isinstance(gcode_text, list):
            gcode_list = "".join(gcode_text)
        else:
            gcode_list = gcode_text
        
        # Store gcode text for debugging
        plugin_dir = os.path.dirname(__file__)
        output_path = os.path.join(plugin_dir, "gcode.txt")
        try:
            with open(output_path, "w") as debug_file:
                debug_file.write(gcode_list)
        except Exception as e:
            Logger.log("w", f"[PrintPlugin] Could not write debug gcode: {e}")

        return gcode_list
        
    def on_print_finished(self):
        self.is_printing = False
        Logger.log("d", "[PrintPlugin] on_print_finished called")
        self._cleanup_ui()
        
        # Show message after cleanup
        QTimer.singleShot(100, lambda: self.printView.print_finished_message())

    def on_print_error(self, message):
        self.is_printing = False
        Logger.log("d", f"[PrintPlugin] on_print_error called: {message}")
        self._cleanup_ui()
        
        # Show message after cleanup
        QTimer.singleShot(100, lambda: self.printView.show_warning(message))

    def on_thread_finished(self):
        """Called when the thread actually finishes"""
        Logger.log("d", "[PrintPlugin] Thread finished signal received")
        # Give a small delay before cleanup to ensure all signals are processed
        QTimer.singleShot(100, self.job.cancel)

    def on_cancelled(self):
        self.is_printing = False
        """Called when worker emits cancelled signal"""
        Logger.log("d", "[PrintPlugin] Worker cancelled signal received")
        self._cleanup_ui()
        
        # Show message after cleanup
        QTimer.singleShot(100, lambda: self.printView.print_cancelled_message())
               
    def print_process(self):
        Logger.log("d", "[PrintPlugin] print_process called")
        
        if self.is_printing:
            self.printView.show_warning("A print job is already in progress.")
            return
        
        # Clean up any existing thread first
        if self.job.thread is not None or self.job.worker is not None:
            Logger.log("d", "[PrintPlugin] Cleaning up existing thread")
            self.job.cancel()
        
        try:
            # Get output path FIRST (before showing dialog)
            save_path, _ = self.printView.ask_output_path()
            if not save_path:
                Logger.log("d", "[PrintPlugin] User cancelled file selection")
             
                return
            
            output_dir = os.path.dirname(save_path)
            Logger.log("d", f"[PrintPlugin] Output directory: {output_dir}")
            
            # Reset layers
            try:
                self.reset_layers()
            except Exception as e:
                Logger.log("e", f"[PrintPlugin] Error resetting layers: {e}")
                self.printView.geometry_processing_error(f"{e} \n Slice the model and try again.")
               
                return

            # Extract gcode
            gcode = self.extract_gcode()
            if gcode is None:
                Logger.log("e", "[PrintPlugin] No gcode available")
               
                return

            Logger.log("d", f"[PrintPlugin] Gcode extracted, length: {len(gcode)}")
            
            # NOW show dialog and busy cursor after we have everything ready
            self.printView.show_printing_dialog()
            self.printView.set_busy_cursor()

            # Create new thread and worker
            Logger.log("d", "[PrintPlugin] Creating worker and thread")
            self.is_printing = True
            self.job.start(gcode, output_dir)

        except Exception as e:
            Logger.logException("e", "[PrintPlugin] Error while printing file")
            self.printView.show_warning(str(e))
            self._cleanup_ui()
            # Cleanup thread after UI cleanup
            QTimer.singleShot(200, self.job.cancel)

