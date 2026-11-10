"""Exercise process naming with real Mach-O executables, not just script text."""

import plistlib
import shutil
import subprocess
from pathlib import Path

import pytest

from atbclone.core.clone_task import CloneTask
from atbclone.core.engines import HardCloneEngine
from atbclone.core.models import AppInfo
from atbclone.recipes.models import Recipe


@pytest.fixture
def bundle(tmp_path):
    """Build a minimal native app whose executable reports its kernel-resolved path."""
    app = tmp_path / "Original.app"
    macos = app / "Contents/MacOS"
    macos.mkdir(parents=True)
    source = tmp_path / "process.c"
    source.write_text('''#include <libproc.h>
#include <stdio.h>
#include <unistd.h>
int main(void) {
    char path[PROC_PIDPATHINFO_MAXSIZE];
    if (proc_pidpath(getpid(), path, sizeof(path)) <= 0) return 1;
    puts(path);
    return 0;
}
''')
    subprocess.run(["clang", "-Wl,-headerpad,0x1000", str(source), "-o", str(macos / "Original")], check=True)
    metadata = {"CFBundleIdentifier": "com.atbclone.test", "CFBundleExecutable": "Original", "CFBundlePackageType": "APPL"}
    (app / "Contents/Info.plist").write_bytes(plistlib.dumps(metadata))
    task = CloneTask(
        source=AppInfo(app, "com.atbclone.test", "Original", macos / "Original", False),
        dest_path=app, data_dir=tmp_path / "Data", clone_name="WeWork",
        new_bundle_id="com.atbclone.test.clone",
        recipe=Recipe(bundle_id="com.atbclone.test", app_name="Original", strategy="hard_clone"),
    )
    return task, macos


@pytest.mark.parametrize("launcher", [False, True])
@pytest.mark.parametrize("name", ["WeWork", "Original", "微信 Work's $name"])
def test_real_process_names_and_signatures(bundle, launcher, name):
    """Verify process paths, compatibility aliases and signatures for supported names."""
    task, macos = bundle
    task.clone_name = name
    original = macos / "Original"
    main = macos / "Original.bin" if launcher else original
    if launcher:
        shutil.copy2(original, main)
    helper_app = task.dest_path / "Contents/Helpers/Helper.app"
    helper = helper_app / "Contents/MacOS/Helper"
    helper.parent.mkdir(parents=True)
    shutil.copy2(original, helper)
    helper_plist = helper_app / "Contents/Info.plist"
    helper_plist.write_bytes(plistlib.dumps({"CFBundleIdentifier": "com.atbclone.test.helper", "CFBundleExecutable": "Helper", "CFBundlePackageType": "APPL"}))
    standalone = task.dest_path / "Contents/Frameworks/network-helper"
    standalone.parent.mkdir(parents=True)
    shutil.copy2(original, standalone)
    # Shared libraries, scripts and external symlinks must not be renamed.
    library = standalone.parent / "libtest.dylib"
    library.write_bytes(b"\xcf\xfa\xed\xfe" + b"\0" * 8 + b"\x06\0\0\0")
    script_file = macos / "script"
    script_file.write_text("#!/bin/sh\nexit 0\n")
    script_file.chmod(0o755)
    (macos / "external").symlink_to("/bin/echo")

    script = HardCloneEngine._build_process_name_cmd(task, main)
    subprocess.run(["/bin/bash", "-ec", script], check=True)
    for old, expected in [(main, name), (helper, name + "-Helper"), (standalone, name + "-network-helper")]:
        result = subprocess.run([str(old)], check=True, capture_output=True, text=True)
        assert Path(result.stdout.strip()).name == expected
    assert library.is_file() and not library.is_symlink()
    assert script_file.is_file() and not script_file.is_symlink()
    assert (macos / "external").readlink() == Path("/bin/echo")
    root_plist = task.dest_path / "Contents/Info.plist"
    entry = plistlib.loads(root_plist.read_bytes())["CFBundleExecutable"]
    assert entry == (name + "-Launcher" if launcher else name)
    assert not (macos / entry).is_symlink()
    assert plistlib.loads(helper_plist.read_bytes())["CFBundleExecutable"] == name + "-Helper"
    (macos / "external").unlink()  # External links are intentionally not valid signed resources.
    library.unlink()  # The header-only dylib above is a scan fixture, not signable code.
    for app in (helper_app, task.dest_path):
        subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(app)], check=True, capture_output=True)
        subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)], check=True, capture_output=True)


