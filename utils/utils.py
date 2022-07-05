import sys

import PyQt5.QtWidgets
from PyQt5.Qt import *
from typing import Tuple, Any, List, Union, Callable, Dict, Optional
import functools
import json

from utils.common import Path
from utils.threads import Thread


# constants
STD_FONT = "Calibri"
STD_FONTSIZE = 11
HINT_gridLayout = Union[
    Union[
        Tuple[
            QWidget,
            Union[
                Tuple[int, int],                    # Tuple[x, y]
                Tuple[int, int, int, int]           # Tuple[x, y, rowSpawn, columnSpawn]
            ]
        ],
        Tuple[
            QWidget,
            Union[
                Tuple[int, int],                    # Tuple[x, y]
                Tuple[int, int, int, int]           # Tuple[x, y, rowSpawn, columnSpawn]
            ],
            Qt.Alignment
        ]
    ],
    Union[
        Tuple[
            QLayout,
            Union[
                Tuple[int, int],                    # Tuple[x, y]
                Tuple[int, int, int, int]           # Tuple[x, y, rowSpawn, columnSpawn]
            ]
        ],
        Tuple[
            QLayout,
            Union[
                Tuple[int, int],                    # Tuple[x, y]
                Tuple[int, int, int, int]           # Tuple[x, y, rowSpawn, columnSpawn]
            ],
            Qt.Alignment
        ]
    ],
]

# | --------------- Overwrites --------------- |

class QComboBox(QComboBox):
    """
    @Overwrite

    1) Due of a bug in the library, ``Qt.QComboBox`` gets overwritten to show a placeholder at combo boxes.
    Inherits from ``Qt.QComboBox``

    2) Because ``Qt.QComboBox`` doesn't provide to bold the placeholder text ``Qt.QComboBox`` gets overwritten.
    """

    def __init__(self, isPlaceholderBold: bool = False, boldPart: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isPlaceholderBold = isPlaceholderBold


    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))

        # draw the combobox frame, focusrect and selected etc.
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)

        if self.currentIndex() < 0:
            opt.palette.setBrush(
                QPalette.ButtonText,
                opt.palette.brush(QPalette.ButtonText).color().lighter()
            )

            if self.placeholderText():
                opt.currentText = self.placeholderText()

            if self.isPlaceholderBold and self.placeholderText():
                font = self.font()
                font.setBold(True)
                painter.setFont(font)


        # draw the icon and text
        painter.drawControl(QStyle.CE_ComboBoxLabel, opt)


# | --------------- Own Classes --------------- |

class ScrollLabel(QScrollArea):

    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)


        content = QWidget(self)
        self.setWidget(content)

        lay = QVBoxLayout(content)

        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        lay.addWidget(self.label)

    def setText(self, text: str):
        self.label.setText(text)


