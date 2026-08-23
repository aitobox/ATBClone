from unittest.mock import MagicMock
from atbclone.core.state import CloneRecord
from atbclone.gui.components.clone_card import CloneCard


def test_clone_card_render_and_actions():
    record = CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="soft_clone",
        dest_path="/Users/test/ATBClone/Apps/WeChat2.app",
        data_dir="/Users/test/ATBClone/data/WeChat2",
        created_at="2026-08-20T10:00:00Z",
    )

    on_launch = MagicMock()
    on_open_dir = MagicMock()
    on_update = MagicMock()
    on_edit = MagicMock()
    on_detail = MagicMock()
    on_delete = MagicMock()

    card = CloneCard(
        record=record,
        on_launch=on_launch,
        on_open_dir=on_open_dir,
        on_update=on_update,
        on_edit=on_edit,
        on_detail=on_detail,
        on_delete=on_delete,
    )

    assert "WeChat2" in card.label_name.text
    assert "Soft" in card.label_strategy.text or "软包装" in card.label_strategy.text or "克隆" in card.label_strategy.text

