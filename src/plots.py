import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class MultiRealTimePlot(pg.PlotWidget):
    def __init__(self, title):
        super().__init__()
        self.setBackground("#1e1e1e")
        self.setTitle(title, color="#888", size="10pt")
        self.showGrid(x=True, y=True, alpha=0.3)

        self.addLegend(offset=(30, 30))

        self.curves = {}
        self.data_storage = {}

    def add_curve(self, name, color):
        pen = pg.mkPen(color=color, width=2)
        self.curves[name] = self.plot(pen=pen, name=name)
        self.data_storage[name] = []

    def update_curve(self, name, new_point):
        if name in self.curves:
            self.data_storage[name].append(new_point)

            # Limit to 100 points
            # if len(self.data_storage[name]) > 100:
            #     self.data_storage[name].pop(0)

            self.curves[name].setData(self.data_storage[name])


class RealTimePlot(pg.PlotWidget):
    def __init__(self, title, color="#00d1ff"):
        super().__init__()
        self.setBackground("#1e1e1e")
        self.setTitle(title, color="#888", size="10pt")
        self.showGrid(x=True, y=True, alpha=0.3)
        self.curve = self.plot(pen=pg.mkPen(color=color, width=2))
        self.data = []

    def update_plot(self, new_point):
        self.data.append(new_point)
        # if len(self.data) > 100:
        #     self.data.pop(0)

        self.curve.setData(self.data)


class BarGraph(pg.PlotWidget):
    def __init__(self, title, categories, color="#00d1ff"):
        super().__init__()
        self.setBackground("#1e1e1e")
        self.setTitle(title, color="#888", size="10pt")

        # Define categories (x-axis positions)
        self.categories = categories
        self.x = np.arange(len(categories))
        self.heights = np.zeros(len(categories))

        # Create BarGraphItem
        self.bar_item = pg.BarGraphItem(
            x=self.x, height=self.heights, width=0.6, brush=color
        )
        self.addItem(self.bar_item)

        self.getAxis("bottom").setTicks(
            [[(i, label) for i, label in enumerate(categories)]]
        )

    def update_bars(self, new_heights):
        self.heights = new_heights
        self.bar_item.setOpts(height=self.heights)


class RpmSpeedPlot(pg.PlotWidget):
    def __init__(self, title):
        super().__init__()
        self.setBackground("#1e1e1e")
        self.setTitle(title, color="#888", size="10pt")

        # Oś Lewa (RPM)
        self.p1 = self.getPlotItem()
        self.p1.setLabel("left", "Obroty (RPM)", color="#00ff88")
        self.p1.showGrid(x=True, y=True, alpha=0.2)

        # Oś Prawa (Prędkość)
        self.p2 = pg.ViewBox()
        self.p1.scene().addItem(self.p2)
        self.p1.getAxis("right").linkToView(self.p2)
        self.p2.setXLink(self.p1)
        self.p1.getAxis("right").setLabel("Prędkość (km/h)", color="#00d1ff")

        # Krzywe
        self.curve_rpm = self.p1.plot(pen=pg.mkPen(color="#00ff88", width=2))
        self.curve_speed = pg.PlotCurveItem(pen=pg.mkPen(color="#00d1ff", width=2))
        self.p2.addItem(self.curve_speed)

        self.data_rpm = []
        self.data_speed = []

        # Synchronizacja osi przy zmianie rozmiaru okna
        self.p1.getViewBox().sigResized.connect(self.update_views)
        self.update_views()

    def update_views(self):
        self.p2.setGeometry(self.p1.getViewBox().sceneBoundingRect())
        self.p2.linkedViewChanged(self.p1.getViewBox(), self.p2.XAxis)

    def update_plot(self, rpm=None, speed=None):
        if rpm is not None:
            self.data_rpm.append(rpm)
        if speed is not None:
            self.data_speed.append(speed)

        # Limit punktów (np. ostatnie 150)
        self.data_rpm = self.data_rpm[-150:]
        self.data_speed = self.data_speed[-150:]

        self.curve_rpm.setData(self.data_rpm)
        self.curve_speed.setData(self.data_speed)
