"""Transaction record kept alongside account state.

Lab 9 did not have a transaction log — Project 1 adds one so the GUI
can show history and so auditors can reconstruct any balance.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class Transaction:
    """A single deposit, withdrawal, or account-opening event.

    Attributes:
        timestamp: ISO-8601 local time when the transaction occurred.
        account_name: Name of the account involved.
        kind: One of ``OPEN``, ``DEPOSIT``, ``WITHDRAW``, ``INTEREST``,
            or ``CLOSE``.
        amount: Dollar amount of the transaction.
        balance_after: Balance immediately after the transaction.
        detail: Optional free-text describing the event.
    """

    timestamp: str
    account_name: str
    kind: str
    amount: float
    balance_after: float
    detail: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Serialize the transaction for CSV storage."""
        return {
            "timestamp": self.timestamp,
            "account_name": self.account_name,
            "kind": self.kind,
            "amount": f"{self.amount:.2f}",
            "balance_after": f"{self.balance_after:.2f}",
            "detail": self.detail,
        }


class TransactionLog:
    """CSV-backed append-only log of every Transaction."""

    CSV_FIELDS: List[str] = [
        "timestamp",
        "account_name",
        "kind",
        "amount",
        "balance_after",
        "detail",
    ]
    MAX_ROWS: int = 2000  # Keep the log bounded.

    def __init__(self, csv_path: str) -> None:
        """Load any existing log entries into memory.

        Args:
            csv_path: Absolute path to the transactions CSV file.
        """
        self._csv_path: str = csv_path
        self._rows: List[Transaction] = []
        self._load()

    def _load(self) -> None:
        """Read every existing row, skipping malformed entries."""
        if not os.path.exists(self._csv_path):
            return
        try:
            with open(self._csv_path, "r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    try:
                        self._rows.append(
                            Transaction(
                                timestamp=row["timestamp"],
                                account_name=row["account_name"],
                                kind=row["kind"],
                                amount=float(row["amount"]),
                                balance_after=float(row["balance_after"]),
                                detail=row.get("detail", ""),
                            )
                        )
                    except (KeyError, ValueError):
                        continue
        except OSError:
            self._rows = []

    def _save(self) -> None:
        """Rewrite the full log to disk."""
        directory = os.path.dirname(self._csv_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
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
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            account_name=account_name,
            kind=kind,
            amount=float(amount),
            balance_after=float(balance_after),
            detail=detail,
        )
        self._rows.append(txn)
        if len(self._rows) > self.MAX_ROWS:
            self._rows = self._rows[-self.MAX_ROWS :]
        try:
            self._save()
        except OSError:
            # Logging must not crash the UI; we keep the entry in memory.
            pass
        return txn

    def for_account(self, account_name: str) -> List[Transaction]:
        """Return every transaction for the named account, newest first."""
        return list(
            reversed([r for r in self._rows if r.account_name == account_name])
        )

    def all_recent(self, limit: int = 200) -> List[Transaction]:
        """Return the newest transactions across every account.

        Args:
            limit: Maximum rows to return.

        Returns:
            Newest-first list capped at ``limit`` entries.
        """
        if limit <= 0:
            return []
        return list(reversed(self._rows[-limit:]))

    def clear(self) -> None:
        """Erase every logged transaction."""
        self._rows.clear()
        try:
            self._save()
        except OSError:
            pass
