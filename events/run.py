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

            data["displayBtn_ONOFF"] = displayBtn_ONOFF_newState

        else:
            displayBtn_ONOFF_label = "OFF"
            displayBtn_ONOFF_newState = "ON"
            data["displayBtn_ONOFF"] = displayBtn_ONOFF_newState

        with open(Path.json_States, "w+") as fdata:
            json.dump(data, fdata, sort_keys=True, indent=4)


        if displayBtn_ONOFF_label == "ON":
            displayBtn_ONOFF_color = Color.green
        elif displayBtn_ONOFF_label == "OFF":
            displayBtn_ONOFF_color = Color.red
        else:
            raise TypeError("'displayBtn_ONOFF_label' is neither 'ON' nor 'OFF'.")

        serialPort = Serial(baudrate=115200, port="COM6")
        feedback = serialPort.serialWrite(f"display_{displayBtn_ONOFF_newState.lower()}\n", 3)
        print(feedback)

        self.mainWindow.displayBtn_ONOFF.setText(displayBtn_ONOFF_label)
        self.mainWindow.displayBtn_ONOFF.setStyleSheet(f"color: #{displayBtn_ONOFF_color}")

        createMessageBox(
            self.mainWindow,
            "Display ON/OFF",
            f"Successfully turned {displayBtn_ONOFF_newState.lower()} display!",
            [QMessageBox.Ok],
            QMessageBox.Information
        )
