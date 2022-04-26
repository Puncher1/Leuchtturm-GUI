from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import MainWindow

import sys
import traceback
import re
import datetime
import pytz
import serial

from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication

from utils.utils import createMessageBox, createDialog, createLabelText, createGridLayout, createImageLabel


class ErrorHandler:

    def __init__(self, main_window: QMainWindow):
        self.__main_window = main_window
        self.__no_response_msg_box = None

    def __getLocalDatetime(self, tz_str: str):
        """
        Returns the local datetime from a specific timezone.

        :param tz_str: The timezone: str

        :return: The datetime object of the specific timezone: datetime.datetime
        """

        tz = pytz.timezone(tz_str)
        utc_dt = datetime.datetime.utcnow()
        tz_dtOffset = utc_dt.astimezone(tz)
        utc_offset = tz_dtOffset.strftime("%z")
        utc_offsetHours = re.search("\d{2}", utc_offset)
        utc_offsetHours = int(utc_offsetHours.group(0))

        tz_dt = utc_dt + datetime.timedelta(hours=utc_offsetHours)
        return tz_dt

    def on_error(self, exc_type, exc_error, exc_tb):
        """
        Global error handler which executes a ``Qt.QMessageBox`` with the traceback.
        By clicking the 'Ok' button or closing the traceback window will exit the program.
        """

        lines = traceback.format_exception(exc_type, exc_error, exc_tb)
        full_traceback_text = ''.join(lines)

        if exc_type == serial.serialutil.SerialTimeoutException:

            if str(exc_error) == "unexpected timeout":
                createMessageBox(
                    self.__main_window,
                    "An unexpected error has occurred! (timeout)",
                    f"{full_traceback_text}"
                    f"\n\nPlease contact SCA (Tel. 267) if this error remain.",
                    [QMessageBox.Ok],
                    QMessageBox.Critical
                )
                cet_dt = self.__getLocalDatetime("CET")
                cet_dtString = cet_dt.strftime("%y%m%d_%H%M%S")

                errorFile = open(f"./log/error-{cet_dtString}.txt", "w+")
                errorFile.write(full_traceback_text)

            else:
                createMessageBox(
                    self.__main_window,
                    "Timeout",
                    "The operation is canceled due of a timeout while reading/writing from/to nucleo-board."
                    "\nPlease check the data and power connection.",
                    [QMessageBox.Ok],
                    QMessageBox.Critical
                )

        else:
            createMessageBox(
                self.__main_window,
                "An unexpected error has occurred!",
                f"{full_traceback_text}"
                f"\n\nPlease contact SCA (Tel. 267) if this error remain.",
                [QMessageBox.Ok],
                QMessageBox.Critical
            )

            cet_dt = self.__getLocalDatetime("CET")
            cet_dtString = cet_dt.strftime("%y%m%d_%H%M%S")

            errorFile = open(f"./log/error-{cet_dtString}.txt", "w+")
            errorFile.write(full_traceback_text)

        if exc_type == serial.serialutil.SerialTimeoutException:
            return

        QApplication.quit()

    def on_response_error(self, state: bool):

        if not state:
            error_label = createLabelText(
                text="The nucleo-board don't respond while communicating to it."
                     "\nPlease check the data and power connection.",
                isWordWrap=True,
            )

            error_img_label = createImageLabel("./utils/images/error_icon.png", (50, 50), 35)

            layout = createGridLayout(
                (error_img_label, (0, 0)),
                (error_label, (1, 0)),
            )

            self.__no_response_msg_box = createDialog(
                self.__main_window,
                size=(450, 90),
                winTitle="No Response",
                winFlags=[Qt.WindowSystemMenuHint, Qt.WindowTitleHint],
                layout=layout
            )

            self.__no_response_msg_box.exec()
        else:
            if self.__no_response_msg_box is not None:
                self.__no_response_msg_box.close()

