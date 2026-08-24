"""Unit tests for BinaryArgumentProber."""

from pathlib import Path
import pytest

from atbclone.core.argument_prober import BinaryArgumentProber, ArgumentProbeResult


def test_extract_binary_strings(tmp_path: Path):
    dummy_bin = tmp_path / "dummy_bin"
    dummy_bin.write_bytes(b"\x00\x01\x02--user-data-dir\x00some_other_string\x00\xff")
    strings = BinaryArgumentProber.extract_binary_strings(dummy_bin)
    assert "--user-data-dir" in strings
    assert "some_other_string" in strings


def test_probe_data_dir_argument_user_data_dir(tmp_path: Path):
    dummy_bin = tmp_path / "app_chromium"
    dummy_bin.write_bytes(b"MachO_HEADER\x00--user-data-dir\x00--lang\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag == "--user-data-dir"
    assert res.template == "--user-data-dir={{ATB_DATA_DIR}}"


def test_probe_data_dir_argument_data_dir(tmp_path: Path):
    dummy_bin = tmp_path / "app_custom"
    dummy_bin.write_bytes(b"MachO_HEADER\x00--data-dir=\x00--other\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag == "--data-dir"
    assert res.template == "--data-dir={{ATB_DATA_DIR}}"


def test_probe_data_dir_argument_datadir(tmp_path: Path):
    dummy_bin = tmp_path / "app_custom_datadir"
    dummy_bin.write_bytes(b"MachO_HEADER\x00--datadir=\x00--other\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag == "--datadir"
    assert res.template == "--datadir={{ATB_DATA_DIR}}"


def test_probe_data_dir_argument_config_dir(tmp_path: Path):
    dummy_bin = tmp_path / "app_custom_config"
    dummy_bin.write_bytes(b"MachO_HEADER\x00--config-dir\x00--other\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag == "--config-dir"
    assert res.template == "--config-dir={{ATB_DATA_DIR}}"


def test_probe_data_dir_argument_profile_space(tmp_path: Path):
    dummy_bin = tmp_path / "app_gecko"
    dummy_bin.write_bytes(b"MachO_HEADER\x00-profile <path>\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag == "-profile"
    assert res.template == "-profile {{ATB_DATA_DIR}}"


def test_probe_data_dir_argument_none(tmp_path: Path):
    dummy_bin = tmp_path / "app_native"
    dummy_bin.write_bytes(b"MachO_HEADER\x00CocoaApp\x00NSWindow\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag is None
    assert res.template is None


def test_probe_nonexistent_binary(tmp_path: Path):
    res = BinaryArgumentProber.probe_data_dir_argument(tmp_path / "nonexistent")
    assert res.flag is None
    assert res.template is None
