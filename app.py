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
- run tab
- create functions for things (if needed, done for editor tab)
- docstrings update for utils functions
- docstrings on_... functions

"""


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
        self.setWindowIcon(QIcon("C:/DEV/PROJECTS/Leuchtturm/Leuchtturm-GUI/utils/images/lighthouse.png"))

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

        buttonLayout = createGridLayout(
            (buttonNew, (1, 0)),
            (buttonDel, (1, 1)),
            (buttonClear, (1, 2))
        )

        editorLayout = createGridLayout(
            (titleWidget, (0, 0)),
            (editorDescWidget, (0, 1)),
            (buttonLayout, (5, 1)),
            (self.tableWidget, (0, 2))
        )

        editorWidget = QWidget()
        editorWidget.setLayout(editorLayout)

        runWidget = QWidget()

        runTitle = createLabelText(
            "Run",
            fontSize=18,
            bold=True,
            underline=True,
            rect=(10, 0, 300, 45),
            parent=runWidget
        )

        tabHTML = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        runDescription = createLabelText(
            "Here, you can change the dot-matrix display."
            "<br>Select a text at <i><b>Pre-created Texts</b></i> and press <b><i>Update text</i></b> to display a text.",
            fontSize=11,
            rect=(10, 50, 500, 50),
            parent=runWidget
        )

        displayTitle = createLabelText(
            "Dot-Matrix Display",
            fontSize=13,
            bold=True,
            rect=(42, 140, 150, 30),
            parent=runWidget
        )

        displayBtn_ONOFF = createPushButton(
            (60, 30),
            "ON/OFF",
            fontSize=11,
            rect=(20, 180, 0, 0),
            parent=runWidget,
            func=None       # TODO
        )

        displayBtn_UpdateText = createPushButton(
            (85, 30),
            "Update text",
            fontSize=11,
            rect=(120, 180, 0, 0),
            parent=runWidget,
            func=None       # TODO
        )

        runningLightTitle = createLabelText(
            text="Running Light",    # TODO: size overwrites rect size --> maybe dynamic?
            fontSize=13,
            bold=True,
            rect=(527, 140, 150, 30),
            parent=runWidget
        )

        runningLightBtn_ONOFF = createPushButton(
            (60, 30),
            "ON/OFF",
            fontSize=11,
            rect=(540, 180, 71, 31),
            parent=runWidget,
            func=None       # TODO
        )

        runningLightSpeed_Slider = createSlider(
            (25, 100),
            minVal=1,
            maxVal=100,
            singleStep=1,
            orientation=Qt.Vertical,
            rect=(555, 230, 21, 160),
            parent=runWidget,
            func=None   # TODO
        )

        runningLightSpeed_Label = createLabelText(
            "Speed",
            fontSize=10,
            rect=(510, 265, 31, 21),
            parent=runWidget
        )

        precreatedTextsTitle = createLabelText(
            "Pre-created Texts",
            fontSize=13,
            bold=True,
            rect=(40, 280, 130, 21),
            parent=runWidget
        )

        with open("C:/DEV/PROJECTS/Leuchtturm/Leuchtturm-GUI/utils/json/texts.json", "r") as fdata:
            data = json.load(fdata)

        pecreatedTexts_Dropdown = createComboBox(
            items=list(data.keys()),
            fontSize=11,
            placeholder="Select text",
            rect=(40, 310, 151, 23),
            parent=runWidget
        )

        currentTextTitle = createLabelText(
            "Current Text",
            fontSize=13,
            bold=True,
            rect=(40, 360, 121, 23),
            parent=runWidget
        )

        currentText_LineEdit = createLineEdit(
            10,
            placeholder="No text showing",
            fontSize=11,
            rect=(40, 390, 151, 22),
            parent=runWidget
        )

        self.tabs = createTab(
            [
                (runWidget, QIcon("C:/DEV/PROJECTS/Leuchtturm/Leuchtturm-GUI/utils/images/icons/execute_dark.png"), "Run"),
                (editorWidget, QIcon("C:/DEV/PROJECTS/Leuchtturm/Leuchtturm-GUI/utils/images/icons/notebook.png"), "Editor")
            ],
            self.on_tab_changed
        )
        self.setCentralWidget(self.tabs)


    def on_tab_changed(self):
        updateEditorTable(self.tableWidget, self.tabs)



app = QApplication([])
# app.setStyle("Fusion")
app.setWindowIcon(QIcon(os.path.join(basedir, 'C:/DEV/PROJECTS/Leuchtturm/Leuchtturm-GUI/utils/images/leuchtturm.ico')))

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

