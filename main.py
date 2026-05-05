import random
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QCheckBox
)

from src.components import ErrorCard, MetricCard
from src.plots import BarGraph, MultiRealTimePlot, RealTimePlot, RpmSpeedPlot
from src.map import TelemetryMap

# Global Style
DARK_THEME = """
    QMainWindow { background-color: #121212; }
    QFrame#Card {
        background-color: #1e1e1e;
        border-radius: 8px;
        border: 1px solid #333;
    }
    QLabel { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    QLabel#Value { font-size: 24px; font-weight: bold; color: #00d1ff; }
    QLabel#Title { font-size: 12px; color: #888; text-transform: uppercase; }
"""


class TelemetryDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OBD2 Telemetry Dashboard")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_THEME)

        self.serial = QSerialPort()

        # central widget
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        self.error_layout = QVBoxLayout()
        self.error_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Build UI
        self.create_pages()
        self.create_toolbar()

        # Automatically try to connect to available ESP32/USB port
        self.auto_connect()

        # for map testing
        self.x = 50.02557915602892
        self.y = 22.007746519509208

        # TEST AREA
        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate)
        self.timer.start(1000)

    def simulate(self):

        rpm: int = random.randrange(1000, 3500)
        speed: int = random.randrange(25, 65)

        self.rpm_card.update_value(rpm)
        self.rpm_speed_graph.update_plot(rpm, speed)
        self.load_card.update_value(int(random.randrange(1, 100)))
        self.coolant_temp_card.update_value(float(random.randrange(-40, 40)))
        self.oil_temp_card.update_value(int(random.randrange(0, 765)))

        self.telemetry_map.update_position(self.x, self.y, rpm, speed)

        self.x += 0.0001
        self.y += 0.0001

        self.fuel_trim_graph.update_curve("stft1", int(random.randrange(-20, 20)))
        self.fuel_trim_graph.update_curve("stft2", int(random.randrange(-20, 20)))
        self.fuel_trim_graph.update_curve("ltft1", int(random.randrange(-20, 20)))
        self.fuel_trim_graph.update_curve("ltft2", int(random.randrange(-20, 20)))

        self.add_error("test error code")

    def create_pages(self):
        # PAGE 1: CURRENT DATA
        self.page_data = QWidget()
        self.main_layout = QGridLayout(self.page_data)
        self.main_layout.setSpacing(15)  # Spacing

        self.oil_temp_card = MetricCard("Engine oil temp", " C", "#ffcc00")
        self.rpm_card = MetricCard("Engine Speed", " RPM", "#00ff88")
        self.load_card = MetricCard("Engine Load", "%", "#ff4444")
        self.coolant_temp_card = MetricCard("Coolant Temp", " C", "#3820d4")

        self.main_layout.addWidget(self.oil_temp_card, 0, 0)
        self.main_layout.addWidget(self.rpm_card, 0, 1)
        self.main_layout.addWidget(self.load_card, 0, 2)
        self.main_layout.addWidget(self.coolant_temp_card, 0, 3)

        # RPM/SPEED PLOT (LEFT), MAP (RIGHT)
        self.rpm_speed_graph = RpmSpeedPlot("Korelacja RPM / Prędkość")
        self.main_layout.addWidget(self.rpm_speed_graph, 1, 0, 1, 2) # Row 1, Col 0, Span 2

        map_container = QWidget()
        map_vbox = QVBoxLayout(map_container)
        map_vbox.setContentsMargins(0, 0, 0, 0)

        self.snap_checkbox = QCheckBox("Snap view")
        self.snap_checkbox.setChecked(True)
        self.snap_checkbox.setStyleSheet("color: #888; font-size: 10pt;")

        self.telemetry_map = TelemetryMap()

        self.snap_checkbox.stateChanged.connect(self.toggle_map_snap)

        map_vbox.addWidget(self.snap_checkbox)
        map_vbox.addWidget(self.telemetry_map)

        self.main_layout.addWidget(map_container, 1, 2, 1, 2) # Row 1, Col 2, Span 2

        self.central_stack.addWidget(self.page_data)

        # PAGE 2: FUEL TRIM
        self.page_fuel_trim = QWidget()
        layout_fuel = QGridLayout(self.page_fuel_trim)
        self.fuel_trim_graph = MultiRealTimePlot("Fuel Trim (STFT/LTFT)")
        layout_fuel.addWidget(self.fuel_trim_graph, 1, 1, 1, 1)

        self.fuel_trim_graph.add_curve("stft1", "Red")
        self.fuel_trim_graph.add_curve("stft2", "Blue")
        self.fuel_trim_graph.add_curve("ltft1", "Green")
        self.fuel_trim_graph.add_curve("ltft2", "Yellow")

        self.central_stack.addWidget(self.page_fuel_trim)

        # PAGE 3: ERROR CODES
        self.page_errors = QWidget()
        main_page_layout = QVBoxLayout(self.page_errors)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        self.layout_errors = QVBoxLayout(scroll_content)
        self.layout_errors.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(scroll_content)
        main_page_layout.addWidget(scroll)

        self.central_stack.addWidget(self.page_errors)

    def toggle_map_snap(self, state):
        # state == 2 checked
        # state == 0 unchecked
        self.telemetry_map.auto_center = (state == 2)

    def add_error(self, message, timestamp=""):
        error = ErrorCard(message, timestamp)
        self.layout_errors.addWidget(error)

    def create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        # Current Data
        data_act = QAction("Current Data", self)
        data_act.triggered.connect(lambda: self.central_stack.setCurrentIndex(0))
        toolbar.addAction(data_act)

        toolbar.addSeparator()

        # Fuel Trim
        tire_act = QAction("Fuel Trim", self)
        tire_act.triggered.connect(lambda: self.central_stack.setCurrentIndex(1))
        toolbar.addAction(tire_act)

        toolbar.addSeparator()

        # Error Codes
        error_act = QAction("Error Codes", self)
        error_act.triggered.connect(lambda: self.central_stack.setCurrentIndex(2))
        toolbar.addAction(error_act)

    def auto_connect(self):
        available_ports = QSerialPortInfo.availablePorts()
        if not available_ports:
            print("No serial ports found")
            return

        target_port = available_ports[0].portName()
        self.serial.setPortName(target_port)

        # Settings
        self.serial.setBaudRate(115200)
        self.serial.setDataBits(QSerialPort.DataBits.Data8)
        self.serial.setParity(QSerialPort.Parity.NoParity)
        self.serial.setStopBits(QSerialPort.StopBits.OneStop)
        self.serial.setFlowControl(QSerialPort.FlowControl.NoFlowControl)

        if self.serial.open(QSerialPort.OpenModeFlag.ReadOnly):
            print(f"Connected to {target_port}")
            self.serial.readyRead.connect(self.handle_serial_data)
        else:
            QMessageBox.critical(self, "Serial Error", f"Could not open {target_port}")

    def handle_serial_data(self):

        while self.serial.canReadLine():
            try:
                line_bytes = self.serial.readLine()
                raw_data = line_bytes.data().decode("utf-8").strip()

                print(f"Received = {raw_data}")

                if not raw_data or "=" not in raw_data:
                    continue

                param, value = raw_data.split("=", 1)

                if param == "ENGINE_SPEED":
                    self.rpm_card.update_value(int(value))
                    self.rpm_speed_graph.update_plot(int(value), int(value)) # Do zmiany
                elif param == "ENGINE_LOAD":
                    self.load_card.update_value(int(value))
                elif param == "VEHICLE_SPEED":
                    self.rpm_speed_graph.update_plot(int(value), int(value)) # Do zmiany
                elif param == "COOLANT_TEMP":
                    self.coolant_temp_card.update_value(float(value))
                elif param == "OIL_TEMP":
                    self.oil_temp_card.update_value(int(value))
                elif "STFT" in param or "LTFT" in param:
                    self.fuel_trim_graph.update_curve(param.lower(), int(value))

            except (UnicodeDecodeError, ValueError) as e:
                print(f"Parsing error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelemetryDashboard()
    window.show()
    sys.exit(app.exec())
