import sys, os
from ctypes import windll

from events.editor import EditorEvents
from events.error_handler import on_error
from utils.utils import *


# **************** PROGRAM ****************
basedir = os.path.dirname(__file__)

appID = 'sca.leuchtturm.v1.0'
windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)


"""
TODO:
- create functions for things (done for editor tab)
- comment on_... functions
- Functions in different files
- run tab

"""

# Global

# ******************************* Main Window *******************************

class MainWindow(QMainWindow):
    """
    The main window of the application.
    Inherits from ``Qt.QMainWindow``
    """

    def __init__(self):
        super().__init__()
        self.editor = EditorEvents(self)

        self.setWindowTitle("Leuchtturm")
        self.setFixedSize(700, 500)
        self.setWindowIcon(QIcon("./images/lighthouse.png"))

        windowFont = QFont("Calibri", 10)
        self.setFont(windowFont)

        titleWidget = createLabelText("Editor", fontSize=18, bold=True, underline=True)

        descWidget = createLabelText(
            "Here, you can add your pre-created texts which you can then simply select and send to the dot-matrix display "
            "(even if the program has restarted).",
            fontSize=11
        )

        descWidget.setWordWrap(True)
        descWidget.setFixedSize(590, 50)

        self.tableWidget = createTable(20, 2, [(0, 100), (1, 475)], False, True, False, True, True)

        buttonNew = createPushButton(
            text="New",
            buttonSize=(25, 50),
            fontSize=11,
            func=self.editor.on_btnNew_pressed
        )

        buttonDel = createPushButton(
            text="Del",
            buttonSize=(25, 50),
            fontSize=11,
            func=self.editor.on_btnDel_pressed
        )

        buttonClear = createPushButton(
            text="Clear",
            buttonSize=(25, 50),
            fontSize=11,
            func=self.editor.on_btnClear_pressed
        )

        buttonLayout = createGridLayout(
            (buttonNew, (1, 0)),
            (buttonDel, (1, 1)),
            (buttonClear, (1, 2))
        )

        editorLayout = createGridLayout(
            (titleWidget, (0, 0)),
            (descWidget, (0, 1)),
            (buttonLayout, (5, 1)),
            (self.tableWidget, (0, 2))
        )

        editorWidget = QWidget()
        editorWidget.setLayout(editorLayout)

        self.tabs = createTab(
            [
                (QLabel("Hallo"), QIcon("./images/icons/execute_dark.png"), "Run"),
                (editorWidget, QIcon("./images/icons/notebook.png"), "Editor")
            ],
            self.on_tab_changed
        )
        self.setCentralWidget(self.tabs)


    def on_tab_changed(self):
        updateEditorTable(self.tableWidget, self.tabs)


    # **************************************** EDITOR TAB *******************************************


app = QApplication([])
app.setWindowIcon(QIcon(os.path.join(basedir, 'images/leuchtturm.ico')))

sys.excepthook = on_error

window = MainWindow()
window.show()
app.exec()


# def serial_ports():
#     """
#     Lists every COM port available on the system.
#
#     :return: List of strings
#     """
#
#     ports = ['COM%s' % (i + 1) for i in range(256)]
#
#     result = []
#     for port in ports:
#         try:
#             s = serial.Serial(port)
#             s.close()
#             result.append(port)
#         except (OSError, serial.SerialException):
#             pass
#     return result
#
# print(serial_ports())
#
# ser = serial.Serial()
# ser.baudrate = 115200
# try:
#     ser.port = "COM6"
# except serial.SerialException as e:
#     print(f"Error: {e}"
#           f"\nMake sure this COM Port isn't already in use and try again.")
# else:
#     ser.close()
#     try:
#         ser.open()
#     except serial.SerialException as e:
#         print(f"Error: {e}"
#               f"\nMake sure this COM Port exists.")
#     else:
#         myString = "Halo\n"
#         myString = myString.encode()
#
#
#         bytes = ser.write(myString)
#         print(len(myString))
#         print(bytes)
#
#         if bytes != len(myString):
#             print(1)
#             print("Error! Write operation failed.")
#         else:
#             print(2)
#             readString = ser.read(len(myString))
#             print(readString)
#         ser.close()

