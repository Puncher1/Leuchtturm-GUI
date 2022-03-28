import json

from utils.utils import *
from utils.common import Path, Dict, Color
from utils.serial_interface import Serial


class RunEvents:

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow


    def on_btnDisplayONOFF_pressed(self):
        with open(Path.json_States, "r") as fdata:
            data = json.load(fdata)

        if "displayBtn_ONOFF" in data.keys():
            displayBtn_ONOFF_state = data["displayBtn_ONOFF"]
            displayBtn_ONOFF_newState = Dict.invert_ONOFF[displayBtn_ONOFF_state]
            displayBtn_ONOFF_label = displayBtn_ONOFF_state

        else:
            displayBtn_ONOFF_label = "OFF"
            displayBtn_ONOFF_newState = "ON"


        if displayBtn_ONOFF_label == "ON":
            displayBtn_ONOFF_color = Color.green
        elif displayBtn_ONOFF_label == "OFF":
            displayBtn_ONOFF_color = Color.red
        else:
            raise TypeError("'displayBtn_ONOFF_label' is neither 'ON' nor 'OFF'.")

        serialPort = Serial(baudrate=115200, port="COM6", timeout=2)
        feedback = serialPort.serialWrite(f"display_{displayBtn_ONOFF_newState.lower()}\n", 3)

        self.mainWindow.displayBtn_ONOFF.setText(displayBtn_ONOFF_label)
        self.mainWindow.displayBtn_ONOFF.setStyleSheet(f"color: #{displayBtn_ONOFF_color}")

        data["displayBtn_ONOFF"] = displayBtn_ONOFF_newState

        with open(Path.json_States, "w+") as fdata:
            json.dump(data, fdata, sort_keys=True, indent=4)

        createMessageBox(
            self.mainWindow,
            "Display ON/OFF",
            f"Successfully turned {displayBtn_ONOFF_newState.lower()} display!",
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

            with open(Path.json_States, "r") as fdata:
                data = json.load(fdata)
                data["currentTextLabel"] = selectedTextLabel

                with open(Path.json_States, "w+") as fdata:
                    json.dump(data, fdata, sort_keys=True, indent=4)

            serialPort = Serial(baudrate=115200, port="COM6", timeout=2)
            feedback = serialPort.serialWrite(f"update_text\n", 3)

            serialPort = Serial(baudrate=115200, port="COM6")
            feedback = serialPort.serialWrite(f"{selectedText}\n", len(selectedText.encode()))

            createMessageBox(
                self.mainWindow,
                "Update Text",
                f'Successfully updated the current text with the label "{selectedTextLabel}".',
                [QMessageBox.Ok],
                QMessageBox.Information
            )


