from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import MainWindow

import time
import inspect
from typing import Optional

import serial
from PyQt5.Qt import *

from utils.common import Color
from utils.utils import createMessageBox
from utils.threads import Thread


_STD_BAUDRATE = 115200
_STD_PORT = "COM6"
_STD_TIMEOUT = 0.5     # seconds


class _Comms:

    def __init__(self, baudrate: int = _STD_BAUDRATE, port: str = _STD_PORT, timeout: int = _STD_TIMEOUT):
        self.__ser = _Serial(baudrate, port, timeout)

    def get_board_state_ser(self):
        result = self.__ser.serialWrite("get_board_state\n")
        return result

    def get_display_state_ser(self):
        result = self.__ser.serialWrite("get_display_state\n")
        return result

    def get_text_ser(self):
        result = self.__ser.serialWrite("get_text\n")
        return result

    def exec_task_ser(self, task: str, text: Optional[str]):
        if task in ["display_on\n", "display_off\n"]:
            feedback = self.__ser.serialWrite(task)

        elif task == "update_text\n":
            if text is not None:
                feedback = self.__ser.serialWrite("update_text\n")
                feedback = self.__ser.serialWrite(f"{text}\n")
            else:
                raise ValueError(f"text not provided")

        else:
            raise ValueError(f"'{task}' is not a valid task")

        return feedback


class Tasks:

    def __init__(self, main_window: MainWindow):
        super().__init__()

        self.__main_window = main_window
        self.__comms = _Comms()

        self.__task = None
        self.__text = None
        self.__feedback = None
        self.__task_done = False
        self.global_error = False

        self.__board_state_timeout = False
        self.__close_no_response_error = False

        self.running = True

    def loop(self, progress_callback):
        caller_stack = inspect.stack()
        caller_func = caller_stack[1][3]

        raise_error = False
        if not caller_func == "<module>":
            if "self" in list(caller_stack[1][0].f_locals):
                caller_class = caller_stack[1][0].f_locals["self"].__class__.__name__
                caller_method = caller_stack[1][0].f_code.co_name
                caller = f"{caller_class}.{caller_method}"

                if not caller == "Thread.run":
                    raise_error = True
            else:
                raise_error = True

        else:
            raise_error = True

        if raise_error:
            raise Exception("Loop was not called in thread.")


        wait_pv = 0
        wait_cyc = 10

        while True:
            if not self.running:
                break

            if self.__board_state_timeout:
                self.__main_window.displayBtn_ONOFF.setDisabled(True)
                self.__main_window.displayBtn_UpdateText.setDisabled(True)
                self.__main_window.displayBtn_ONOFF.setStyleSheet("color: #000000")
                self.__main_window.displayBtn_ONOFF.setText("...")
                self.__main_window.currentText_ScrollLabel.setText("Loading...")

                print("board timeout")

                if not self.__close_no_response_error:
                    progress_callback.emit(self.__close_no_response_error)

                self.__close_no_response_error = True

                try:
                    board_state = self.__comms.get_board_state_ser()
                except serial.SerialTimeoutException:
                    pass
                else:
                    self.__board_state_timeout = False

                continue
            else:
                if self.__close_no_response_error:
                    progress_callback.emit(self.__close_no_response_error)
                    self.__close_no_response_error = False
                    wait_pv = 10        # to immediately update GUI


            if wait_pv >= wait_cyc:
                print("sec loop")
                wait_pv = 0

                if not self.running:
                    break

                # get actual state
                try:
                    state = self.__comms.get_display_state_ser()
                    state = state.decode()

                except (serial.SerialException, serial.SerialTimeoutException):
                    print("display_error")
                    self.__board_state_timeout = True
                    continue

                else:
                    if state == "ON":
                        state = "OFF"
                        color = Color.red
                    elif state == "OFF":
                        state = "ON"
                        color = Color.green
                    else:
                        raise ValueError("'state' is neither 'ON' nor 'OFF'.")

                    self.__main_window.displayBtn_ONOFF.setStyleSheet("color: #{}".format(color))
                    self.__main_window.displayBtn_ONOFF.setText(state)
                    self.__main_window.displayBtn_ONOFF.setEnabled(True)

                if not self.running:
                    break

                # get actual text
                try:
                    text = self.__comms.get_text_ser()
                    text = text.decode()

                except serial.SerialTimeoutException:
                    print("text_error")
                    self.__board_state_timeout = True
                    continue

                else:
                    self.__main_window.currentText_ScrollLabel.setText(text)

                # get board state
                try:
                    board_state = self.__comms.get_board_state_ser()
                except serial.SerialTimeoutException:
                    print("board_error")
                    self.__board_state_timeout = True
                    continue

                else:
                    self.__main_window.displayBtn_UpdateText.setEnabled(True)

                if not self.running:
                    break

            else:
                wait_pv += 1

            if not self.running:
                break

            if self.__task is not None:
                feedback = self.__comms.exec_task_ser(self.__task, self.__text)
                self.__feedback = feedback
                self.__task_done = True
                self.__task = None
                wait_pv = 10           # to immediately update GUI

            time.sleep(0.01)

    def __set_task(self, cmd: str, text: str = None):
        self.__task = cmd
        self.__text = text

        while not self.__task_done and not self.global_error:
            pass

        self.__task_done = False
        return self.__feedback, self.global_error

    def set_display_state(self, state: str):
        if state == "ON":
            feedback = self.__set_task("display_on\n")
        elif state == "OFF":
            feedback = self.__set_task("display_off\n")
        else:
            raise ValueError("'state' is neither 'ON' nor 'OFF'.")

        return feedback

    def set_text(self, text: str):
        feedback = self.__set_task("update_text\n")
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

    def serialWrite(self, string: str):

        try:
            self.ser.open()
        except Exception as e:
            print(f"ERROR OPENING: {e}")
            self.ser.close()

            if "PermissionError" in e.args[0]:
                raise serial.SerialException(f"{e}. Make sure this COM Port exists and isn't already in use.")

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

            feedback = self.ser.read(1500)
            feedback = feedback.split(b"\0")[0].strip()

            print(f"{encodedString=}, {feedback=}")

            if feedback is None or feedback == b"":
                self.ser.close()
                raise serial.SerialTimeoutException(f"Read operation timed out and didn't receive any feedback. "
                                                    f"Please check the data and power connection.")
            self.ser.close()

            return feedback

    def serialRead(self, size: int = 1):
        try:
            self.ser.open()
        except serial.SerialException as e:
            self.ser.close()

            if "PermissionError" in e.args[0]:
                raise serial.SerialException(f"{e}. Make sure this COM Port exists and isn't already in use.")

            else:
                raise serial.SerialException(e)

        try:
            result = self.ser.read(size)
        except serial.SerialException as e:
            self.ser.close()
            raise serial.SerialException(f"Read operation failed! Error {e}")

        self.ser.close()

        return result
