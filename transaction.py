"""Transaction record kept alongside account state.

Lab 9 did not have a transaction log — Project 1 adds one so the GUI
can show history and so any balance can be reconstructed.
"""

import csv


class Transaction:
    """A single deposit, withdrawal, or account-opening event."""

    def __init__(
        self,
        sequence: int,
        account_name: str,
        kind: str,
        amount: float,
        balance_after: float,
        detail: str = "",
    ) -> None:
        """Create a transaction record.

        Args:
            sequence: Auto-incrementing event number; the first transaction
                stored is 1, the second is 2, and so on.
            account_name: Name of the account involved.
            kind: One of OPEN, DEPOSIT, WITHDRAW, INTEREST, or CLOSE.
            amount: Dollar amount of the transaction.
            balance_after: Balance immediately after the transaction.
            detail: Optional free-text describing the event.
        """
        self.sequence = sequence
        self.account_name = account_name
        self.kind = kind
        self.amount = amount
        self.balance_after = balance_after
        self.detail = detail

    def to_dict(self) -> dict:
        """Serialize the transaction for CSV storage.

        Returns:
            A dictionary of strings keyed by CSV column name.
        """
        return {
            "sequence": str(self.sequence),
            "account_name": self.account_name,
            "kind": self.kind,
            "amount": f"{self.amount:.2f}",
            "balance_after": f"{self.balance_after:.2f}",
            "detail": self.detail,
        }


class TransactionLog:
    """CSV-backed append-only log of every Transaction."""

    CSV_FIELDS = [
        "sequence",
        "account_name",
        "kind",
        "amount",
        "balance_after",
        "detail",
    ]
    MAX_ROWS = 2000  # Keep the log bounded.

    def __init__(self, csv_path: str) -> None:
        """Load any existing log entries into memory.

        Args:
            csv_path: Path to the transactions CSV file (created on first save).
        """
        self._csv_path = csv_path
        self._rows = []
        self._next_sequence = 1
        self._load()

    def _load(self) -> None:
        """Read every existing row, skipping malformed entries."""
        try:
            handle = open(self._csv_path, "r", newline="", encoding="utf-8")
        except FileNotFoundError:
            return
        except OSError:
            self._rows = []
            return
        try:
            reader = csv.DictReader(handle)
            for row in reader:
                try:
                    self._rows.append(
                        Transaction(
                            sequence=int(row["sequence"]),
                            account_name=row["account_name"],
                            kind=row["kind"],
                            amount=float(row["amount"]),
                            balance_after=float(row["balance_after"]),
                            detail=row.get("detail", ""),
                        )
                    )
                except (KeyError, ValueError):
                    # Skip a corrupt row so the rest of the log loads.
                    continue
        finally:
            handle.close()
        # Resume numbering after the highest sequence already on disk.
        if self._rows:
            self._next_sequence = self._rows[-1].sequence + 1

    def _write(self) -> None:
        """Rewrite the full log to disk."""
        with open(self._csv_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
            for row in self._rows:
                writer.writerow(row.to_dict())

    def record(
        self,
        account_name: str,
        kind: str,
        amount: float,
        balance_after: float,
        detail: str = "",
    ) -> Transaction:
        """Append a transaction and persist the log.

        Args:
            account_name: Name on the affected account.
            kind: Event type, e.g. ``DEPOSIT``.
            amount: Dollar amount involved.
            balance_after: Balance immediately after the event.
            detail: Optional free-text detail.

        Returns:
            The stored Transaction instance.
        """
        txn = Transaction(
            sequence=self._next_sequence,
            account_name=account_name,
            kind=kind,
            amount=float(amount),
            balance_after=float(balance_after),
            detail=detail,
        )
        self._next_sequence += 1
        self._rows.append(txn)
        if len(self._rows) > self.MAX_ROWS:
            self._rows = self._rows[-self.MAX_ROWS:]
        try:
            self._write()
        except OSError:
            # Logging must not crash the UI; we keep the entry in memory.
            pass
        return txn

    def for_account(self, account_name: str) -> list:
        """Return every transaction for the named account, newest first.

        Args:
            account_name: The account to filter by.

        Returns:
            List of Transaction objects, newest first.
        """
        matches = []
        for row in self._rows:
            if row.account_name == account_name:
                matches.append(row)
        matches.reverse()
        return matches

    def all_recent(self, limit: int = 200) -> list:
        """Return the newest transactions across every account.

        Args:
            limit: Maximum rows to return.

        Returns:
            Newest-first list capped at ``limit`` entries.
        """
        if limit <= 0:
            return []
        recent = self._rows[-limit:]
        recent = list(recent)
        recent.reverse()
        return recent

    def clear(self) -> None:
        """Erase every logged transaction."""
        self._rows = []
        try:
            self._write()
        except OSError:
            pass
