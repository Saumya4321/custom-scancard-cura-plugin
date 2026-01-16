from UM.Extension import Extension
from UM.Logger import Logger
from UM.Application import Application
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QApplication, QDockWidget
from .print_pipeline import PrintPipeline
from .printView import printView
from .print_job_service import PrintJobService
from .laser_control_panel import LaserControlPanel
import os

class PrintController(Extension):
    def __init__(self):
        super().__init__()
        self.addMenuItem("Send to scancard", self.print_process)
        self.addMenuItem("Toggle Laser Controls", self.toggle_laser_panel)  # Add menu item
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
        
        # Use Qt.QueuedConnection to ensure proper thread-safe UI updates
        self.job.progress_layer.connect(self._schedule_layer_update, Qt.ConnectionType.QueuedConnection)
        self.job.finished.connect(self.on_print_finished, Qt.ConnectionType.QueuedConnection)
        self.job.error.connect(self.on_print_error, Qt.ConnectionType.QueuedConnection)
        self.job.cancelled.connect(self.on_cancelled, Qt.ConnectionType.QueuedConnection)
        self.job.progress_updated.connect(self.on_progress_updated, Qt.ConnectionType.QueuedConnection)
        
        # Throttle layer updates to prevent rapid UI changes
        self._pending_layer_update = None
        self._layer_update_timer = QTimer()
        self._layer_update_timer.setSingleShot(True)
        self._layer_update_timer.timeout.connect(self._do_layer_update)
        self._layer_update_interval = 1  # Update every layer for live preview
        self._last_layer_update_time = 0  # Track timing
        
        # Defer dock panel creation until UI is ready
        self.laser_dock = None
        self.laser_panel = None
        QTimer.singleShot(1000, self._setup_laser_dock_panel)  # Delay 1 second
        
        self.Logger.log("d", "[PrintPlugin] Initialized successfully")

    def _setup_laser_dock_panel(self):
        """Create and add the laser control dock panel to Cura's UI"""
        try:
            # Get the main window
            main_window = self.app.getMainWindow()
            
            if not main_window:
                self.Logger.log("w", "[PrintPlugin] Main window not ready, retrying in 1 second")
                QTimer.singleShot(1000, self._setup_laser_dock_panel)
                return
            
            # Create the laser control panel first
            self.laser_panel = LaserControlPanel()
            
            # Connect signals from the panel to handlers
            self.laser_panel.connect_requested.connect(self._on_laser_connect)
            self.laser_panel.home_laser_requested.connect(self._on_laser_home)
            self.laser_panel.laser_on_requested.connect(self._on_laser_on)
            self.laser_panel.laser_off_requested.connect(self._on_laser_off)
            self.laser_panel.power_changed.connect(self._on_power_changed)
            self.laser_panel.delay_changed.connect(self._on_delay_changed)
            self.laser_panel.pattern_changed.connect(self._on_pattern_changed)
            self.laser_panel.correction_changed.connect(self._on_correction_changed)
            self.laser_panel.mode_changed.connect(self._on_mode_changed)
            self.laser_panel.fetch_values_requested.connect(self._on_fetch_values)
            
            # Create the dock widget
            self.laser_dock = QDockWidget("Laser Controls")
            self.laser_dock.setObjectName("LaserControlDock")
            
            # Set the panel as the dock widget's content
            self.laser_dock.setWidget(self.laser_panel)
            
            # Configure dock widget BEFORE adding to main window
            self.laser_dock.setAllowedAreas(
                Qt.DockWidgetArea.LeftDockWidgetArea | 
                Qt.DockWidgetArea.RightDockWidgetArea |
                Qt.DockWidgetArea.BottomDockWidgetArea
            )
            
            # Allow moving and floating
            self.laser_dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable |
                QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                QDockWidget.DockWidgetFeature.DockWidgetClosable
            )
            
            # Set a reasonable size
            self.laser_dock.setMinimumWidth(420)
            self.laser_dock.setMinimumHeight(600)
            
            # Prevent it from floating initially
            self.laser_dock.setFloating(False)
            
            # Add to main window - try bottom area instead
            main_window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.laser_dock)
            
            # Ensure visibility
            self.laser_dock.setVisible(True)
            
            self.Logger.log("d", "[PrintPlugin] Laser control dock panel created successfully")
                
        except Exception as e:
            self.Logger.log("e", f"[PrintPlugin] Error creating laser dock panel: {e}")
            import traceback
            self.Logger.log("e", traceback.format_exc())

    # Laser control signal handlers
    def toggle_laser_panel(self):
        """Toggle the visibility of the laser control panel"""
        if self.laser_dock:
            self.laser_dock.setVisible(not self.laser_dock.isVisible())
            Logger.log("d", f"[PrintPlugin] Laser dock visibility: {self.laser_dock.isVisible()}")
        else:
            Logger.log("w", "[PrintPlugin] Laser dock not initialized yet")
            # Try to create it now
            self._setup_laser_dock_panel()
    
    def _on_laser_connect(self, port):
        """Handle laser connection request"""
        Logger.log("d", f"[PrintPlugin] Laser connect to {port}")
        # TODO: Implement actual serial connection logic here
        # For now, just update the UI
        # self.laser_panel.set_connection_status(True)
        pass
        
    def _on_laser_home(self):
        """Handle laser homing request"""
        Logger.log("d", "[PrintPlugin] Laser home requested")
        # TODO: Implement laser homing logic
        pass
        
    def _on_laser_on(self):
        """Handle laser on request"""
        Logger.log("d", "[PrintPlugin] Laser ON requested")
        # TODO: Implement laser on logic
        pass
        
    def _on_laser_off(self):
        """Handle laser off request"""
        Logger.log("d", "[PrintPlugin] Laser OFF requested")
        # TODO: Implement laser off logic
        pass
        
    def _on_power_changed(self, power):
        """Handle laser power change"""
        Logger.log("d", f"[PrintPlugin] Laser power changed to {power}%")
        # TODO: Send power command to laser controller
        pass
        
    def _on_delay_changed(self, delay):
        """Handle mark delay change"""
        Logger.log("d", f"[PrintPlugin] Mark delay changed to {delay}")
        # TODO: Send delay command to laser controller
        pass
        
    def _on_pattern_changed(self, pattern):
        """Handle pattern change"""
        Logger.log("d", f"[PrintPlugin] Pattern changed to {pattern}")
        # TODO: Send pattern command to laser controller
        pass
        
    def _on_correction_changed(self, is_on):
        """Handle correction mode change"""
        Logger.log("d", f"[PrintPlugin] Correction changed to {'ON' if is_on else 'OFF'}")
        # TODO: Send correction command to laser controller
        pass
        
    def _on_mode_changed(self, mode):
        """Handle mode change"""
        Logger.log("d", f"[PrintPlugin] Mode changed to {mode}")
        # TODO: Send mode command to laser controller
        pass
        
    def _on_fetch_values(self):
        """Handle fetch values request"""
        Logger.log("d", "[PrintPlugin] Fetch values requested")
        # TODO: Implement fetching monitored values from hardware
        # Example of updating values:
        # self.laser_panel.update_monitored_value("12V monitoring", "12.3V")
        # self.laser_panel.update_monitored_value("Galvo supply", "5.1V")
        pass

    def _schedule_layer_update(self, layer_number):
        """Schedule a layer update with throttling to prevent UI glitches"""
        import time
        current_time = time.time()
        
        # Only update if at least 500ms have passed since last update
        # This prevents rapid-fire updates that make the glitch more noticeable
        time_since_last = current_time - self._last_layer_update_time
        if time_since_last < 0.5:  # 500ms minimum between updates
            Logger.log("d", f"[PrintPlugin] Skipping layer update {layer_number} (too soon)")
            return
        
        Logger.log("d", f"[PrintPlugin] Scheduling layer update to {layer_number}")
        self._pending_layer_update = layer_number
        
        # Only update if timer isn't already running (throttle updates)
        if not self._layer_update_timer.isActive():
            self._layer_update_timer.start(200)  # 200ms delay to batch updates

    def _do_layer_update(self):
        """Actually perform the layer update"""
        import time
        if self._pending_layer_update is not None:
            layer_num = self._pending_layer_update
            self._pending_layer_update = None
            self._last_layer_update_time = time.time()  # Track when update happened
            self.update_layer_preview(layer_num)

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
        
        # Stop any pending layer updates
        self._layer_update_timer.stop()
        self._pending_layer_update = None
        
        self.printView.restore_cursor()
        self.printView.close_printing_dialog()
      
    def update_layer_preview(self, layer_number):
        """Update Cura's preview to show the layer that was just printed"""
        Logger.log("d", f"[PrintPlugin] Updating preview to layer {layer_number}")
        try:
            # Get fresh reference to active view
            current_view = self.controller.getActiveView()
            
            if current_view and hasattr(current_view, 'setLayer'):
                # Only update the layer, don't touch setPath
                # setPath might be causing unnecessary redraws
                current_view.setLayer(layer_number)
                Logger.log("d", f"[PrintPlugin] Preview updated to layer {layer_number}")
            else:
                Logger.log("w", "[PrintPlugin] Preview not available - user may not be in Preview mode")
        except Exception as e:
            Logger.log("e", f"[PrintPlugin] Error updating preview: {e}")

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

    def on_progress_updated(self, current_layer, total_layers):
        """Update progress bar in the dialog"""
        self.printView.update_progress(current_layer, total_layers)
        
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