from pathlib import Path

from atbclone.core import (
    DEFAULT_APPS_DIR,
    DEFAULT_ATB_DIR,
    DEFAULT_DATA_DIR,
    DEFAULT_RECIPES_DIR,
    DEFAULT_STATE_FILE,
)
from atbclone.core import CloneRecord as CoreCloneRecord
from atbclone.core import STATE_FILE as CORE_STATE_FILE
from atbclone.core import StateManager as CoreStateManager
from atbclone.core.config import (
    DEFAULT_APPS_DIR as CONFIG_APPS_DIR,
)
from atbclone.core.config import (
    DEFAULT_ATB_DIR as CONFIG_ATB_DIR,
)
from atbclone.core.config import (
    DEFAULT_DATA_DIR as CONFIG_DATA_DIR,
)
from atbclone.core.config import (
    DEFAULT_RECIPES_DIR as CONFIG_RECIPES_DIR,
)
from atbclone.core.config import (
    DEFAULT_STATE_FILE as CONFIG_STATE_FILE,
)
from atbclone.core.state import STATE_FILE, CloneRecord, StateManager


def test_state_file_default():
    assert DEFAULT_ATB_DIR == Path.home() / "ATBClone"
    assert DEFAULT_STATE_FILE == Path.home() / "ATBClone" / "clones.yaml"
    assert DEFAULT_DATA_DIR == Path.home() / "ATBClone" / "Data"
    assert DEFAULT_RECIPES_DIR == Path.home() / "ATBClone" / "recipes"
    assert DEFAULT_APPS_DIR == Path.home() / "ATBClone" / "Apps"
    assert CONFIG_ATB_DIR == DEFAULT_ATB_DIR
    assert CONFIG_STATE_FILE == DEFAULT_STATE_FILE
    assert CONFIG_DATA_DIR == DEFAULT_DATA_DIR
    assert CONFIG_RECIPES_DIR == DEFAULT_RECIPES_DIR
    assert CONFIG_APPS_DIR == DEFAULT_APPS_DIR

    assert STATE_FILE == DEFAULT_STATE_FILE
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
        data_dir=str(tmp_path / ".atbclone" / "Data" / "微信2"),
        created_at="2026-08-18T14:00:00+00:00",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:1080",
        new_bundle_id="com.tencent.xinWeChat.atb2",
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
    assert loaded_rec.data_dir == str(tmp_path / ".atbclone" / "Data" / "微信2")
    assert loaded_rec.created_at == "2026-08-18T14:00:00+00:00"
    assert loaded_rec.proxy_enabled is True
    assert loaded_rec.proxy_summary == "http://127.0.0.1:1080"
    assert loaded_rec.new_bundle_id == "com.tencent.xinWeChat.atb2"


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
        data_dir=str(tmp_path / ".atbclone" / "Data" / "QQ2"),
        created_at="2026-08-18T14:00:00+00:00",
    )
    assert rec.proxy_enabled is False
    assert rec.proxy_summary == ""
    assert rec.new_bundle_id == ""

    mgr.add(rec)
    loaded = mgr.load()
    assert len(loaded) == 1
    assert loaded[0].proxy_enabled is False
    assert loaded[0].proxy_summary == ""
    assert loaded[0].new_bundle_id == ""


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
        data_dir=str(tmp_path / ".atbclone" / "Data" / "微信2"),
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
        data_dir=str(tmp_path / ".atbclone" / "Data" / "微信2"),
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


def test_clone_record_language_support_and_backward_compatibility(tmp_path):
    state_file = tmp_path / "clones.yaml"
    mgr = StateManager(state_file)

    # 1. Default language should be "system"
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
    assert rec.language == "system"

    # 2. Custom language should be saved and loaded
    rec_custom = CloneRecord(
        clone_name="WeChat_EN",
        source_app="微信",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(tmp_path / "WeChat_EN.app"),
        data_dir=str(tmp_path / "Data" / "WeChat_EN"),
        created_at="2026-08-18T14:00:00+00:00",
        language="en",
    )
    mgr.save([rec, rec_custom])
    loaded = mgr.load()
    assert len(loaded) == 2
    assert loaded[0].language == "system"
    assert loaded[1].language == "en"

    # 3. Backward compatibility with old YAML without language field
    old_yaml_content = """
- clone_name: OldClone
  source_app: App
  source_path: /Applications/App.app
  bundle_id: com.app.old
  strategy: soft_clone
  dest_path: /Applications/OldClone.app
  data_dir: /Data/OldClone
  created_at: 2026-08-01T00:00:00+00:00
"""
    state_file.write_text(old_yaml_content, encoding="utf-8")
    loaded_old = mgr.load()
    assert len(loaded_old) == 1
    assert loaded_old[0].clone_name == "OldClone"
    assert loaded_old[0].language == "system"

