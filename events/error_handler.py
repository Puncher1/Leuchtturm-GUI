import sys
import traceback
import re
import datetime
import pytz
import serial

from PyQt5.Qt import QMessageBox, QMainWindow

from utils.utils import createMessageBox


class ErrorHandler:

    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window

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

            if str(exc_error) == "no response":
                createMessageBox(
                    self.main_window,
                    "444 No Response",
                    "The nucleo-board don't respond while communicating to it."
                    "\nPlease check the data and power connection.",
                    [QMessageBox.Ok],
                    QMessageBox.Critical
                )
            else:
                createMessageBox(
                    self.main_window,
                    "408 Timeout",
                    "The operation is canceled due of a timeout while reading/writing from/to nucleo-board."
                    "\nPlease check the data and power connection.",
                    [QMessageBox.Ok],
                    QMessageBox.Critical
                )

        else:
            createMessageBox(
                self.main_window,
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

        if exc_type == serial.serialutil.SerialTimeoutException and str(exc_error) not in ["no response"]:
            return

        sys.exit(1)