def createLabelText(text: str, size: Tuple[int, int] = None, font: str = STD_FONT, fontSize: int = STD_FONTSIZE,
                    bold: bool = False, underline: bool = False, italic: bool = False, border_px: int = None,
                    textColor: str = None, isMarkdown: bool = False, isAutoResize: bool = False,
                    isWordWrap: bool = False, isScrollable: bool = False,
                    textAlignment: Union[Qt.Alignment, Qt.AlignmentFlag] = None, rect: Tuple[int, int, int, int] = None,
                    parent: QWidget = None):
    """
    Creates a ``Qt.QLabel`` with the passed arguments and returns it.

    :param text: The text which is on the label; str
    :param size: The size of the label (default to None); Tuple[x: int, y: int]
    :param font: The font which has the label's text (default to "Calibri"); str
    :param fontSize: The font's size (default to 10); int
    :param bold: Whether the text should be bold or not (default to False); bool
    :param underline: Whether the text should be underlined or not (default to False); bool
    :param italic: Whether the text should be italic or not (default to False); bool
    :param border_px: How thick the borderline of the label should be in pixels. If None, no border is shown (default to None): int
    :param isMarkdown: Whether the text format should support markdown or not (default to False): bool
    :param isAutoResize: Whether the label should auto resize with the text or not (default to False): bool
    :param isWordWrap: Whether the label should wrap the words to the next line or not (default to False): bool
    :param textAlignment: The alignment for the text (default to None): Union[Qt.Alignment, Qt.AlignmentFlag]
    :param rect: The geometry of the widget (default to None): Tuple[left: int, top: int, width: int, height: int]
    :param parent: The parent widget on which the label should be placed on (default to None): QWidget

    :return: The Label: Qt.QLabel
    """

    textFont = QFont(font, fontSize)

    if bold:
        textFont.setBold(True)

    if underline:
        textFont.setUnderline(True)

    if italic:
        textFont.setItalic(True)

    if isScrollable:
        label = ScrollLabel()
    else:
        label = QLabel()

    if isMarkdown:
        label.setTextFormat(Qt.TextFormat.MarkdownText)

    if textColor is not None:
        label.setStyleSheet(f"color: {textColor}")

    if parent is not None:
        label.setParent(parent)

    if size is not None:
        label.setFixedSize(size[0], size[1])

    label.setText(text)
    label.setFont(textFont)

    if rect is not None:
        label.setGeometry(QRect(rect[0], rect[1], rect[2], rect[3]))

    if border_px:
        label.setStyleSheet(f"border: {border_px}px solid black;")

    if isAutoResize:
        label.adjustSize()

    if isWordWrap:
        label.setWordWrap(True)

    if textAlignment:
        label.setAlignment(textAlignment)

    return label


def createImageLabel(path: str, labelSize: Tuple[int, int], imageScale: int = None):
    """
    Creates a ``Qt.QLabel`` with ``Qt.QPixmap``
    
    :param path: The path of the image.
    :param labelSize: The size of the label: Tuple[w: int, h: int]
    :param imageScale: The scale of the image: int

    :return: The label: Qt.QLabel
    """

    label = QLabel()
    pixmap = QPixmap(path)
    if imageScale is not None:
        pixmap = pixmap.scaledToWidth(imageScale)

    label.setPixmap(pixmap)

    label.setFixedWidth(labelSize[0])
    label.setFixedHeight(labelSize[1])

    return label

def createPushButton(buttonSize: Tuple[int, int], disabled: bool = False, text: str = None, font: str = STD_FONT, fontSize: int = STD_FONTSIZE,
                     textColor: str = None, bold: bool = False, underline: bool = False, italic: bool = False, image: Tuple[str, Tuple[int, int]] = None,
                     toolTip: str = None, func: Callable = None, rect: Tuple[int, int, int, int] = None, parent: QWidget = None):
    """
    Creates a ``Qt.QPushButton`` with the passed arguments and returns it.

    :param text: The text which is on the button (default to None): str
    :param buttonSize: The size of the button: Tuple[x: int, y: int]
    :param font: The font which has the button's text (default to "Calibri"): str
    :param fontSize: The font's size (default to 10): int
    :param textColor: The text color of the button. If None, the color is black (0x000000)
    :param bold: Whether the text should be bold or not (default to False): bool
    :param underline: Whether the text should be underlined or not (default to False): bool
    :param italic: Whether the text should be italic or not (default to False): bool
    :param image: An image which replaces the button (default to None): Tuple[image_path: str, Tuple[x: int, y: int]]
    :param func: The follow-up function which gets called when the button is pressed (default to None): Callable
    :param toolTip: The text of the tool tip (text when hovering over the button) (default to None: str
    :param rect: The geometry of the widget (default to None): Tuple[left: int, top: int, width: int, height: int]
    :param parent: The parent widget on which the button should be placed on (default to None): QWidget

    :return: The push-button: Qt.QPushButton
    """

    if image is None and text is None:
        raise ValueError("Wrong parameters passed. Make sure either text or image is not None.")

    button = QPushButton()

    if parent is not None:
        button.setParent(parent)

    button.setFixedSize(buttonSize[0], buttonSize[1])

    if image is None:
        textFont = QFont(font, fontSize)

        if bold:
            textFont.setBold(True)

        if underline:
            textFont.setUnderline(True)

        if italic:
            textFont.setItalic(True)

        if textColor:
            button.setStyleSheet('color: #{}'.format(textColor))

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

    if toolTip is not None:
        button.setToolTip(toolTip)

    if rect is not None:
        button.setGeometry(QRect(rect[0], rect[1], rect[2], rect[3]))

    if func is not None:
        button.clicked.connect(func)

    button.setDisabled(disabled)

    return button


