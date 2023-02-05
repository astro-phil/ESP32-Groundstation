import socket
import select
import struct
import threading
from devices import Controls
from PyQt5.QtCore import pyqtSignal
import time
import numpy as np


class Telemetry(object):  #
    def __init__(self) -> None:
        self.engines = [0.0, 0.0, 0.0, 0.0]
        self.attitude = [0.0, 0.0, 0.0]
        self.altitude = 0
        self.cycletime = 0
        self.armed = False
        self.voltage = 0

    def getSize(self):
        return 11


class BlackBox(object):
    def __init__(self, size: int = 10000) -> None:
        self.recording = False
        self.data_length = size
        self.index = 0
        self.storage = np.zeros((self.data_length, 11))
        self.timestamp = np.zeros((self.data_length, 1))
        self.labels = ["Roll", "Pitch", "Yaw", "Engine 1", "Engine 2", "Engine 3", "Engine 4", "Altitude"]

    def start_recording(self):
        self.startTime = time.time()
        self.recording = True
        self.index = 0

    def stop_recording(self):
        self.recording = False

    def record(self, telemetry: Telemetry):
        if not self.recording:
            return
        if self.index >= self.data_length:
            self.recording = False
            return
        data = []
        data.extend(telemetry.attitude)
        data.extend(telemetry.engines)
        data.append(telemetry.altitude)
        data.append(telemetry.voltage)
        data.append(telemetry.cycletime)
        data.append(telemetry.armed)
        self.storage[self.index, :] = np.array(data)
        self.timestamp[self.index] = time.time() - self.startTime
        self.index += 1


class Timeout(object):
    def __init__(self, time) -> None:
        self._time = time
        self.timer = time

    def reset(self):
        self.timer = self._time

    def tick(self):
        self.timer -= 1
        return self.timer > 0


