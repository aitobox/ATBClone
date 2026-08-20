"""Tests for ATBClone core config management (YAML format)."""

import json
from pathlib import Path
import yaml
import pytest

from atbclone.core import config
from atbclone.core.config import (
    DEFAULT_CONFIG_FILE,
    load_config,
    save_config,
    get_config_value,
    set_config_value,
)


def test_default_config_file_path():
    assert DEFAULT_CONFIG_FILE.name == "config.yaml"


def test_load_config_nonexistent(tmp_path, monkeypatch):
    test_cfg = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

    assert load_config() == {}


def test_save_and_load_config_yaml(tmp_path, monkeypatch):
    test_cfg = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

    data = {
        "language": "zh",
        "minimize_to_tray": True,
        "custom_settings": {"nested": "value", "count": 42},
    }
    save_config(data)

    assert test_cfg.exists()
    # Check that it's valid YAML
    with open(test_cfg, "r", encoding="utf-8") as f:
        loaded_raw = yaml.safe_load(f)
    assert loaded_raw == data

    # Check via load_config
    assert load_config() == data


def test_legacy_json_fallback(tmp_path, monkeypatch):
    test_cfg_yaml = tmp_path / "config.yaml"
    test_cfg_json = tmp_path / "config.json"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg_yaml)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

    # Write legacy json
    legacy_data = {"language": "ja", "minimize_to_tray": False}
    with open(test_cfg_json, "w", encoding="utf-8") as f:
        json.dump(legacy_data, f)

    # Config yaml doesn't exist yet -> loads legacy json
    assert not test_cfg_yaml.exists()
    assert load_config() == legacy_data

    # Once a new setting is saved, it writes to config.yaml
    set_config_value("minimize_to_tray", True)
    assert test_cfg_yaml.exists()
    assert get_config_value("minimize_to_tray") is True
    assert get_config_value("language") == "ja"


def test_get_and_set_config_value(tmp_path, monkeypatch):
    test_cfg = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

    assert get_config_value("non_existent", default="fallback") == "fallback"

    set_config_value("theme", "dark")
    assert get_config_value("theme") == "dark"

    set_config_value("minimize_to_tray", True)
    assert get_config_value("minimize_to_tray") is True
    assert get_config_value("theme") == "dark"


def test_corrupted_config_handling(tmp_path, monkeypatch):
    test_cfg = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

    with open(test_cfg, "w", encoding="utf-8") as f:
        f.write("invalid: yaml: : : [}")

    assert load_config() == {}
    assert get_config_value("anything", "default") == "default"