def test_process_name_collision_fails_before_renaming(bundle):
    """Preserve existing resources when the requested process filename is occupied."""
    task, macos = bundle
    (macos / "WeWork").write_text("existing resource")
    script = HardCloneEngine._build_process_name_cmd(task, macos / "Original")
    result = subprocess.run(["/bin/bash", "-ec", script], capture_output=True, check=False)
    assert result.returncode != 0
    assert (macos / "Original").is_file() and not (macos / "Original").is_symlink()
    assert (macos / "WeWork").read_text() == "existing resource"


@pytest.mark.parametrize("strategy", ["dylib", "launcher"])
def test_hard_clone_launches_with_custom_process_name(bundle, strategy):
    """Run the full hard-clone pipeline and confirm both injection modes launch the renamed process."""
    task, _ = bundle
    task.dest_path = task.source.path.parent / "WeWork.app"
    task.injection_strategy = strategy
    HardCloneEngine.execute(task, needs_admin=False)
    info = plistlib.loads((task.dest_path / "Contents/Info.plist").read_bytes())
    executable = task.dest_path / "Contents/MacOS" / info["CFBundleExecutable"]
    result = subprocess.run([str(executable)], check=True, capture_output=True, text=True)
    assert Path(result.stdout.strip()).name == "WeWork"
    assert task.source.executable.is_file() and not task.source.executable.is_symlink()


