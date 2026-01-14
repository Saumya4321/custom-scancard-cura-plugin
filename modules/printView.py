from PyQt6.QtWidgets import QFileDialog, QMessageBox, QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtCore import QObject, pyqtSignal, Qt

class printView(QObject):
    cancel_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.print_dialog = None
        self.progress_bar = None
        self.progress_label = None
        self.cursor_overridden = False

    def show_printing_dialog(self):
        """Create a custom non-modal dialog with progress bar"""
        if self.print_dialog is not None:
            self.print_dialog.close()
            self.print_dialog = None
            
        # Create a simple QDialog instead of QMessageBox
        self.print_dialog = QDialog()
        self.print_dialog.setWindowTitle("Printing in progress")
        
        # Make it a tool window that stays on top but doesn't interfere
        self.print_dialog.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.print_dialog.setWindowModality(Qt.WindowModality.NonModal)
        
        # Create layout with some styling
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel("Streaming data to scan card.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("QLabel { font-size: 12pt; padding: 10px; }")
        layout.addWidget(label)
        
        # Add progress label
        self.progress_label = QLabel("Layer 0 of 0 (0%)")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("QLabel { font-size: 10pt; padding: 5px; }")
        layout.addWidget(self.progress_label)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Add cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._on_cancel)
        cancel_btn.setStyleSheet("QPushButton { padding: 5px 15px; margin-top: 10px; }")
        layout.addWidget(cancel_btn)
        
        self.print_dialog.setLayout(layout)
        self.print_dialog.setMinimumWidth(350)
        self.print_dialog.setFixedSize(self.print_dialog.sizeHint())
        
        # Position it in the corner to be less obtrusive
        screen_geometry = QApplication.primaryScreen().geometry()
        dialog_geometry = self.print_dialog.geometry()
        x = screen_geometry.width() - dialog_geometry.width() - 50
        y = 50
        self.print_dialog.move(x, y)
        
        # Show the dialog without activating it
        self.print_dialog.show()
        self.print_dialog.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

    def update_progress(self, current_layer, total_layers):
        """Update the progress bar and label"""
        if self.progress_bar and self.progress_label:
            percentage = int((current_layer / total_layers) * 100) if total_layers > 0 else 0
            self.progress_bar.setValue(percentage)
            self.progress_label.setText(f"Layer {current_layer} of {total_layers} ({percentage}%)")

    def _on_cancel(self):
        self.cancel_requested.emit()

    def close_printing_dialog(self):
        if self.print_dialog:
            self.print_dialog.hide()
            self.print_dialog.close()
            self.print_dialog.deleteLater()
            self.print_dialog = None
            self.progress_bar = None
            self.progress_label = None

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
        
    def set_busy_cursor(self):
        if not self.cursor_overridden:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.cursor_overridden = True
       
    def restore_cursor(self):
        if self.cursor_overridden:
            QApplication.restoreOverrideCursor()
            self.cursor_overridden = False
        else:
            pass