from math import cos, sin
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygon, QPixmap, QColor, QFont, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QLabel,
    QTreeView,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QAbstractItemView,
)
from PyQt5.QtCore import Qt, QPoint
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from connection import Telemetry, BlackBox


class Heading:
    def __init__(self, parent=None, size=(300, 300)):
        self.label = QLabel()
        self.size = size
        self.parent = parent
        canvas = QPixmap(size[0], size[1])
        self.label.setPixmap(canvas)
        self.white = QColor("#ffffff")
        self.black = QColor("#000000")
        self.red = QColor("#a00000")

    def update(
        self,
        yaw=0,
    ):
        iyaw = -int(yaw)
        painter = QPainter(self.label.pixmap())
        painter.setBrush(QBrush(self.white))
        painter.setPen(QPen(self.white, 2, Qt.PenStyle.SolidLine))
        painter.drawRect(0, 0, self.size[0], self.size[1])
        painter.translate(self.size[0] / 2, self.size[1] / 2)
        painter.setPen(QPen(self.black, 2, Qt.PenStyle.DashLine))
        painter.drawEllipse(
            -int(self.size[0] / 3), -int(self.size[1] / 3), int(self.size[0] / 1.5), int(self.size[1] / 1.5)
        )
        painter.drawLine(0, int(self.size[1] / 2), 0, -int(self.size[1] / 2))
        painter.rotate(iyaw)
        painter.setBrush(QBrush(self.red))
        painter.setPen(QPen(self.red, 2, Qt.PenStyle.SolidLine))
        painter.drawLine(0, int(self.size[1] / 2.5), 0, -int(self.size[1] / 2.5))
        points = [
            QPoint(0, -int(self.size[1] / 4)),
            QPoint(-int(self.size[0] / 6), int(self.size[1] / 5)),
            QPoint(int(self.size[0] / 6), int(self.size[1] / 5)),
        ]
        poly = QPolygon(points)
        painter.drawPolygon(poly)

    def getWidget(self):
        return self.label


