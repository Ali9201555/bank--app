"""Controllers for the Bank application.

Sit between the PyQt6 views and the pure-Python models. Validation and
error translation happen here so the GUI only has to pass raw strings
and show resulting messages.
"""

from controllers.bank_controller import BankController

__all__ = ["BankController"]
