"""Tests for ATBClone CLI entrypoint."""

from click.testing import CliRunner

from atbclone.cli.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ATBClone - macOS application cloning engine." in result.output
    assert "clone" in result.output
    assert "doctor" in result.output
    assert "list" in result.output
    assert "probe" in result.output
    assert "recipe" in result.output
    assert "remove" in result.output
    assert "update" in result.output
    assert "version" in result.output
    assert "wizard" in result.output


def test_cli_subcommands_english_help():
    runner = CliRunner(env={"COLUMNS": "160"})

    # clone
    res = runner.invoke(cli, ["clone", "--help"])
    assert res.exit_code == 0
    assert "Clone a macOS application." in res.output
    assert "Clone application name." in res.output
    assert "Display name shown in Dock/Finder" in res.output
    assert "Path to custom icon file" in res.output
    assert "Target output directory" in res.output

    # doctor
    res = runner.invoke(cli, ["doctor", "--help"])
    assert res.exit_code == 0
    assert "Check environment prerequisites" in res.output

    # list
    res = runner.invoke(cli, ["list", "--help"])
    assert res.exit_code == 0
    assert "List all cloned applications." in res.output

    # probe
    res = runner.invoke(cli, ["probe", "--help"])
    assert res.exit_code == 0
    assert "Probe application architecture, entitlements, and recommended recipe." in res.output
    assert "Save recipe to local recipe repository" in res.output
    assert "Save generated recipe YAML to specified file path." in res.output
    assert "Output probe results in JSON format." in res.output

    # recipe
    res = runner.invoke(cli, ["recipe", "--help"])
    assert res.exit_code == 0
    assert "Manage and inspect application clone recipes." in res.output

    # recipe list
    res = runner.invoke(cli, ["recipe", "list", "--help"])
    assert res.exit_code == 0
    assert "List all built-in recipes." in res.output

    # recipe show
    res = runner.invoke(cli, ["recipe", "show", "--help"])
    assert res.exit_code == 0
    assert "Show recipe details for a specific bundle ID." in res.output

    # remove
    res = runner.invoke(cli, ["remove", "--help"])
    assert res.exit_code == 0
    assert "Remove a cloned application." in res.output
    assert "Also delete the data directory." in res.output

    # update
    res = runner.invoke(cli, ["update", "--help"])
    assert res.exit_code == 0
    assert "Update a cloned application." in res.output

    # version
    res = runner.invoke(cli, ["version", "--help"])
    assert res.exit_code == 0
    assert "Display ATBClone version and environment information." in res.output

    # wizard
    res = runner.invoke(cli, ["wizard", "--help"])
    assert res.exit_code == 0
    assert "Interactive cloning wizard." in res.output