def createLineEdit(maxLength: int, size: Tuple[int, int] = None, placeholder: str = None, font: str = STD_FONT,
                   fontSize: int = STD_FONTSIZE, isReadOnly: bool = False, rect: Tuple[int, int, int, int] = None,
                   parent: QWidget = None):
    """
    Creates a ``Qt.QLineEdit`` with the passed arguments and returns it.

    :param maxLength: The maximum length (max. amount of symbols) of the input: int
    :param size: The size of the text field (default to None): Tuple[x: int, y: int]
    :param placeholder: The placeholder text (default to None): str
    :param font: The font which has the button's text (default to "Calibri"): str
    :param fontSize: The font's size (default to 10): int
    :param isReadOnly: Whether the line edit is read only or not (default to False): bool
    :param rect: The geometry of the widget (default to None): Tuple[left: int, top: int, width: int, height: int]
    :param parent: The parent widget on which the line edit should be placed on (default to None): QWidget

    :return: The line edit: Qt.QLineEdit
    """

    textFont = QFont(font, fontSize)

    textField = QLineEdit()

    if parent is not None:
        textField.setParent(parent)

    textField.setMaxLength(maxLength)
    textField.setPlaceholderText(placeholder)
    textField.setFont(textFont)

    if isReadOnly:
        textField.setReadOnly(True)

    if rect is not None:
        textField.setGeometry(QRect(rect[0], rect[1], rect[2], rect[3]))

    if size is not None:
        textField.setFixedSize(size[0], size[1])

    return textField


def createTable(rowCount: int, colCount: int, colsWidth: List[Tuple[int, int]] = None, isCellSelection: bool = True,
                isRowSelection: bool = True, isEditingTrigger: bool = True, isHHeaderFixed: bool = False,
                isVHeaderFixed: bool = False, rect: Tuple[int, int, int, int] = None, parent: QWidget = None):
    """
    Creates a ``Qt.QTableWidget`` with the passed arguments and returns it.

    :param rowCount: The amount of rows which the table should have: int
    :param colCount: The amount of columns which the table should have: int
    :param colsWidth: The columns' width, default to None: List[Tuple[col: int, width: int]]
    :param isCellSelection: Whether the cell selection should be activated or not, default to True: bool
    :param isRowSelection: Whether the row selection should be activated or not, default to True: bool
    :param isEditingTrigger: Whether the editing trigger should be activated or not, default to True: bool
    :param isHHeaderFixed: Whether the horizontal header should be fixed or not, default to False: bool
    :param isVHeaderFixed: Whether the vertical header should be fixed or not, default to False: bool
    :param rect: The geometry of the widget (default to None): Tuple[left: int, top: int, width: int, height: int]
    :param parent: The parent widget on which the button should be placed on (default to None): QWidget

    :return: The table: Qt.QTableWidget
    """

    table = QTableWidget()

    if parent is not None:
        table.setParent(parent)

    table.setRowCount(rowCount)
    table.setColumnCount(colCount)

    if colsWidth is not None:
        for colWidth in colsWidth:
            col = colWidth[0]
            w = colWidth[1]
            table.setColumnWidth(col, w)

    if not isCellSelection:
        table.setSelectionMode(QAbstractItemView.NoSelection)

    if not isRowSelection:
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

    if not isEditingTrigger:
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    if isHHeaderFixed:
        tableHHeader = table.horizontalHeader()
        tableHHeader.setSectionResizeMode(QHeaderView.Fixed)

    if isVHeaderFixed:
        tableVHeader = table.verticalHeader()
        tableVHeader.setSectionResizeMode(QHeaderView.Fixed)

    if rect is not None:
        table.setGeometry(QRect(rect[0], rect[1], rect[2], rect[3]))

    return table


