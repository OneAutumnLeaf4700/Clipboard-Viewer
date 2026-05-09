from datetime import datetime
from unittest.mock import MagicMock, patch

from clipboard_monitor import ClipboardItem, ClipboardMonitor


class TestClipboardItem:
    def test_default_timestamp_is_now(self):
        before = datetime.now()
        item = ClipboardItem("text", "hi")
        after = datetime.now()
        assert before <= item.timestamp <= after
        assert item.data_type == "text"
        assert item.content == "hi"
        assert item.favorite is False

    def test_explicit_timestamp_preserved(self):
        ts = datetime(2026, 1, 1, 12, 0)
        item = ClipboardItem("text", "x", timestamp=ts)
        assert item.timestamp == ts


def _mock_app_with_clipboard(*, has_urls=False, urls=None, has_image=False, has_text=False, text_value=""):
    mime = MagicMock()
    mime.hasUrls.return_value = has_urls
    mime.urls.return_value = urls or []
    mime.hasImage.return_value = has_image
    mime.hasText.return_value = has_text
    mime.text.return_value = text_value

    clipboard = MagicMock()
    clipboard.mimeData.return_value = mime
    app = MagicMock()
    app.clipboard.return_value = clipboard
    return app


class TestMonitoringOptions:
    def test_set_monitoring_options(self):
        mon = ClipboardMonitor()
        mon.set_monitoring_options(monitor_text=False, monitor_images=True, monitor_files=False)
        assert mon.monitor_text is False
        assert mon.monitor_images is True
        assert mon.monitor_files is False


class TestGetClipboardData:
    def test_text(self):
        mon = ClipboardMonitor()
        app = _mock_app_with_clipboard(has_text=True, text_value="hello")
        with patch("clipboard_monitor.QApplication.instance", return_value=app):
            dtype, content = mon.get_clipboard_data()
        assert dtype == "text"
        assert content == "hello"

    def test_files(self):
        mon = ClipboardMonitor()
        url = MagicMock()
        url.isLocalFile.return_value = True
        url.toLocalFile.return_value = "/tmp/x"
        app = _mock_app_with_clipboard(has_urls=True, urls=[url])
        with patch("clipboard_monitor.QApplication.instance", return_value=app):
            dtype, content = mon.get_clipboard_data()
        assert dtype == "files"
        assert content == ["/tmp/x"]

    def test_unknown(self):
        mon = ClipboardMonitor()
        app = _mock_app_with_clipboard()
        with patch("clipboard_monitor.QApplication.instance", return_value=app):
            dtype, content = mon.get_clipboard_data()
        assert dtype == "unknown"
        assert content is None

    def test_no_app_returns_error(self):
        mon = ClipboardMonitor()
        with patch("clipboard_monitor.QApplication.instance", return_value=None):
            dtype, _ = mon.get_clipboard_data()
        assert dtype == "error"

    def test_text_skipped_when_disabled(self):
        mon = ClipboardMonitor()
        mon.monitor_text = False
        app = _mock_app_with_clipboard(has_text=True, text_value="hello")
        with patch("clipboard_monitor.QApplication.instance", return_value=app):
            dtype, _ = mon.get_clipboard_data()
        assert dtype == "unknown"

    def test_files_skipped_when_disabled(self):
        mon = ClipboardMonitor()
        mon.monitor_files = False
        url = MagicMock()
        url.isLocalFile.return_value = True
        url.toLocalFile.return_value = "/tmp/x"
        app = _mock_app_with_clipboard(has_urls=True, urls=[url])
        with patch("clipboard_monitor.QApplication.instance", return_value=app):
            dtype, _ = mon.get_clipboard_data()
        # When files are disabled, falls through to text/unknown
        assert dtype == "unknown"


class TestCheckClipboard:
    def test_emits_on_new_text(self):
        mon = ClipboardMonitor()
        received = []
        mon.new_content.connect(received.append)
        with patch.object(mon, "get_clipboard_data", return_value=("text", "hello")):
            mon.check_clipboard()
        assert len(received) == 1
        assert received[0].data_type == "text"
        assert received[0].content == "hello"

    def test_no_emit_on_unchanged_content(self):
        mon = ClipboardMonitor()
        mon.last_clipboard_content = "hello"
        received = []
        mon.new_content.connect(received.append)
        with patch.object(mon, "get_clipboard_data", return_value=("text", "hello")):
            mon.check_clipboard()
        assert received == []

    def test_no_emit_on_none_content(self):
        mon = ClipboardMonitor()
        received = []
        mon.new_content.connect(received.append)
        with patch.object(mon, "get_clipboard_data", return_value=("unknown", None)):
            mon.check_clipboard()
        assert received == []

    def test_no_emit_when_type_disabled(self):
        mon = ClipboardMonitor()
        mon.monitor_text = False
        received = []
        mon.new_content.connect(received.append)
        with patch.object(mon, "get_clipboard_data", return_value=("text", "hello")):
            mon.check_clipboard()
        assert received == []


class TestStartStopMonitoring:
    def test_start_calls_timer_with_interval(self):
        mon = ClipboardMonitor()
        with patch.object(mon.timer, "start") as mock_start:
            mon.start_monitoring(interval=500)
            mock_start.assert_called_once_with(500)

    def test_stop_calls_timer_stop(self):
        mon = ClipboardMonitor()
        with patch.object(mon.timer, "stop") as mock_stop:
            mon.stop_monitoring()
            mock_stop.assert_called_once()
