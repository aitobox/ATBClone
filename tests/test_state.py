from pathlib import Path

from atbclone.core import STATE_FILE as CORE_STATE_FILE
from atbclone.core import CloneRecord as CoreCloneRecord
from atbclone.core import StateManager as CoreStateManager
from atbclone.core.state import STATE_FILE, CloneRecord, StateManager


def test_state_file_default():
    assert STATE_FILE == Path.home() / ".AIToBox" / "clones.yaml"
    assert CORE_STATE_FILE == STATE_FILE
    assert CoreCloneRecord is CloneRecord
    assert CoreStateManager is StateManager


def test_load_empty(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)
    records = mgr.load()
    assert records == []


def test_load_empty_file_content(tmp_path):
    state_file = tmp_path / "clones.yaml"
    state_file.write_text("", encoding="utf-8")
    mgr = StateManager(state_file)
    assert mgr.load() == []


def test_load_corrupted_yaml(tmp_path):
    state_file = tmp_path / "clones.yaml"
    state_file.write_text("::: invalid yaml {{{", encoding="utf-8")
    mgr = StateManager(state_file)
    assert mgr.load() == []


def test_load_non_list_yaml(tmp_path):
    state_file = tmp_path / "clones.yaml"
    state_file.write_text("key: value\nanother: 123", encoding="utf-8")
    mgr = StateManager(state_file)
    assert mgr.load() == []


def test_state_manager_str_path(tmp_path):
    state_file = str(tmp_path / "clones.yaml")
    mgr = StateManager(state_file)
    assert isinstance(mgr.state_file, Path)
    assert mgr.load() == []


def test_add_and_load(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)

    rec = CloneRecord(
        clone_name="微信2",
        source_app="微信",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(tmp_path / "Applications" / "微信2.app"),
        data_dir=str(tmp_path / ".AIToBox" / "Data" / "微信2"),
        created_at="2026-08-18T14:00:00+00:00",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:1080",
    )
    mgr.add(rec)

    loaded = mgr.load()
    assert len(loaded) == 1
    loaded_rec = loaded[0]
    assert loaded_rec.clone_name == "微信2"
    assert loaded_rec.source_app == "微信"
    assert loaded_rec.source_path == "/Applications/WeChat.app"
    assert loaded_rec.bundle_id == "com.tencent.xinWeChat"
    assert loaded_rec.strategy == "hard_clone"
    assert loaded_rec.dest_path == str(tmp_path / "Applications" / "微信2.app")
    assert loaded_rec.data_dir == str(tmp_path / ".AIToBox" / "Data" / "微信2")
    assert loaded_rec.created_at == "2026-08-18T14:00:00+00:00"
    assert loaded_rec.proxy_enabled is True
    assert loaded_rec.proxy_summary == "http://127.0.0.1:1080"


def test_add_defaults(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)

    rec = CloneRecord(
        clone_name="QQ2",
        source_app="QQ",
        source_path="/Applications/QQ.app",
        bundle_id="com.tencent.qq",
        strategy="soft_clone",
        dest_path=str(tmp_path / "Applications" / "QQ2.app"),
        data_dir=str(tmp_path / ".AIToBox" / "Data" / "QQ2"),
        created_at="2026-08-18T14:00:00+00:00",
    )
    assert rec.proxy_enabled is False
    assert rec.proxy_summary == ""

    mgr.add(rec)
    loaded = mgr.load()
    assert len(loaded) == 1
    assert loaded[0].proxy_enabled is False
    assert loaded[0].proxy_summary == ""


def test_add_existing_updates_record(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)

    rec1 = CloneRecord(
        clone_name="微信2",
        source_app="微信",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(tmp_path / "Applications" / "微信2.app"),
        data_dir=str(tmp_path / ".AIToBox" / "Data" / "微信2"),
        created_at="2026-08-18T14:00:00+00:00",
    )
    mgr.add(rec1)

    rec2 = CloneRecord(
        clone_name="微信2",
        source_app="微信",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(tmp_path / "Applications" / "微信2.app"),
        data_dir=str(tmp_path / ".AIToBox" / "Data" / "微信2"),
        created_at="2026-08-18T15:00:00+00:00",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:8080",
    )
    mgr.add(rec2)

    loaded = mgr.load()
    assert len(loaded) == 1
    assert loaded[0].created_at == "2026-08-18T15:00:00+00:00"
    assert loaded[0].proxy_enabled is True
    assert loaded[0].proxy_summary == "http://127.0.0.1:8080"


def test_remove_existing(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)

    rec1 = CloneRecord(
        clone_name="微信2",
        source_app="微信",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(tmp_path / "微信2.app"),
        data_dir=str(tmp_path / "Data" / "微信2"),
        created_at="2026-08-18T14:00:00+00:00",
    )
    rec2 = CloneRecord(
        clone_name="微信3",
        source_app="微信",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(tmp_path / "微信3.app"),
        data_dir=str(tmp_path / "Data" / "微信3"),
        created_at="2026-08-18T14:05:00+00:00",
    )
    mgr.add(rec1)
    mgr.add(rec2)

    assert len(mgr.load()) == 2
    removed = mgr.remove("微信2")
    assert removed is True

    remaining = mgr.load()
    assert len(remaining) == 1
    assert remaining[0].clone_name == "微信3"


def test_remove_nonexistent(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)
    assert mgr.remove("nonexistent") is False


def test_get_existing(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)

    rec = CloneRecord(
        clone_name="微信2",
        source_app="微信",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(tmp_path / "微信2.app"),
        data_dir=str(tmp_path / "Data" / "微信2"),
        created_at="2026-08-18T14:00:00+00:00",
    )
    mgr.add(rec)

    found = mgr.get("微信2")
    assert found is not None
    assert found.clone_name == "微信2"
    assert found.source_app == "微信"


def test_get_nonexistent(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)
    assert mgr.get("nonexistent") is None


def test_save_creates_parent_dirs(tmp_path):
    state_file = tmp_path / "nested" / "sub" / "dir" / "clones.yaml"
    assert not state_file.parent.exists()

    mgr = StateManager(state_file)
    rec = CloneRecord(
        clone_name="微信2",
        source_app="微信",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(tmp_path / "微信2.app"),
        data_dir=str(tmp_path / "Data" / "微信2"),
        created_at="2026-08-18T14:00:00+00:00",
    )
    mgr.save([rec])

    assert state_file.exists()
    assert state_file.parent.exists()
    loaded = mgr.load()
    assert len(loaded) == 1
    assert loaded[0].clone_name == "微信2"
