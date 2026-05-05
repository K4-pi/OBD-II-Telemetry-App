import time
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
        axis = pg.DateAxisItem(orientation='bottom')
        super().__init__(axisItems={'bottom': axis})
        self.setBackground("#1e1e1e")
        self.setTitle(title, color="#888", size="10pt")
        self.showGrid(x=True, y=True, alpha=0.3)
        self.curve = self.plot(pen=pg.mkPen(color=color, width=2))
        self.data = []
        self.timestamps = []

    def update_plot(self, new_point, current_time):
        self.timestamps.append(current_time)
        self.data.append(new_point)

        self.curve.setData(self.timestamps, self.data)


# class BarGraph(pg.PlotWidget):
#     def __init__(self, title, categories, color="#00d1ff"):
#         super().__init__()
#         self.setBackground("#1e1e1e")
#         self.setTitle(title, color="#888", size="10pt")

#         # Define categories (x-axis positions)
#         self.categories = categories
#         self.x = np.arange(len(categories))
#         self.heights = np.zeros(len(categories))

#         # Create BarGraphItem
#         self.bar_item = pg.BarGraphItem(
#             x=self.x, height=self.heights, width=0.6, brush=color
#         )
#         self.addItem(self.bar_item)

#         self.getAxis("bottom").setTicks(
#             [[(i, label) for i, label in enumerate(categories)]]
#         )

#     def update_bars(self, new_heights):
#         self.heights = new_heights
#         self.bar_item.setOpts(height=self.heights)
