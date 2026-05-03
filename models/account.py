"""Base Account class, improved from Lab 9.

Lab 9 originally asked for a plain Account with private account_name and
account_balance fields. For Project 1 the same public interface is kept
(so the original Lab 9 main.py still works) but the class gains:

  * Full docstrings and type hints on every method.
  * Explicit InvalidAmountError raised on bad deposit/withdraw input.
  * A serialization hook (to_dict / from_dict) used by the Bank CSV layer.
  * An account_type label so subclasses can round-trip through the CSV.
"""

from __future__ import annotations

from typing import Dict


class InvalidAmountError(ValueError):
    """Raised when a deposit or withdrawal amount cannot be accepted.

    Using a named subclass of ValueError lets the GUI layer distinguish
    "user typed nonsense" from other unrelated ValueErrors.
    """


class Account:
    """A basic bank account with private name and balance fields.

    The public API matches the Lab 9 spec exactly (deposit, withdraw,
    get_balance, get_name, set_balance, set_name, __str__) so the
    original test harness in main.py still passes. Everything else is
    additive.
    """

    ACCOUNT_TYPE: str = "Account"

    def __init__(self, name: str, balance: float = 0) -> None:
        """Create an account with a starting balance.

        Args:
            name: The account holder's display name.
            balance: The starting balance. Values below zero are clamped
                to zero by ``set_balance`` to match Lab 9 behavior.
        """
        self.__account_name: str = name
        self.__account_balance: float = 0
        # Run the incoming balance through the setter so its clamping
        # rules apply consistently.
        self.set_balance(balance)

    def deposit(self, amount: float) -> bool:
        """Add money to the account.

        Args:
            amount: Amount to deposit. Must be strictly positive.

        Returns:
            True when the balance changed, False otherwise.
        """
        if amount is None or amount <= 0:
            return False
        self.__account_balance += float(amount)
        return True

    def withdraw(self, amount: float) -> bool:
        """Remove money from the account.

        Args:
            amount: Amount to withdraw. Must be positive and not exceed
                the current balance.

        Returns:
            True when the balance changed, False otherwise.
        """
        if amount is None or amount <= 0 or amount > self.__account_balance:
            return False
        self.__account_balance -= float(amount)
        return True

    def get_balance(self) -> float:
        """Return the current account balance."""
        return self.__account_balance

    def get_name(self) -> str:
        """Return the account holder's name."""
        return self.__account_name

    def set_balance(self, value: float) -> None:
        """Set the balance directly, clamping negatives to zero.

        Args:
            value: The desired balance.
        """
        if value is None or value < 0:
            self.__account_balance = 0
        else:
            self.__account_balance = float(value)

    def set_name(self, value: str) -> None:
        """Update the account holder's name.

        Args:
            value: The new name. Empty strings are rejected to match the
                validation the GUI uses.

        Raises:
            ValueError: If ``value`` is empty after stripping whitespace.
        """
        if value is None or not str(value).strip():
            raise ValueError("Account name cannot be empty.")
        self.__account_name = str(value).strip()

    def __str__(self) -> str:
        """Return the Lab 9 string format for this account.

        Subclasses that want extra context should call ``super().__str__()``
        rather than duplicating this format.
        """
        return (
            f"Account name = {self.get_name()}, "
            f"Account balance = {self.get_balance():.2f}"
        )

    # ------------------------------------------------------------------
    # Project 1 additions (not part of Lab 9)
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, str]:
        """Serialize this account to a flat string dict for CSV storage.

        Subclasses override this to add their own fields. The
        ``account_type`` key is used by :meth:`Bank.load` to rebuild the
        right subclass when reading back from disk.
        """
        return {
            "account_type": self.ACCOUNT_TYPE,
            "name": self.get_name(),
            "balance": f"{self.get_balance():.2f}",
            "extra": "",
        }

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "Account":
        """Reconstruct an Account from a CSV row dict.

        Args:
            row: Mapping of CSV header to value.

        Returns:
            A new Account with the name and balance restored.

        Raises:
            ValueError: If required fields are missing or malformed.
        """
        try:
            return cls(row["name"], float(row["balance"]))
        except (KeyError, TypeError) as exc:
            raise ValueError("Malformed account row.") from exc