class DroneThrust:
    def __init__(self, parent=None, size=(300, 300)):
        self.label = QLabel()
        self.size = size
        self.parent = parent
        canvas = QPixmap(size[0], size[1])
        self.label.setPixmap(canvas)
        self.white = QColor("#ffffff")
        self.black = QColor("#000000")
        self.red = QColor("#a00000")

    def update(self, eng1=0, eng2=0, eng3=0, eng4=0):
        ieng1 = int(eng1 * 70)
        ieng2 = int(eng2 * 70)
        ieng3 = int(eng3 * 70)
        ieng4 = int(eng4 * 70)
        painter = QPainter(self.label.pixmap())
        painter.setBrush(QBrush(self.white))
        painter.setPen(QPen(self.white, 2, Qt.PenStyle.SolidLine))
        painter.drawRect(0, 0, self.size[0], self.size[1])
        painter.translate(self.size[0] / 2, self.size[1] / 2)

        painter.setPen(QPen(self.black, 2, Qt.PenStyle.SolidLine))
        painter.drawEllipse(int(-self.size[0] / 4 - 45), int(-self.size[1] / 4 - 45), 90, 90)
        painter.drawEllipse(int(self.size[0] / 4 - 45), int(-self.size[1] / 4 - 45), 90, 90)
        painter.drawEllipse(int(self.size[0] / 4 - 45), int(self.size[1] / 4 - 45), 90, 90)
        painter.drawEllipse(int(-self.size[0] / 4 - 45), int(self.size[1] / 4 - 45), 90, 90)
        painter.setPen(QPen(self.red, 20, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(self.red))
        painter.drawEllipse(int(-self.size[0] / 4 - ieng1 / 2), int(-self.size[1] / 4 - ieng1 / 2), ieng1, ieng1)
        painter.drawEllipse(int(self.size[0] / 4 - ieng2 / 2), int(-self.size[1] / 4 - ieng2 / 2), ieng2, ieng2)  #
        painter.drawEllipse(int(-self.size[0] / 4 - ieng3 / 2), int(self.size[1] / 4 - ieng3 / 2), ieng3, ieng3)
        painter.drawEllipse(int(self.size[0] / 4 - ieng4 / 2), int(self.size[1] / 4 - ieng4 / 2), ieng4, ieng4)

        painter.setPen(QPen(self.black, 2, Qt.PenStyle.SolidLine))
        painter.drawLine(int(-self.size[0] / 4), int(self.size[1] / 4), int(self.size[0] / 4), int(-self.size[1] / 4))
        painter.drawLine(int(-self.size[0] / 4), int(-self.size[1] / 4), int(self.size[0] / 4), int(self.size[1] / 4))
        painter.end()

    def getWidget(self):
        return self.label


class ControlStick:
    def __init__(self, parent=None, size=(200, 200)):
        self.label = QLabel()
        self.size = size
        self.parent = parent
        canvas = QPixmap(size[0], size[1])
        self.label.setPixmap(canvas)
        self.white = QColor("#ffffff")
        self.black = QColor("#000000")
        self.red = QColor("#a00000")

    def update(self, x=0, y=0):
        ix = int(self.size[0] * x * 0.5)
        iy = int(self.size[0] * y * 0.5)
        painter = QPainter(self.label.pixmap())
        painter.setBrush(QBrush(self.white))
        painter.setPen(QPen(self.white, 2, Qt.PenStyle.SolidLine))
        painter.drawRect(0, 0, self.size[0], self.size[1])
        painter.translate(self.size[0] / 2, self.size[1] / 2)
        painter.setPen(QPen(self.black, 2, Qt.PenStyle.DashLine))
        painter.drawLine(0, int(self.size[1] / 2.1), 0, int(-self.size[1] / 2.1))
        painter.drawLine(int(self.size[0] / 2.1), 0, int(-self.size[0] / 2.1), 0)

        painter.setPen(QPen(self.red, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(self.red))
        painter.drawEllipse(ix - 10, iy - 10, 20, 20)
        painter.end()

    def getWidget(self):
        return self.label


class Horizon:
    def __init__(self, parent=None, size=(1000, 1000)):
        self.label = QLabel()
        self.size = size
        self.parent = parent
        canvas = QPixmap(size[0], size[1])
        self.label.setPixmap(canvas)
        self.ground = QColor("#9c3e00")
        self.sky = QColor("#00bfff")
        self.black = QColor("#000000")
        self.grey = QColor("#D0D0D0")
        self.red = QColor("#FF0000")

    def update(self, pitchDeg=0, rollDeg=0, altitude=0, voltage=0):
        roll = rollDeg * 3.14159 / 180
        pitch = pitchDeg * 3.14159 / 180

        painter = QPainter(self.label.pixmap())
        painter.setPen(QPen(self.ground, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(self.ground, 1))
        painter.drawRect(0, 0, self.size[0], self.size[1])

        painter.translate(
            self.size[0] / 2 - sin(-roll) * sin(pitch) * self.size[0] / 2,
            self.size[0] / 2 + pitchDeg * self.size[1] / 100 * cos(-roll),
        )

        painter.setPen(QPen(self.sky, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(self.sky, 1))

        painter.rotate(-rollDeg)
        painter.drawRect(int(-self.size[0]), int(-self.size[0] * 2), int(self.size[0] * 2), int(self.size[1] * 2))
        painter.setFont(QFont("Decorative", 10))
        painter.setPen(QPen(self.black, 2, Qt.PenStyle.SolidLine))
        for x in range(-9, 9):
            if x % 2 == 0:
                painter.drawText(0, int(self.size[1] * x / 9), "{}°".format(10 * x))
                painter.drawLine(
                    int(-self.size[0] / 6), int(self.size[1] * x / 9), int(self.size[0] / 6), int(self.size[1] * x / 9)
                )
            else:
                painter.drawLine(
                    int(-self.size[0] / 12),
                    int(self.size[1] * x / 9),
                    int(self.size[0] / 12),
                    int(self.size[1] * x / 9),
                )

        painter.rotate(rollDeg)
        painter.translate(sin(-roll) * sin(pitch) * self.size[0] / 2, -pitchDeg * self.size[1] / 100 * cos(-roll))
        painter.setBrush(QBrush(self.grey, 1))
        painter.drawRect(int(self.size[0] / 3.95), -40, 100, 80)
        if voltage < 3500:
            painter.setBrush(QBrush(self.red, 1))
        painter.drawRect(-int(self.size[0] / 3.95) - 100, -40, 100, 80)

        painter.setPen(QPen(self.black, 10, Qt.PenStyle.SolidLine))
        painter.drawLine(int(-self.size[0] / 4), int(+self.size[1] / 3), int(-self.size[0] / 4), int(-self.size[1] / 3))
        painter.drawLine(int(self.size[0] / 4), int(+self.size[1] / 3), int(self.size[0] / 4), int(-self.size[1] / 3))
        painter.setFont(QFont("Decorative", 13))

        painter.drawText(-int(self.size[0] / 2.9), 0, "{:04d}".format(int(voltage)))
        painter.drawText(int(self.size[0] / 3.7), 0, "{:04d}".format(int(altitude)))
        painter.setFont(QFont("Decorative", 9))
        painter.drawText(-int(self.size[0] / 3.05), 30, "V")
        painter.drawText(int(self.size[0] / 3.4), 30, "mm")

        painter.end()
        # self.root.update()

    def getWidget(self):
        return self.label


class Configuration:
    def __init__(self, parent=None):
        self.parent = parent
        self.marked = set()
        self.diff = dict()
        self.parents = dict()

        self.fe = QFrame()
        self.lt = QVBoxLayout()
        self.fe.setLayout(self.lt)

        self.le = QLabel()
        self.le.setText("Configuration")
        self.le.setFont(QFont("Arial", 13))
        self.lt.addWidget(self.le)

        self.tv = QTreeView()
        self.lt.addWidget(self.tv)

        self.ml = QStandardItemModel(0, 3, self.tv)
        self.ml.setHeaderData(0, Qt.Horizontal, "Name")
        self.ml.setHeaderData(1, Qt.Horizontal, "Value")
        self.ml.setHeaderData(2, Qt.Horizontal, "ID")
        self.tv.setModel(self.ml)

        self.tv.doubleClicked.connect(self._onEdit)
        self.tv.expandAll()

    def addParent(self, name):
        nametem = QStandardItem(str(name))
        nametem.setEditable(False)
        nonetem = QStandardItem("None")
        nonetem.setEditable(False)
        noidtem = QStandardItem("None")
        noidtem.setEditable(False)
        self.ml.appendRow([nametem, nonetem, noidtem])
        self.parents[name] = nametem

    def addItem(self, group, child, value, id):
        nametem = QStandardItem(str(child))
        nametem.setEditable(False)
        idtem = QStandardItem(str(id))
        idtem.setEditable(False)
        valuetem = QStandardItem(str(round(value, 6)))
        if group not in self.parents.keys():
            self.addParent(group)
        self.parents[group].appendRow([nametem, valuetem, idtem])
        self.tv.expandAll()

    def _onEdit(self, index):
        if index.column() == 1 and index.sibling(index.row(), 1).data() != "None":
            # print(index.parent().row(), index.row(), index.sibling(index.row(), 1).data())
            # print(
            self.ml.setData(index.sibling(index.row(), 0), QBrush(Qt.blue), Qt.ForegroundRole)
            self.ml.setData(index.sibling(index.row(), 1), QBrush(Qt.blue), Qt.ForegroundRole)
            self.ml.setData(index.sibling(index.row(), 2), QBrush(Qt.blue), Qt.ForegroundRole)
            self.marked.add(str(index.parent().row()) + ":" + str(index.row()))

    def getDiff(self):
        for loc in self.marked:
            row = loc.split(":")
            row_parent = int(row[0])
            row_child = int(row[1])
            self.diff[loc] = (
                self.ml.index(row_child, 2, parent=self.ml.index(row_parent, 0)).data(),
                self.ml.index(row_child, 1, parent=self.ml.index(row_parent, 0)).data(),
            )
        self.marked.clear()
        return self.diff

    def changeColor(self, location, color):
        row = location.split(":")
        row_parent = int(row[0])
        row_child = int(row[1])
        self.ml.setData(
            self.ml.index(row_child, 0, parent=self.ml.index(row_parent, 0)), QBrush(QColor(color)), Qt.ForegroundRole
        )
        self.ml.setData(
            self.ml.index(row_child, 1, parent=self.ml.index(row_parent, 0)), QBrush(QColor(color)), Qt.ForegroundRole
        )
        self.ml.setData(
            self.ml.index(row_child, 2, parent=self.ml.index(row_parent, 0)), QBrush(QColor(color)), Qt.ForegroundRole
        )
        pass

    def clear(self):
        self.parents = dict()
        self.ml.clear()
        self.ml = QStandardItemModel(0, 3, self.tv)
        self.ml.setHeaderData(0, Qt.Horizontal, "Name")
        self.ml.setHeaderData(1, Qt.Horizontal, "Value")
        self.ml.setHeaderData(2, Qt.Horizontal, "ID")
        self.tv.setModel(self.ml)

    def getWidget(self):
        return self.fe


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.index2plot = []
        self.window_size = 100
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("PyQt Matplotlib Example")
        self.colors = ["r-", "g-", "b-", "y-"]
        self.draw()

    def setBlackBox(self, blackbox: BlackBox):
        self.blackbox = blackbox

    def start(self, index2plot):
        self.index2plot = index2plot
        self.ax.cla()
        self.ax.set_title("PyQt Matplotlib Example")
        self.lines = []

    def updatePlot(self, index2plot):
        if self.blackbox.index < self.window_size:
            return
        self.index2plot = index2plot
        self.lines = []
        lim_max = []
        lim_min = []
        for i in index2plot:
            lim_max.append(np.max(self.blackbox.storage[: self.blackbox.index, i]))
            lim_min.append(np.min(self.blackbox.storage[: self.blackbox.index, i]))
        self.ax.cla()
        for x, i in enumerate(self.index2plot):
            (line,) = self.ax.plot(
                range(self.window_size),
                self.blackbox.storage[self.blackbox.index - self.window_size : self.blackbox.index, i],
                self.colors[x],
                linewidth=1,
                label=self.blackbox.labels[i],
            )
            self.lines.append(line)
        self.ax.set_ylim([min(lim_min), max(lim_max)])
        self.ax.legend()
        self.draw()

    def end(self):
        self.ax.cla()
        for x, i in enumerate(self.index2plot):
            self.ax.plot(
                self.blackbox.timestamp[: self.blackbox.index],
                self.blackbox.storage[: self.blackbox.index, i],
                self.colors[x],
                linewidth=0.5,
                label=self.blackbox.labels[i],
            )
        self.draw()

    def drawPlot(self):
        if not self.blackbox.recording:
            return
        if self.blackbox.index >= self.window_size and len(self.lines) == 0:
            for x, i in enumerate(self.index2plot):
                (line,) = self.ax.plot(
                    range(self.window_size),
                    self.blackbox.storage[self.blackbox.index - self.window_size : self.blackbox.index, i],
                    self.colors[x],
                    linewidth=1,
                    label=self.blackbox.labels[i],
                )
                self.lines.append(line)
            self.ax.legend()
        if self.blackbox.index > self.window_size:
            for x, i in enumerate(self.index2plot):
                self.lines[x].set_ydata(
                    self.blackbox.storage[self.blackbox.index - self.window_size : self.blackbox.index, i]
                )
        self.draw()


class DataSelector:
    def __init__(self, parent=None, width=300) -> None:
        self.parent = parent
        self.width = width

        self.fe = QFrame()
        self.lt = QVBoxLayout()
        self.fe.setLayout(self.lt)

        self.le = QLabel(self.fe)
        self.le.setText("Telemetry")
        self.le.setFont(QFont("Arial", 13))
        self.lt.addWidget(self.le)

        self.list = QListWidget(self.fe)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lt.addWidget(self.list)
        self.fe.setMaximumWidth(width)

        self.fess = QFrame()
        self.ltss = QHBoxLayout()
        self.fess.setLayout(self.ltss)
        self.lt.addWidget(self.fess)

        self.bpst = QPushButton(self.fess)
        self.bpst.setText("Start Recording")
        self.bpst.clicked.connect(self.toggleRecording)
        self.ltss.addWidget(self.bpst)

        self.bpue = QPushButton(self.fe)
        self.bpue.setText("Update plot")
        self.bpue.clicked.connect(self.updatePlot)
        self.lt.addWidget(self.bpue)

    def setPointer(self, canvas: PlotCanvas, blackbox: BlackBox):
        self.canvas = canvas
        self.blackbox = blackbox
        self.list.addItems(self.blackbox.labels)

    def toggleRecording(self):
        if not self.blackbox.recording:
            self.bpst.setText("End Recording")
            selectedIndex = []
            for item in self.list.selectedItems():
                selectedIndex.append(self.list.indexFromItem(item).row())
            self.canvas.start(selectedIndex)
            self.blackbox.start_recording()
        else:
            self.bpst.setText("Start Recording")
            self.canvas.end()
            self.blackbox.stop_recording()

    def updatePlot(self):
        selectedIndex = []
        for item in self.list.selectedItems():
            selectedIndex.append(self.list.indexFromItem(item).row())
        self.canvas.updatePlot(selectedIndex)
        pass

    def getWidget(self):
        return self.fe
