"""Compatibility shim preserving the Lab 9 import surface.

The Lab 9 starter ``main.py`` does ``from accounts import *``. Project 1
organizes the classes into proper modules, but keeping this file makes
the original lab tester work without modification so graders can verify
that Lab 9 behavior is intact.
"""

from account import Account
from checking_account import CheckingAccount
from saving_account import SavingAccount

__all__ = ["Account", "SavingAccount", "CheckingAccount"]
