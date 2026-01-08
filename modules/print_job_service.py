from PyQt6.QtCore import QObject, QThread, pyqtSignal
from UM.Logger import Logger
from .print_worker import PrintWorker


class PrintJobService(QObject):
    progress_layer = pyqtSignal(int)
    finished = pyqtSignal()
    cancelled = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, pipeline):
        super().__init__()
        self.pipeline = pipeline
        self.thread = None
        self.worker = None
        self._cleanup_in_progress = False

    def start(self, gcode, output_dir):
        Logger.log("d", "[PrintJobService] Starting print job")

        self.thread = QThread()
        self.worker = PrintWorker(self.pipeline, gcode, output_dir)
        self.worker.moveToThread(self.thread)

        # Worker execution
        self.thread.started.connect(self.worker.run)

        # Forward worker signals
        self.worker.progress_layer.connect(self.progress_layer)
        self.worker.finished.connect(self.finished)
        self.worker.cancelled.connect(self.cancelled)
        self.worker.error.connect(self.error)

        # Shutdown rules
        self.worker.finished.connect(self.thread.quit)
        self.worker.cancelled.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.thread.finished.connect(self._cleanup)

        Logger.log("d", "[PrintPlugin] Starting thread")
        self.thread.start()
        Logger.log("d", "[PrintPlugin] Thread started")

    def cancel(self):
        Logger.log("d", "[PrintJobService] Cancel requested")
        if self.worker:
            self.worker.stop()
       

    def _cleanup(self):
        if self._cleanup_in_progress:
            return

        self._cleanup_in_progress = True
        Logger.log("d", "[PrintJobService] Cleaning up thread")

        if self.worker is not None:
            # Disconnect all signals to prevent issues
            try:
                self.worker.progress_layer.disconnect()
            except:
                pass
            try:
                self.worker.finished.disconnect()
            except:
                pass
            try:
                self.worker.error.disconnect()
            except:
                pass
            try:
                self.worker.cancelled.disconnect()
            except:
                pass
        
        if self.thread is not None:
            # Disconnect thread signals
            try:
                self.thread.started.disconnect()
            except:
                pass
            try:
                self.thread.finished.disconnect()
            except:
                pass
            
            # Wait for thread to finish (with timeout)
            if self.thread.isRunning():
                Logger.log("d", "[PrintPlugin] Waiting for thread to finish")
                self.thread.quit()
                if not self.thread.wait(3000):  # Wait max 3 seconds
                    Logger.log("w", "[PrintPlugin] Thread did not finish, terminating")
                    self.thread.terminate()
                    self.thread.wait()
            
            Logger.log("d", "[PrintPlugin] Thread stopped")
        
        self.thread = None
        self.worker = None
        self._cleanup_in_progress = False
        Logger.log("d", "[PrintPlugin] Cleanup complete")
