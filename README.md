# Bank App — Project 1

An improved version of **Lab 9** (Accounts and SavingAccount) rebuilt as
a full **PyQt6** desktop application. The original Lab 9 classes still
work as specified — the same `main.py` test harness produces the same
output — but they're now wrapped in a graphical banking interface with
CSV persistence, transaction history, an added checking-account subclass,
and complete input validation.

## Features

- **PyQt6 GUI** with an account table, action buttons, and dialogs for
  opening accounts and entering deposit/withdrawal amounts.
- **Three account types** showcasing inheritance:
  - `Account` — Lab 9's base class.
  - `SavingAccount` — $100 minimum, 2% interest on every 5th deposit.
  - `CheckingAccount` — $50 overdraft limit, $5 overdraft fee.
- **CSV persistence** — every account and every transaction is written
  to CSV so state survives a restart.
- **Transaction log** — timestamped entries for every open, deposit,
  withdrawal, interest application, and close. Viewable per-account or
  across the whole bank.
- **Input validation** on every field:
  - Names cannot be empty or longer than 40 characters.
  - Amounts must parse to a positive number (leading `$` and commas ok).
  - Duplicate account names are rejected.
- **Exception handling** — all file I/O is wrapped; bad rows are skipped
  rather than crashing the load; a top-level handler in `main.py`
  surfaces any startup exception in a dialog.

## Lab 9 compatibility

The original `main.py` from Lab 9 still runs unchanged. Drop the lab's
test harness next to this project and the Lab 9 expected output is
reproduced exactly. This is what `accounts.py` at the project root is
for — it re-exports the classes from their new modules.

## Project structure

```
bank_app/
├── main.py                         # Project 1 GUI entry point
├── accounts.py                     # Lab 9 compatibility shim
├── requirements.txt
├── models/
│   ├── __init__.py
│   ├── account.py                  # Base Account (Lab 9 improved)
│   ├── saving_account.py           # SavingAccount (Lab 9 improved)
│   ├── checking_account.py         # New subclass for Project 1
│   ├── transaction.py              # Transaction + TransactionLog
│   └── bank.py                     # CSV-backed account collection
├── controllers/
│   ├── __init__.py
│   └── bank_controller.py          # Input validation + ops
├── views/
│   ├── __init__.py
│   ├── main_window.py              # Main QMainWindow
│   ├── open_account_dialog.py      # Open-account form
│   ├── amount_dialog.py            # Deposit / withdraw amount form
│   └── history_dialog.py           # Transaction history viewer
└── data/
    ├── accounts.csv                # Created on first save
    └── transactions.csv            # Created on first transaction
```

## Installation

1. Install Python 3.10 or newer.
2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

## Running

```
python main.py
```

## How the OOP concepts map to the code

| Concept                  | Location                                               |
|--------------------------|--------------------------------------------------------|
| Encapsulation / data hiding | `Account.__account_name`, `Account.__account_balance`, `SavingAccount.__deposit_count`, `CheckingAccount.__overdraft_count` |
| Inheritance              | `SavingAccount(Account)` and `CheckingAccount(Account)`                |
| Method overriding        | `SavingAccount.deposit/withdraw/set_balance/__str__`, `CheckingAccount.withdraw/__str__` |
| Class variables          | `SavingAccount.MINIMUM`, `SavingAccount.RATE`, `CheckingAccount.OVERDRAFT_LIMIT`, `CheckingAccount.OVERDRAFT_FEE` |
| Polymorphism             | `Bank.total()` and `main_window` both iterate a `List[Account]` without branching on type |
| Separation of concerns   | `models/`, `views/`, `controllers/` packages           |
| Docstrings + type hints  | Every function in every module                         |

## Requirement checklist for Project 1

- [x] PyQt6 GUI (no tkinter).
- [x] Code organized into `models/`, `views/`, `controllers/` packages.
- [x] Data stored in CSV (`accounts.csv`, `transactions.csv`).
- [x] Keyboard input validation on every field.
- [x] Exception handling around file I/O and user input.
- [x] OOP best practices — classes, data hiding, inheritance, polymorphism.
- [x] Docstrings for every function.
- [x] Type hints on every function header.
- [x] Descriptive names throughout.
