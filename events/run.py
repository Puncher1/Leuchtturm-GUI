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
        with open(Path.json_States, "r") as fdata:
            data = json.load(fdata)

        displayBtn_ONOFF_text = self.mainWindow.displayBtn_ONOFF.text()

        if displayBtn_ONOFF_text == "ON":
            displayBtn_ONOFF_task = "OFF"
        elif displayBtn_ONOFF_text == "OFF":
            displayBtn_ONOFF_task = "ON"
        else:
            raise ValueError("'displayBtn_ONOFF_text' is neither 'ON' nor 'OFF'.")

        feedback = self.mainWindow.tasks.set_display_state(displayBtn_ONOFF_task)
        print(feedback)

        createMessageBox(
            self.mainWindow,
            "Display ON/OFF",
            f"Successfully turned {displayBtn_ONOFF_task.lower()} display!",
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

            updateRunDropdown(self.mainWindow.precreatedTexts_Dropdown)

            feedback = self.mainWindow.tasks.set_text(selectedText, len(selectedText.encode()))

            with open(Path.json_States, "r") as fdata:
                data = json.load(fdata)
                data["currentTextLabel"] = selectedTextLabel

                with open(Path.json_States, "w+") as fdata:
                    json.dump(data, fdata, sort_keys=True, indent=4)

            updateRunDropdown(self.mainWindow.precreatedTexts_Dropdown)

            createMessageBox(
                self.mainWindow,
                "Update Text",
                f'Successfully updated the current text with the label "{selectedTextLabel}".',
                [QMessageBox.Ok],
                QMessageBox.Information
            )


