"""CheckingAccount — a second subclass added for Project 1.

Lab 9 only required Account and SavingAccount. Adding a third concrete
subclass strengthens the inheritance demonstration required by the
Project 1 rubric and gives the GUI a realistic second account type to
showcase.
"""

from models.account import Account


class CheckingAccount(Account):
    """Everyday account with a configurable overdraft allowance.

    Unlike a SavingAccount, a checking account has no minimum balance,
    accrues no interest, and may be overdrawn up to ``OVERDRAFT_LIMIT``
    dollars. Each overdraft charges a flat ``OVERDRAFT_FEE``.

    Class constants:
        OVERDRAFT_LIMIT: Maximum negative balance allowed, in dollars.
        OVERDRAFT_FEE: Flat fee charged any time the account goes negative.
    """

    OVERDRAFT_LIMIT = 50.0
    OVERDRAFT_FEE = 5.0
    ACCOUNT_TYPE = "CheckingAccount"

    def __init__(self, name: str, balance: float = 0) -> None:
        """Create a checking account.

        Args:
            name: The account holder's display name.
            balance: The starting balance. Negative openings are clamped
                to zero by the base class.
        """
        super().__init__(name, balance)
        self.__overdraft_count = 0

    def withdraw(self, amount: float) -> bool:
        """Withdraw, allowing the balance to go up to -OVERDRAFT_LIMIT.

        Overrides the base class to explicitly permit a negative balance.
        The base Account's ``set_balance`` clamps negatives to zero, so
        we set the private balance directly through a helper instead.

        Args:
            amount: Amount to withdraw. Must be strictly positive.

        Returns:
            True on success, False when the withdrawal would exceed the
            overdraft limit or the amount is invalid.
        """
        if amount is None or amount <= 0:
            return False
        projected = self.get_balance() - float(amount)
        if projected < -CheckingAccount.OVERDRAFT_LIMIT:
            return False

        # Bypass the base set_balance (which clamps at 0) so checking
        # accounts can run a negative balance.
        self._apply_raw_balance(projected)
        if projected < 0:
            self.__overdraft_count += 1
            # Apply the overdraft fee on top of the withdrawal.
            self._apply_raw_balance(projected - CheckingAccount.OVERDRAFT_FEE)
        return True

    def _apply_raw_balance(self, value: float) -> None:
        """Set the balance without the zero-floor clamp.

        This helper is used by ``withdraw`` to allow intentional negative
        balances. It is kept out of the public API so callers must go
        through the ordinary deposit/withdraw methods.

        Args:
            value: The raw balance to assign.
        """
        # We need the mangled attribute name because ``__account_balance``
        # is private on the base Account class.
        self._Account__account_balance = float(value)

    def get_overdraft_count(self) -> int:
        """Return how many times this account has gone negative."""
        return self.__overdraft_count

    def __str__(self) -> str:
        """Return a CHECKING ACCOUNT labeled string."""
        return f"CHECKING ACCOUNT: {super().__str__()}"

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize including the overdraft counter."""
        row = super().to_dict()
        row["account_type"] = self.ACCOUNT_TYPE
        row["extra"] = str(self.__overdraft_count)
        return row

    @classmethod
    def from_dict(cls, row: dict) -> "CheckingAccount":
        """Restore a checking account along with its overdraft counter.

        Args:
            row: Mapping of CSV header to value.

        Returns:
            A CheckingAccount with the same balance and overdraft count
            as was saved.

        Raises:
            ValueError: If required fields are missing or malformed.
        """
        try:
            account = cls(row["name"], float(row["balance"]))
            count_text = row.get("extra") or "0"
            account._CheckingAccount__overdraft_count = int(count_text)
            return account
        except (KeyError, TypeError):
            raise ValueError("Malformed checking account row.")
