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
)

from src.components import ErrorCard, MetricCard
from src.plots import BarGraph, MultiRealTimePlot, RealTimePlot

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

        from PyQt6.QtSerialPort import QSerialPort

        self.serial = QSerialPort()

        # Stacked Widget (central widget)
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        self.error_layout = QVBoxLayout()
        self.error_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Build UI
        self.create_pages()
        self.create_toolbar()

        # Automatically try to connect to available ESP32/USB port
        self.auto_connect()

        # TEST AREA
        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate)
        self.timer.start(500)

    def simulate(self):

        self.speed_card.update_value(int(random.randrange(1000, 3500)))
        self.speed_graph.update_plot(int(random.randrange(25, 65)))
        self.load_card.update_value(int(random.randrange(1, 100)))
        self.coolant_temp_card.update_value(float(random.randrange(-40, 40)))
        self.fuel_pressure_card.update_value(int(random.randrange(0, 765)))

        self.fuel_trim_graph.update_curve("stft1", int(random.randrange(-20, 20)))
        self.fuel_trim_graph.update_curve("stft2", int(random.randrange(-20, 20)))
        self.fuel_trim_graph.update_curve("ltft1", int(random.randrange(-20, 20)))
        self.fuel_trim_graph.update_curve("ltft2", int(random.randrange(-20, 20)))

        self.add_error("test error code")

        load_values = [random.randrange(-20, 20) for _ in range(5)]
        self.torque_graph.update_bars(load_values)

    def create_pages(self):
        # PAGE 1: CURRENT DATA
        self.page_data = QWidget()
        self.main_layout = QGridLayout(self.page_data)
        self.main_layout.setSpacing(15)  # Spacing

        self.fuel_pressure_card = MetricCard("Fuel Pressure", " kPa", "#ffcc00")
        self.speed_card = MetricCard("Engine Speed", " RPM", "#00ff88")
        self.load_card = MetricCard("Engine Load", "%", "#ff4444")
        self.coolant_temp_card = MetricCard("Coolant Temp", " C", "#3820d4")

        self.main_layout.addWidget(self.fuel_pressure_card, 0, 0)
        self.main_layout.addWidget(self.speed_card, 0, 1)
        self.main_layout.addWidget(self.load_card, 0, 2)
        self.main_layout.addWidget(self.coolant_temp_card, 0, 3)

        # self.torque_graph = RealTimePlot("Torque vs RPM", "#ffcc00")
        # self.main_layout.addWidget(self.torque_graph, 1, 0, 1, 2) # Row 1, Col 0, spans 2 cols

        self.torque_graph = BarGraph(
            "Torque vs RPM",
            [
                "Idle",
                "Point 1",
                "Point 2",
                "Point 3",
                "Point 4",
            ],
            color="#ff4444",
        )
        self.torque_graph.setMouseEnabled(x=False, y=False)
        self.torque_graph.hideButtons()
        self.torque_graph.setYRange(-125, 130)
        self.main_layout.addWidget(self.torque_graph, 1, 2, 1, 2)

        self.speed_graph = RealTimePlot("Vehicle Speed (km/h)", "#00d1ff")
        self.main_layout.addWidget(
            self.speed_graph, 1, 0, 1, 2
        )  # Row 1, Col 2, spans 2 cols

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

        if self.serial.open(QSerialPort.OpenModeFlag.ReadOnly):
            print(f"Connected to {target_port}")
        else:
            QMessageBox.critical(self, "Serial Error", f"Could not open {target_port}")

    def handle_serial_data(self):

        while self.serial.canReadLine():
            raw_data = self.serial.readLine().data().decode().strip()

            if "=" in raw_data:
                print(f":{raw_data}")

                try:
                    param, value = raw_data.split("=")

                    if param == "ENGINE_SPEED":
                        self.speed_card.update_value(int(value))

                    elif param == "ENGINE_LOAD":
                        self.load_card.update_value(int(value))

                    elif param == "VEHICLE_SPEED":
                        self.speed_graph.update_plot(int(value))

                    elif param == "COOLANT_TEMP":
                        self.coolant_temp_card.update_value(float(value))

                    elif param == "FUEL_PRESSURE":
                        self.fuel_pressure_card.update_value(int(value))

                    elif param == "STFT1":
                        self.fuel_trim_graph.update_curve("stft1", int(value))

                    elif param == "STFT2":
                        self.fuel_trim_graph.update_curve("stft2", int(value))

                    elif param == "LTFT1":
                        self.fuel_trim_graph.update_curve("ltft1", int(value))

                    elif param == "LTFT2":
                        self.fuel_trim_graph.update_curve("ltft2", int(value))

                    elif param == "ENGINE_PERECENT_TORQUE":
                        tab = [int(x) for x in value.split(",")]

                        if len(tab) == 5:
                            self.torque_graph.update_bars(tab)
                        else:
                            print("torque_graph data list not 5")

                except Exception as e:
                    print(f"Data Parsing Error: {e}\nReceived: {raw_data}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelemetryDashboard()
    window.show()
    sys.exit(app.exec())
