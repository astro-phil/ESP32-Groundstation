from inputs import get_gamepad
import math
import threading
from PyQt5.QtCore import pyqtSignal

DEADZONE = 0.008
EXPO = 1.5


class Controls(object):
    rx = 0
    ry = 0
    lx = 0
    ly = 0
    tr = 0

    def __init__(self) -> None:
        pass


class XboxController(object):
    MAX_JOY_VAL = math.pow(2, 15)
    MAX_TRIG_VAL = math.pow(2, 8)

    def __init__(self, controls: Controls, frameskip: int) -> None:
        self.controls = controls
        self.frameskip = frameskip

    def connectSignals(self, controlSignal: pyqtSignal, messageSignal: pyqtSignal) -> None:
        self.controlSignal = controlSignal
        self.messageSignal = messageSignal

    def connect(self) -> None:
        self.telemetryThread = threading.Thread(target=self._connect, args=())
        self.telemetryThread.daemon = True
        self.telemetryThread.start()

    def _connect(self) -> None:
        while True:
            for _ in range(self.frameskip):
                try:
                    events = get_gamepad()
                except Exception as e:
                    self.messageSignal.emit(str(e))
                    break

                for event in events:
                    if event.code == "ABS_Y":
                        value = -event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                        if abs(value) > DEADZONE:
                            self.controls.ly = math.copysign(
                                math.pow(abs((value - math.copysign(DEADZONE, value)) / (1 - DEADZONE)), EXPO), value
                            )
                        else:
                            self.controls.ly = 0
                    elif event.code == "ABS_X":
                        value = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                        if abs(value) > DEADZONE:
                            self.controls.lx = math.copysign(
                                math.pow(abs((value - math.copysign(DEADZONE, value)) / (1 - DEADZONE)), EXPO), value
                            )
                        else:
                            self.controls.lx = 0
                    elif event.code == "ABS_RY":
                        value = -event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                        if abs(value) > DEADZONE:
                            self.controls.ry = math.copysign(
                                math.pow(abs((value - math.copysign(DEADZONE, value)) / (1 - DEADZONE)), EXPO), value
                            )
                        else:
                            self.controls.ry = 0
                    elif event.code == "ABS_RX":
                        value = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                        if abs(value) > DEADZONE:
                            self.controls.rx = math.copysign(
                                math.pow(abs((value - math.copysign(DEADZONE, value)) / (1 - DEADZONE)), EXPO), value
                            )
                        else:
                            self.controls.rx = 0
                    elif event.code == "ABS_RZ":
                        value = event.state / XboxController.MAX_TRIG_VAL  # normalize between -1 and 1
                        if abs(value) > DEADZONE:
                            self.controls.tr = (value - math.copysign(DEADZONE, value)) / (1 - DEADZONE)
                        else:
                            self.controls.tr = 0

            else:
                self.controlSignal.emit()
                continue
            break
            # time.sleep(self.samplerate)
