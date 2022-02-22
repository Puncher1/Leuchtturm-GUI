"""


"""


try:
    from PyQt5.QtCore import QSize, QMutex, Qt
    from PyQt5.QtWidgets import *
    from PyQt5 import QtGui
    from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap, QFont
    from random import choice
    import functools

    import serial
    import sys, os
    import json

    import typing
    from typing import Tuple, Union, Callable, List

    from threading import Thread

    basedir = os.path.dirname(__file__)

    try:
        from ctypes import windll
        appID = 'sca.leuchtturm.v1.0'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)
    except ImportError as e:
        print(f"{e.__class__.__name__}: {e}")

    stdFont = "Calibri"
    stdFontSize = 10


    """
    TODO:
    - pass arguments to connect function instead of use self
    - create functions for things
    - run tab
    
    """

    def createLabelText(text: str, size: Tuple[int, int] = None, font: str = stdFont, fontSize: int = stdFontSize, bold: bool = False, underline: bool = False, italic: bool = False) -> QLabel:
        """
        Creates a ``Qt.QLabel`` with the passed arguments and returns it.

        :param text: The text which is on the label; str
        :param size: The size of the label (default to None); Tuple[x: int, y: int]
        :param font: The font which has the label's text (default to "Calibri"); str
        :param fontSize: The font's size (default to 10); int
        :param bold: Whether the text should be bold or not (default to False); bool
        :param underline: Whether the text should be underlined or not (default to False); bool
        :param italic: Whether the text should be italic or not (default to False); bool
        :return: The Label: Qt.QLabel
        """

        textFont = QFont(font, fontSize)

        if bold:
            textFont.setBold(True)

        if underline:
            textFont.setUnderline(True)

        if italic:
            textFont.setItalic(True)

        label = QLabel()

        if size is not None:
            label.setFixedSize(size[0], size[1])

        label.setText(text)
        label.setFont(textFont)

        return label


    def createPushButton(buttonSize: Tuple[int, int], text: str = None, font: str = stdFont, fontSize: int = stdFontSize, bold: bool = False, underline: bool = False, italic: bool = False,
                         image: Tuple[str, Tuple[int, int]] = None, func: Callable = None) -> QPushButton:
        """
        Creates a ``Qt.QPushButton`` with the passed arguments and returns it.

        :param text: The text which is on the button (default to None); str
        :param buttonSize: The size of the button; Tuple[x: int, y: int]
        :param font: The font which has the button's text (default to "Calibri"); str
        :param fontSize: The font's size (default to 10); int
        :param bold: Whether the text should be bold or not (default to False); bool
        :param underline: Whether the text should be underlined or not (default to False); bool
        :param italic: Whether the text should be italic or not (default to False); bool
        :param image: An image which replaces the button (default to None): Tuple[image_path; str, Tuple[x: int, y: int]]
        :param func: The follow-up function which is called when the button is pressed (default to None); Callable
        :return: The Label: Qt.QPushButton
        """

        if image is None and text is None:
            print(f"{createPushButton.__code__}"
                  f"\nValue Error: Wrong parameters passed. Make sure either text or image is not None.")
            exit()

        button = QPushButton()
        button.setFixedSize(buttonSize[1], buttonSize[0])

        if image is None:
            textFont = QFont(font, fontSize)

            if bold:
                textFont.setBold(True)

            if underline:
                textFont.setUnderline(True)

            if italic:
                textFont.setItalic(True)

            button.setFont(textFont)
            button.setText(text)

        else:
            image_path = image[0]
            x = image[1][0]
            y = image[1][1]

            if text is None:
                button.setIcon(QIcon(image_path))
                button.setIconSize(QSize(x, y))
            else:
                button.setIcon(QIcon(image_path, text))
                button.setIconSize(QSize(x, y))

        if func is not None:
            button.clicked.connect(func)

        return button


    def createLineEdit(maxLength: int, size: Tuple[int, int] = None, placeholder: str = None, font: str = stdFont, fontSize: int = stdFontSize) -> QLineEdit:
        """
        Creates a ``Qt.QLineEdit`` with the passed arguments and returns it.

        :param maxLength: The maximum length (max. amount of symbols) of the input; int
        :param size: The size of the text field (default to None); Tuple[x: int, y: int]
        :param placeholder: The placeholder text (default to None); str
        :param font: The font which has the button's text (default to "Calibri"); str
        :param fontSize: The font's size (default to 10); int
        :return: Qt.QLineEdit
        """

        textFont = QFont(font, fontSize)

        textField = QLineEdit()

        textField.setMaxLength(maxLength)
        textField.setPlaceholderText(placeholder)
        textField.setFont(textFont)

        if size is not None:
            textField.setFixedSize(size[0], size[1])

        return textField

    def createGridLayout(*args: Union[Tuple[QWidget, Tuple[int, int]], Tuple[QLayout, Tuple[int, int]]]):
        """
        Creates a ``Qt.QGridLayout`` with the passed arguments and returns it.

        :param args: The target/s which should be placed into the layout; Union[Tuple[QWidget, Tuple[x: int, y: int]], Tuple[QLayout, Tuple[x: int, y: int]]]
        :return: Qt.QGridLayout
        """

        layout = QGridLayout()

        for arg in args:
            target = arg[0]
            x = arg[1][0]
            y = arg[1][1]

            if "layout" in target.__class__.__name__.lower():
                layout.addLayout(target, y, x)
            else:
                layout.addWidget(target, y, x)

        return layout


    def createMessageBox(mainWindow: QMainWindow, boxTitle: str, boxText: str,
                         stdBtns: List[Union[QMessageBox.StandardButtons, QMessageBox.StandardButton]], icon: QMessageBox.Icon,
                         func: Callable = None):
        """
        Creates a ``Qt.QMessageBox`` and executes it.

        :param mainWindow: The main window. It's needed to align the message box above the main window; QMainWindow
        :param boxTitle: The message box's title; str
        :param boxText: The message box's text; str
        :param stdBtns: The standard buttons of the message box; Union[QMessageBox.StandardButtons, QMessageBox.StandardButton]
        :param icon: The message box's icon (not window icon): QMessageBox.Icon
        """

        msgBox = QMessageBox(mainWindow)
        msgBox.setWindowTitle(boxTitle)
        msgBox.setText(boxText)
        msgBox.setStandardButtons(functools.reduce(lambda x, y: x | y, stdBtns))
        msgBox.setIcon(icon)

        if func is not None:
            msgBox.accepted.connect(lambda: func(msgBox.clickedButton().text()))
            msgBox.rejected.connect(lambda: func(msgBox.clickedButton().text()))

        msgBox.exec()


    def updateEditorTable(table: QTableWidget, tabs: QTabWidget):
        """
        Updates the table (``Qt.QTabelWidget``) in the editor tab.

        :param table: The editor table; QTableWidget
        :param tabs: The tabs; QTabWidget
        """

        tabName = tabs.tabText(tabs.currentIndex())
        if tabName == "Editor":

            stdItemFont = QFont("Calibri", 12)
            stdItemFont.setBold(True)

            stdLabelItem = QTableWidgetItem()
            stdLabelItem.setText("Label")
            stdLabelItem.setFont(stdItemFont)
            stdLabelItem.setTextAlignment(Qt.AlignCenter)

            stdTextItem = QTableWidgetItem()
            stdTextItem.setText("Text")
            stdTextItem.setFont(stdItemFont)
            stdTextItem.setTextAlignment(Qt.AlignCenter)

            itemFont = QFont("Calibri", 11)

            table.clear()
            table.setItem(0, 0, stdLabelItem)
            table.setItem(0, 1, stdTextItem)

            with open("./json/texts.json", "r") as fdata:
                data = json.load(fdata)

            col = 0
            row = 1
            for k, v in data.items():
                labelItem = QTableWidgetItem()
                labelItem.setTextAlignment(Qt.AlignCenter)
                labelItem.setFont(itemFont)
                labelItem.setText(k)

                textItem = QTableWidgetItem()
                textItem.setTextAlignment(Qt.AlignCenter)
                textItem.setFont(itemFont)
                textItem.setText(v)

                table.setItem(row, col, labelItem)
                table.setItem(row, col + 1, textItem)

                row += 1


    class MainWindow(QMainWindow):

        def __init__(self):
            super().__init__()
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

            self.tableWidget = QTableWidget()
            self.tableWidget.setRowCount(20)
            self.tableWidget.setColumnCount(2)
            self.tableWidget.setColumnWidth(0, 100)
            self.tableWidget.setColumnWidth(1, 496)
            self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
            self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

            tableHHeader = self.tableWidget.horizontalHeader()
            tableHHeader.setSectionResizeMode(QHeaderView.Fixed)

            tableVHeader = self.tableWidget.verticalHeader()
            tableVHeader.setSectionResizeMode(QHeaderView.Fixed)

            buttonNew = createPushButton(
                text="New",
                buttonSize=(25, 50),
                fontSize=11,
                func=self.on_btn_editor_new_pressed
            )

            buttonDel = createPushButton(
                text="Del",
                buttonSize=(25, 50),
                fontSize=11,
                func=self.on_btn_editor_del_pressed
            )

            buttonClear = createPushButton(
                text="Clear",
                buttonSize=(25, 50),
                fontSize=11,
                func=self.on_btn_editor_clear_pressed
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

            self.tabs = QTabWidget()
            self.tabs.addTab(QLabel("Hallo"), QIcon("./images/icons/execute_dark.png"), "Run")
            self.tabs.addTab(editorWidget, QIcon("./images/icons/notebook.png"), "Editor")
            self.tabs.currentChanged.connect(self.on_tab_changed)
            self.setCentralWidget(self.tabs)


        def on_tab_changed(self):
            updateEditorTable(self.tableWidget, self.tabs)

        # **************************************** EDITOR TAB *******************************************

        def on_btn_editor_new_pressed(self):

            with open("./json/texts.json", "r") as fdata:
                data = json.load(fdata)

            if len(data.keys()) >= 19:
                createMessageBox(self, "New Text", "Maximum reached!", [QMessageBox.Ok], QMessageBox.Critical)

            else:

                self.dlgNewText = QDialog(self, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                self.dlgNewText.setFixedSize(500, 280)
                self.dlgNewText.setWindowTitle("New Text")


                titleWidget = createLabelText("New Text", fontSize=18, bold=True, underline=True)
                descWidget = createLabelText("Please type your text and a specific label into the text-fields"
                                             "\nbelow."
                                             "\nNOTE: The maximum length of the text is 1500 and the maximum"
                                             "\nlength of the label is 10 symbols.",
                                             fontSize=11
                )

                inputTextLabel = createLabelText(
                    "Text:",
                    fontSize=11
                )

                self.inputText = createLineEdit(
                    1500,
                    placeholder="Enter your text",
                    fontSize=11
                )

                inputLabelLabel = createLabelText(
                    "Label: ",
                    fontSize=11
                )

                self.inputLabel = createLineEdit(
                    10,
                    placeholder="Enter your label",
                    fontSize=11
                )

                self.dlgNewTextBtnBox = QDialogButtonBox()
                self.dlgNewTextBtnBox.addButton("Create && Save", QDialogButtonBox.AcceptRole)
                self.dlgNewTextBtnBox.addButton("Cancel", QDialogButtonBox.RejectRole)
                self.dlgNewTextBtnBox.accepted.connect(lambda: self.on_btns_newtext_pressed(QDialogButtonBox.Save))
                self.dlgNewTextBtnBox.rejected.connect(lambda: self.on_btns_newtext_pressed(QDialogButtonBox.Cancel))

                emptyTextLabel = createLabelText("")

                layout = createGridLayout(
                    (titleWidget, (1, 0)),
                    (descWidget, (1, 1)),
                    (emptyTextLabel, (0, 2)),
                    (inputLabelLabel, (0, 3)),
                    (self.inputLabel, (1, 3)),
                    (inputTextLabel, (0, 4)),
                    (self.inputText, (1, 4)),
                    (emptyTextLabel, (1, 5)),
                    (self.dlgNewTextBtnBox, (1, 6)),
                )


                self.dlgNewText.setLayout(layout)
                self.dlgNewText.exec()


        def on_btn_editor_del_pressed(self):
            with open("./json/texts.json", "r") as fdata:
                data = json.load(fdata)

                if len(data.keys()) == 0:
                    createMessageBox(self, "Delete Text", "No texts existing!", [QMessageBox.Ok], QMessageBox.Critical)

                else:
                    self.dlgDelText = QDialog(self, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                    self.dlgDelText.setFixedSize(500, 180)
                    self.dlgDelText.setWindowTitle("Delete Text")

                    titleWidget = createLabelText("Delete Text", fontSize=18, bold=True, underline=True)
                    descWidget = createLabelText(
                        "Please choose the text you want to delete below.",
                        fontSize=11
                    )

                    self.delDropdownWidget = QComboBox()
                    self.delDropdownWidget.addItems(data.keys())

                    self.dlgDelTextBtnBox = QDialogButtonBox()
                    self.dlgDelTextBtnBox.addButton("Delete && Save", QDialogButtonBox.AcceptRole)
                    self.dlgDelTextBtnBox.addButton("Cancel", QDialogButtonBox.RejectRole)
                    self.dlgDelTextBtnBox.accepted.connect(lambda: self.on_btns_deltext_pressed(QDialogButtonBox.Save))
                    self.dlgDelTextBtnBox.rejected.connect(lambda: self.on_btns_deltext_pressed(QDialogButtonBox.Cancel))

                    layout = createGridLayout(
                        (titleWidget, (0, 0)),
                        (descWidget, (0, 1)),
                        (self.delDropdownWidget, (0, 2)),
                        (self.dlgDelTextBtnBox, (1, 3))
                    )

                    self.dlgDelText.setLayout(layout)
                    self.dlgDelText.exec()


        def on_btn_editor_clear_pressed(self):
            with open("./json/texts.json", "r") as fdata:
                data = json.load(fdata)

                if len(data.keys()) == 0:
                    createMessageBox(self, "Clear Texts", "No texts existing!", [QMessageBox.Ok], QMessageBox.Critical)
                else:
                    createMessageBox(self, "Clear Texts", "Are you sure you want to delete every text?", [QMessageBox.Yes, QMessageBox.No],
                                    QMessageBox.Warning, self.on_btns_cleartext_pressed)


        def on_btns_newtext_pressed(self, btn):

            if btn == QDialogButtonBox.Save:

                label = self.inputLabel.text()
                text = self.inputText.text()

                if label == "" and text == "":

                    createMessageBox(self, "Error!", "Text and Label is empty, please try again",
                                     [QMessageBox.Ok], QMessageBox.Critical)

                elif label == "":
                    createMessageBox(self, "Error!", "Label is empty, please try again.",
                                     [QMessageBox.Ok], QMessageBox.Critical)

                elif text == "":
                    createMessageBox(self, "Error!", "Text is emtpy, please try again.",
                                     [QMessageBox.Ok], QMessageBox.Critical)
                else:

                    with open("./json/texts.json", "r") as fdata:
                        data = json.load(fdata)

                        if label not in data.keys():
                            data[label] = text

                            with open("./json/texts.json", "w+") as fdata:
                                json.dump(data, fdata, sort_keys=True, indent=4)

                            updateEditorTable(self.tableWidget, self.tabs)
                            self.dlgNewText.close()
                            createMessageBox(self, "New Text", "Your text has been created!", [QMessageBox.Ok], QMessageBox.Information)


                        else:
                            createMessageBox(self, "Error!", "This label already exists, please try again..",
                                             [QMessageBox.Ok], QMessageBox.Critical)
                            with open("./json/texts.json", "w+") as fdata:
                                json.dump(data, fdata, sort_keys=True, indent=4)


            elif btn == QDialogButtonBox.Cancel:
                self.dlgNewText.close()


        def on_btns_deltext_pressed(self, btn):

            if btn == QDialogButtonBox.Save:
                selectedLabel = self.delDropdownWidget.currentText()

                with open("./json/texts.json", "r") as fdata:
                    data = json.load(fdata)
                    del data[selectedLabel]
                    with open("./json/texts.json", "w+") as fdata:
                        json.dump(data, fdata, sort_keys=True, indent=4)

                    updateEditorTable(self.tableWidget, self.tabs)
                    self.dlgDelText.close()
                    createMessageBox(self, "Delete Text", "Your text has been deleted!", [QMessageBox.Ok], QMessageBox.Information)

            elif btn == QDialogButtonBox.Cancel:
                self.dlgDelText.close()


        def on_btns_cleartext_pressed(self, btnName):
            btnName = btnName.strip("&")

            if btnName == "Yes":
                with open("./json/texts.json", "r") as fdata:
                    data = json.load(fdata)
                    data = {}
                    with open("./json/texts.json", "w+") as fdata:
                        json.dump(data, fdata, sort_keys=True, indent=4)

                    updateEditorTable(self.tableWidget, self.tabs)
                    createMessageBox(self, "Clear Texts", "All texts have been deleted!", [QMessageBox.Ok],
                                     QMessageBox.Information)

    app = QApplication([])
    app.setWindowIcon(QIcon(os.path.join(basedir, 'images/leuchtturm.ico')))

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
except Exception as e:
    print(f"{e.__class__.__name__}: {e}")