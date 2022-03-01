import sys, os
from ctypes import windll

from events.editor import EditorEvents
from events.error_handler import on_error
from utils.utils import *

from PyQt5 import uic


# Program init
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

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWidget(QWidget):

    def __init__(self):
        super(MainWidget, self).__init__()

        uic.loadUi("./leuchtturm.ui", self)

# Main
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
        self.setWindowIcon(QIcon("utils/images/lighthouse.png"))

        windowFont = QFont("Calibri", 10)
        self.setFont(windowFont)

        titleWidget = createLabelText("Editor", fontSize=18, bold=True, underline=True)

        editorDescWidget = createLabelText(
            "Here, you can add your pre-created texts which you can then simply select and send to the dot-matrix display "
            "(even if the program has restarted).",
            fontSize=11
        )

        editorDescWidget.setWordWrap(True)
        editorDescWidget.setFixedSize(590, 50)

        self.tableWidget = createTable(20, 2, [(0, 100), (1, 475)], False, True, False, True, True)

        buttonNew = createPushButton(
            text="New",
            buttonSize=(50, 25),
            fontSize=11,
            func=self.editor.on_btnNew_pressed
        )

        buttonDel = createPushButton(
            text="Del",
            buttonSize=(50, 25),
            fontSize=11,
            func=self.editor.on_btnDel_pressed
        )

        buttonClear = createPushButton(
            text="Clear",
            buttonSize=(50, 25),
            fontSize=11,
            func=self.editor.on_btnClear_pressed
        )

        # buttonLayout = createGridLayout(
        #     (buttonNew, (1, 0)),
        #     (buttonDel, (1, 1)),
        #     (buttonClear, (1, 2))
        # )
        #
        # editorLayout = createGridLayout(
        #     (titleWidget, (0, 0)),
        #     (editorDescWidget, (0, 1)),
        #     (buttonLayout, (5, 1)),
        #     (self.tableWidget, (0, 2))
        # )

        # editorWidget = QWidget()
        # editorWidget.setLayout(editorLayout)

        runWidget = QWidget()

        displayTitle = createLabelText(
            "Dot-Matrix Display",
            fontSize=11,
            bold=True,
            rect=(50, 70, 141, 21),
            parent=runWidget
        )

        displayBtn_ONOFF = createPushButton(
            (55, 25),
            "ON/OFF",
            fontSize=10,
            rect=(20, 110, 71, 31),
            parent=runWidget,
            func=None       # TODO
        )

        displayBtn_UpdateText = createPushButton(
            (75, 25),
            "Update text",
            fontSize=10,
            rect=(120, 110, 101, 31),
            parent=runWidget,
            func=None       # TODO
        )

        runningLightTitle = createLabelText(
            text="Running Light",    # TODO: size overwrites rect size --> maybe dynamic?
            fontSize=11,
            bold=True,
            rect=(530, 80, 111, 21),
            parent=runWidget
        )

        runningLightBtn_ONOFF = createPushButton(
            (55, 25),
            "ON/OFF",
            fontSize=10,
            rect=(540, 110, 71, 31),
            parent=runWidget,
            func=None       # TODO
        )

        runningLightSpeed_Slider = createSlider(
            (25, 100),
            minVal=1,
            maxVal=100,
            singleStep=1,
            orientation=Qt.Vertical,
            rect=(590, 160, 21, 160),
            parent=runWidget,
            func=None   # TODO
        )

        runningLightSpeed_Label = createLabelText(
            "Speed",
            fontSize=10,
            rect=(540, 195, 31, 21),
            parent=runWidget
        )


        self.tabs = createTab(
            [
                (runWidget, QIcon("utils/images/icons/execute_dark.png"), "Run"),
                # (editorWidget, QIcon("utils/images/icons/notebook.png"), "Editor")
            ],
            self.on_tab_changed
        )
        self.setCentralWidget(self.tabs)


    def on_tab_changed(self):
        updateEditorTable(self.tableWidget, self.tabs)



app = QApplication([])
app.setWindowIcon(QIcon(os.path.join(basedir, 'utils/images/leuchtturm.ico')))

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

