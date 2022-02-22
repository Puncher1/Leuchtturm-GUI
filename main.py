import threading
from threading import Thread
import time

import PySimpleGUI as sg
import datetime

red_error = "#c93c3c"
green_success = "#50a650"
black = "#000000"
gray = "#7a7a7a"
lightGray = "#a8a8a8"
darkGray = "#333333"
azureBlue = "#3c80c9"

titleFont = ("Calibri", 24, 'underline')
stdFont = ("Calibri", 15, '')


class GUI:

    def __init__(self):
        self.__futDate = None
        self.__isError = False
        self.__isCheck = False
        self.__totSeconds = None
        self.__threadWindow = None
        self.__threadCooldown = None

    @property  # which is also the getter
    def futDate(self):
        return self.__futDate

    @futDate.setter
    def futDate(self, x: datetime.datetime):
        self.__futDate = x

    @property
    def isError(self):
        return self.__isError

    @isError.setter
    def isError(self, x: bool):
        self.__isError = x

    @property
    def isCheck(self):
        return self.__isCheck

    @isCheck.setter
    def isCheck(self, x: bool):
        self.__isCheck = x

    @property
    def totSeconds(self):
        return self.__totSeconds

    @totSeconds.setter
    def totSeconds(self, x: float):
        self.__totSeconds = x

    @property
    def threadWindow(self):
        return self.__threadWindow

    @threadWindow.setter
    def threadWindow(self, x: Thread):
        self.__threadWindow = x

    @property
    def threadCooldown(self):
        return self.__threadCooldown

    @threadCooldown.setter
    def threadCooldown(self, x: Thread):
        self.__threadCooldown = x


def loopCooldown(g: GUI()):
    procThread = threading.currentThread()
    g.futDate = datetime.datetime.now() + datetime.timedelta(seconds=5)

    while getattr(procThread, "do_run", True):
        if g.isCheck:
            currDate = datetime.datetime.now()
            remainDate = g.futDate - currDate
            g.totSeconds = remainDate.total_seconds()

            if g.totSeconds > 0:
                g.isError = True
            else:
                g.isError = False

        time.sleep(0.1)


def createWindow(g: GUI):
    procThread = threading.currentThread()

    layout = [
        [
            sg.Text(
                "Leuchtturm Dot-Matrix\n\n\n",
                background_color=darkGray,
                font=titleFont
            )
        ],
        [sg.Text(
            "Geben Sie im untenstehenden Textfeld Ihr Text ein:",
            background_color=darkGray,
            font=stdFont
        )],
        [
            sg.Input(
                "",
                font=stdFont,
                key="_INPUT_"
            ),
            sg.Button(
                button_color=darkGray,
                image_filename="./images/icons/bug.png",
                image_size=(28, 28),
                image_subsample=18,
                border_width=0
            )
        ],
        [sg.Text(
            "",
            text_color=red_error,
            background_color=darkGray,
            font=stdFont,
            size=(45, 2),
            key="_STATUS_"
        )]
    ]
    window = sg.Window(title="Leuchtturm", layout=layout, margins=(100, 80), background_color=darkGray)

    while getattr(procThread, "do_run", True):
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        elif list(values.keys())[0] == "_INPUT_":
            if g.isError:
                window.Element("_INPUT_").update("")
                window.Element("_STATUS_").update(
                    f"Das war ein wenig zu schnell... In {round(g.totSeconds, 2)}s erneut versuchen.",
                    text_color=red_error,
                    font=stdFont
                )
            else:
                inputText = values["_INPUT_"]                                                                            # TODO: Transfer to uC
                if inputText in [None, ""]:
                    window.Element("_INPUT_").update("")
                    window.Element("_STATUS_").update(
                        "Fehler! Stellen Sie sicher, dass Sie keinen leeren Text eingeben.",
                        text_color=red_error,
                        font=stdFont
                    )
                else:
                    window.Element("_INPUT_").update("")
                    window.Element("_STATUS_").update("Der Text wurde erfolgreich versendet!", text_color=green_success)
                    g.futDate = datetime.datetime.now() + datetime.timedelta(seconds=5)
                    g.isCheck = True

    g.threadWindow.do_run = False
    g.threadCooldown.do_run = False
    window.close()


if __name__ == "__main__":
    gui = GUI()

    gui.threadWindow = Thread(target=createWindow, args=(gui,))
    gui.threadCooldown = Thread(target=loopCooldown, args=(gui,))

    gui.threadWindow.start()
    gui.threadCooldown.start()
