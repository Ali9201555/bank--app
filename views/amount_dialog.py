"""Dialog that prompts for a deposit or withdrawal amount."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QWidget,
)


class AmountDialog(QDialog):
    """Shared dialog used for both deposit and withdrawal flows."""

    def __init__(
        self,
        title: str,
        account_label: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Build the amount spin box.

        Args:
            title: Window title, e.g. "Deposit".
            account_label: Displayed at the top so the user can confirm
                which account they are acting on.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._amount: float = 0.0
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(320)

        form = QFormLayout(self)

        info = QLabel(account_label)
        info.setStyleSheet("font-weight: 600;")
        form.addRow(info)

        self._amount_spin = QDoubleSpinBox()
        self._amount_spin.setRange(0.01, 1_000_000.0)
        self._amount_spin.setDecimals(2)
        self._amount_spin.setPrefix("$ ")
        self._amount_spin.setValue(20.0)
        form.addRow("Amount:", self._amount_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_submit)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _on_submit(self) -> None:
        """Capture the amount and accept, rejecting non-positive values."""
        value = self._amount_spin.value()
        if value <= 0:
            QMessageBox.warning(
                self,
                "Invalid amount",
                "Please enter an amount greater than zero.",
            )
            return
        self._amount = round(value, 2)
        self.accept()

    def get_amount_text(self) -> str:
        """Return the amount formatted as a plain decimal string."""
        return f"{self._amount:.2f}"
