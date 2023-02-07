# pylint: disable=missing-docstring
import sys
import matplotlib

matplotlib.use("Qt5Agg")
from classes import Horizon, Configuration, ControlStick, DroneThrust, Heading, DataSelector, PlotCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from connection import Tower, Telemetry, BlackBox
from devices import XboxController, Controls
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QTabWidget,
    QGridLayout,
    QWidget,
    QFrame,
    QApplication,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QLabel,
)


class MainWindow(QWidget):
    configUpdate = pyqtSignal(str, str)
    addItem = pyqtSignal(str, str, float, int)
    messageSignal = pyqtSignal(str)
    controlSignal = pyqtSignal()
    periodic = QTimer()

    def __init__(self, size=()):
        super(MainWindow, self).__init__()
        self.wt_root = QWidget()
        self.wt_root.resize(1920, 1100)
        self.wt_root.setWindowTitle("Horizon")

        # Layout
        self.lt_main = QHBoxLayout()
        self.wt_root.setLayout(self.lt_main)
        self.fe_info = QFrame()
        self.lt_main.addWidget(self.fe_info)
        self.lt_info = QVBoxLayout()
        self.fe_info.setLayout(self.lt_info)

        self.fe_connect = QFrame()
        self.lt_connect = QHBoxLayout()
        self.fe_connect.setLayout(self.lt_connect)
        self.lt_info.addWidget(self.fe_connect)

        self.tb_main = QTabWidget()
        self.tb_main.setFont(QFont("Times font", 10))
        self.fe_animation = QFrame()
        self.fe_graph = QFrame()
        self.tb_main.addTab(self.fe_animation, "Animation")
        self.tb_main.addTab(self.fe_graph, "Graphs")
        self.lt_main.addWidget(self.tb_main)
        self.lt_animation = QGridLayout()
        self.fe_animation.setLayout(self.lt_animation)
        self.lt_graph = QGridLayout()
        self.fe_graph.setLayout(self.lt_graph)

        # Animation
        self.ll_ip = QLabel(self.fe_connect)
        self.ll_ip.setText("IP.Adresse:")
        self.lt_connect.addWidget(self.ll_ip)
        self.le_ip = QLineEdit(self.fe_connect)
        self.le_ip.setText("192.168.4.1")
        self.lt_connect.addWidget(self.le_ip)
        self.pb_connect = QPushButton("connect", self.fe_info)
        self.lt_info.addWidget(self.pb_connect)
        self.config = Configuration(self.fe_info)
        self.lt_info.addWidget(self.config.getWidget())
        self.pb_update = QPushButton("write config", self.fe_info)
        self.lt_info.addWidget(self.pb_update)
        self.pb_connect.clicked.connect(self.connect)
        self.pb_update.clicked.connect(self.configurate)

        self.horizon = Horizon(None, size=(900, 900))
        self.control_left = ControlStick(size=(300, 300))
        self.control_right = ControlStick(size=(300, 300))
        self.drone_thrust = DroneThrust()
        self.heading = Heading()
        self.controls = Controls()
        self.controller = XboxController(self.controls, 1)
        self.controller.connectSignals(self.controlSignal, self.messageSignal)

        self.blackbox = BlackBox()
        self.telemetry = Telemetry()
        self.tower = Tower()
        self.tower.connectSignals(self.configUpdate, self.addItem, self.messageSignal)
        self.tower.connectClasses(self.telemetry, self.blackbox, self.controls)
        self.configUpdate.connect(self.config.changeColor)
        self.addItem.connect(self.config.addItem)
        self.messageSignal.connect(self.showDialog)
        self.periodic.timeout.connect(self.redrawTelemetry)
        self.controlSignal.connect(self.redrawControl)

        self.lt_animation.addWidget(self.control_left.getWidget(), 1, 0)
        self.lt_animation.addWidget(self.heading.getWidget(), 0, 0)
        self.lt_animation.addWidget(self.horizon.getWidget(), 0, 1, 2, 1)
        self.lt_animation.addWidget(self.control_right.getWidget(), 1, 2)
        self.lt_animation.addWidget(self.drone_thrust.getWidget(), 0, 2)

        # Graph
        self.figure = PlotCanvas(self.fe_graph)
        self.figure.setBlackBox(self.blackbox)
        self.navbar = NavigationToolbar2QT(self.figure, self.fe_graph)
        self.lt_graph.addWidget(self.navbar, 0, 1)
        self.lt_graph.addWidget(self.figure, 1, 1)
        self.selector = DataSelector(self.fe_graph)
        self.selector.setPointer(self.figure, self.blackbox)
        self.lt_graph.addWidget(self.selector.getWidget(), 0, 0, 2, 1)

    def connect(self):
        self.config.clear()
        self.tower.getHandshake(self.le_ip.text())
        self.tower.runTelemetry()
        self.tower.runControl()

    def configurate(self):
        self.tower.updateConfig(self.config.getDiff())

    def showDialog(self, message):
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setText(message)
        msgbox.setWindowTitle("Information")
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgbox.exec_()

    def redrawTelemetry(self):
        eng = self.telemetry.engines
        if self.tb_main.currentIndex() == 0:
            self.drone_thrust.update(eng[0], eng[1], eng[2], eng[3])
            att = self.telemetry.attitude
            self.horizon.update(att[0], att[1], self.telemetry.altitude, self.telemetry.voltage)
            self.heading.update(att[2])
            self.wt_root.update()
        elif self.tb_main.currentIndex() == 1:
            self.figure.drawPlot()

    def redrawControl(self):
        if self.tb_main.currentIndex() == 0:
            self.control_left.update(self.controls.lx, self.controls.ly)
            self.control_right.update(self.controls.rx, self.controls.ry)
            self.wt_root.update()

    def show(self):
        self.control_left.update(0.0, 0.0)
        self.horizon.update()
        self.heading.update(0)
        self.control_right.update(0.0, 0.0)
        self.drone_thrust.update(0.0, 0.0, 0.0, 0.0)
        self.controller.connect()
        self.periodic.setInterval(25)
        self.periodic.start()
        self.wt_root.show()


app = QApplication(sys.argv)
main = MainWindow()
app.setStyle("Oxygen")
main.show()
sys.exit(app.exec_())