def createTab(tabs: List[Tuple[Any, Union[QIcon, None], str]], func: Callable = None,
              rect: Tuple[int, int, int, int] = None, parent: QWidget = None):
    """
    Creates a ``Qt.QTabWidget`` with the passed arguments and returns it.

    :param tabs: The tabs which should be added to the tab widget: List[Tuple[widget: Any, icon: Union[QIcon, None], label: str]]
    :param func: The follow-up function which gets called when the tab changed, default to None: Callable
    :param rect: The geometry of the widget (default to None): Tuple[left: int, top: int, width: int, height: int]
    :param parent: The parent widget on which the button should be placed on (default to None): QWidget

    :return: The tab: Qt.QTabWidget
    """


    tabWidget = QTabWidget()

    if parent is not None:
        tabWidget.setParent(parent)

    for tab in tabs:
        widget = tab[0]
        icon = tab[1]
        label = tab[2]

        tabWidget.addTab(widget, icon, label)

    if rect is not None:
        tabWidget.setGeometry(QRect(rect[0], rect[1], rect[2], rect[3]))

    if func is not None:
        tabWidget.currentChanged.connect(func)

    return tabWidget


def createCheckBox(text: str, func: Callable = None):
    """

    :param text: The text of the checkbox
    :param func: The follow-up function which gets called when the checkbox state changed: Callable
    :return:
    """

    checkBox = QCheckBox(text)

    if func is not None:
        checkBox.stateChanged.connect(lambda: func(checkBox.isChecked()))

    return checkBox


def createMessageBox(mainWindow: QMainWindow, boxTitle: str, boxText: str,
                     stdBtns: List[Union[QMessageBox.StandardButtons, QMessageBox.StandardButton]], icon: QMessageBox.Icon,
                     textFormat: Qt.TextFormat = None, checkBox: QCheckBox = None, func: Callable = None, return_: bool = False):
    """
    Creates a ``Qt.QMessageBox`` and executes it.

    :param mainWindow: The main window. It's needed to align the message box above the main window: QMainWindow
    :param boxTitle: The message box's title: str
    :param boxText: The message box's text: str
    :param stdBtns: The standard buttons of the message box: Union[QMessageBox.StandardButtons, QMessageBox.StandardButton]
    :param icon: The message box's icon (not window icon): QMessageBox.Icon
    :param textFormat: The text format of the text (default to None): Qt.TextFormat
    :param func: The follow-up function which gets called when the buttons get clicked, default to None: Callable
    :param return_: Whether the message box should be return or not
    """

    msgBox = QMessageBox(mainWindow)
    msgBox.setWindowTitle(boxTitle)
    msgBox.setText(boxText)
    msgBox.setStandardButtons(functools.reduce(lambda x, y: x | y, stdBtns))
    msgBox.setIcon(icon)

    if textFormat is not None:
        msgBox.setTextFormat(textFormat)

    if checkBox is not None:
        msgBox.setCheckBox(checkBox)

    if func is not None:
        msgBox.accepted.connect(lambda: func(msgBox.clickedButton().text(), msgBox))
        msgBox.rejected.connect(lambda: func(msgBox.clickedButton().text(), msgBox))

    if return_:
        return msgBox
    else:
        msgBox.exec()


