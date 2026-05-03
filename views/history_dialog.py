"""Dialog showing the transaction history for one account."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.transaction import TransactionLog


class HistoryDialog(QDialog):
    """Scrollable table of one account's or all accounts' transactions."""

    def __init__(
        self,
        log: TransactionLog,
        account_name: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Build the table and populate it.

        Args:
            log: The TransactionLog to query.
            account_name: When set, only that account's rows are shown.
                Otherwise every recent transaction is shown.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        title = (
            f"Transactions — {account_name}"
            if account_name
            else "All Recent Transactions"
        )
        self.setWindowTitle(title)
        self.setMinimumSize(640, 380)

        rows = (
            log.for_account(account_name)
            if account_name
            else log.all_recent(200)
        )

        layout = QVBoxLayout(self)

        table = QTableWidget(len(rows), 5)
        table.setHorizontalHeaderLabels(
            ["Timestamp", "Account", "Kind", "Amount", "Balance After"]
        )
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        for row_index, txn in enumerate(rows):
            table.setItem(row_index, 0, QTableWidgetItem(txn.timestamp))
            table.setItem(row_index, 1, QTableWidgetItem(txn.account_name))
            table.setItem(row_index, 2, QTableWidgetItem(txn.kind))
            table.setItem(row_index, 3, QTableWidgetItem(f"${txn.amount:.2f}"))
            table.setItem(
                row_index, 4, QTableWidgetItem(f"${txn.balance_after:.2f}")
            )

        layout.addWidget(table)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_button = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_button is not None:
            close_button.clicked.connect(self.accept)
        layout.addWidget(buttons)
