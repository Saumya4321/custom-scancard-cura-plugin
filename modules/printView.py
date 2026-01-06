from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, Qt

class printView(QObject):
    cancel_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.print_dialog = None

    def show_printing_dialog(self):
        self.print_dialog = QMessageBox()
        self.print_dialog.setWindowTitle("Printing in progress")
        self.print_dialog.setText(
            "Streaming data to scan card.\n\nPlease wait…"
        )
        self.print_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
        self.print_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.print_dialog.buttonClicked.connect(self._on_cancel)
        self.print_dialog.rejected.connect(self._on_cancel)
        self.print_dialog.show()

    def _on_cancel(self):
        self.cancel_requested.emit()

    def close_printing_dialog(self):
        if self.print_dialog:
            self.print_dialog.close()
            self.print_dialog = None


    def ask_output_path(self):
        return QFileDialog.getSaveFileName(
                None, "Save Geometry", "", "Text Files (*.txt)"
            )

    def confirm_next_layer(self, i, n):
        return QMessageBox.question(
                    None,
                    "Print Plugin",
                    f"Sent {n} UDP payloads of layer {i} to scan card. \nContinue to next layer?"
                )

    def print_finished_message(self):
        QMessageBox.information(None, "Print Plugin", "Print job finished!")

    def print_cancelled_message(self):
        QMessageBox.information(None, "Print Plugin", "Print job cancelled by user.")

    def show_warning(self, message):
        QMessageBox.critical(None, "Print Plugin", str(message))


    def geometry_processing_error(self, message):
        QMessageBox.warning(None, "Print Plugin",
                            message)