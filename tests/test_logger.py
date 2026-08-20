from pathlib import Path
import tempfile
import logging
import pytest
from atbclone.core.logger import (
    get_logger,
    read_logs,
    clear_logs,
    get_log_file_path,
    add_log_listener,
    remove_log_listener,
    setup_logging,
)


def test_logger_file_writing_and_reading(tmp_path):
    log_file = tmp_path / "test.log"
    setup_logging(log_file=log_file)

    logger = get_logger("test_module")
    logger.info("Hello ATBClone Test")
    logger.error("Something went wrong")

    content = read_logs(log_file=log_file)
    assert "Hello ATBClone Test" in content
    assert "[INFO] [atbclone.test_module]" in content or "[INFO] [test_module]" in content
    assert "Something went wrong" in content
    assert "[ERROR]" in content


def test_clear_logs(tmp_path):
    log_file = tmp_path / "test_clear.log"
    setup_logging(log_file=log_file)
    logger = get_logger("test_clear")
    logger.info("Record 1")
    assert "Record 1" in read_logs(log_file=log_file)

    clear_logs(log_file=log_file)
    content = read_logs(log_file=log_file)
    assert "Record 1" not in content
    assert "Log file cleared by user" in content


def test_broadcast_listener():
    messages = []

    def _listener(msg: str):
        messages.append(msg)

    add_log_listener(_listener)
    try:
        logger = get_logger("broadcast_test")
        logger.info("Live broadcast message")
        assert any("Live broadcast message" in m for m in messages)
    finally:
        remove_log_listener(_listener)
