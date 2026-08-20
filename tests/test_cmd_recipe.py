"""Unit tests for the `recipe` CLI subcommand group."""

from pathlib import Path
from click.testing import CliRunner

from atbclone.cli.main import cli
from atbclone.recipes.loader import RecipeLoader


def test_recipe_list():
    runner = CliRunner(env={"COLUMNS": "160"})
    result = runner.invoke(cli, ["recipe", "list"])
    assert result.exit_code == 0
    assert "com.tencent.xinWeChat" in result.output
    assert "com.google.Chrome" in result.output
    assert "Bundle ID" in result.output
    assert "App Name" in result.output or "应用名称" in result.output
    assert "Strategy" in result.output or "策略" in result.output
    assert "Strip Sandbox" in result.output or "解除沙盒" in result.output


def test_recipe_list_shows_all():
    runner = CliRunner(env={"COLUMNS": "160"})
    result = runner.invoke(cli, ["recipe", "list"])
    assert result.exit_code == 0
    # Count occurrences of strategy types
    hard_count = result.output.count("hard_clone")
    soft_count = result.output.count("soft_clone")
    assert hard_count + soft_count == len(list(RecipeLoader.BUILTIN_DIR.glob("*.yaml")))


def test_recipe_list_sorted():
    runner = CliRunner(env={"COLUMNS": "160"})
    result = runner.invoke(cli, ["recipe", "list"])
    assert result.exit_code == 0
    # hard_clone should appear before soft_clone
    first_hard = result.output.find("hard_clone")
    first_soft = result.output.find("soft_clone")
    assert first_hard != -1 and first_soft != -1
    assert first_hard < first_soft


def test_recipe_show_builtin():
    runner = CliRunner(env={"COLUMNS": "160"})
    result = runner.invoke(cli, ["recipe", "show", "com.tencent.xinWeChat"])
    assert result.exit_code == 0
    assert "hard_clone" in result.output
    assert "bundle_id: com.tencent.xinWeChat" in result.output


def test_recipe_show_not_found():
    runner = CliRunner(env={"COLUMNS": "160"})
    result = runner.invoke(cli, ["recipe", "show", "com.nonexistent.app"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_recipe_show_local_override(tmp_path: Path):
    runner = CliRunner(env={"COLUMNS": "160"})
    custom_recipe = tmp_path / "com.tencent.xinWeChat.yaml"
    custom_recipe.write_text(
        "bundle_id: com.tencent.xinWeChat\napp_name: 微信Custom\nstrategy: hard_clone\n",
        encoding="utf-8",
    )

    old_local_dir = RecipeLoader.LOCAL_DIR
    try:
        RecipeLoader.LOCAL_DIR = tmp_path
        result = runner.invoke(cli, ["recipe", "show", "com.tencent.xinWeChat"])
        assert result.exit_code == 0
        assert "local override" in result.output
        assert "微信Custom" in result.output
    finally:
        RecipeLoader.LOCAL_DIR = old_local_dir


def test_recipe_help():
    runner = CliRunner(env={"COLUMNS": "160"})
    result = runner.invoke(cli, ["recipe", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "show" in result.output
