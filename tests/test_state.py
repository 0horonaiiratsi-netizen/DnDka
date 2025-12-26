from pathlib import Path

import pytest

from app.models import CampaignCreate, CampaignUpdate, Message, PlayerCreate
from app.state import StateStore


def test_create_update_delete_campaign(tmp_path: Path):
    db = tmp_path / "db.json"
    store = StateStore(db)
    created = store.add_campaign(
        CampaignCreate(title="Test", summary="sum", tone="light", setting="mars")
    )
    updated = store.update_campaign(
        created.id, CampaignUpdate(title="Updated", summary="New summary")
    )
    assert updated.title == "Updated"
    assert updated.summary == "New summary"
    store.delete_campaign(created.id)
    assert store.list_campaigns() == []


def test_add_remove_player(tmp_path: Path):
    db = tmp_path / "db.json"
    store = StateStore(db)
    campaign = store.add_campaign(
        CampaignCreate(title="Test", summary="sum", tone="light", setting="mars")
    )
    updated = store.add_player(
        campaign.id,
        PlayerCreate(
            name="Player",
            character_name="Hero",
            character_class="Fighter",
            level=1,
            backstory="",
        ),
    )
    player_id = updated.players[0].id
    store.remove_player(campaign.id, player_id)
    refreshed = store.get_campaign(campaign.id)
    assert refreshed.players == []


def test_clear_log(tmp_path: Path):
    db = tmp_path / "db.json"
    store = StateStore(db)
    campaign = store.add_campaign(
        CampaignCreate(title="Test", summary="sum", tone="light", setting="mars")
    )
    store.add_message(campaign.id, Message(author="DM", text="Hello"))
    cleared = store.clear_log(campaign.id)
    assert cleared.log == []
