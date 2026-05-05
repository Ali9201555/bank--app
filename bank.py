"""Bank — in-memory collection of accounts with CSV persistence.

The Bank owns the list of Account objects. The original Lab 9
``get_bank_total()`` helper lives here as :meth:`total`.
"""

import csv

from account import Account, make_account_from_dict
from checking_account import CheckingAccount, make_checking_account_from_dict
from saving_account import SavingAccount, make_saving_account_from_dict


class Bank:
    """Holds every account and persists them to a CSV file."""

    CSV_FIELDS = ["account_type", "name", "balance", "extra"]

    def __init__(self, csv_path: str) -> None:
        """Load any existing accounts from disk.

        Args:
            csv_path: Absolute path to the accounts CSV file.
        """
        self._csv_path = csv_path
        self._accounts = []
        self.load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Replace the in-memory account list with what's on disk.

        Malformed rows are skipped rather than aborting the full load so
        a single bad record does not lock users out of every account.
        """
        self._accounts = []
        try:
            handle = open(self._csv_path, "r", newline="", encoding="utf-8")
        except FileNotFoundError:
            # No saved file yet, start with an empty list.
            return
        except OSError:
            self._accounts = []
            return
        try:
            reader = csv.DictReader(handle)
            for row in reader:
                account = self._row_to_account(row)
                if account is not None:
                    self._accounts.append(account)
        finally:
            handle.close()

    def _row_to_account(self, row: dict) -> Account:
        """Rebuild one Account from a CSV row, or return None on failure.

        Args:
            row: Mapping of CSV header to value.

        Returns:
            The rebuilt Account or None if the row is unusable.
        """
        account_type = row.get("account_type") or Account.ACCOUNT_TYPE
        try:
            if account_type == SavingAccount.ACCOUNT_TYPE:
                return make_saving_account_from_dict(row)
            if account_type == CheckingAccount.ACCOUNT_TYPE:
                return make_checking_account_from_dict(row)
            if account_type == Account.ACCOUNT_TYPE:
                return make_account_from_dict(row)
            # Unknown type label — skip the row.
            return None
        except ValueError:
            return None

    def write(self) -> None:
        """Write every account back to the CSV.

        The ``data`` directory is committed to the repository, so the
        write target always exists when the app runs.

        Raises:
            OSError: If the file cannot be written. Callers should catch
                this at the controller layer.
        """
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
            raise ValueError(f"An account named {name!r} already exists.")
        self._accounts.append(account)
        self.write()

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
        self.write()

    def find_by_name(self, name: str) -> Account:
        """Return the account with the given name, or None.

        Args:
            name: The account holder name to look up.

        Returns:
            The matching Account, or None if no account is found.
        """
        clean = (name or "").strip()
        for account in self._accounts:
            if account.get_name() == clean:
                return account
        return None

    def list_accounts(self) -> list:
        """Return every account in insertion order."""
        return list(self._accounts)

    def count(self) -> int:
        """Return the number of accounts held by the bank."""
        return len(self._accounts)

    def total(self, accounts: list = None) -> float:
        """Return the sum of balances, matching Lab 9's get_bank_total().

        Args:
            accounts: Optional iterable of accounts to sum. When None,
                every account the bank owns is summed.

        Returns:
            The total dollar balance as a float.
        """
        if accounts is None:
            accounts = self._accounts
        total_amount = 0.0
        for account in accounts:
            total_amount += account.get_balance()
        return total_amount
