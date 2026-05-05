"""Entry point for the Project 1 Bank application.

Run with:
    python main.py

The launcher wires every model, controller, and view together and then
hands control to the Qt event loop.
"""

import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication, QMessageBox

from bank_controller import BankController
from bank import Bank
from transaction import TransactionLog
from main_window import MainWindow


def _data_dir() -> str:
    """Return the absolute path to the ``data`` directory beside main.py.

    Creates the directory if it does not exist.

    Returns:
        Absolute path to the data folder.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    data = os.path.join(here, "data")
    os.makedirs(data, exist_ok=True)
    return data


def main() -> int:
    """Bootstrap the app and return the Qt exit code.

    Returns:
        Integer exit code from QApplication.exec.
    """
    data = _data_dir()

    bank = Bank(os.path.join(data, "accounts.csv"))
    log = TransactionLog(os.path.join(data, "transactions.csv"))
    controller = BankController(bank, log)

    app = QApplication(sys.argv)
    app.setApplicationName("Bank — Project 1")

    window = MainWindow(controller)
    window.show()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        # Catch every other exception so a crash during startup shows a
        # dialog instead of just a silent stack trace.
        message = traceback.format_exc()
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal error", message)
        raise
