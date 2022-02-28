import json
from utils.utils import *


class EditorEvents:

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow


    def on_btnNew_pressed(self):
        with open("./utils/json/texts.json", "r") as fdata:
            data = json.load(fdata)

        if len(data.keys()) >= 19:

            createMessageBox(self.mainWindow, "New Text", "Maximum reached!", [QMessageBox.Ok], QMessageBox.Critical)

        else:
            titleWidget = createLabelText("New Text", fontSize=18, bold=True, underline=True)
            descWidget = createLabelText("Please type your text and a specific label into the text-fields"
                                         "\nbelow."
                                         "\nNOTE: The maximum length of the text is 1500 and the maximum"
                                         "\nlength of the label is 10 characters.",
                                         fontSize=11
                                         )

            inputTextLabel = createLabelText(
                "Text:",
                fontSize=11
            )

            self.mainWindow.inputText = createLineEdit(
                1500,
                placeholder="Enter your text",
                fontSize=11
            )

            inputLabelLabel = createLabelText(
                "Label: ",
                fontSize=11
            )

            self.mainWindow.inputLabel = createLineEdit(
                10,
                placeholder="Enter your label",
                fontSize=11
            )

            dlgNewTextBtnBox = createDialogButtonBox(
                [
                    ("Create && Save", QDialogButtonBox.AcceptRole),
                    ("Cancel", QDialogButtonBox.RejectRole)
                ],
                (self.on_btnsNewText_pressed, {'btn': QDialogButtonBox.Save}),
                (self.on_btnsNewText_pressed, {'btn': QDialogButtonBox.Cancel})
            )

            emptyTextLabel = createLabelText("")

            layout = createGridLayout(
                (titleWidget, (1, 0)),
                (descWidget, (1, 1)),
                (emptyTextLabel, (0, 2)),
                (inputLabelLabel, (0, 3)),
                (self.mainWindow.inputLabel, (1, 3)),
                (inputTextLabel, (0, 4)),
                (self.mainWindow.inputText, (1, 4)),
                (emptyTextLabel, (1, 5)),
                (dlgNewTextBtnBox, (1, 6)),
            )

            self.mainWindow.dlgNewText = createDialog(self.mainWindow, (500, 280), "New Text",
                                           [Qt.WindowSystemMenuHint, Qt.WindowTitleHint, Qt.WindowCloseButtonHint],
                                           layout)
            self.mainWindow.dlgNewText.exec()


    def on_btnDel_pressed(self):
        with open("./utils/json/texts.json", "r") as fdata:
            data = json.load(fdata)

            if len(data.keys()) == 0:
                createMessageBox(self.mainWindow, "Delete Text", "No texts existing!", [QMessageBox.Ok], QMessageBox.Critical)

            else:
                titleWidget = createLabelText("Delete Text", fontSize=18, bold=True, underline=True)
                descWidget = createLabelText(
                    "Please choose the text you want to delete below.",
                    fontSize=11
                )

                self.mainWindow.delDropdownWidget = createComboBox(data.keys())

                self.mainWindow.dlgDelTextBtnBox = createDialogButtonBox(
                    [
                        ("Delete && Save", QDialogButtonBox.AcceptRole),
                        ("Cancel", QDialogButtonBox.RejectRole)
                    ],
                    (self.on_btnsDelText_pressed, {'btn': QDialogButtonBox.Save}),
                    (self.on_btnsDelText_pressed, {'btn': QDialogButtonBox.Cancel})
                )

                layout = createGridLayout(
                    (titleWidget, (0, 0)),
                    (descWidget, (0, 1)),
                    (self.mainWindow.delDropdownWidget, (0, 2)),
                    (self.mainWindow.dlgDelTextBtnBox, (1, 3))
                )

                self.mainWindow.dlgDelText = createDialog(self.mainWindow, (500, 180), "Delete Text",
                                               [Qt.WindowSystemMenuHint, Qt.WindowTitleHint, Qt.WindowCloseButtonHint],
                                               layout)
                self.mainWindow.dlgDelText.exec()


    def on_btnClear_pressed(self):
        with open("./utils/json/texts.json", "r") as fdata:
            data = json.load(fdata)

            if len(data.keys()) == 0:
                createMessageBox(self.mainWindow, "Clear Texts", "No texts existing!", [QMessageBox.Ok], QMessageBox.Critical)
            else:
                createMessageBox(self.mainWindow, "Clear Texts", "Are you sure you want to delete every text?",
                                 [QMessageBox.Yes, QMessageBox.No],
                                 QMessageBox.Warning, self.on_btnsClearText_pressed)


    def on_btnsNewText_pressed(self, btn):
        if btn == QDialogButtonBox.Save:

            label = self.mainWindow.inputLabel.text()
            text = self.mainWindow.inputText.text()

            if label == "" and text == "":
                createMessageBox(self.mainWindow, "Error!", "Text and Label is empty, please try again",
                                 [QMessageBox.Ok], QMessageBox.Critical)

            elif label == "":
                createMessageBox(self.mainWindow, "Error!", "Label is empty, please try again.",
                                 [QMessageBox.Ok], QMessageBox.Critical)

            elif text == "":
                createMessageBox(self.mainWindow, "Error!", "Text is emtpy, please try again.",
                                 [QMessageBox.Ok], QMessageBox.Critical)
            else:

                with open("./utils/json/texts.json", "r") as fdata:
                    data = json.load(fdata)

                    if label not in data.keys():
                        data[label] = text

                        with open("./utils/json/texts.json", "w+") as fdata:
                            json.dump(data, fdata, sort_keys=True, indent=4)

                        updateEditorTable(self.mainWindow.tableWidget, self.mainWindow.tabs)
                        self.mainWindow.dlgNewText.close()
                        createMessageBox(self.mainWindow, "New Text", "Your text has been created!", [QMessageBox.Ok],
                                         QMessageBox.Information)


                    else:
                        createMessageBox(self.mainWindow, "Error!", "This label already exists, please try again..",
                                         [QMessageBox.Ok], QMessageBox.Critical)
                        with open("./utils/json/texts.json", "w+") as fdata:
                            json.dump(data, fdata, sort_keys=True, indent=4)


        elif btn == QDialogButtonBox.Cancel:
            self.mainWindow.dlgNewText.close()

        else:
            raise TypeError(f"Unexpected argument '{btn}'.")


    def on_btnsDelText_pressed(self, btn):
        if btn == QDialogButtonBox.Save:
            selectedLabel = self.mainWindow.delDropdownWidget.currentText()

            with open("./utils/json/texts.json", "r") as fdata:
                data = json.load(fdata)
                del data[selectedLabel]
                with open("./utils/json/texts.json", "w+") as fdata:
                    json.dump(data, fdata, sort_keys=True, indent=4)

                updateEditorTable(self.mainWindow.tableWidget, self.mainWindow.tabs)
                self.mainWindow.dlgDelText.close()
                createMessageBox(self.mainWindow, "Delete Text", "Your text has been deleted!", [QMessageBox.Ok],
                                 QMessageBox.Information)

        elif btn == QDialogButtonBox.Cancel:
            self.mainWindow.dlgDelText.close()


    def on_btnsClearText_pressed(self, btnName):
        btnName = btnName.strip("&")

        if btnName == "Yes":
            with open("./utils/json/texts.json", "r") as fdata:
                data = {}
                with open("./utils/json/texts.json", "w+") as fdata:
                    json.dump(data, fdata, sort_keys=True, indent=4)

                updateEditorTable(self.mainWindow.tableWidget, self.mainWindow.tabs)
                createMessageBox(self.mainWindow, "Clear Texts", "All texts have been deleted!", [QMessageBox.Ok],
                                 QMessageBox.Information)