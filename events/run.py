from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import MainWindow

import json

from utils.utils import *
from utils.common import Path, Dict, Color

class RunEvents:

    def __init__(self, mainWindow: MainWindow):
        self.mainWindow = mainWindow


    def on_btnDisplayONOFF_pressed(self):
        print("task sent")

        with open(Path.json_States, "r") as fdata:
            data = json.load(fdata)

        displayBtn_ONOFF_text = self.mainWindow.displayBtn_ONOFF.text()

        feedback = self.mainWindow.tasks.set_display_state(displayBtn_ONOFF_text)
        print(feedback)

        createMessageBox(
            self.mainWindow,
            "Display ON/OFF",
            f"Successfully turned {displayBtn_ONOFF_text.lower()} display!",
            [QMessageBox.Ok],
            QMessageBox.Information
        )


    def on_btnUpdateText_pressed(self):
        selectedTextLabel = self.mainWindow.precreatedTexts_Dropdown.currentText()

        if selectedTextLabel == "":
            createMessageBox(
                self.mainWindow,
                "Update Text",
                "No text selected, please try again.",
                [QMessageBox.Ok],
                QMessageBox.Critical
            )

        else:
            with open(Path.json_Texts, "r") as fdata:
                data = json.load(fdata)
                selectedText = data[selectedTextLabel]

            currentText = self.mainWindow.currentText_ScrollLabel.label.text()
            if selectedText == currentText:
                createMessageBox(
                    self.mainWindow,
                    "Update Text",
                    "Text already on display, please choose another.",
                    [QMessageBox.Ok],
                    QMessageBox.Critical
                )
            else:
                updateRunDropdown(self.mainWindow.precreatedTexts_Dropdown)

                feedback, global_error = self.mainWindow.tasks.set_text(selectedText)

                if global_error:
                    return

                updateRunDropdown(self.mainWindow.precreatedTexts_Dropdown)

                createMessageBox(
                    self.mainWindow,
                    "Update Text",
                    f'Successfully updated the current text with the label "{selectedTextLabel}".',
                    [QMessageBox.Ok],
                    QMessageBox.Information
                )


