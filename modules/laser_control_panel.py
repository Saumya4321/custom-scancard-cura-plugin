from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QRadioButton,
                             QButtonGroup, QGroupBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from UM.Logger import Logger


class LaserControlPanel(QWidget):
    """Dock panel for laser control settings"""
    
    # Signals for communication with controller
    connect_requested = pyqtSignal(str)  # COM port
    home_laser_requested = pyqtSignal()
    laser_on_requested = pyqtSignal()
    laser_off_requested = pyqtSignal()
    power_changed = pyqtSignal(float)  # Laser power percentage
    delay_changed = pyqtSignal(float)  # Mark delay
    pattern_changed = pyqtSignal(str)  # "circle" or "square"
    correction_changed = pyqtSignal(bool)  # True for ON, False for OFF
    mode_changed = pyqtSignal(int)  # 0 or 1
    fetch_values_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        Logger.log("d", "[LaserControlPanel] Initialized")
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout for the widget
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        # Title
        title = QLabel("Dual Laser Controller")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2196F3;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)
        
        # COM Port Connection Section
        content_layout.addWidget(self._create_connection_section())
        
        # Separator
        content_layout.addWidget(self._create_separator())
        
        # Laser Parameters Section
        content_layout.addWidget(self._create_parameters_section())
        
        # Separator
        content_layout.addWidget(self._create_separator())
        
        # Control Buttons Section
        content_layout.addWidget(self._create_control_buttons())
        
        # Separator
        content_layout.addWidget(self._create_separator())
        
        # Pattern Selection Section
        content_layout.addWidget(self._create_pattern_section())
        
        # Separator
        content_layout.addWidget(self._create_separator())
        
        # Correction and Mode Section
        content_layout.addWidget(self._create_correction_mode_section())
        
        # Separator
        content_layout.addWidget(self._create_separator())
        
        # Monitored Values Section
        content_layout.addWidget(self._create_monitored_section())
        
        # Add stretch to push everything to top
        content_layout.addStretch()
        
        # Set the layout for content widget
        content_widget.setLayout(content_layout)
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        
        # Set a reasonable minimum size
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        
    def _create_connection_section(self):
        """Create COM port connection section"""
        group = QGroupBox("Connection")
        layout = QVBoxLayout()
        
        # COM port selection
        port_layout = QHBoxLayout()
        port_label = QLabel("COM port:")
        self.com_port_combo = QComboBox()
        self.com_port_combo.addItems(["COM3", "COM4", "COM5", "COM6", "COM7", "COM8"])
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.com_port_combo)
        layout.addLayout(port_layout)
        
        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #2196F3;
            }
        """)
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn)
        
        group.setLayout(layout)
        return group
        
    def _create_parameters_section(self):
        """Create laser parameters section"""
        group = QGroupBox("Change Laser Parameters")
        layout = QVBoxLayout()
        
        # Laser power
        power_layout = QHBoxLayout()
        power_label = QLabel("Laser power:")
        self.power_input = QLineEdit()
        self.power_input.setPlaceholderText("0-100")
        self.power_input.textChanged.connect(self._on_power_changed)
        percent_label = QLabel("%")
        power_layout.addWidget(power_label)
        power_layout.addWidget(self.power_input)
        power_layout.addWidget(percent_label)
        layout.addLayout(power_layout)
        
        # Mark delay
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Mark delay:")
        self.delay_input = QLineEdit()
        self.delay_input.setPlaceholderText("delay value")
        self.delay_input.textChanged.connect(self._on_delay_changed)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_input)
        layout.addLayout(delay_layout)
        
        group.setLayout(layout)
        return group
        
    def _create_control_buttons(self):
        """Create laser control buttons"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Home Laser button
        self.home_btn = QPushButton("Home Laser")
        self.home_btn.setStyleSheet("""
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
        """)
        self.home_btn.clicked.connect(self._on_home_clicked)
        layout.addWidget(self.home_btn)
        
        # Laser On button
        self.laser_on_btn = QPushButton("Laser On")
        self.laser_on_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        self.laser_on_btn.clicked.connect(self._on_laser_on_clicked)
        layout.addWidget(self.laser_on_btn)
        
        # Laser Off button
        self.laser_off_btn = QPushButton("Laser Off")
        self.laser_off_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DA190B;
            }
        """)
        self.laser_off_btn.clicked.connect(self._on_laser_off_clicked)
        layout.addWidget(self.laser_off_btn)
        
        widget.setLayout(layout)
        return widget
        
    def _create_pattern_section(self):
        """Create pattern selection section"""
        group = QGroupBox("Set Pattern")
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Circle pattern button
        self.circle_btn = QPushButton("●")
        self.circle_btn.setFixedSize(80, 80)
        self.circle_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 40px;
                font-size: 30pt;
            }
            QPushButton:hover {
                background-color: #DA190B;
            }
        """)
        self.circle_btn.clicked.connect(lambda: self._on_pattern_clicked("circle"))
        layout.addWidget(self.circle_btn)
        
        # Square pattern button
        self.square_btn = QPushButton("■")
        self.square_btn.setFixedSize(80, 80)
        self.square_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 30pt;
            }
            QPushButton:hover {
                background-color: #DA190B;
            }
        """)
        self.square_btn.clicked.connect(lambda: self._on_pattern_clicked("square"))
        layout.addWidget(self.square_btn)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
        
    def _create_correction_mode_section(self):
        """Create correction and mode selection section"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Correction group
        correction_group = QGroupBox()
        correction_group.setStyleSheet("QGroupBox { background-color: #BBDEFB; border-radius: 5px; }")
        correction_layout = QVBoxLayout()
        
        self.correction_on_radio = QRadioButton("Correction ON")
        self.correction_off_radio = QRadioButton("Correction OFF")
        self.correction_off_radio.setChecked(True)
        
        self.correction_group = QButtonGroup()
        self.correction_group.addButton(self.correction_on_radio, 1)
        self.correction_group.addButton(self.correction_off_radio, 0)
        self.correction_group.buttonClicked.connect(self._on_correction_changed)
        
        correction_layout.addWidget(self.correction_on_radio)
        correction_layout.addWidget(self.correction_off_radio)
        correction_group.setLayout(correction_layout)
        layout.addWidget(correction_group)
        
        # Mode group
        mode_group = QGroupBox()
        mode_group.setStyleSheet("QGroupBox { background-color: #C8E6C9; border-radius: 5px; }")
        mode_layout = QVBoxLayout()
        
        self.mode_0_radio = QRadioButton("Mode 0")
        self.mode_1_radio = QRadioButton("Mode 1")
        self.mode_0_radio.setChecked(True)
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.mode_0_radio, 0)
        self.mode_group.addButton(self.mode_1_radio, 1)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        
        mode_layout.addWidget(self.mode_0_radio)
        mode_layout.addWidget(self.mode_1_radio)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        widget.setLayout(layout)
        return widget
        
    def _create_monitored_section(self):
        """Create monitored values section"""
        group = QGroupBox("Monitored Values")
        layout = QVBoxLayout()
        
        # Create dictionary to store value displays
        self.monitored_values = {}
        
        monitored_items = [
            "12V monitoring",
            "Galvo supply",
            "12V monitoring",
            "CO2 laser 1",
            "5V monitoring",
            "5V monitoring",
            "External monitoring",
            "CO2 laser 2"
        ]
        
        for item in monitored_items:
            item_layout = QHBoxLayout()
            label = QLabel(item + ":")
            value_display = QLineEdit()
            value_display.setReadOnly(True)
            value_display.setStyleSheet("background-color: white;")
            item_layout.addWidget(label)
            item_layout.addWidget(value_display)
            layout.addLayout(item_layout)
            self.monitored_values[item] = value_display
        
        # Fetch Values button
        self.fetch_btn = QPushButton("Fetch Values")
        self.fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
        """)
        self.fetch_btn.clicked.connect(self._on_fetch_clicked)
        layout.addWidget(self.fetch_btn)
        
        group.setLayout(layout)
        return group
        
    def _create_separator(self):
        """Create a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line
        
    # Signal emission methods
    def _on_connect_clicked(self):
        port = self.com_port_combo.currentText()
        self.connect_requested.emit(port)
        Logger.log("d", f"[LaserControlPanel] Connect requested for {port}")
        
    def _on_home_clicked(self):
        self.home_laser_requested.emit()
        Logger.log("d", "[LaserControlPanel] Home laser requested")
        
    def _on_laser_on_clicked(self):
        self.laser_on_requested.emit()
        Logger.log("d", "[LaserControlPanel] Laser ON requested")
        
    def _on_laser_off_clicked(self):
        self.laser_off_requested.emit()
        Logger.log("d", "[LaserControlPanel] Laser OFF requested")
        
    def _on_power_changed(self, text):
        try:
            if text:
                power = float(text)
                if 0 <= power <= 100:
                    self.power_changed.emit(power)
        except ValueError:
            pass
            
    def _on_delay_changed(self, text):
        try:
            if text:
                delay = float(text)
                self.delay_changed.emit(delay)
        except ValueError:
            pass
            
    def _on_pattern_clicked(self, pattern):
        self.pattern_changed.emit(pattern)
        Logger.log("d", f"[LaserControlPanel] Pattern changed to {pattern}")
        
    def _on_correction_changed(self):
        is_on = self.correction_on_radio.isChecked()
        self.correction_changed.emit(is_on)
        Logger.log("d", f"[LaserControlPanel] Correction changed to {'ON' if is_on else 'OFF'}")
        
    def _on_mode_changed(self):
        mode = 0 if self.mode_0_radio.isChecked() else 1
        self.mode_changed.emit(mode)
        Logger.log("d", f"[LaserControlPanel] Mode changed to {mode}")
        
    def _on_fetch_clicked(self):
        self.fetch_values_requested.emit()
        Logger.log("d", "[LaserControlPanel] Fetch values requested")
        
    # Public methods for updating UI
    def update_monitored_value(self, name, value):
        """Update a monitored value display"""
        if name in self.monitored_values:
            self.monitored_values[name].setText(str(value))
            
    def set_connection_status(self, connected):
        """Update connection button based on status"""
        if connected:
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DA190B;
                }
            """)
        else:
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #64B5F6;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #42A5F5;
                }
            """)