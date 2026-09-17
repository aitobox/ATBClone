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
