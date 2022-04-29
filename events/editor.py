import json
from utils.utils import *
from utils.common import Path


class EditorEvents:
    """
    Represents all events in the editor tab.
    """

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

    def on_btnNew_pressed(self):
        """
        Called when the new-button is pressed.

        Opens a new window in which the user can enter a label and a text which should be added to the editor table
        (which are then selectable in the run dropdown).
        """

        with open(Path.json_Texts, "r") as fdata:
            data = json.load(fdata)

        if len(data.keys()) >= 19:

            createMessageBox(self.mainWindow, "New Text", "Maximum reached!", [QMessageBox.Ok], QMessageBox.Critical)

        else:
            titleWidget = createLabelText("New Text", fontSize=18, bold=True, underline=True)
            descWidget = createLabelText("Please type your text and a specific label into the text-fields"
                                         "\nbelow."
                                         "\nNOTE: The maximum length of the text is 489 and the maximum"
                                         "\nlength of the label is 10 characters.",
                                         )

            inputTextLabel = createLabelText(
                "Text:",
            )

            self.inputText = createLineEdit(
                489,
                placeholder="Enter your text",
            )

            inputLabelLabel = createLabelText(
                "Label: ",
            )

            self.inputLabel = createLineEdit(
                10,
                placeholder="Enter your label",
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
                (self.inputLabel, (1, 3)),
                (inputTextLabel, (0, 4)),
                (self.inputText, (1, 4)),
                (emptyTextLabel, (1, 5)),
                (dlgNewTextBtnBox, (1, 6)),
            )

            self.dlgNewText = createDialog(self.mainWindow, (500, 280), "New Text",
                                           [Qt.WindowSystemMenuHint, Qt.WindowTitleHint, Qt.WindowCloseButtonHint],
                                           layout)
            self.dlgNewText.exec()

    def on_btnDel_pressed(self):
        """
        Called when the del-button is pressed.

        Opens a new window in which the user can select a text which should be deleted from the editor table.
        """

        with open(Path.json_Texts, "r") as fdata:
            data = json.load(fdata)

            if len(data.keys()) == 0:
                createMessageBox(self.mainWindow, "Delete Text", "No texts existing!", [QMessageBox.Ok], QMessageBox.Critical)

            else:
                titleWidget = createLabelText("Delete Text", fontSize=18, bold=True, underline=True)
                descWidget = createLabelText(
                    "Please choose the text you want to delete below.",
                )

                self.delDropdownWidget = createComboBox(data.keys())

                self.dlgDelTextBtnBox = createDialogButtonBox(
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
                    (self.delDropdownWidget, (0, 2)),
                    (self.dlgDelTextBtnBox, (1, 3))
                )

                self.dlgDelText = createDialog(self.mainWindow, (500, 180), "Delete Text",
                                               [Qt.WindowSystemMenuHint, Qt.WindowTitleHint, Qt.WindowCloseButtonHint],
                                               layout)
                self.dlgDelText.exec()

    def on_btnClear_pressed(self):
        """
        Called when the clear-button is pressed.

        Opens a confirmation window in which the user has to confirm that he want to delete all textes.
        """

        with open(Path.json_Texts, "r") as fdata:
            data = json.load(fdata)

            if len(data.keys()) == 0:
                createMessageBox(self.mainWindow, "Clear Texts", "No texts existing!", [QMessageBox.Ok], QMessageBox.Critical)
            else:
                createMessageBox(self.mainWindow, "Clear Texts", "Are you sure you want to delete every text?",
                                 [QMessageBox.Yes, QMessageBox.No],
                                 QMessageBox.Warning, func=self.on_btnsClearText_pressed)

    def on_btnsNewText_pressed(self, btn):
        """
        Called when the "Create & Save"-button in the "New"-window is pressed.

        Adds a text with its label to the editor table.
        """

        if btn == QDialogButtonBox.Save:

            label = self.inputLabel.text()
            text = self.inputText.text()

            valid, invalidChars = checkValidStr(text)

            if label == "" and text == "":
                createMessageBox(self.mainWindow, "Error!", "Text and Label is empty, please try again",
                                 [QMessageBox.Ok], QMessageBox.Critical)

            elif label == "":
                createMessageBox(self.mainWindow, "Error!", "Label is empty, please try again.",
                                 [QMessageBox.Ok], QMessageBox.Critical)

            elif text == "":
                createMessageBox(self.mainWindow, "Error!", "Text is emtpy, please try again.",
                                 [QMessageBox.Ok], QMessageBox.Critical)

            elif not valid:
                createMessageBox(self.mainWindow, "Error!", f"Text has invalid symbols ({', '.join(invalidChars)}), please try again.",
                                 [QMessageBox.Ok], QMessageBox.Critical)

            else:

                with open(Path.json_Texts, "r") as fdata:
                    data = json.load(fdata)

                    if label not in data.keys():
                        data[label] = text

                        with open(Path.json_Texts, "w+") as fdata:
                            json.dump(data, fdata, sort_keys=True, indent=4)

                        updateEditorTable(self.mainWindow.tableWidget)
                        self.dlgNewText.close()
                        createMessageBox(self.mainWindow, "New Text", "Your text has been created!", [QMessageBox.Ok],
                                         QMessageBox.Information)


                    else:
                        createMessageBox(self.mainWindow, "Error!", "This label already exists, please try again..",
                                         [QMessageBox.Ok], QMessageBox.Critical)
                        with open(Path.json_Texts, "w+") as fdata:
                            json.dump(data, fdata, sort_keys=True, indent=4)


        elif btn == QDialogButtonBox.Cancel:
            self.dlgNewText.close()

        else:
            raise TypeError(f"Unexpected argument '{btn}'.")

    def on_btnsDelText_pressed(self, btn):
        """
        Called when the "Delete & Save"-button in the "Del"-window is pressed.

        Deletes a text with its label from the editor table.
        """

        if btn == QDialogButtonBox.Save:
            selectedLabel = self.delDropdownWidget.currentText()

            with open(Path.json_Texts, "r") as fdata:
                data = json.load(fdata)
                del data[selectedLabel]
                with open(Path.json_Texts, "w+") as fdata:
                    json.dump(data, fdata, sort_keys=True, indent=4)

                updateEditorTable(self.mainWindow.tableWidget)
                self.dlgDelText.close()
                createMessageBox(self.mainWindow, "Delete Text", "Your text has been deleted!", [QMessageBox.Ok],
                                 QMessageBox.Information)

        elif btn == QDialogButtonBox.Cancel:
            self.dlgDelText.close()

    def on_btnsClearText_pressed(self, btnName, msgBox):
        """
        Called when the "Yes"- or "No"-button in the "Clear"-confirmation-window is pressed.

        Executes or cancels the deletion.
        """

        btnName = btnName.strip("&")

        if btnName == "Yes":
            with open(Path.json_Texts, "r") as fdataTexts:
                dataTexts = json.load(fdataTexts)

                dataTexts = {}

                with open(Path.json_Texts, "w+") as fdataTexts:
                    json.dump(dataTexts, fdataTexts, sort_keys=True, indent=4)

                updateEditorTable(self.mainWindow.tableWidget)
                createMessageBox(self.mainWindow, "Clear Texts", "All texts have been deleted!", [QMessageBox.Ok],
                                 QMessageBox.Information)