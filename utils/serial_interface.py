import time
import inspect
from typing import Optional

from utils.common import Color

import serial
from PyQt5.Qt import *


_STD_BAUDRATE = 115200
_STD_PORT = "COM6"
_STD_TIMEOUT = 1     # seconds


class _Comms:

    def __init__(self, baudrate: int = _STD_BAUDRATE, port: str = _STD_PORT, timeout: int = _STD_TIMEOUT):
        self.__ser = _Serial(baudrate, port, timeout)

    def get_board_state_ser(self):
        result = self.__ser.serialWrite("get_board_state\n", 3)
        return result

    def get_display_state_ser(self):
        result = self.__ser.serialWrite("get_display_state\n", 3)
        return result

    def get_text_ser(self):
        result = self.__ser.serialWrite("get_text\n", 1500)
        return result


    def exec_task_ser(self, task: str, text: Optional[str]):
        if task in ["display_on\n", "display_off\n"]:
            feedback = self.__ser.serialWrite(task, 3)

        if task == "update_text\n" and text is not None:
            feedback = self.__ser.serialWrite("update_text\n", 3)

        else:
            raise ValueError(f"'{task}' is not a valid task")

        return feedback


class Tasks:

    def __init__(self, main_window: QMainWindow):
        super().__init__()

        self.__main_window = main_window
        self.__comms = _Comms()

        self.__task = None
        self.__text = None
        self.__feedback = None
        self.__task_done = False

        self.__board_state_exc_count = 0

        self.running = True

    def loop(self):
        caller_stack = inspect.stack()
        caller_class = caller_stack[1][0].f_locals["self"].__class__.__name__
        caller_method = caller_stack[1][0].f_code.co_name
        caller = f"{caller_class}.{caller_method}"

        if not caller == "Thread.run":
            raise RuntimeError("Loop was not called in thread.")

        wait_pv = 0
        wait_cyc = 100
        while True:
            if not self.running:
                break

            if self.__board_state_exc_count >= 2:
                raise serial.SerialTimeoutException("no response")

            self.__task_done = False
            if wait_pv >= wait_cyc:
                wait_pv = 0

                if not self.running:
                    break

                # get board state
                try:
                    board_state = self.__comms.get_board_state_ser()
                    self.__board_state_exc_count = 0

                except serial.SerialTimeoutException:
                    self.__board_state_exc_count += 1

                if not self.running:
                    break

                # get actual state
                try:
                    state = self.__comms.get_display_state_ser()

                    if state == "ON":
                        color = Color.green
                    elif state == "OFF":
                        color = Color.red
                    else:
                        raise ValueError("'state' is neither 'ON' nor 'OFF'.")

                except serial.SerialTimeoutException:
                    state = "..."
                    color = Color.black
                    self.__main_window.displayBtn_ONOFF.setDisabled(True)

                finally:
                    print(f"{state=}")
                    self.__main_window.displayBtn_ONOFF.setStyleSheet("color: #{}".format(color))
                    self.__main_window.displayBtn_ONOFF.setText(state.strip())

                if not self.running:
                    break

                # get actual text
                try:
                    text = self.__comms.get_text_ser()
                except serial.SerialTimeoutException:
                    text = "Loading..."
                finally:
                    print(f"{text=}")
                    self.__main_window.currentText_ScrollLabel.setText(text.strip())

            else:
                wait_pv += 1

            if not self.running:
                break

            if self.__task is not None:
                feedback = self.__comms.exec_task_ser(self.__task, self.__text)
                self.__feedback = feedback
                self.__task_done = True
                self.__task = None

            time.sleep(0.01)

    def __set_task(self, cmd: str, text: str = None):
        self.__task = cmd
        self.__text = text

        while not self.__task_done:
            pass

        return self.__feedback

    def set_display_state(self, state: str):
        if state == "ON":
            feedback = self.__set_task("display_on\n")
        elif state == "OFF":
            feedback = self.__set_task("display_off\n")
        else:
            raise ValueError("'state' is neither 'ON' nor 'OFF'.")

        return feedback

    def set_text(self, text: str):
        feedback = self.__set_task("update_text\n", text)
        return feedback


class _Serial:

    def __init__(self, baudrate: int, port: str, timeout: int = None):
        self.baudrate = baudrate
        self.port = port
        self.timeout = timeout

        self.ser = serial.Serial()
        self.ser.baudrate = self.baudrate
        self.ser.port = self.port
        self.ser.timeout = self.timeout
        self.ser.write_timeout = self.timeout

    def _serial_ports(self):
        """
        Lists every COM port available on the system.

        :return: List of strings
        """

        ports = ['COM%s' % (i + 1) for i in range(256)]

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException) as e:
                pass

        return result

    def serialWrite(self, string: str, size: int = None):
        if self.port not in self._serial_ports():
            raise serial.SerialException(f"Make sure this COM Port exists.")

        try:
            self.ser.open()
        except serial.SerialException as e:
            self.ser.close()

            if "PermissionError" in e.args[0]:
                raise serial.SerialException(f"{e}. Make sure this COM Port isn't already in use.")

            else:
                raise serial.SerialException(e)
        else:
            encodedString = string.encode()

            try:
                bytes = self.ser.write(encodedString)
            except Exception as e:
                self.ser.close()
                raise serial.SerialException(f"Write operation failed! Error: {e}")

            if bytes != len(encodedString):
                self.ser.close()
                raise serial.SerialException(f"Write operation failed!")

            if size:
                feedback = self.ser.read(size)
            else:
                feedback = self.ser.read(len(encodedString))
            print(f"{feedback=}")
            if feedback is None or feedback == b"":
                self.ser.close()
                raise serial.SerialTimeoutException(f"Read operation timed out and didn't receive any feedback. "
                                                    f"Please check the data and power connection.")

            self.ser.close()
            return feedback

    def serialRead(self, size: int = 1):
        if self.port not in self._serial_ports():
            raise serial.SerialException(f"Make sure this COM Port exists.")

        try:
            self.ser.open()
        except serial.SerialException as e:
            self.ser.close()

            if "PermissionError" in e.args[0]:
                raise serial.SerialException(f"{e}. Make sure this COM Port isn't already in use.")

            else:
                raise serial.SerialException(e)

        try:
            result = self.ser.read(size)
        except serial.SerialException as e:
            self.ser.close()
            raise serial.SerialException(f"Read operation failed! Error {e}")

        self.ser.close()

        return result
