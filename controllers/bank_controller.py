"""Controller mediating between the GUI and the bank models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from models.account import Account
from models.bank import Bank
from models.checking_account import CheckingAccount
from models.saving_account import SavingAccount
from models.transaction import TransactionLog


@dataclass
class OperationResult:
    """Uniform return type for controller methods.

    Attributes:
        success: True when the operation changed state.
        message: Human-readable summary safe to show in a status bar.
    """

    success: bool
    message: str


class BankController:
    """Validates GUI input, mutates the Bank, and writes the txn log."""

    ACCOUNT_TYPE_LABELS: List[str] = [
        "Checking",
        "Saving",
        "Account (basic)",
    ]

    def __init__(self, bank: Bank, log: TransactionLog) -> None:
        """Store references to the shared bank and transaction log.

        Args:
            bank: The Bank model holding every account.
            log: The append-only TransactionLog for audit history.
        """
        self._bank: Bank = bank
        self._log: TransactionLog = log

    # ------------------------------------------------------------------
    # Input validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def parse_amount(raw: str) -> float:
        """Parse an amount string, raising ValueError on bad input.

        Accepts a leading ``$`` and commas so users can paste values from
        a statement without having to strip them first.

        Args:
            raw: Raw text from the dialog's amount field.

        Returns:
            The parsed positive float.

        Raises:
            ValueError: If the input is empty, not a number, or negative.
        """
        if raw is None:
            raise ValueError("Amount is required.")
        cleaned = str(raw).strip().lstrip("$").replace(",", "")
        if not cleaned:
            raise ValueError("Amount is required.")
        try:
            value = float(cleaned)
        except ValueError as exc:
            raise ValueError("Amount must be a number.") from exc
        if value <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(value, 2)

    @staticmethod
    def validate_name(raw: str) -> str:
        """Validate and normalize a new account holder's name.

        Args:
            raw: Raw text from the name field.

        Returns:
            The stripped, non-empty name.

        Raises:
            ValueError: If the name is empty or overly long.
        """
        if raw is None:
            raise ValueError("Account name is required.")
        name = str(raw).strip()
        if not name:
            raise ValueError("Account name is required.")
        if len(name) > 40:
            raise ValueError("Account name must be 40 characters or fewer.")
        return name

    # ------------------------------------------------------------------
    # Account CRUD
    # ------------------------------------------------------------------

    def open_account(
        self,
        account_type: str,
        name: str,
        starting_balance_text: str,
    ) -> OperationResult:
        """Create a new account of the requested type.

        Args:
            account_type: One of the labels in ``ACCOUNT_TYPE_LABELS``.
            name: Account holder's name.
            starting_balance_text: Raw text for the opening balance.
                Ignored for Saving accounts (they always start at
                ``SavingAccount.MINIMUM``).

        Returns:
            An OperationResult describing the outcome.
        """
        try:
            clean_name = self.validate_name(name)
        except ValueError as exc:
            return OperationResult(False, str(exc))

        # Saving accounts always start at MINIMUM by Lab 9 rules.
        if account_type == "Saving":
            account: Account = SavingAccount(clean_name)
            starting = account.get_balance()
        else:
            try:
                starting = (
                    self.parse_amount(starting_balance_text)
                    if starting_balance_text
                    else 0.0
                )
            except ValueError as exc:
                return OperationResult(False, str(exc))

            if account_type == "Checking":
                account = CheckingAccount(clean_name, starting)
            else:
                account = Account(clean_name, starting)

        try:
            self._bank.add_account(account)
        except ValueError as exc:
            return OperationResult(False, str(exc))

        self._log.record(
            account_name=clean_name,
            kind="OPEN",
            amount=starting,
            balance_after=account.get_balance(),
            detail=f"Opened {account_type} account",
        )
        return OperationResult(
            True,
            f"Opened {account_type} account for {clean_name}.",
        )

    def close_account(self, name: str) -> OperationResult:
        """Remove the account with the given name.

        Args:
            name: The account holder's name.

        Returns:
            An OperationResult describing the outcome.
        """
        account = self._bank.find_by_name(name)
        if account is None:
            return OperationResult(False, f"No account named {name!r}.")
        final_balance = account.get_balance()
        try:
            self._bank.remove_account(name)
        except KeyError as exc:
            return OperationResult(False, str(exc))
        self._log.record(
            account_name=name,
            kind="CLOSE",
            amount=final_balance,
            balance_after=0.0,
            detail="Account closed",
        )
        return OperationResult(True, f"Closed account {name!r}.")

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------

    def deposit(self, name: str, amount_text: str) -> OperationResult:
        """Deposit into the named account.

        Args:
            name: Account holder's name.
            amount_text: Raw text from the amount field.

        Returns:
            An OperationResult describing the outcome.
        """
        account = self._bank.find_by_name(name)
        if account is None:
            return OperationResult(False, f"No account named {name!r}.")

        try:
            amount = self.parse_amount(amount_text)
        except ValueError as exc:
            return OperationResult(False, str(exc))

        before = account.get_balance()
        success = account.deposit(amount)
        if not success:
            return OperationResult(False, "Deposit rejected by the account.")
        after = account.get_balance()
        self._bank.save()
        self._log.record(
            account_name=name,
            kind="DEPOSIT",
            amount=amount,
            balance_after=after,
            detail=f"Deposit of ${amount:.2f}",
        )

        # A saving account may have silently triggered interest on this
        # deposit. Detect that and add a separate INTEREST log row so the
        # history tells the full story.
        if isinstance(account, SavingAccount):
            expected_after = before + amount
            if after > expected_after + 0.001:
                self._log.record(
                    account_name=name,
                    kind="INTEREST",
                    amount=after - expected_after,
                    balance_after=after,
                    detail=(
                        f"Interest at {SavingAccount.RATE * 100:.1f}% "
                        f"applied after 5 deposits"
                    ),
                )

        return OperationResult(
            True,
            f"Deposited ${amount:.2f}. New balance: ${after:.2f}.",
        )

    def withdraw(self, name: str, amount_text: str) -> OperationResult:
        """Withdraw from the named account.

        Args:
            name: Account holder's name.
            amount_text: Raw text from the amount field.

        Returns:
            An OperationResult describing the outcome.
        """
        account = self._bank.find_by_name(name)
        if account is None:
            return OperationResult(False, f"No account named {name!r}.")

        try:
            amount = self.parse_amount(amount_text)
        except ValueError as exc:
            return OperationResult(False, str(exc))

        success = account.withdraw(amount)
        if not success:
            # Explain the common failure modes so the user knows why.
            if isinstance(account, SavingAccount):
                detail = (
                    "Withdrawal rejected: would drop below the "
                    f"${SavingAccount.MINIMUM:.2f} minimum balance."
                )
            elif isinstance(account, CheckingAccount):
                detail = (
                    "Withdrawal rejected: exceeds the "
                    f"${CheckingAccount.OVERDRAFT_LIMIT:.2f} overdraft limit."
                )
            else:
                detail = "Withdrawal rejected: insufficient funds."
            return OperationResult(False, detail)

        after = account.get_balance()
        self._bank.save()
        self._log.record(
            account_name=name,
            kind="WITHDRAW",
            amount=amount,
            balance_after=after,
            detail=f"Withdrawal of ${amount:.2f}",
        )
        return OperationResult(
            True,
            f"Withdrew ${amount:.2f}. New balance: ${after:.2f}.",
        )

    # ------------------------------------------------------------------
    # Read-only helpers used by the views
    # ------------------------------------------------------------------

    def list_accounts(self) -> List[Account]:
        """Return every account in insertion order."""
        return self._bank.list_accounts()

    def get_total(self) -> float:
        """Return the combined balance across every account."""
        return self._bank.total()

    def find_account(self, name: str) -> Optional[Account]:
        """Return the account with the given name, or None."""
        return self._bank.find_by_name(name)

    def transaction_log(self) -> TransactionLog:
        """Expose the transaction log for the history dialog."""
        return self._log
