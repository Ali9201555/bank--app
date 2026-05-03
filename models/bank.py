"""Bank — in-memory collection of accounts with CSV persistence.

The Bank owns both the list of :class:`~models.account.Account` objects
and the :class:`~models.transaction.TransactionLog`. The original
Lab 9 `get_bank_total()` helper lives here as :meth:`total`.
"""

from __future__ import annotations

import csv
import os
from typing import Dict, Iterable, List, Optional, Type

from models.account import Account
from models.checking_account import CheckingAccount
from models.saving_account import SavingAccount


class Bank:
    """Holds every account and persists them to a CSV file."""

    CSV_FIELDS: List[str] = ["account_type", "name", "balance", "extra"]

    # Maps the stored ``account_type`` label back to a class. Adding a new
    # subclass only requires one line here.
    _TYPE_MAP: Dict[str, Type[Account]] = {
        Account.ACCOUNT_TYPE: Account,
        SavingAccount.ACCOUNT_TYPE: SavingAccount,
        CheckingAccount.ACCOUNT_TYPE: CheckingAccount,
    }

    def __init__(self, csv_path: str) -> None:
        """Load any existing accounts from disk.

        Args:
            csv_path: Absolute path to the accounts CSV file.
        """
        self._csv_path: str = csv_path
        self._accounts: List[Account] = []
        self.load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Replace the in-memory account list with what's on disk.

        Malformed rows are skipped rather than aborting the full load so
        a single bad record does not lock users out of every account.
        """
        self._accounts.clear()
        if not os.path.exists(self._csv_path):
            return
        try:
            with open(self._csv_path, "r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    account = self._row_to_account(row)
                    if account is not None:
                        self._accounts.append(account)
        except OSError:
            self._accounts.clear()

    def _row_to_account(self, row: Dict[str, str]) -> Optional[Account]:
        """Rebuild one Account from a CSV row, or return None on failure.

        Args:
            row: Mapping of CSV header to value.

        Returns:
            The rebuilt Account or None if the row is unusable.
        """
        account_type = row.get("account_type") or Account.ACCOUNT_TYPE
        cls = self._TYPE_MAP.get(account_type)
        if cls is None:
            return None
        try:
            return cls.from_dict(row)
        except ValueError:
            return None

    def save(self) -> None:
        """Write every account back to the CSV.

        Raises:
            OSError: If the file cannot be written. Callers should catch
                this at the controller layer.
        """
        directory = os.path.dirname(self._csv_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self._csv_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
            for account in self._accounts:
                writer.writerow(account.to_dict())

    # ------------------------------------------------------------------
    # Account collection operations
    # ------------------------------------------------------------------

    def add_account(self, account: Account) -> None:
        """Register a new account.

        Args:
            account: The fully constructed Account (or subclass) to add.

        Raises:
            ValueError: If an account with the same name already exists.
                Names are treated as unique identifiers for this app.
        """
        name = account.get_name().strip()
        if self.find_by_name(name) is not None:
            raise ValueError(
                f"An account named {name!r} already exists."
            )
        self._accounts.append(account)
        self.save()

    def remove_account(self, name: str) -> None:
        """Remove an account by name.

        Args:
            name: The name of the account to remove.

        Raises:
            KeyError: If no account by that name exists.
        """
        target = self.find_by_name(name)
        if target is None:
            raise KeyError(f"No account named {name!r}.")
        self._accounts.remove(target)
        self.save()

    def find_by_name(self, name: str) -> Optional[Account]:
        """Return the account with the given name, or None."""
        name = (name or "").strip()
        for account in self._accounts:
            if account.get_name() == name:
                return account
        return None

    def list_accounts(self) -> List[Account]:
        """Return every account in insertion order."""
        return list(self._accounts)

    def count(self) -> int:
        """Return the number of accounts held by the bank."""
        return len(self._accounts)

    def total(self, accounts: Optional[Iterable[Account]] = None) -> float:
        """Return the sum of balances, matching Lab 9's get_bank_total().

        Args:
            accounts: Optional iterable of accounts to sum. When omitted,
                every account the bank owns is summed.

        Returns:
            The total dollar balance as a float.
        """
        if accounts is None:
            accounts = self._accounts
        total = 0.0
        for account in accounts:
            total += account.get_balance()
        return total