@pytest.mark.parametrize("launcher", [False, True])
def test_helper_name_collision_preserves_original_paths(bundle, launcher):
    """Reject a clone name that would turn an existing helper path into the main process."""
    task, macos = bundle
    task.clone_name = "Helper"
    original = macos / "Original"
    main = macos / "Original.bin" if launcher else original
    if launcher:
        shutil.copy2(original, main)
    helper = macos / "Helper"
    shutil.copy2(original, helper)
    before = {path: path.read_bytes() for path in (original, main, helper)}
    plist = task.dest_path / "Contents/Info.plist"
    original_plist = plist.read_bytes()

    script = HardCloneEngine._build_process_name_cmd(task, main)
    result = subprocess.run(["/bin/bash", "-ec", script], capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "Process name conflicts" in result.stderr
    for path, data in before.items():
        assert not path.is_symlink()
        assert path.read_bytes() == data
    assert plist.read_bytes() == original_plist


def test_process_names_handles_missing_and_corrupted_bundle_gracefully(bundle, tmp_path):
    """Ensure process renaming exits gracefully instead of crashing on missing or corrupted bundles."""
    task, macos = bundle
    # 1. Missing Info.plist: should exit cleanly with 0
    (task.dest_path / "Contents/Info.plist").unlink()
    script = HardCloneEngine._build_process_name_cmd(task, macos / "Original")
    res = subprocess.run(["/bin/bash", "-ec", script], capture_output=True, text=True, check=False)
    assert res.returncode == 0

    # 2. Info.plist missing CFBundleExecutable: should exit cleanly with 0
    (task.dest_path / "Contents/Info.plist").write_bytes(plistlib.dumps({"CFBundleIdentifier": "com.test"}))
    script = HardCloneEngine._build_process_name_cmd(task, macos / "Original")
    res = subprocess.run(["/bin/bash", "-ec", script], capture_output=True, text=True, check=False)
    assert res.returncode == 0

    # 3. Truncated or corrupt binary file: should not crash is_executable with struct.error
    (task.dest_path / "Contents/Info.plist").write_bytes(
        plistlib.dumps({"CFBundleIdentifier": "com.test", "CFBundleExecutable": "Original"})
    )
    corrupt = macos / "corrupt_mach_o"
    corrupt.write_bytes(b"\xca\xfe")  # truncated fat header
    corrupt.chmod(0o755)
    script = HardCloneEngine._build_process_name_cmd(task, macos / "Original")
    res = subprocess.run(["/bin/bash", "-ec", script], capture_output=True, text=True, check=False)
    assert res.returncode == 0


def test_process_names_respects_relative_plist_path(tmp_path):
    """Ensure process renaming respects task.source.relative_plist_path for non-standard bundles."""
    app = tmp_path / "Wrapped.app"
    inner_plist = app / "WrappedBundle/Info.plist"
    inner_plist.parent.mkdir(parents=True)
    inner_macos = app / "WrappedBundle/MacOS"
    inner_macos.mkdir(parents=True)

    metadata = {"CFBundleIdentifier": "com.atbclone.wrapped", "CFBundleExecutable": "InnerApp"}
    inner_plist.write_bytes(plistlib.dumps(metadata))

    bin_path = inner_macos / "InnerApp"
    # Write minimal executable
    source = tmp_path / "inner.c"
    source.write_text("int main(void){return 0;}")
    subprocess.run(["clang", str(source), "-o", str(bin_path)], check=True)

    task = CloneTask(
        source=AppInfo(
            path=app,
            bundle_id="com.atbclone.wrapped",
            app_name="Wrapped",
            executable=bin_path,
            has_sandbox=False,
            is_ios_app=False,
            relative_plist_path=Path("WrappedBundle/Info.plist"),
        ),
        dest_path=app,
        data_dir=tmp_path / "Data",
        clone_name="WrappedClone",
        new_bundle_id="com.atbclone.wrapped.clone",
        recipe=Recipe(bundle_id="com.atbclone.wrapped", app_name="Wrapped", strategy="hard_clone"),
    )

    script = HardCloneEngine._build_process_name_cmd(task, bin_path)
    res = subprocess.run(["/bin/bash", "-ec", script], capture_output=True, text=True, check=False)
    assert res.returncode == 0
    updated_plist = plistlib.loads(inner_plist.read_bytes())
    assert updated_plist["CFBundleExecutable"] == "WrappedClone"
    assert (inner_macos / "WrappedClone").is_file()


def test_electron_helpers_in_frameworks_preserved(bundle):
    """Ensure Electron/Chromium helper bundles in Frameworks and Resources are not renamed."""
    task, macos = bundle
    task.clone_name = "QQClone"
    task.recipe.app_type = "electron"
    original = macos / "Original"

    helper_app = task.dest_path / "Contents/Frameworks/QQ Helper.app"
    helper_macos = helper_app / "Contents/MacOS"
    helper_macos.mkdir(parents=True)
    shutil.copy2(original, helper_macos / "QQ Helper")
    helper_plist = helper_app / "Contents/Info.plist"
    helper_plist.write_bytes(plistlib.dumps({
        "CFBundleIdentifier": "com.tencent.qq.helper",
        "CFBundleExecutable": "QQ Helper",
        "CFBundlePackageType": "APPL",
    }))

    res_plugin_app = task.dest_path / "Contents/Resources/app/Plugin.app"
    res_plugin_macos = res_plugin_app / "Contents/MacOS"
    res_plugin_macos.mkdir(parents=True)
    shutil.copy2(original, res_plugin_macos / "Plugin")
    res_plugin_plist = res_plugin_app / "Contents/Info.plist"
    res_plugin_plist.write_bytes(plistlib.dumps({
        "CFBundleIdentifier": "com.tencent.qq.plugin",
        "CFBundleExecutable": "Plugin",
        "CFBundlePackageType": "APPL",
    }))

    # Nested sub-app (e.g. QQEXGuild.app inside Contents/MacOS/)
    nested_app = macos / "QQEXGuild.app"
    nested_macos = nested_app / "Contents/MacOS"
    nested_macos.mkdir(parents=True)
    shutil.copy2(original, nested_macos / "QQEXGuild")
    nested_plist = nested_app / "Contents/Info.plist"
    nested_plist.write_bytes(plistlib.dumps({
        "CFBundleIdentifier": "com.tencent.qq.guild",
        "CFBundleExecutable": "QQEXGuild",
        "CFBundlePackageType": "APPL",
    }))
    nested_helper = nested_app / "Contents/Frameworks/QQEXGuild Helper.app/Contents/MacOS"
    nested_helper.mkdir(parents=True)
    shutil.copy2(original, nested_helper / "QQEXGuild Helper")
    nested_helper_plist = nested_app / "Contents/Frameworks/QQEXGuild Helper.app/Contents/Info.plist"
    nested_helper_plist.write_bytes(plistlib.dumps({
        "CFBundleIdentifier": "com.tencent.qq.guild.helper",
        "CFBundleExecutable": "QQEXGuild Helper",
        "CFBundlePackageType": "APPL",
    }))

    script = HardCloneEngine._build_process_name_cmd(task, original)
    res = subprocess.run(["/bin/bash", "-ec", script], capture_output=True, text=True, check=False)
    assert res.returncode == 0

    # Main binary renamed
    assert (macos / "QQClone").is_file()
    assert (macos / "Original").is_symlink()

    # Electron helper in Frameworks MUST NOT be renamed
    assert (helper_macos / "QQ Helper").is_file()
    assert not (helper_macos / "QQ Helper").is_symlink()
    assert not (helper_macos / "QQClone-QQ Helper").exists()

    # Electron helper Info.plist MUST NOT be modified
    data = plistlib.loads(helper_plist.read_bytes())
    assert data["CFBundleExecutable"] == "QQ Helper"

    # Resources plugin MUST NOT be renamed
    assert (res_plugin_macos / "Plugin").is_file()
    assert not (res_plugin_macos / "Plugin").is_symlink()
    assert not (res_plugin_macos / "QQClone-Plugin").exists()
    plugin_data = plistlib.loads(res_plugin_plist.read_bytes())
    assert plugin_data["CFBundleExecutable"] == "Plugin"

    # Nested sub-app and its helpers MUST NOT be renamed
    assert (nested_macos / "QQEXGuild").is_file()
    assert not (nested_macos / "QQEXGuild").is_symlink()
    assert (nested_helper / "QQEXGuild Helper").is_file()
    assert not (nested_helper / "QQEXGuild Helper").is_symlink()
    assert plistlib.loads(nested_plist.read_bytes())["CFBundleExecutable"] == "QQEXGuild"
    assert plistlib.loads(nested_helper_plist.read_bytes())["CFBundleExecutable"] == "QQEXGuild Helper"


def test_wechat_nested_appex_and_helpers_preserved(bundle):
    """Ensure Cocoa apps embedding WeChatAppEx (WMPF/CEF) preserve nested sub-apps and helpers."""
    task, macos = bundle
    task.clone_name = "WeChatClone"
    task.recipe.app_type = "cocoa"
    original = macos / "Original"

    # 1. Nested WeChatAppEx.app under Contents/MacOS/
    appex = macos / "WeChatAppEx.app"
    appex_macos = appex / "Contents/MacOS"
    appex_macos.mkdir(parents=True)
    shutil.copy2(original, appex_macos / "WeChatAppEx")
    appex_plist = appex / "Contents/Info.plist"
    appex_plist.write_bytes(plistlib.dumps({
        "CFBundleIdentifier": "com.tencent.xinWeChat.WeChatAppEx",
        "CFBundleExecutable": "WeChatAppEx",
        "CFBundlePackageType": "APPL",
    }))

    # 2. Embedded WeChatAppEx Framework and its Helper app
    framework = appex / "Contents/Frameworks/WeChatAppEx Framework.framework/Versions/C"
    helper_macos = framework / "Helpers/WeChatAppEx Helper.app/Contents/MacOS"
    helper_macos.mkdir(parents=True)
    shutil.copy2(original, helper_macos / "WeChatAppEx Helper")
    helper_plist = framework / "Helpers/WeChatAppEx Helper.app/Contents/Info.plist"
    helper_plist.write_bytes(plistlib.dumps({
        "CFBundleIdentifier": "com.tencent.xinWeChat.WeChatAppEx.helper",
        "CFBundleExecutable": "WeChatAppEx Helper",
        "CFBundlePackageType": "APPL",
    }))

    script = HardCloneEngine._build_process_name_cmd(task, original)
    res = subprocess.run(["/bin/bash", "-ec", script], capture_output=True, text=True, check=False)
    assert res.returncode == 0

    # Main binary renamed
    assert (macos / "WeChatClone").is_file()
    assert (macos / "Original").is_symlink()

    # WeChatAppEx sub-app binary and plist MUST NOT be renamed
    assert (appex_macos / "WeChatAppEx").is_file()
    assert not (appex_macos / "WeChatAppEx").is_symlink()
    assert not (appex_macos / "WeChatClone-WeChatAppEx").exists()
    appex_data = plistlib.loads(appex_plist.read_bytes())
    assert appex_data["CFBundleExecutable"] == "WeChatAppEx"

    # Embedded WeChatAppEx Helper binary and plist MUST NOT be renamed
    assert (helper_macos / "WeChatAppEx Helper").is_file()
    assert not (helper_macos / "WeChatAppEx Helper").is_symlink()
    assert not (helper_macos / "WeChatClone-WeChatAppEx Helper").exists()
    helper_data = plistlib.loads(helper_plist.read_bytes())
    assert helper_data["CFBundleExecutable"] == "WeChatAppEx Helper"



