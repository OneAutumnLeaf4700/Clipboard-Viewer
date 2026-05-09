import json
from datetime import datetime, timedelta

import pytest

from clipboard_monitor import ClipboardItem
from history_manager import HistoryManager


@pytest.fixture
def history(temp_db_path):
    h = HistoryManager(db_path=temp_db_path)
    # Disable age-based auto cleanup by default so tests can use arbitrary
    # historical timestamps without items being silently retention-trimmed.
    # Tests that exercise cleanup opt in via set_auto_cleanup_days().
    h.auto_cleanup_days = 0
    return h


def make_item(content="hello", data_type="text", timestamp=None, favorite=False):
    item = ClipboardItem(data_type, content, timestamp)
    item.favorite = favorite
    return item


class TestAddAndRetrieve:
    def test_add_text_item(self, history):
        history.add_item(make_item("hello"))
        items = history.get_all_items()
        assert len(items) == 1
        assert items[0].content == "hello"
        assert items[0].data_type == "text"

    def test_get_all_items_orders_newest_first(self, history):
        history.add_item(make_item("old", timestamp=datetime(2026, 1, 1)))
        history.add_item(make_item("new", timestamp=datetime(2026, 6, 1)))
        items = history.get_all_items()
        assert items[0].content == "new"
        assert items[1].content == "old"

    def test_files_item_roundtrips_list(self, history):
        history.add_item(make_item(content=["/path/a", "/path/b"], data_type="files"))
        items = history.get_all_items()
        assert items[0].data_type == "files"
        assert items[0].content == ["/path/a", "/path/b"]

    def test_get_items_by_type(self, history):
        history.add_item(make_item("a", data_type="text"))
        history.add_item(make_item(["/p"], data_type="files"))
        text = history.get_items_by_type("text")
        files = history.get_items_by_type("files")
        assert len(text) == 1 and text[0].data_type == "text"
        assert len(files) == 1 and files[0].data_type == "files"


class TestFavorites:
    def test_toggle_marks_favorite(self, history):
        history.add_item(make_item("a"))
        item_id = history.get_all_items()[0].id
        assert history.toggle_favorite(item_id) is True

    def test_toggle_twice_returns_to_original(self, history):
        history.add_item(make_item("a"))
        item_id = history.get_all_items()[0].id
        history.toggle_favorite(item_id)
        assert history.toggle_favorite(item_id) is False

    def test_get_favorites_returns_only_favorites(self, history):
        history.add_item(make_item("a"))
        history.add_item(make_item("b"))
        items = history.get_all_items()
        history.toggle_favorite(items[0].id)
        favs = history.get_favorites()
        assert len(favs) == 1

    def test_toggle_unknown_returns_none(self, history):
        assert history.toggle_favorite(9999) is None


class TestDeleteAndClear:
    def test_delete_item(self, history):
        history.add_item(make_item("a"))
        item_id = history.get_all_items()[0].id
        assert history.delete_item(item_id) is True
        assert history.get_all_items() == []

    def test_clear_history_keeps_favorites_by_default(self, history):
        history.add_item(make_item("plain"))
        history.add_item(make_item("fav"))
        items = history.get_all_items()
        history.toggle_favorite(items[0].id)
        history.clear_history()
        remaining = history.get_all_items()
        assert len(remaining) == 1
        assert remaining[0].content == "fav"

    def test_clear_history_all(self, history):
        history.add_item(make_item("a"))
        history.add_item(make_item("b"))
        history.clear_history(keep_favorites=False)
        assert history.get_all_items() == []


class TestCleanup:
    def test_max_items_trims_oldest(self, history):
        history.set_max_history_items(3)
        for i in range(5):
            history.add_item(
                make_item(
                    f"item-{i}",
                    timestamp=datetime(2026, 1, 1) + timedelta(minutes=i),
                )
            )
        contents = [i.content for i in history.get_all_items()]
        assert len(contents) == 3
        assert "item-0" not in contents
        assert "item-1" not in contents

    def test_max_items_does_not_trim_favorites(self, history):
        history.set_max_history_items(2)
        history.add_item(make_item("fav", timestamp=datetime(2026, 1, 1)))
        items = history.get_all_items()
        history.toggle_favorite(items[0].id)
        for i in range(5):
            history.add_item(
                make_item(
                    f"plain-{i}",
                    timestamp=datetime(2026, 1, 2) + timedelta(minutes=i),
                )
            )
        favs = history.get_favorites()
        assert any(item.content == "fav" for item in favs)

    def test_age_cleanup_removes_old(self, history):
        history.set_auto_cleanup_days(1)
        history.add_item(make_item("old", timestamp=datetime.now() - timedelta(days=5)))
        history.add_item(make_item("new"))
        contents = [i.content for i in history.get_all_items()]
        assert "old" not in contents
        assert "new" in contents


class TestSearch:
    def test_search_text(self, history):
        history.add_item(make_item("apple pie"))
        history.add_item(make_item("banana split"))
        results = history.search_items("apple")
        assert len(results) == 1
        assert results[0].content == "apple pie"

    def test_search_case_insensitive(self, history):
        history.add_item(make_item("Apple Pie"))
        results = history.search_items("apple")
        assert len(results) == 1

    def test_search_with_data_type_filter(self, history):
        history.add_item(make_item("apple", data_type="text"))
        history.add_item(make_item(["/apple/pie"], data_type="files"))
        results = history.search_items("apple", data_type_filter="text")
        assert len(results) == 1
        assert results[0].data_type == "text"

    def test_search_in_file_paths(self, history):
        history.add_item(make_item(["/photos/apple.png"], data_type="files"))
        history.add_item(make_item(["/photos/banana.png"], data_type="files"))
        results = history.search_items("apple")
        assert len(results) == 1


class TestExport:
    def test_export_json(self, history, tmp_path):
        history.add_item(make_item("hello"))
        history.add_item(make_item(["/a", "/b"], data_type="files"))
        out = tmp_path / "export.json"
        assert history.export_history(str(out), format_type="json") is True
        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data) == 2
        contents = [d["content"] for d in data]
        assert "hello" in contents
        assert ["/a", "/b"] in contents

    def test_export_csv(self, history, tmp_path):
        history.add_item(make_item("hello"))
        out = tmp_path / "export.csv"
        assert history.export_history(str(out), format_type="csv") is True
        text = out.read_text(encoding="utf-8")
        assert "hello" in text
        assert "Timestamp" in text

    def test_export_image_content_replaced_with_placeholder(self, history, tmp_path):
        history.add_item(make_item(b"binary-image-bytes", data_type="image"))
        out = tmp_path / "export.json"
        history.export_history(str(out), format_type="json")
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data[0]["content"] == "[image data]"
