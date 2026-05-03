"""Main banking window."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controllers.bank_controller import BankController, OperationResult
from models.checking_account import CheckingAccount
from models.saving_account import SavingAccount
from views.amount_dialog import AmountDialog
from views.history_dialog import HistoryDialog
from views.open_account_dialog import OpenAccountDialog


class MainWindow(QMainWindow):
    """Top-level window listing every account and exposing actions.

    The left side shows the account table; the right side shows a panel
    of buttons for operations on the selected row.
    """

    def __init__(self, controller: BankController) -> None:
        """Build the UI and populate the initial data.

        Args:
            controller: The shared BankController.
        """
        super().__init__()
        self._controller: BankController = controller

        self.setWindowTitle("Bank — Project 1")
        self.resize(880, 520)

        self._build_menu()
        self._build_central_widget()
        self._build_status_bar()

        self._refresh_table()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        """Create the File and Tools menus."""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        open_action = QAction("&Open New Account...", self)
        open_action.triggered.connect(self._on_open_account)
        file_menu.addAction(open_action)

        close_action = QAction("&Close Selected Account", self)
        close_action.triggered.connect(self._on_close_account)
        file_menu.addAction(close_action)

        file_menu.addSeparator()
        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        tools_menu = menu_bar.addMenu("&Tools")
        all_history_action = QAction("All &Recent Transactions...", self)
        all_history_action.triggered.connect(self._on_show_all_history)
        tools_menu.addAction(all_history_action)

    def _build_central_widget(self) -> None:
        """Lay out the table on the left and the action panel on the right."""
        central = QWidget(self)
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Left: account table
        left = QVBoxLayout()
        left.setSpacing(8)

        left.addWidget(QLabel("Accounts"))

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Type", "Name", "Balance", "Notes"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        left.addWidget(self._table, stretch=1)

        self._total_label = QLabel("Total at the bank: $0.00")
        self._total_label.setStyleSheet("font-weight: 700; font-size: 14px;")
        self._total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        left.addWidget(self._total_label)

        root.addLayout(left, stretch=3)

        # Right: action buttons
        right = QVBoxLayout()
        right.setSpacing(8)

        right.addWidget(QLabel("Actions"))

        self._open_button = self._action_button("Open Account", "#2d8f47")
        self._open_button.clicked.connect(self._on_open_account)
        right.addWidget(self._open_button)

        self._deposit_button = self._action_button("Deposit", "#2d6cdf")
        self._deposit_button.clicked.connect(self._on_deposit)
        right.addWidget(self._deposit_button)

        self._withdraw_button = self._action_button("Withdraw", "#c98a2e")
        self._withdraw_button.clicked.connect(self._on_withdraw)
        right.addWidget(self._withdraw_button)

        self._history_button = self._action_button("View History", "#5e4bd5")
        self._history_button.clicked.connect(self._on_view_history)
        right.addWidget(self._history_button)

        self._close_button = self._action_button("Close Account", "#c0392b")
        self._close_button.clicked.connect(self._on_close_account)
        right.addWidget(self._close_button)

        right.addStretch(1)

        root.addLayout(right, stretch=1)

    @staticmethod
    def _action_button(label: str, color_hex: str) -> QPushButton:
        """Create one of the right-side action buttons.

        Args:
            label: Displayed label.
            color_hex: Accent color for the button background.

        Returns:
            The configured QPushButton.
        """
        button = QPushButton(label)
        button.setMinimumHeight(40)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color_hex};
                color: white;
                font-weight: 600;
                border-radius: 8px;
                padding: 8px 12px;
            }}
            QPushButton:disabled {{
                background-color: #888;
                color: #ddd;
            }}
            """
        )
        return button

    def _build_status_bar(self) -> None:
        """Create the bottom status bar for operation feedback."""
        status = QStatusBar(self)
        self.setStatusBar(status)
        status.showMessage("Ready")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_open_account(self) -> None:
        """Open the new-account dialog."""
        dialog = OpenAccountDialog(self._controller, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            name = dialog.opened_account_name()
            self._set_status(f"Opened account for {name}.")
            self._refresh_table()
            if name is not None:
                self._select_row_by_name(name)

    def _on_close_account(self) -> None:
        """Close the currently selected account after a confirmation."""
        account = self._selected_account()
        if account is None:
            QMessageBox.information(
                self, "Nothing selected", "Select an account to close."
            )
            return
        reply = QMessageBox.question(
            self,
            "Close account",
            f"Close the account for {account.get_name()}? "
            "This does not zero the balance in the log.",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        result = self._controller.close_account(account.get_name())
        self._apply_result(result)
        self._refresh_table()

    def _on_deposit(self) -> None:
        """Deposit into the selected account."""
        account = self._selected_account()
        if account is None:
            QMessageBox.information(
                self, "Nothing selected", "Select an account to deposit into."
            )
            return
        dialog = AmountDialog(
            title="Deposit",
            account_label=(
                f"Depositing into: {account.get_name()}"
                f"\nCurrent balance: ${account.get_balance():.2f}"
            ),
            parent=self,
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        result = self._controller.deposit(account.get_name(), dialog.get_amount_text())
        self._apply_result(result)
        self._refresh_table()

    def _on_withdraw(self) -> None:
        """Withdraw from the selected account."""
        account = self._selected_account()
        if account is None:
            QMessageBox.information(
                self, "Nothing selected", "Select an account to withdraw from."
            )
            return
        dialog = AmountDialog(
            title="Withdraw",
            account_label=(
                f"Withdrawing from: {account.get_name()}"
                f"\nCurrent balance: ${account.get_balance():.2f}"
            ),
            parent=self,
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        result = self._controller.withdraw(account.get_name(), dialog.get_amount_text())
        self._apply_result(result)
        self._refresh_table()

    def _on_view_history(self) -> None:
        """Show the history for the selected account."""
        account = self._selected_account()
        if account is None:
            QMessageBox.information(
                self,
                "Nothing selected",
                "Select an account, or use Tools → All Recent Transactions.",
            )
            return
        dialog = HistoryDialog(
            log=self._controller.transaction_log(),
            account_name=account.get_name(),
            parent=self,
        )
        dialog.exec()

    def _on_show_all_history(self) -> None:
        """Show transactions across every account."""
        dialog = HistoryDialog(
            log=self._controller.transaction_log(),
            account_name=None,
            parent=self,
        )
        dialog.exec()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _selected_account(self):
        """Return the Account represented by the current table row.

        Returns:
            The selected Account or None when nothing is selected.
        """
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 1)
        if item is None:
            return None
        return self._controller.find_account(item.text())

    def _select_row_by_name(self, name: str) -> None:
        """Highlight the row whose second cell matches the given name."""
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 1)
            if item is not None and item.text() == name:
                self._table.selectRow(row)
                return

    def _apply_result(self, result: OperationResult) -> None:
        """Show a controller's result in the status bar.

        Args:
            result: The OperationResult returned by the controller.
        """
        self._set_status(result.message)
        if not result.success:
            # Any rejection we want the user to notice — pop a dialog on
            # top of the status-bar message so they cannot miss it.
            QMessageBox.warning(self, "Operation failed", result.message)

    def _set_status(self, message: str) -> None:
        """Proxy for status-bar updates so the string is set in one place."""
        self.statusBar().showMessage(message, 5000)

    def _refresh_table(self) -> None:
        """Repopulate the account table from the controller."""
        accounts = self._controller.list_accounts()
        self._table.setRowCount(len(accounts))
        for row, account in enumerate(accounts):
            type_label = type(account).__name__
            self._table.setItem(row, 0, QTableWidgetItem(type_label))
            self._table.setItem(row, 1, QTableWidgetItem(account.get_name()))
            self._table.setItem(
                row, 2, QTableWidgetItem(f"${account.get_balance():.2f}")
            )

            notes = ""
            if isinstance(account, SavingAccount):
                notes = (
                    f"Deposits: {account.get_deposit_count()}  ·  "
                    f"Min ${SavingAccount.MINIMUM:.0f}  ·  "
                    f"{SavingAccount.RATE * 100:.0f}% every 5"
                )
            elif isinstance(account, CheckingAccount):
                notes = (
                    f"Overdrafts: {account.get_overdraft_count()}  ·  "
                    f"Limit ${CheckingAccount.OVERDRAFT_LIMIT:.0f}"
                )
            self._table.setItem(row, 3, QTableWidgetItem(notes))

        self._total_label.setText(
            f"Total at the bank: ${self._controller.get_total():.2f}"
        )
        enable = len(accounts) > 0
        self._deposit_button.setEnabled(enable)
        self._withdraw_button.setEnabled(enable)
        self._history_button.setEnabled(enable)
        self._close_button.setEnabled(enable)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt signature
        """Flush any in-memory state before Qt tears the window down.

        Args:
            event: The Qt close event.
        """
        # Persistence is already saved eagerly on every mutation; this is
        # just a defensive final flush in case something queued up.
        try:
            self._controller._bank.save()  # noqa: SLF001 - ok at shutdown
        except OSError:
            pass
        super().closeEvent(event)
