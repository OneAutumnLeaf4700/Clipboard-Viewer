from unittest.mock import MagicMock, patch

from utils.clipboard_utils import get_clipboard_data


def _mock_app(*, has_urls=False, urls=None, has_image=False, has_text=False, text_value=""):
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


def test_text_returns_text_tuple():
    app = _mock_app(has_text=True, text_value="hello")
    with patch("utils.clipboard_utils.QApplication.instance", return_value=app):
        dtype, content = get_clipboard_data()
    assert dtype == "text"
    assert content == "hello"


def test_files_returns_local_paths():
    url = MagicMock()
    url.isLocalFile.return_value = True
    url.toLocalFile.return_value = "/path/x"
    app = _mock_app(has_urls=True, urls=[url])
    with patch("utils.clipboard_utils.QApplication.instance", return_value=app):
        dtype, content = get_clipboard_data()
    assert dtype == "files"
    assert content == ["/path/x"]


def test_files_skipped_when_not_local():
    url = MagicMock()
    url.isLocalFile.return_value = False
    app = _mock_app(has_urls=True, urls=[url])
    with patch("utils.clipboard_utils.QApplication.instance", return_value=app):
        dtype, content = get_clipboard_data()
    assert dtype == "unknown"
    assert content is None


def test_unknown_when_no_supported_type():
    app = _mock_app()
    with patch("utils.clipboard_utils.QApplication.instance", return_value=app):
        dtype, content = get_clipboard_data()
    assert dtype == "unknown"
    assert content is None


def test_no_app_returns_error():
    with patch("utils.clipboard_utils.QApplication.instance", return_value=None):
        dtype, _ = get_clipboard_data()
    assert dtype == "error"
