import sys, os
from ctypes import windll
import time
import serial

from events.editor import EditorEvents
from events.run import RunEvents
from events.error_handler import on_error
from utils.utils import *
from utils.common import Path, Dict, Color
from utils.serial_interface import Serial

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
- apply run stuff (display on/off, speed, running light on/off, ...) on uC by writing via UART
- run stuff (display on/off, speed, running light on/off, ...) check with real state (read from uC)

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
        self.run = RunEvents(self)

        self.setWindowTitle("Leuchtturm")
        self.setFixedSize(700, 500)
        self.setWindowIcon(QIcon(Path.png_MainIcon))

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

        with open(Path.json_States, "r") as fdata:
            data = json.load(fdata)

        if "displayBtn_ONOFF" in data.keys():
            displayBtn_ONOFF_label = Dict.invert_ONOFF[data["displayBtn_ONOFF"]]
        else:
            displayBtn_ONOFF_label = "ON"

        if displayBtn_ONOFF_label == "ON":
            displayBtn_ONOFF_color = Color.green
        elif displayBtn_ONOFF_label == "OFF":
            displayBtn_ONOFF_color = Color.red
        else:
            raise TypeError("'displayBtn_ONOFF_label' is neither 'ON' nor 'OFF'.")

        self.displayBtn_ONOFF = createPushButton(
            (60, 30),
            displayBtn_ONOFF_label,
            fontSize=11,
            textColor=displayBtn_ONOFF_color,
            rect=(20, 180, 0, 0),
            parent=runWidget,
            func=self.run.on_btnDisplayONOFF_pressed
        )

        displayBtn_UpdateText = createPushButton(
            (85, 30),
            "Update text",
            fontSize=11,
            rect=(120, 180, 0, 0),
            parent=runWidget,
            func=self.run.on_btnUpdateText_pressed
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

        with open(Path.json_Texts, "r") as fdata:
            data = json.load(fdata)

        if len(list(data.keys())) == 0:
            placeholder = "No texts available"
        else:
            placeholder = "Select text"

        self.precreatedTexts_Dropdown = createComboBox(
            items=list(data.keys()),
            fontSize=11,
            placeholder=placeholder,
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

        self.currentText_LineEdit = createLineEdit(
            10,
            placeholder="No text showing",
            fontSize=11,
            rect=(40, 390, 151, 22),
            parent=runWidget,
            isReadOnly=True
        )

        self.tabs = createTab(
            [
                (runWidget, QIcon(Path.png_ExecutiveDark), "Run"),
                (editorWidget, QIcon(Path.png_Notebook), "Editor")
            ],
            self.on_tab_changed
        )
        self.setCentralWidget(self.tabs)


    def on_tab_changed(self):
        tabName = self.tabs.tabText(self.tabs.currentIndex())

        if tabName == "Editor":
            updateEditorTable(self.tableWidget)

        elif tabName == "Run":
            updateRunDropdown(self.precreatedTexts_Dropdown)


app = QApplication([])
# app.setStyle("Fusion")
app.setWindowIcon(QIcon(os.path.join(basedir, Path.ico_MainIcon)))

sys.excepthook = on_error

window = MainWindow()
window.show()

app.exec()




