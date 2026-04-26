from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QLabel)
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

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def update_value(self, value):
        self.value_label.setText(f"{value}{self.unit}")
