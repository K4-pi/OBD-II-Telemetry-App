from PyQt6.QtSvg import QSvgGenerator
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtCore import QRect, Qt, QRectF

import datetime

class Report:
    def __init__(self, telemetry_data):
        self.data = telemetry_data

    def generate_svg(self, filename, graph_widgets=None):
        generator = QSvgGenerator()
        generator.setFileName(filename)
        # generator.setSize(800, 1100)
        generator.setViewBox(QRect(0, 0, 800, 1100))
        generator.setTitle("OBD-II Telemetry Report")
        generator.setDescription(f"Generated on {datetime.datetime.now()}")

        painter = QPainter()
        painter.begin(generator)

        # HEADER
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(40, 60, "Telemetry Session Report")

        painter.setFont(QFont("Arial", 10))
        painter.drawText(40, 90, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # STATS
        avg_speed = sum(self.data['speed']) / len(self.data['speed']) if self.data['speed'] else 0
        avg_rpm = sum(self.data['rpm']) / len(self.data['rpm']) if self.data['rpm'] else 0

        max_load = max(self.data['load']) if self.data['load'] else 0
        max_coolant = max(self.data['coolant']) if self.data['coolant'] else 0
        min_coolant = min(self.data['coolant']) if self.data['coolant'] else 0

        max_oil_temp = max(self.data['oil_temp']) if self.data['oil_temp'] else 0
        min_oil_temp = min(self.data['oil_temp']) if self.data['oil_temp'] else 0

        stats_text = (
            f"Average Speed: {avg_speed:.2f} km/h\n"
            f"Average Engine Speed: {avg_rpm:.2f} RPM\n"
            f"Maximum Engine Load: {max_load} %\n\n"

            f"Highest Coolant Temp: {max_coolant} C\n"
            f"Lowest Coolant Temp: {min_coolant} C\n"
            f"Highest Oil Temp: {max_oil_temp} C\n"
            f"Lowest Oil Temp: {min_oil_temp} C\n"

            f"Data Points Collected: {len(self.data['speed'])}"
        )

        painter.setFont(QFont("Arial", 12))
        painter.drawText(QRect(40, 130, 720, 100), Qt.AlignmentFlag.AlignLeft, stats_text)

        # EXPORT GRAPHS
        if graph_widgets:

            current_y = 270
            graph_height = 400

            for g in graph_widgets:
                target_rect = QRect(40, current_y, 720, graph_height)

                g.render(painter, QRectF(target_rect))

                current_y += (graph_height + 50)

        painter.end()

        print(f"Report saved as {filename}")
