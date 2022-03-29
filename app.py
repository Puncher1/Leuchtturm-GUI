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

# App init
basedir = os.path.dirname(__file__)

appID = 'sca.leuchtturm.v1.0'
windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)


"""
TODO:
Run Tab
- Dot-Matrix Display
    - Add label called "Current Text: "
    - Add label (with border) which shows current text next to other label -> Text receive from nucleo board
    
- Pre-created texts
    - The dropdown is called ...
        - ... "No text available" if no text are available
        - ... "Select text" if texts are available but nothing selected
        - ... "Selected: {label}", if a text is selected    
    
- apply run stuff (display on/off, speed, running light on/off, ...) on uC by writing via UART
- run stuff (display on/off, speed, running light on/off, ...) check with real state (read from uC)
- create functions for things (if needed, done for editor tab)
- Show text tool tip

Kommunikation mit Nucleo Board:
- Loop jede X ms
    - Aufgabe 1): sendet an Board "get_display_state", Nucleo Board sendet State (entweder "ON " oder "OFF") -> update "displayBtn_ONOFF"
        - manuelle Veränderung von "displayBtn_ONOFF" löschen! Nur von realen state (Nucleo Board State)
        - Falls Übertragung failed, dann ist "displayBtn_ONOFF" = "OFF"
    - Aufgabe 2): Aufgabe von Benutzer ausführen 
    - Aufgabe 3): sendet an Board "get_text", Nucleo Board sendet aktuellen Text, welcher in einer Variable gespeichert ist
        - Nucleo Board sendet immer 1500 Zeichen (maximaler Text) (Rest ist aufgefüllt)
        - Aktueller Text wird in json "currentText" gespeichert und neben "Current Text: " ausgegeben (update on change)

- Nucleo Board überprüft, ob PC noch "lebt" (ob Verbindung noch vorhanden ist)
    - Nucleo Board erhält jede X ms "get_display_state". Falls dieses nicht mehr ankommt nach z.B 1s, dann ist die Verbindung weg
    - Falls Verbindung weg: Standardtext ausgeben
    
- Nucleo Board wird neugestartet (z.B. Strom raus und wieder rein)
    - Standardtext ausgeben

Editor Tab
- edit button to change context of texts

Others
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
        self.run = RunEvents(self)

        self.setWindowTitle("Leuchtturm")
        self.setFixedSize(700, 500)
        self.setWindowIcon(QIcon(Path.png_MainIcon))

        self.windowFont = QFont("Calibri", 10)
        self.setFont(self.windowFont)

        self.titleWidget = createLabelText("Editor", fontSize=18, bold=True, underline=True)

        self.editorDescWidget = createLabelText(
            "Here, you can add your pre-created texts which you can then simply select and send to the dot-matrix display "
            "(even if the program has restarted)."
            
        )

        self.editorDescWidget.setWordWrap(True)
        self.editorDescWidget.setFixedSize(590, 50)

        self.tableWidget = createTable(20, 2, [(0, 100), (1, 475)], False, True, False, True, True)

        self.buttonNew = createPushButton(
            text="New",
            buttonSize=(50, 25),
            func=self.editor.on_btnNew_pressed
        )

        self.buttonDel = createPushButton(
            text="Del",
            buttonSize=(50, 25),
            func=self.editor.on_btnDel_pressed
        )

        self.buttonClear = createPushButton(
            text="Clear",
            buttonSize=(50, 25),
            func=self.editor.on_btnClear_pressed
        )

        self.buttonLayout = createGridLayout(
            (self.buttonNew, (1, 0)),
            (self.buttonDel, (1, 1)),
            (self.buttonClear, (1, 2))
        )

        self.editorLayout = createGridLayout(
            (self.titleWidget, (0, 0)),
            (self.editorDescWidget, (0, 1)),
            (self.buttonLayout, (5, 1)),
            (self.tableWidget, (0, 2))
        )

        self.editorWidget = QWidget()
        self.editorWidget.setLayout(self.editorLayout)

        self.runWidget = QWidget()

        self.runTitle = createLabelText(
            "Run",
            fontSize=18,
            bold=True,
            underline=True,
            rect=(10, 0, 300, 45),
            parent=self.runWidget
        )

        self.runDescription = createLabelText(
            "Here, you can change the dot-matrix display."
            "<br>Select a text at <i><b>Pre-created Texts</b></i> and press <b><i>Update text</i></b> to display a text.",
            isMarkdown=True,
            rect=(10, 50, 500, 50),
            parent=self.runWidget
        )

        self.displayTitle = createLabelText(
            "Dot-Matrix Display",
            fontSize=13,
            bold=True,
            rect=(42, 140, 145, 30),
            parent=self.runWidget
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
            text=displayBtn_ONOFF_label,
            textColor=displayBtn_ONOFF_color,
            rect=(42, 170, 0, 0),
            parent=self.runWidget,
            func=self.run.on_btnDisplayONOFF_pressed
        )

        self.displayBtn_UpdateText = createPushButton(
            (85, 30),
            text="Update text",
            rect=(42, 205, 0, 0),
            parent=self.runWidget,
            func=self.run.on_btnUpdateText_pressed
        )

        with open(Path.json_States, "r") as fdataStates:
            dataStates = json.load(fdataStates)

        if "currentTextLabel" not in dataStates.keys() or "displayBtn_ONOFF" not in dataStates.keys():
            viewTextBtn_text = "No text showing"

        else:
            if "displayBtn_ONOFF" not in dataStates.keys():
                viewTextBtn_text = "No text showing"
            else:
                viewTextBtn_text = "View text"


        self.currentText_Label = createLabelText(
            "Current Text:",
            bold=True,
            border_px=1,
            rect=(42, 240, 100, 20),
            parent=self.runWidget
        )

        self.currentText_LineEdit = createLabelText(
            text="asd",     # json: "currentText"
            isScrollable=True,
            rect=(150, 240, 300, 50),
            parent=self.runWidget
        )

        self.runningLightTitle = createLabelText(
            text="Running Light",    # TODO: size overwrites rect size --> maybe dynamic?
            fontSize=13,
            bold=True,
            rect=(527, 140, 150, 30),
            parent=self.runWidget
        )

        self.runningLightBtn_ONOFF = createPushButton(
            (60, 30),                       # TODO: size overwrites rect size --> maybe dynamic?
            text="ON/OFF",
            rect=(540, 180, 71, 31),
            parent=self.runWidget,
            func=None       # TODO
        )

        self.runningLightSpeed_Slider = createSlider(
            (25, 100),
            minVal=1,
            maxVal=100,
            singleStep=1,
            orientation=Qt.Vertical,
            rect=(555, 230, 21, 160),
            parent=self.runWidget,
            func=None   # TODO
        )

        self.runningLightSpeed_Label = createLabelText(
            "Speed",
            fontSize=10,
            rect=(510, 265, 31, 21),
            parent=self.runWidget
        )

        self.precreatedTextsTitle = createLabelText(
            "Pre-created Texts",
            fontSize=13,
            bold=True,
            rect=(40, 310, 130, 21),
            parent=self.runWidget
        )

        with open(Path.json_Texts, "r") as fdataTexts:
            dataTexts = json.load(fdataTexts)

        with open(Path.json_States, "r") as fdataStates:
            dataStates = json.load(fdataStates)

        if len(list(dataTexts.keys())) == 0:
            placeholder = "No texts available"

        elif "currentTextLabel" not in dataStates.keys():
            placeholder = "Select text"

        else:
            placeholder = f"Selected: {dataStates['currentTextLabel']}"

        self.precreatedTexts_Dropdown = createComboBox(
            items=list(dataTexts.keys()),
            placeholder=placeholder,
            isPlaceholderBold=True,
            rect=(40, 340, 170, 23),
            parent=self.runWidget
        )

        self.tabs = createTab(
            [
                (self.runWidget, QIcon(Path.png_ExecutiveDark), "Run"),
                (self.editorWidget, QIcon(Path.png_Notebook), "Editor")
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


proxyStyle = QProxyStyle()
app = QApplication([])
# app.setStyle("Fusion")
app.setStyle(proxyStyle)
app.setWindowIcon(QIcon(os.path.join(basedir, Path.ico_MainIcon)))

sys.excepthook = on_error

window = MainWindow()
window.show()

app.exec()




