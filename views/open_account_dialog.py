"""Dialog for opening a new bank account."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QWidget,
)

from controllers.bank_controller import BankController


class OpenAccountDialog(QDialog):
    """Modal dialog that collects the fields needed to open an account."""

    def __init__(
        self,
        controller: BankController,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Lay out the fields and wire up OK/Cancel.

        Args:
            controller: Controller the dialog calls to create the account.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._controller: BankController = controller
        self._opened_name: Optional[str] = None
        self.setWindowTitle("Open New Account")
        self.setModal(True)
        self.setMinimumWidth(340)

        form = QFormLayout(self)

        self._type_combo = QComboBox()
        self._type_combo.addItems(BankController.ACCOUNT_TYPE_LABELS)
        self._type_combo.currentTextChanged.connect(self._on_type_changed)
        form.addRow("Account type:", self._type_combo)

        self._name_edit = QLineEdit()
        self._name_edit.setMaxLength(40)
        self._name_edit.setPlaceholderText("Jane Doe")
        form.addRow("Holder name:", self._name_edit)

        self._balance_spin = QDoubleSpinBox()
        self._balance_spin.setRange(0.0, 1_000_000.0)
        self._balance_spin.setDecimals(2)
        self._balance_spin.setPrefix("$ ")
        self._balance_spin.setValue(0.0)
        form.addRow("Starting balance:", self._balance_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_submit)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self._on_type_changed(self._type_combo.currentText())

    def _on_type_changed(self, text: str) -> None:
        """Disable the balance field when a Saving account is selected.

        Args:
            text: The newly selected account type label.
        """
        is_saving = text.startswith("Saving")
        self._balance_spin.setEnabled(not is_saving)
        if is_saving:
            # Saving accounts always start at the class minimum per Lab 9.
            self._balance_spin.setSpecialValueText("$ 100.00 (minimum)")
            self._balance_spin.setValue(0.0)
        else:
            self._balance_spin.setSpecialValueText("")

    def _on_submit(self) -> None:
        """Ask the controller to open the account.

        Invalid input is reported through a warning dialog; the main
        dialog stays open so the user can correct the field.
        """
        result = self._controller.open_account(
            account_type=self._type_combo.currentText().split(" ")[0],
            name=self._name_edit.text(),
            starting_balance_text=f"{self._balance_spin.value():.2f}",
        )
        if not result.success:
            QMessageBox.warning(self, "Could not open account", result.message)
            return
        self._opened_name = self._name_edit.text().strip()
        self.accept()

    def opened_account_name(self) -> Optional[str]:
        """Return the name of the account that was opened, or None."""
        return self._opened_name
