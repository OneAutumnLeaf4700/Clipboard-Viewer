from datetime import datetime, timedelta

import pytest

from utils.database import DatabaseManager


@pytest.fixture
def db(temp_db_path):
    return DatabaseManager(db_path=temp_db_path)


class TestSchema:
    def test_init_creates_tables_for_inserts(self, db):
        item_id = db.insert_item("text", b"hello")
        assert item_id is not None and item_id > 0

    def test_get_connection_enables_foreign_keys(self, db):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        assert cursor.fetchone()[0] == 1
        conn.close()


class TestItems:
    def test_insert_then_get_by_id(self, db):
        item_id = db.insert_item(
            "text", b"hello", timestamp=datetime(2026, 5, 9, 12, 0)
        )
        row = db.get_item_by_id(item_id)
        assert row is not None
        _, _, dtype, content, fav = row
        assert dtype == "text"
        assert content == b"hello"
        assert fav == 0

    def test_get_items_orders_newest_first(self, db):
        old = datetime(2026, 1, 1)
        new = datetime(2026, 6, 1)
        db.insert_item("text", b"old", timestamp=old)
        db.insert_item("text", b"new", timestamp=new)
        rows = db.get_items()
        assert len(rows) == 2
        assert rows[0][3] == b"new"
        assert rows[1][3] == b"old"

    def test_get_items_filters_by_type(self, db):
        db.insert_item("text", b"hi")
        db.insert_item("image", b"img-bytes")
        text_rows = db.get_items(data_type="text")
        assert len(text_rows) == 1
        assert text_rows[0][2] == "text"

    def test_get_items_favorites_only(self, db):
        db.insert_item("text", b"a")
        b_id = db.insert_item("text", b"b", favorite=True)
        favs = db.get_items(favorites_only=True)
        assert len(favs) == 1
        assert favs[0][0] == b_id

    def test_get_items_respects_limit_and_offset(self, db):
        for i in range(5):
            db.insert_item(
                "text",
                f"item-{i}".encode(),
                timestamp=datetime(2026, 1, i + 1),
            )
        first_two = db.get_items(limit=2)
        assert len(first_two) == 2
        next_two = db.get_items(limit=2, offset=2)
        first_ids = {row[0] for row in first_two}
        next_ids = {row[0] for row in next_two}
        assert first_ids.isdisjoint(next_ids)

    def test_update_item(self, db):
        item_id = db.insert_item("text", b"hello")
        assert db.update_item(item_id, content=b"world", favorite=True) is True
        row = db.get_item_by_id(item_id)
        assert row[3] == b"world"
        assert row[4] == 1

    def test_update_item_with_no_valid_fields_returns_false(self, db):
        item_id = db.insert_item("text", b"hello")
        assert db.update_item(item_id, bogus="x") is False

    def test_delete_item(self, db):
        item_id = db.insert_item("text", b"x")
        assert db.delete_item(item_id) is True
        assert db.get_item_by_id(item_id) is None

    def test_get_item_by_unknown_id_returns_none(self, db):
        assert db.get_item_by_id(99999) is None


class TestClearHistory:
    def test_keep_favorites_default(self, db):
        db.insert_item("text", b"plain")
        fav_id = db.insert_item("text", b"keeper", favorite=True)
        assert db.clear_history() is True
        rows = db.get_items()
        assert len(rows) == 1
        assert rows[0][0] == fav_id

    def test_clear_all(self, db):
        db.insert_item("text", b"a")
        db.insert_item("text", b"b", favorite=True)
        db.clear_history(keep_favorites=False)
        assert db.get_items() == []


class TestSettings:
    def test_default_when_missing(self, db):
        assert db.get_setting("missing") is None
        assert db.get_setting("missing", default="x") == "x"

    def test_set_then_get(self, db):
        db.set_setting("theme", "dark")
        assert db.get_setting("theme") == "dark"

    def test_set_overwrites_existing(self, db):
        db.set_setting("theme", "dark")
        db.set_setting("theme", "light")
        assert db.get_setting("theme") == "light"

    def test_set_coerces_to_string(self, db):
        db.set_setting("count", 42)
        assert db.get_setting("count") == "42"


class TestTags:
    def test_add_returns_id(self, db):
        tid = db.add_tag("work")
        assert tid is not None and tid > 0

    def test_add_duplicate_returns_existing_id(self, db):
        tid1 = db.add_tag("work")
        tid2 = db.add_tag("work")
        assert tid1 == tid2

    def test_tag_and_untag_item(self, db):
        item_id = db.insert_item("text", b"hello")
        tag_id = db.add_tag("important")
        assert db.tag_item(item_id, tag_id) is True
        tags = db.get_item_tags(item_id)
        assert [(t[1]) for t in tags] == ["important"]
        assert db.untag_item(item_id, tag_id) is True
        assert db.get_item_tags(item_id) == []

    def test_get_all_tags_sorted(self, db):
        db.add_tag("zeta")
        db.add_tag("alpha")
        names = [t[1] for t in db.get_all_tags()]
        assert names == ["alpha", "zeta"]

    def test_cascade_delete_removes_item_tag_links(self, db):
        item_id = db.insert_item("text", b"x")
        tag_id = db.add_tag("t")
        db.tag_item(item_id, tag_id)
        db.delete_item(item_id)
        assert db.get_item_tags(item_id) == []


class TestSearch:
    def test_text_search_finds_matches(self, db):
        db.insert_item("text", b"hello world")
        db.insert_item("text", b"goodbye world")
        rows = db.search_items("hello")
        assert len(rows) == 1
        assert rows[0][3] == b"hello world"

    def test_text_search_only_returns_text_items(self, db):
        db.insert_item("image", b"hello-image-bytes")
        db.insert_item("text", b"hello text")
        rows = db.search_items("hello")
        assert len(rows) == 1
        assert rows[0][2] == "text"

    def test_search_with_favorites_filter(self, db):
        db.insert_item("text", b"hello plain")
        db.insert_item("text", b"hello fav", favorite=True)
        rows = db.search_items("hello", favorites_only=True)
        assert len(rows) == 1

    def test_search_with_tag_filter(self, db):
        tagged_id = db.insert_item("text", b"hello tagged")
        db.insert_item("text", b"hello untagged")
        tag_id = db.add_tag("important")
        db.tag_item(tagged_id, tag_id)
        rows = db.search_items("hello", tag_id=tag_id)
        assert len(rows) == 1
        assert rows[0][0] == tagged_id

    def test_search_respects_limit(self, db):
        for i in range(3):
            db.insert_item("text", f"hello-{i}".encode())
        rows = db.search_items("hello", limit=2)
        assert len(rows) == 2
