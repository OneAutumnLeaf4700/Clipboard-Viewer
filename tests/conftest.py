"""Shared pytest fixtures and platform shims.

Mocks the `keyboard` module at import time so tests run on Linux/macOS where
the real library requires root access for global hooks. Also provides a
session-wide QCoreApplication for Qt signal emission and a temp DB path
fixture for isolated database tests.
"""

import sys
from unittest.mock import MagicMock

if "keyboard" not in sys.modules:
    sys.modules["keyboard"] = MagicMock()

import pytest


@pytest.fixture(scope="session", autouse=True)
def _qcore_app():
    from PyQt6.QtCore import QCoreApplication
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv or [""])
    return app


@pytest.fixture
def temp_db_path(tmp_path):
    return str(tmp_path / "data" / "test_history.db")