def createDialog(mainWindow: QMainWindow, size: Tuple[int, int], winTitle: str, winFlags: List[Qt.WindowFlags] = None,
                 layout: Union[QGridLayout, QHBoxLayout, QVBoxLayout] = None, isCloseButton: bool = True):
    """
    Creates a ``Qt.QDialog`` with the passed arguments and returns it.

    :param mainWindow: The main window. It's needed to align the message box above the main window: QMainWindow
    :param size: The size of the dialog window: Tuple[x: int, y: int]
    :param winTitle: The title of the dialog window: str
    :param winFlags: The flags of the dialog window, default to None: List[Qt.WindowFlags]
    :param layout: The layout of the dialog window, default to None: Union[QGridLayout, QHBoxLayout, QVBoxLayout]

    :return: The dialog window: QDialog
    """

    dlg = QDialog(mainWindow, functools.reduce(lambda a, b: a | b, winFlags))
    if not isCloseButton:
        dlg.setWindowFlag(Qt.WindowCloseButtonHint, False)

    x = size[0]
    y = size[1]
    dlg.setFixedSize(x, y)
    dlg.setWindowTitle(winTitle)
    dlg.setLayout(layout)

    return dlg


def createDialogButtonBox(btns: List[Union[Tuple[str, QDialogButtonBox.ButtonRole], QDialogButtonBox.StandardButton]], acceptedFunc: Tuple[Callable, Dict[str, Any]] = None,
                          rejectedFunc: Tuple[Callable, Dict[str, Any]] = None):
    """
    Creates a ``Qt.QDialogButtonBox`` with the passed arguments and returns it.

    :param btns: The buttons which gets added to the button box: List[Union[Tuple[label: str, btn_role: QDialogButtonBox.ButtonRole], std_btn: QDialogButtonBox.StandardButton]]
    :param acceptedFunc: The function and his kwargs which gets called when a button with QDialogButtonBox.AcceptRole gets clicked, default to None: Tuple[func: Callable, kwargs: Dict[attr: str, value: Any]]
    :param rejectedFunc: The function and his kwargs which gets called when a button with QDialogButtonBox.RejectRole gets clicked, default to None: Tuple[func: Callable, kwargs: Dict[attr: str, value: Any]]

    :return: The button box: Qt.QDialogButtonBox
    """


    dlgBtnBox = QDialogButtonBox()

    for btn in btns:
        if type(btn) == tuple:
            btnLabel = btn[0]
            btnRole = btn[1]
            dlgBtnBox.addButton(btnLabel, btnRole)

        elif type(btn) == QDialogButtonBox.StandardButton:
            dlgBtnBox.addButton(btn)

        else:
            raise TypeError(f"Unexpected type '{btn.__class__.__name__}'")

    if acceptedFunc is not None:
        func_accept = acceptedFunc[0]
        kwargs_accept: dict = acceptedFunc[1]

        dlgBtnBox.accepted.connect(lambda: func_accept(**kwargs_accept))

    if rejectedFunc is not None:
        func_reject = rejectedFunc[0]
        kwargs_reject: dict = rejectedFunc[1]

        dlgBtnBox.rejected.connect(lambda: func_reject(**kwargs_reject))

    return dlgBtnBox


def createComboBox(items: List[str], placeholder: str = None, isPlaceholderBold: bool = False,
                   fontStr: str = STD_FONT, fontSize: int = STD_FONTSIZE, rect: Tuple[int, int, int, int] = None,
                   parent: QWidget = None):
    """
    Creates a ``Qt.QComboBox`` (dropdown) with the passed arguments and returns it.

    :param items: The items which should be added to the dropdown: List[str]
    :param placeholder: The placeholder of the dropdown (default to None): str
    :param isPlaceholderBold: Whether the placeholder is bold or not (default to False): bool
    :param fontStr: The font which has the dropdown's text (default to "Calibri"): str
    :param fontSize: The font's size (default to 10): int
    :param rect: The geometry of the widget (default to None): Tuple[left: int, top: int, width: int, height: int]
    :param parent: The parent widget on which the button should be placed on (default to None): QWidget

    :return: The dropdown: Qt.QComboBox
    """

    for item in items:
        if type(item) != str:
            raise TypeError(f"Unexpected type '{item.__class__.__name__}'")

    comboBox = QComboBox(isPlaceholderBold=isPlaceholderBold)
    font = QFont(fontStr, fontSize)
    comboBox.setFont(font)

    if parent is not None:
        comboBox.setParent(parent)

    comboBox.addItems(items)

    if rect is not None:
        comboBox.setGeometry(QRect(rect[0], rect[1], rect[2], rect[3]))

    if placeholder is not None:
        comboBox.setPlaceholderText(placeholder)
        comboBox.setCurrentIndex(-1)

    return comboBox




