
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class viewHelper:
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