"""Views package for the Bank application.

PyQt6 widgets only. The views import controllers, never models, so the
persistence layer can be swapped without touching GUI code.
"""

from views.main_window import MainWindow

__all__ = ["MainWindow"]
