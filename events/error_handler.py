import sys
import traceback
import re
import datetime
import pytz
import serial


from PyQt5.Qt import QMessageBox


def __getLocalDatetime(tz_str: str):
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


def on_error(exc_type, exc_error, exc_tb):
    """
    Global error handler which executes a ``Qt.QMessageBox`` with the traceback.
    By clicking the 'Ok' button or closing the traceback window will exit the program.
    """

    lines = traceback.format_exception(exc_type, exc_error, exc_tb)
    full_traceback_text = ''.join(lines)

    if exc_type == serial.serialutil.SerialTimeoutException:
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Timeout!")
        msgBox.setText("The operation is canceled due of a timeout while reading/writing from/to nucleo-board."
                       "\nPlease check the data and power connection.")

        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setIcon(QMessageBox.Critical)

    else:
        msgBox = QMessageBox()
        msgBox.setWindowTitle("An unexpected error has occurred!")
        msgBox.setText(f"{full_traceback_text}"
                       f"\n\nPlease contact SCA (Tel. 267) if this error remain.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setIcon(QMessageBox.Critical)

    cet_dt = __getLocalDatetime("CET")
    cet_dtString = cet_dt.strftime("%y%m%d_%H%M%S")

    errorFile = open(f"./log/error-{cet_dtString}.txt", "w+")
    errorFile.write(full_traceback_text)

    msgBox.exec()

    if exc_type == serial.serialutil.SerialTimeoutException:
        return

    sys.exit(1)