from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import MainWindow

import json

from utils.utils import *
from utils.common import Path, Dict, Color

class RunEvents:
    """
    Represents all events in the run tab.
    """

    def __init__(self, mainWindow: MainWindow):
        self.mainWindow = mainWindow

    def on_btnDisplayONOFF_pressed(self):
        """
        Called when the display-ONOFF-button is pressed.

        Turns on/off the display and updates the button's text.
        """

        displayBtn_ONOFF_text = self.mainWindow.displayBtn_ONOFF.text()
        feedback, global_error = self.mainWindow.tasks.set_display_state(displayBtn_ONOFF_text)

        if global_error:
            return

        createMessageBox(
            self.mainWindow,
            "Display ON/OFF",
            f"Successfully turned {displayBtn_ONOFF_text.lower()} display!",
            [QMessageBox.Ok],
            QMessageBox.Information
        )

    def on_btnUpdateText_pressed(self):
        """
        Called when the "Update text"-button is pressed.

        Updates the text of the display, the "Current Text"-label and the "Precreated Texts"-dropdown.
        """

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

                selectedText += self.mainWindow.TEXT_GAP        # to create a "gap" at the end of string
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

    def on_btnRunninglightONOFF_pressed(self):
        """
        Called when the runninglight-ONOFF-button is pressed.

        Turns on/off the runninglight of the display, the "Current Text"-label and updates the button's text.
        """

        runninglightBtn_ONOFF_text = self.mainWindow.runningLightBtn_ONOFF.text()
        feedback, global_error = self.mainWindow.tasks.set_runninglight_state(runninglightBtn_ONOFF_text)

        if global_error:
            return

        createMessageBox(
            self.mainWindow,
            "Running Light ON/OFF",
            f"Successfully turned {runninglightBtn_ONOFF_text.lower()} running light!",
            [QMessageBox.Ok],
            QMessageBox.Information
        )

    def on_sliderRunninglight_released(self):
        """
        Called when the runninglight-slider was released.

        Updates the speed of the runninglight.
        """

        runninglight_speed = self.mainWindow.runningLightSpeed_Slider.value()
        feedback, global_error = self.mainWindow.tasks.set_runninglight_speed(str(runninglight_speed))

        if global_error:
            return

        feedback = feedback.decode("cp1252")
        createMessageBox(
            self.mainWindow,
            "Running Light Speed",
            f"Successfully changed speed to {feedback}%",
            [QMessageBox.Ok],
            QMessageBox.Information
        )

    def on_sliderRunninglightSpeed_changed(self):
        """
        Called when the runninglight-slider's value has changed.

        Updates the runninglight-speed-label below the slider (realtime slider-value).
        """

        runninglight_speed = self.mainWindow.runningLightSpeed_Slider.value()
        self.mainWindow.runningLightSpeedValue_Label.setText(str(runninglight_speed))

    def on_sliderBrightness_released(self):
        """
        Called when the brightness-slider was released.

        Updates the brightness of the display.
        """

        duty_cycle_percent = self.mainWindow.brightness_Slider.value()
        duty_cycle = round((16 / 100) * int(duty_cycle_percent))
        if duty_cycle == 0:
            duty_cycle = 1

        feedback, global_error = self.mainWindow.tasks.set_brightness(str(duty_cycle))
        feedback = feedback.decode("cp1252")

        feedback = round((100 / 16) * int(feedback))

        if global_error:
            return

        createMessageBox(
            self.mainWindow,
            "Dot Matrix Brightness",
            f"Successfully changed brightness to {feedback}%",
            [QMessageBox.Ok],
            QMessageBox.Information
        )

        if feedback != duty_cycle_percent:
            self.mainWindow.brightness_Slider.setValue(feedback)

    def on_sliderBrightness_changed(self):
        """
        Called when the brightness-slider's value has changed.

        Updates the brightness-speed-label below the slider (realtime slider-value).
        """

        duty_cycle = self.mainWindow.brightness_Slider.value()
        self.mainWindow.brightnessValue_Label.setText(str(duty_cycle))