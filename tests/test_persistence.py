"""Tests for the persistence module."""

import json

from kerygma_strategy.persistence import JsonStore


class TestJsonStore:
    def test_set_and_get(self):
        store = JsonStore()
        store.set("key", "value")
        assert store.get("key") == "value"

    def test_get_default(self):
        store = JsonStore()
        assert store.get("missing", "default") == "default"

    def test_delete(self):
        store = JsonStore()
        store.set("key", "value")
        store.delete("key")
        assert store.get("key") is None

    def test_keys(self):
        store = JsonStore()
        store.set("a", 1)
        store.set("b", 2)
        assert sorted(store.keys()) == ["a", "b"]

    def test_persistence(self, tmp_path):
        path = tmp_path / "store.json"
        store1 = JsonStore(path)
        store1.set("key", "value")
        store1.save()
        assert path.exists()

        store2 = JsonStore(path)
        assert store2.get("key") == "value"

    def test_from_dict(self):
        store = JsonStore.from_dict({"a": 1, "b": 2})
        assert store.get("a") == 1
        assert store.get("b") == 2

    def test_to_dict(self):
        store = JsonStore()
        store.set("x", 42)
        assert store.to_dict() == {"x": 42}

    def test_is_persistent(self, tmp_path):
        assert JsonStore().is_persistent is False
        assert JsonStore(tmp_path / "test.json").is_persistent is True

    def test_corrupt_file_handled(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("not json at all")
        store = JsonStore(path)
        assert store.to_dict() == {}

    def test_atomic_write(self, tmp_path):
        path = tmp_path / "atomic.json"
        store = JsonStore(path)
        store.set("key", "value")
        store.save()
        # No .tmp file should remain
        assert not (path.with_suffix(".tmp")).exists()
        assert json.loads(path.read_text())["key"] == "value"
