"""Tests for ATBClone CLI entrypoint."""

from click.testing import CliRunner

from atbclone.cli.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ATBClone" in result.output
    assert "clone" in result.output
    assert "doctor" in result.output
    assert "list" in result.output
    assert "recipe" in result.output
    assert "remove" in result.output
    assert "update" in result.output
    assert "wizard" in result.output