class Tower:
    def __init__(
        self, target: str = "192.168.4.1", port: int = 4321, signalRate: float = 0.02, numberOfTries: int = 4
    ) -> None:
        self.target = target
        self.port = port
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.setblocking(True)
        # self.socket.bind(("", port))
        self.numberOfTries = numberOfTries
        self.connected = False
        self.controlled = False
        self.signalRate = signalRate
        self.socket_blocked = False
        self.telemetryThread = None

    def connectSignals(
        self,
        configSignal: pyqtSignal,
        addItemSignal: pyqtSignal,
        messageSignal: pyqtSignal,
    ) -> None:
        self.addItemSignal = addItemSignal
        self.configSignal = configSignal
        self.messageSignal = messageSignal

    def connectClasses(self, telemetry: Telemetry, blackbox: BlackBox, controls: Controls):
        self.telemetry = telemetry
        self.controls = controls
        self.blackbox = blackbox

    def getHandshake(self, target: str) -> None:
        self.socket_blocked = True
        self.target = target

        error = Exception("Number of tries exceeded!")
        mtype = bytearray(struct.pack("B", 1))
        for _ in range(self.numberOfTries):
            try:
                self.socket.sendto(mtype, (self.target, self.port))
                if select.select([self.socket], [], [], 1.0)[0]:
                    dataPair = self.socket.recvfrom(255)
                    # print("Handshake", dataPair)
                    data = dataPair[0]
                    if mtype == bytearray(data[:1]) and len(data) - 2 == int.from_bytes(
                        bytes=data[1:2], byteorder="big", signed=False
                    ):
                        _parameterIndex = [x for x in data[2:]]
                        break
            except Exception as e:
                error = e

        else:
            self.messageSignal.emit(str(error))
            return

        mtype = bytearray(struct.pack("B", 2))
        _config = dict()
        for id in _parameterIndex:
            for _ in range(self.numberOfTries):
                try:
                    bid = bytearray(struct.pack("B", int(id)))
                    self.socket.sendto(mtype + bid, (self.target, self.port))
                    if select.select([self.socket], [], [], 1.0)[0]:
                        dataPair = self.socket.recvfrom(255)
                        data = dataPair[0]
                        # print("Defaults:", data)
                        if bytearray(data[:2]) == mtype + bid:
                            _config[id] = struct.unpack("f", data[2:])[0]
                            break
                except Exception as e:
                    error = e
            else:
                self.messageSignal.emit(str(error))
                return

        mtype = bytearray(struct.pack("B", 4))
        for _ in range(self.numberOfTries):
            try:
                bid = bytearray(struct.pack("B", int(1)))
                self.socket.sendto(mtype + bid, (self.target, self.port))
                if select.select([self.socket], [], [], 1.0)[0]:
                    dataPair = self.socket.recvfrom(255)
                    data = dataPair[0]
                    # print("Telemetry:", data)
                    if bytearray(data[:2]) == mtype + bid:
                        break
            except Exception as e:
                error = e
        else:
            self.messageSignal.emit(str(error))
            return

        for id, value in _config.items():
            group = GROUPS[int(id / 10) + 1]
            child = NAMES[id]
            self.addItemSignal.emit(group, child, value, id)
        self.connected = True
        self.socket_blocked = False

    def updateConfig(self, config: dict) -> None:
        if not self.connected or self.controls.tr > 0.8:
            return
        self.socket_blocked = True
        _toDelete = []
        mtype = bytearray(struct.pack("B", 3))
        for loc, value in config.items():
            for _ in range(self.numberOfTries):
                try:
                    bid = bytearray(struct.pack("B", int(value[0])))
                    bvalue = bytearray(struct.pack("f", float(value[1])))
                    self.socket.sendto(mtype + bid + bvalue, (self.target, self.port))
                    if select.select([self.socket], [], [], 2.0)[0]:
                        dataPair = self.socket.recvfrom(1024)
                        if dataPair[0] == mtype + bid + bvalue:
                            _toDelete.append(loc)
                            self.configSignal.emit(loc, "#00a000")
                            break
                except Exception as e:
                    print(e)
            else:
                self.configSignal.emit(loc, "#a00000")
        for loc in _toDelete:
            del config[loc]
        self.socket_blocked = False

    def runTelemetry(self) -> None:
        if self.telemetryThread != None:
            return
        self.telemetryThread = threading.Thread(target=self._runTelemetry, args=())
        self.telemetryThread.daemon = True
        self.telemetryThread.start()

    def _runTelemetry(self) -> None:
        mtype = bytearray(struct.pack("B", 10))
        timer = Timeout(4)
        while self.connected and timer.tick():
            if select.select([self.socket], [], [], 1.0)[0] and not self.socket_blocked:
                data = self.socket.recvfrom(1024)[0]
                if mtype == bytearray(data[:1]):
                    self.telemetry.cycletime = struct.unpack("B", data[1:2])[0]
                    self.telemetry.armed = struct.unpack("B", data[2:3])[0] != 0
                    # Attitude
                    self.telemetry.attitude[0] = struct.unpack("h", data[3:5])[0] / 160.0
                    self.telemetry.attitude[1] = struct.unpack("h", data[5:7])[0] / 160.0
                    self.telemetry.attitude[2] = struct.unpack("h", data[7:9])[0] / 160.0
                    # Engines
                    self.telemetry.engines[0] = (struct.unpack("H", data[9:11])[0] - 3277) / 3277
                    self.telemetry.engines[1] = (struct.unpack("H", data[11:13])[0] - 3277) / 3277
                    self.telemetry.engines[2] = (struct.unpack("H", data[13:15])[0] - 3277) / 3277
                    self.telemetry.engines[3] = (struct.unpack("H", data[15:17])[0] - 3277) / 3277
                    # Stuff
                    self.telemetry.altitude = struct.unpack("H", data[17:19])[0]
                    self.telemetry.voltage = int(struct.unpack("H", data[19:21])[0] / 3)
                    self.blackbox.record(self.telemetry)
                    timer.reset()
            elif self.socket_blocked:
                timer.reset()
        self.messageSignal.emit("Copter Disconnected!")
        self.connected = False

    def runControl(self) -> None:
        if self.controlled:
            return
        self.controlThread = threading.Thread(target=self._runControl, args=())
        self.controlThread.daemon = True
        self.controlled = True
        self.controlThread.start()

    def _runControl(self) -> None:
        mtype = bytearray(struct.pack("B", 20))
        while self.connected and self.controlled:
            barm = bytearray(struct.pack("B", int(self.controls.tr > 0.8)))  # arm
            bptch = bytearray(struct.pack("h", int(self.controls.ry * 32000)))
            brll = bytearray(struct.pack("h", int(self.controls.rx * 32000)))
            byaw = bytearray(struct.pack("h", int(-self.controls.lx * 32000)))
            bthr = bytearray(struct.pack("h", int(-self.controls.ly * 32000)))
            if not self.socket_blocked:
                self.socket.sendto(mtype + barm + bptch + brll + byaw + bthr, (self.target, self.port))
            time.sleep(self.signalRate)
        self.controlled = False


GROUPS = dict()
GROUPS[1] = "System"
GROUPS[2] = "User"
GROUPS[3] = "Yaw PID"
GROUPS[4] = "RollPitch PID"
GROUPS[5] = "Altitude PID"

NAMES = dict()
for i in range(255):
    NAMES[i] = "Unkown"
NAMES[1] = "Flight mode"
NAMES[2] = "Telemtry FPC"
NAMES[3] = "Altitude Filter"
NAMES[4] = "Voltage Filter"
NAMES[11] = "Thrust Sens"
NAMES[12] = "Pitch & Roll Sens"
NAMES[13] = "Yaw Sens"
NAMES[21] = "Yaw P"
NAMES[22] = "Yaw I"
NAMES[23] = "Yaw D"
NAMES[24] = "Yaw A"
NAMES[25] = "YawDt P"
NAMES[26] = "YawDt I"
NAMES[27] = "YawDt D"
NAMES[28] = "YawDt A"
NAMES[31] = "PR P"
NAMES[32] = "PR I"
NAMES[33] = "PR D"
NAMES[34] = "PR A"
NAMES[35] = "PRdt P"
NAMES[36] = "PRdt I"
NAMES[37] = "PRdt D"
NAMES[38] = "PRdt A"
NAMES[41] = "Alt P"
NAMES[42] = "Alt I"
NAMES[43] = "Alt D"
NAMES[44] = "Alt A"
