"""SavingAccount class, improved from Lab 9.

Same public API the lab specified (deposit, withdraw, set_balance,
apply_interest, __str__) so the Lab 9 main.py still runs unchanged.
Additions for Project 1: type hints, docstrings, and CSV round-trip via
to_dict / from_dict so the deposit counter survives a restart.
"""

from __future__ import annotations

from typing import Dict

from models.account import Account


class SavingAccount(Account):
    """Interest-bearing account with a minimum balance and deposit streak.

    Class constants:
        MINIMUM: Lowest allowed balance. The balance is clamped to this
            value any time ``set_balance`` is called with a smaller value.
        RATE: Interest rate applied every five successful deposits.
    """

    MINIMUM: float = 100
    RATE: float = 0.02
    ACCOUNT_TYPE: str = "SavingAccount"

    def __init__(self, name: str) -> None:
        """Create a savings account seeded with the minimum balance.

        Args:
            name: The account holder's display name.
        """
        super().__init__(name, SavingAccount.MINIMUM)
        self.__deposit_count: int = 0

    def apply_interest(self) -> None:
        """Grow the balance by ``RATE`` percent."""
        self.set_balance(self.get_balance() * (1 + SavingAccount.RATE))

    def deposit(self, amount: float) -> bool:
        """Deposit and automatically apply interest on every 5th deposit.

        Args:
            amount: Amount to deposit. Must be strictly positive.

        Returns:
            True when the balance changed, False otherwise.
        """
        if amount is None or amount <= 0:
            return False

        success = super().deposit(amount)
        if success:
            self.__deposit_count += 1
            if self.__deposit_count % 5 == 0:
                self.apply_interest()
        return success

    def withdraw(self, amount: float) -> bool:
        """Withdraw, but never below the configured minimum balance.

        Args:
            amount: Amount to withdraw. Must be positive and leave the
                account at or above ``MINIMUM``.

        Returns:
            True when the balance changed, False otherwise.
        """
        if amount is None or amount <= 0:
            return False
        if self.get_balance() - amount < SavingAccount.MINIMUM:
            return False
        return super().withdraw(amount)

    def set_balance(self, value: float) -> None:
        """Set the balance, clamping to the minimum instead of zero.

        Args:
            value: The desired balance.
        """
        if value is None or value < SavingAccount.MINIMUM:
            super().set_balance(SavingAccount.MINIMUM)
        else:
            super().set_balance(value)

    def __str__(self) -> str:
        """Return the Lab 9 SAVING ACCOUNT string format."""
        return f"SAVING ACCOUNT: {super().__str__()}"

    # ------------------------------------------------------------------
    # Project 1 persistence helpers
    # ------------------------------------------------------------------

    def get_deposit_count(self) -> int:
        """Return the number of successful deposits on this account."""
        return self.__deposit_count

    def to_dict(self) -> Dict[str, str]:
        """Serialize including the deposit counter used for interest."""
        row = super().to_dict()
        row["account_type"] = self.ACCOUNT_TYPE
        row["extra"] = str(self.__deposit_count)
        return row

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "SavingAccount":
        """Restore a savings account along with its deposit counter.

        Args:
            row: Mapping of CSV header to value.

        Returns:
            A fully rebuilt SavingAccount.

        Raises:
            ValueError: If required fields are missing or malformed.
        """
        try:
            account = cls(row["name"])
            account.set_balance(float(row["balance"]))
            account.__deposit_count = int(row.get("extra") or 0)  # noqa: SLF001
            return account
        except (KeyError, TypeError) as exc:
            raise ValueError("Malformed saving account row.") from exc