def createSlider(size: Tuple[int, int], minVal: int, maxVal: int, singleStep: int, orientation: Qt.Orientation,
                 isDisabled: bool = False, func_onRelease: Callable = None, func_onValueChanged: Callable = None,
                 rect: Tuple[int, int, int, int] = None, parent: QWidget = None):
    """
    Creates a ``Qt.QSlider`` with the passed arguments and returns it.

    :param size: The size of the slider: Tuple[x: int, y: int]
    :param minVal: The minimum value of the slider: int
    :param maxVal: The maximum value of the slider: int
    :param singleStep: The single step size: int
    :param orientation: The orientation of the slide (vertical or horizontal): Qt.Orientation
    :param isDisabled: Whether the slider should be disabled or not (default to False): bool
    :param func_onRelease: The function which gets called when the slider is released, default to None: Callable
    :param func_onValueChanged: The function which gets called when the slider value has changed, default to None: Callable
    :param rect: The geometry of the widget (default to None): Tuple[left: int, top: int, width: int, height: int]
    :param parent: The parent widget on which the button should be placed on (default to None): QWidget

    :return: The slider: Qt.QSlider
    """

    slider = QSlider()

    if parent is not None:
        slider.setParent(parent)

    slider.setFixedSize(size[0], size[1])
    slider.setMinimum(minVal)
    slider.setMaximum(maxVal)
    slider.setOrientation(orientation)

    if rect is not None:
        slider.setGeometry(QRect(rect[0], rect[1], rect[2], rect[3]))

    if func_onRelease is not None:
        slider.sliderReleased.connect(func_onRelease)

    if func_onValueChanged is not None:
        slider.valueChanged.connect(func_onValueChanged)

    if isDisabled:
        slider.setDisabled(True)

    return slider


def createGridLayout(*items: HINT_gridLayout, margins: Union[Tuple[int, int, int, int], QMargins] = None):
    """
    Creates a ``Qt.QGridLayout`` with the passed arguments and returns it.

    :param margins: KWARG
    :param items: The target/s which should be placed into the layout: Union[Tuple[QWidget, Tuple[x: int, y: int], Union[alignment: Qt.Alignment, None]], Tuple[QLayout, Tuple[x: int, y: int], Union[alignment: Qt.Alignment, None]]]
    :return: The grid layout: Qt.QGridLayout
    """

    layout = QGridLayout()

    if margins is not None:
        if type(margins) == QMargins:
            layout.setContentsMargins(margins)

        else:
            left = margins[0]
            top = margins[1]
            right = margins[2]
            bottom = margins[3]
            layout.setContentsMargins(left, top, right, bottom)

    for item in items:
        target = item[0]
        dimensions = item[1]
        x = dimensions[0]
        y = dimensions[1]

        if len(item) < 3:
            if len(dimensions) < 3:
                if "layout" in target.__class__.__name__.lower():
                    layout.addLayout(target, y, x)

                elif type(target) == QSpacerItem:
                    layout.addItem(target, y, x)

                else:
                    layout.addWidget(target, y, x)
            else:
                rowSpawn = dimensions[2]
                colSpawn = dimensions[3]

                if "layout" in target.__class__.__name__.lower():
                    layout.addLayout(target, y, x, rowSpawn, colSpawn)

                elif type(target) == QSpacerItem:
                    layout.addItem(target, y, x, rowSpawn, colSpawn)

                else:
                    layout.addWidget(target, y, x, rowSpawn, colSpawn)

        else:
            alignment = item[2]

            if len(dimensions) < 3:
                if "layout" in target.__class__.__name__.lower():
                    layout.addLayout(target, y, x, alignment=alignment)

                elif type(target) == QSpacerItem:
                    layout.addItem(target, y, x, alignment=alignment)

                else:
                    layout.addWidget(target, y, x, alignment=alignment)
            else:
                rowSpawn = dimensions[2]
                colSpawn = dimensions[3]

                if "layout" in target.__class__.__name__.lower():
                    layout.addLayout(target, y, x, rowSpawn, colSpawn, alignment=alignment)

                elif type(target) == QSpacerItem:
                    layout.addItem(target, y, x, rowSpawn, colSpawn, alignment=alignment)

                else:
                    layout.addWidget(target, y, x, rowSpawn, colSpawn, alignment=alignment)


    return layout


