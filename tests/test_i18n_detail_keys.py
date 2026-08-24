"""Test clone detail injected parameters i18n keys."""

from atbclone.core.i18n import t


def test_detail_injected_i18n_keys():
    keys = [
        "win_detail_section_basic",
        "win_detail_section_injected",
        "win_detail_launch_args",
        "win_detail_env_vars",
        "win_detail_exec_cmd",
        "win_detail_btn_copy_cmd",
        "win_detail_cmd_copied",
        "win_detail_none",
    ]
    for key in keys:
        val_en = t(key, lang="en")
        val_zh = t(key, lang="zh")
        assert val_en != key, f"Missing en translation for {key}"
        assert val_zh != key, f"Missing zh translation for {key}"
