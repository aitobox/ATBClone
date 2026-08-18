"""Tests for ATBClone CLI entrypoint."""

from click.testing import CliRunner

from atbclone.cli.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ATBClone" in result.output
