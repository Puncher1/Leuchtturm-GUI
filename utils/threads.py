import traceback, sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ThreadSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:
    error
        Takes 3 objects which map the traceback.
    """
    error = pyqtSignal(object, object, object)

class Thread(QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    """

    def __init__(self, fn, *args, **kwargs):
        """
        :param fn: The function callback to run on this worker thread. Args and kwargs will be passed through to the runner.
        :type fn: function
        :param args: Arguments to pass to the callback function
        :param kwargs: Keywords to pass to the callback function
        """

        super(Thread, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadSignals()


    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        try:
            print("run fn")
            self.fn(*self.args, **self.kwargs)
        except:
            error = sys.exc_info()[1]
            etype = type(error)
            etrace = error.__traceback__
            try:
                self.signals.error.emit(etype, error, etrace)
            except RuntimeError:
                pass

