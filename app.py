import sys, os
from ctypes import windll
from multiprocessing import Process

from events.editor import EditorEvents
from events.run import RunEvents
from events.error_handler import ErrorHandler
from utils.utils import *
from utils.common import Path, Dict, Color
from utils.serial_interface import Tasks


# App init
basedir = os.path.dirname(__file__)

appID = 'sca.leuchtturm.v1.0'
windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)


"""
TODO:
Run Tab

- !!! TEXT: Ü etc. werden in 2 chars versendet, nicht in einem

Running Light:
- All buttons etc. are disabled if no connection is there
- maybe brightness 

- create functions for things


Kommunikation mit Nucleo Board

!!!
- Nucleo Board überprüft, ob PC noch "lebt" (ob Verbindung noch vorhanden ist)
    - Nucleo Board erhält jede X ms "get_display_state". Falls dieses nicht mehr ankommt nach z.B 1s, dann ist die Verbindung weg
    - Falls Verbindung weg: Standardtext ausgeben + Standardgeschwindigkeit
    
- Nucleo Board wird neugestartet (z.B. Strom raus und wieder rein)
    - Standardtext ausgeben + Standardgeschwindigkeit ausgeben

Others
- docstrings on_... functions
- PEP8


"""


# Main
class MainWindow(QMainWindow):
    """
    The main window of the application.
    Inherits from ``Qt.QMainWindow``
    """

    def __init__(self):
        super().__init__()
        self.TEXT_GAP = "          "

        self.editor = EditorEvents(self)
        self.run = RunEvents(self)
        self.tasks = Tasks(self)

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
            "Here, you can change the dot-matrix display. Select a text at <i><b>Pre-created Texts</b></i> and "
            "press <b><i>Update text</i></b> to display the text. ",
            isWordWrap=True,
            rect=(10, 50, 500, 100),
            parent=self.runWidget
        )

        self.displayTitle = createLabelText(
            "Dot-Matrix Display",
            fontSize=13,
            bold=True,
            rect=(42, 140, 145, 30),
            parent=self.runWidget
        )

        self.displayBtn_ONOFF = createPushButton(
            (60, 30),
            text="...",
            disabled=True,
            rect=(42, 170, 0, 0),
            parent=self.runWidget,
            func=self.run.on_btnDisplayONOFF_pressed
        )

        self.displayBtn_UpdateText = createPushButton(
            (85, 30),
            text="Update text",
            disabled=True,
            rect=(42, 205, 0, 0),
            parent=self.runWidget,
            func=self.run.on_btnUpdateText_pressed
        )

        self.currentText_ScrollLabel = createLabelText(
            text="Loading...",     # json: "currentText"
            isScrollable=True,
            rect=(43, 240, 300, 50),
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
            text="...",
            disabled=True,
            rect=(540, 180, 71, 31),
            parent=self.runWidget,
            func=self.run.on_btnRunninglightONOFF_pressed
        )

        self.runningLightCurrentSpeed_Label = createLabelText(
            text="Current Speed: ...",
            fontSize=11,
            rect=(520, 225, 150, 30),
            parent=self.runWidget
        )

        self.runningLightSpeed_Slider = createSlider(
            (25, 150),
            minVal=1,
            maxVal=100,
            singleStep=1,
            orientation=Qt.Vertical,
            rect=(555, 265, 0, 0),
            parent=self.runWidget,
            func_onRelease=self.run.on_sliderRunninglight_released,
            func_onValueChanged=self.run.on_sliderRunninglightSpeed_changed
        )

        self.runningLightSpeedValue_Label = createLabelText(
            text=str(self.runningLightSpeed_Slider.value()),
            fontSize=10,
            textAlignment=Qt.AlignCenter,
            rect=(555, 415, 25, 20),
            parent=self.runWidget
        )

        self.precreatedTextsTitle = createLabelText(
            "Pre-created Texts",
            fontSize=13,
            bold=True,
            rect=(40, 335, 130, 21),
            parent=self.runWidget
        )

        with open(Path.json_Texts, "r") as fdataTexts:
            dataTexts = json.load(fdataTexts)

        with open(Path.json_States, "r") as fdataStates:
            dataStates = json.load(fdataStates)

        if len(list(dataTexts.keys())) == 0:
            placeholder = "No texts available"

        else:
            placeholder = "Select text"


        self.precreatedTexts_Dropdown = createComboBox(
            items=list(dataTexts.keys()),
            placeholder=placeholder,
            isPlaceholderBold=True,
            rect=(40, 365, 170, 23),
            parent=self.runWidget
        )

        self.warningLabel = createLabelText(
            "Don't unplug the power cable from the device while the display is on!",
            fontSize=10,
            textColor="red",
            rect=(10, 450, 385, 20),
            bold=True,
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

window = MainWindow()
window.show()

error_handler = ErrorHandler(window)
sys.excepthook = error_handler.on_error

createMessageBox(
    window,
    "Important Information",
    "Please turn off the display before unplug the power cable from the device."
    "\n\n**Unplug the cable while the display is on may damage the device!**",
    [QMessageBox.Ok],
    QMessageBox.Information,
    textFormat=Qt.TextFormat.MarkdownText,
)

threadpool = QThreadPool()
thread_task = Thread(window.tasks.loop, window)
thread_task.signals.progress.connect(error_handler.on_response_error)
thread_task.signals.error.connect(error_handler.on_error)
threadpool.start(thread_task)

app.exec_()
window.tasks.running = False
sys.exit(1)




