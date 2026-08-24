"""Unit tests for the `wizard` CLI interactive command."""

from pathlib import Path
from unittest.mock import patch
import pytest
from click.testing import CliRunner

from atbclone.cli.main import cli
from atbclone.core.clone_task import CloneTask
from atbclone.core.models import AppInfo
from atbclone.executor.runner import CloneError
from atbclone.recipes.models import Recipe


@pytest.fixture
def mock_app_info(tmp_path: Path) -> AppInfo:
    app_dir = tmp_path / "WeChat.app"
    app_dir.mkdir(parents=True, exist_ok=True)
    return AppInfo(
        path=app_dir,
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        executable=app_dir / "Contents" / "MacOS" / "WeChat",
        has_sandbox=True,
    )


@pytest.fixture
def mock_soft_recipe() -> Recipe:
    return Recipe(
        bundle_id="com.google.Chrome",
        app_name="Google Chrome",
        strategy="soft_clone",
        launch_args=["--user-data-dir={{ATB_DATA_DIR}}"],
    )


@pytest.fixture
def mock_hard_recipe() -> Recipe:
    return Recipe(
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        strategy="hard_clone",
        environment_injection={
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
        },
    )


def test_wizard_complete_hard_clone(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    # Prompts:
    # 1. app path
    # 2. clone name: default (\n)
    # 3. display_name: default/empty (\n)
    # 4. icon_path: default/empty (\n)
    # 5. output dir: default (\n)
    # 6. data dir: default (\n)
    # 7. proxy: default n (\n)
    # 8. confirm: default y (\n)
    inputs = f"{mock_app_info.path}\n\n\n\n\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info) as mock_inspect, \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe) as mock_match, \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)) as mock_next_name, \
         patch("atbclone.cli.cmd_wizard.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.load", return_value=[]), \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        assert "ATBClone Wizard" in result.output or "ATBClone 小向导" in result.output
        assert "Detecting application..." in result.output or "检测应用..." in result.output
        assert "Application: WeChat" in result.output or "应用: WeChat" in result.output
        assert "Strategy: hard_clone" in result.output or "策略: hard_clone" in result.output
        assert "About to create clone:" in result.output or "即将创建分身:" in result.output
        assert "Name: WeChat2" in result.output or "名称: WeChat2" in result.output
        assert "Data Dir:" in result.output or "数据目录:" in result.output
        assert "Proxy: Not configured" in result.output or "代理: 未配置" in result.output
        assert "Success! Clone created at" in result.output or "成功！" in result.output

        mock_inspect.assert_called_once_with(str(mock_app_info.path))
        mock_match.assert_called_once_with(mock_app_info.bundle_id, app_path=mock_app_info.path)
        mock_hard_exec.assert_called_once()
        mock_soft_exec.assert_not_called()
        mock_state_add.assert_called_once()

        task, needs_admin = mock_hard_exec.call_args[0]
        assert isinstance(task, CloneTask)
        assert task.source == mock_app_info
        assert task.clone_name == "WeChat2"
        assert task.dest_path == Path.home() / "Applications" / "WeChat2.app"
        assert task.new_bundle_id == "com.tencent.xinWeChat.atbclone.2"
        assert task.display_name is None
        assert task.icon_path is None
        assert needs_admin is False

        record = mock_state_add.call_args[0][0]
        assert record.clone_name == "WeChat2"
        assert record.strategy == "hard_clone"
        assert record.proxy_enabled is False


def test_wizard_complete_soft_clone(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    inputs = f"{mock_app_info.path}\n\n\n\n\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("Chrome2", 2)), \
         patch("atbclone.cli.cmd_wizard.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        assert "Strategy: soft_clone" in result.output or "策略: soft_clone" in result.output
        mock_soft_exec.assert_called_once()
        mock_hard_exec.assert_not_called()
        mock_state_add.assert_called_once()


def test_wizard_custom_data_dir(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    custom_dir = tmp_path / "custom_data_dir"
    # Inputs: path, name, display_name, icon, output, data_dir=custom_dir, proxy=n, confirm=y
    inputs = f"{mock_app_info.path}\n\n\n\n\n{custom_dir}\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        task, _ = mock_hard_exec.call_args[0]
        assert task.data_dir == custom_dir.resolve()
        record = mock_state_add.call_args[0][0]
        assert record.data_dir == str(custom_dir.resolve())


def test_wizard_unsupported_data_dir_skips_prompt(tmp_path: Path, mock_app_info: AppInfo):
    runner = CliRunner()
    unsupported_recipe = Recipe(
        bundle_id="dev.zed.Zed",
        app_name="Zed",
        strategy="soft_clone",
        launch_args=[],
        environment_injection={},
    )
    # Inputs: path, name, display_name, icon, output, proxy=n, confirm=y (only 7 items, no data_dir)
    inputs = f"{mock_app_info.path}\n\n\n\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=unsupported_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("Zed2", 2)), \
         patch("atbclone.cli.cmd_wizard.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        assert "Data storage directory" not in result.output and "数据存储目录" not in result.output
        mock_soft_exec.assert_called_once()


def test_wizard_with_proxy(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    # Prompts:
    # 1. app path
    # 2. clone name: default (\n)
    # 3. display_name: empty (\n)
    # 4. icon_path: empty (\n)
    # 5. output dir: default (\n)
    # 6. data dir: default (\n)
    # 7. proxy: y
    # 8. proxy host: 192.168.1.100
    # 9. proxy port: 7890
    # 10. proxy type: socks5
    # 11. confirm: y (\n)
    inputs = f"{mock_app_info.path}\n\n\n\n\n\ny\n192.168.1.100\n7890\nsocks5\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        assert "Proxy: Configured" in result.output or "代理: 已配置" in result.output
        mock_hard_exec.assert_called_once()
        task, _ = mock_hard_exec.call_args[0]
        assert task.recipe.proxy.enabled is True
        assert task.recipe.proxy.host == "192.168.1.100"
        assert task.recipe.proxy.port == 7890
        assert task.recipe.proxy.type == "socks5"

        mock_state_add.assert_called_once()
        record = mock_state_add.call_args[0][0]
        assert record.proxy_enabled is True
        assert record.proxy_summary == "socks5://192.168.1.100:7890"


def test_wizard_cancel(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    # Prompts: path, name, display_name, icon, output, data_dir, proxy, confirm=n
    inputs = f"{mock_app_info.path}\n\n\n\n\n\n\nn\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        mock_hard_exec.assert_not_called()
        mock_state_add.assert_not_called()


def test_wizard_invalid_path_then_valid(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    nonexistent = tmp_path / "NonExistent.app"
    not_app = tmp_path / "SomeFile.txt"
    not_app.touch()

    # Inputs: bad, bad, valid path, name, display_name, icon, output, data_dir, proxy, confirm
    inputs = f"{nonexistent}\n{not_app}\n{mock_app_info.path}\n\n\n\n\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add"):

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        assert "please try again" in result.output or "请重新输入" in result.output
        mock_hard_exec.assert_called_once()


def test_wizard_custom_output_dir_and_admin(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    admin_output = Path("/Applications")
    # Prompts: path, name=CustomWeChat, display_name=empty, icon=empty, output=/Applications, data_dir=default, proxy=n, confirm=y
    inputs = f"{mock_app_info.path}\nCustomWeChat\n\n\n{admin_output}\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.Path.mkdir"), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        mock_hard_exec.assert_called_once()
        task, needs_admin = mock_hard_exec.call_args[0]
        assert needs_admin is True
        assert task.clone_name == "CustomWeChat"
        assert task.dest_path == admin_output / "CustomWeChat.app"


def test_wizard_error_handling(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    inputs = f"{mock_app_info.path}\n\n\n\n\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute", side_effect=CloneError("Execution failed")), \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 1
        assert "Execution failed" in result.output
        mock_state_add.assert_not_called()


def test_wizard_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["wizard", "--help"])
    assert result.exit_code == 0
    assert "向导" in result.output or "wizard" in result.output.lower()


def test_wizard_custom_display_name(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    """Wizard: explicit display_name is passed into CloneTask and shown in confirmation."""
    runner = CliRunner()
    # Prompts: path, name, display_name="我的微信", icon=empty, output, data_dir, proxy, confirm
    inputs = f"{mock_app_info.path}\n\n我的微信\n\n\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add"):

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        assert "我的微信" in result.output
        task, _ = mock_hard_exec.call_args[0]
        assert task.display_name == "我的微信"


def test_wizard_custom_icon(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    """Wizard: valid .icns path is accepted and passed into CloneTask."""
    runner = CliRunner()
    icon_file = tmp_path / "custom.icns"
    icon_file.touch()

    # Prompts: path, name, display_name=empty, icon=custom.icns, output, data_dir, proxy, confirm
    inputs = f"{mock_app_info.path}\n\n\n{icon_file}\n\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add"):

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        assert "Icon:" in result.output or "图标:" in result.output
        task, _ = mock_hard_exec.call_args[0]
        assert task.icon_path == icon_file


def test_wizard_invalid_icon_then_valid(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    """Wizard: non-.icns file rejected, then empty accepted (fallback to original)."""
    runner = CliRunner()
    bad_icon = tmp_path / "icon.png"
    bad_icon.touch()

    # Prompts: path, name, display_name=empty, icon=bad(.png), icon=empty (retry), output, data_dir, proxy, confirm
    inputs = f"{mock_app_info.path}\n\n\n{bad_icon}\n\n\n\n\n\n"

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add"):

        result = runner.invoke(cli, ["wizard"], input=inputs)

        assert result.exit_code == 0
        assert "Must be a .icns file" in result.output or "必须是 .icns 文件" in result.output
        task, _ = mock_hard_exec.call_args[0]
        assert task.icon_path is None


def test_wizard_ios_wrapper_app_fails(tmp_path: Path):
    runner = CliRunner()
    fake_app = tmp_path / "小宇宙.app"
    fake_app.mkdir()

    from atbclone.core.models import AppInfo
    mock_info = AppInfo(
        path=fake_app,
        bundle_id="app.podcast.cosmos",
        app_name="小宇宙",
        executable=fake_app / "Wrapper" / "Podcast.app" / "Podcast",
        has_sandbox=True,
        is_ios_app=True,
    )

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_info):
        result = runner.invoke(cli, ["wizard"], input=f"{fake_app}\n")
        assert result.exit_code == 1
        assert "不支持 iOS on Mac Wrapper 应用" in result.output or "iOS on Mac Wrapper" in result.output

