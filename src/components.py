from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class MetricCard(QFrame):
    def __init__(self, title, unit="", color="#00d1ff"):
        super().__init__()
        self.setObjectName("Card")
        self.setMinimumSize(140, 100)
        layout = QVBoxLayout(self)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("Title")
        self.value_label = QLabel("0.0")
        self.value_label.setObjectName("Value")
        self.value_label.setStyleSheet(f"color: {color};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit = unit

        self.setStyleSheet("""QFrame#Card {
            background-color: #1e1e1e;
            border-radius: 8px;
            border: 1px solid #333;
        }""")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def update_value(self, value):
        self.value_label.setText(f"{value}{self.unit}")

class ErrorCard(QFrame):
    def __init__(self, message, timestamp=""):
        super().__init__()
        self.setObjectName("ErrorCard")
        self.setMaximumHeight(50)
        self.setMinimumHeight(50)

        # Specific styling for Errors
        self.setStyleSheet("""
            QFrame#ErrorCard {
                background-color: #2d1a1a;
                border-radius: 6px;
                border: 1px solid #ff4444;
                margin-bottom: 5px;
            }
            QLabel { color: #ff9999; font-size: 13px; }
            QLabel#Timestamp { color: #886666; font-size: 11px; }
        """)

        layout = QVBoxLayout(self)

        if timestamp:
            self.time_label = QLabel(timestamp)
            self.time_label.setObjectName("Timestamp")
            layout.addWidget(self.time_label)

        self.msg_label = QLabel(message)
        self.msg_label.setWordWrap(True)
        layout.addWidget(self.msg_label)