def updateEditorTable(table: QTableWidget):
    """
    Updates the table (``Qt.QTabelWidget``) in the editor tab.

    :param table: The editor table: QTableWidget
    """

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

    with open(Path.json_Texts, "r") as fdata:
        data = json.load(fdata)

    col = 0
    row = 1
    for k, v in data.items():
        labelItem = QTextEdit()
        labelItem.setFont(itemFont)
        labelItem.setText(k)
        labelItem.setTextInteractionFlags(Qt.TextSelectableByMouse)
        labelItem.setReadOnly(True)
        labelItem.setTextInteractionFlags(Qt.TextSelectableByMouse)
        labelItem.setFrameStyle(QFrame.NoFrame)
        labelItem.setAlignment(Qt.AlignCenter)

        textItem = QTextEdit()
        textItem.setFont(itemFont)
        textItem.setText(v)
        textItem.setReadOnly(True)
        textItem.setTextInteractionFlags(Qt.TextSelectableByMouse)
        textItem.setFrameStyle(QFrame.NoFrame)
        textItem.setAlignment(Qt.AlignCenter)
        textItem.setFixedHeight(round(textItem.document().size().height()))

        table.setCellWidget(row, col, labelItem)
        table.setCellWidget(row, col + 1, textItem)
        table.resizeRowsToContents()

        row += 1


def updateRunDropdown(comboBox: QComboBox):
    """
    Updates the dropdown (``Qt.QComboBox``) to select a pre-created text in the run tab.

    :param comboBox: The dropdown to select a pre-created text: QTableWidget
    """

    with open(Path.json_Texts, "r") as fdataTexts:
        dataTexts = json.load(fdataTexts)

    with open(Path.json_States, "r") as fdataStates:
        dataStates = json.load(fdataStates)

    comboBox.clear()
    comboBox.addItems(dataTexts.keys())

    if len(list(dataTexts.keys())) == 0:
        placeholder = "No texts available"

    else:
        placeholder = "Select text"

    comboBox.setPlaceholderText(placeholder)
    comboBox.setCurrentIndex(-1)


def checkValidStr(string: str):
    """
    Checks if a specific string has invalid chars in it and returns the valid state and a list of all (not duplicated) invalid chars in the specific string.

    :param string: The string which should be checked: str
    :return: The valid state and a list of all (not duplicated) invalid chars in the specific string: bool, list
    """

    validChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜËÀÉÈabcdefghijklmnopqrstuvwxyzäöüëàéè0123456789.,'\"?!@_*#$%&()+-/:;<=>[\]^`{|}~© "

    invalidChars = []
    valid = True
    for char in string:
        if char not in validChars:
            valid = False
            invalidChars.append(char)

    return valid, list(set(invalidChars))

