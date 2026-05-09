"""Tests for HotkeyManager. The `keyboard` module is mocked in conftest.py
so these tests run on platforms where the real library isn't usable."""

import sys

import pytest

from utils.hotkeys import HotkeyManager

_keyboard_mock = sys.modules["keyboard"]


@pytest.fixture(autouse=True)
def reset_keyboard_mock():
    _keyboard_mock.reset_mock()
    yield


@pytest.fixture
def manager():
    return HotkeyManager()


class TestRegister:
    def test_register_calls_keyboard_add_hotkey(self, manager):
        assert manager.register_hotkey("toggle", "ctrl+shift+v") is True
        _keyboard_mock.add_hotkey.assert_called_once()
        args, _ = _keyboard_mock.add_hotkey.call_args
        assert args[0] == "ctrl+shift+v"

    def test_register_stores_metadata(self, manager):
        cb = lambda: None
        manager.register_hotkey("toggle", "ctrl+shift+v", callback=cb)
        entry = manager.registered_hotkeys["toggle"]
        assert entry["key_combination"] == "ctrl+shift+v"
        assert entry["callback"] is cb

    def test_register_replaces_existing(self, manager):
        manager.register_hotkey("toggle", "ctrl+shift+v")
        manager.register_hotkey("toggle", "ctrl+alt+c")
        _keyboard_mock.remove_hotkey.assert_called_with("ctrl+shift+v")
        assert manager.registered_hotkeys["toggle"]["key_combination"] == "ctrl+alt+c"

    def test_register_failure_returns_false(self, manager, monkeypatch):
        def boom(*a, **kw):
            raise RuntimeError("nope")
        monkeypatch.setattr(_keyboard_mock, "add_hotkey", boom)
        assert manager.register_hotkey("toggle", "ctrl+x") is False


class TestUnregister:
    def test_unregister_removes(self, manager):
        manager.register_hotkey("toggle", "ctrl+shift+v")
        assert manager.unregister_hotkey("toggle") is True
        assert "toggle" not in manager.registered_hotkeys
        _keyboard_mock.remove_hotkey.assert_called_with("ctrl+shift+v")

    def test_unregister_unknown_returns_false(self, manager):
        assert manager.unregister_hotkey("nope") is False

    def test_unregister_all(self, manager):
        manager.register_hotkey("a", "ctrl+a")
        manager.register_hotkey("b", "ctrl+b")
        assert manager.unregister_all_hotkeys() is True
        assert manager.registered_hotkeys == {}


class TestUpdate:
    def test_update_changes_combination(self, manager):
        manager.register_hotkey("toggle", "ctrl+shift+v")
        assert manager.update_hotkey("toggle", "ctrl+alt+c") is True
        assert manager.registered_hotkeys["toggle"]["key_combination"] == "ctrl+alt+c"

    def test_update_unknown_returns_false(self, manager):
        assert manager.update_hotkey("nope", "ctrl+x") is False

    def test_update_preserves_callback(self, manager):
        cb = lambda: None
        manager.register_hotkey("toggle", "ctrl+shift+v", callback=cb)
        manager.update_hotkey("toggle", "ctrl+alt+c")
        assert manager.registered_hotkeys["toggle"]["callback"] is cb


class TestTrigger:
    def test_callback_invoked(self, manager):
        triggered = []
        manager.register_hotkey("toggle", "ctrl+shift+v", callback=lambda: triggered.append(True))
        manager._on_hotkey_triggered("toggle")
        assert triggered == [True]

    def test_signal_emitted(self, manager):
        received = []
        manager.hotkey_triggered.connect(received.append)
        manager.register_hotkey("toggle", "ctrl+shift+v")
        manager._on_hotkey_triggered("toggle")
        assert received == ["toggle"]

    def test_trigger_without_callback(self, manager):
        manager.register_hotkey("toggle", "ctrl+shift+v")
        # Should not raise even though no callback was provided
        manager._on_hotkey_triggered("toggle")
