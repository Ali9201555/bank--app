"""Entry point for the Project 1 Bank application.

Run with:
    python main.py

The launcher wires every model, controller, and view together and then
hands control to the Qt event loop.
"""

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from bank_controller import BankController
from bank import Bank
from transaction import TransactionLog
from main_window import MainWindow


def main() -> int:
    """Bootstrap the app and return the Qt exit code.

    Returns:
        Integer exit code from QApplication.exec.
    """
    bank = Bank("data/accounts.csv")
    log = TransactionLog("data/transactions.csv")
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
    except Exception as exc:
        # Catch every other exception so a crash during startup shows a
        # dialog instead of just a silent stack trace.
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal error", str(exc))
        raise
