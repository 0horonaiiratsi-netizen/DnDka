import json
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

from .models import (
    Campaign,
    CampaignCreate,
    CampaignUpdate,
    Message,
    Player,
    PlayerCreate,
)


class StateStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        if not self.db_path.exists():
            self._write({"campaigns": []})

    def _read(self) -> Dict:
        with self.db_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, data: Dict) -> None:
        with self.db_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, default=str)

    def list_campaigns(self) -> List[Campaign]:
        raw = self._read()
        return [Campaign.model_validate(item) for item in raw.get("campaigns", [])]

    def _persist(self, campaigns: List[Campaign]) -> None:
        self._write({"campaigns": [c.model_dump() for c in campaigns]})

    def add_campaign(self, payload: CampaignCreate) -> Campaign:
        with self._lock:
            campaigns = self.list_campaigns()
            campaign = Campaign(**payload.model_dump())
            campaigns.append(campaign)
            self._persist(campaigns)
            return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        for campaign in self.list_campaigns():
            if campaign.id == campaign_id:
                return campaign
        return None

    def update_campaign(self, campaign_id: str, payload: CampaignUpdate) -> Campaign:
        with self._lock:
            campaigns = self.list_campaigns()
            for idx, campaign in enumerate(campaigns):
                if campaign.id == campaign_id:
                    data = campaign.model_dump()
                    for key, value in payload.model_dump(exclude_unset=True).items():
                        data[key] = value
                    updated = Campaign.model_validate(data)
                    campaigns[idx] = updated
                    self._persist(campaigns)
                    return updated
        raise KeyError("Campaign not found")

    def delete_campaign(self, campaign_id: str) -> None:
        with self._lock:
            campaigns = self.list_campaigns()
            new_campaigns = [c for c in campaigns if c.id != campaign_id]
            if len(new_campaigns) == len(campaigns):
                raise KeyError("Campaign not found")
            self._persist(new_campaigns)

    def add_player(self, campaign_id: str, payload: PlayerCreate) -> Campaign:
        with self._lock:
            campaigns = self.list_campaigns()
            for idx, campaign in enumerate(campaigns):
                if campaign.id == campaign_id:
                    campaign.players.append(Player(**payload.model_dump()))
                    campaigns[idx] = campaign
                    self._persist(campaigns)
                    return campaign
        raise KeyError("Campaign not found")

    def remove_player(self, campaign_id: str, player_id: str) -> Campaign:
        with self._lock:
            campaigns = self.list_campaigns()
            for idx, campaign in enumerate(campaigns):
                if campaign.id == campaign_id:
                    new_players = [p for p in campaign.players if p.id != player_id]
                    if len(new_players) == len(campaign.players):
                        raise KeyError("Player not found")
                    campaign.players = new_players
                    campaigns[idx] = campaign
                    self._persist(campaigns)
                    return campaign
        raise KeyError("Campaign not found")

    def add_message(self, campaign_id: str, message: Message) -> Campaign:
        with self._lock:
            campaigns = self.list_campaigns()
            for idx, campaign in enumerate(campaigns):
                if campaign.id == campaign_id:
                    campaign.log.append(message)
                    campaigns[idx] = campaign
                    self._persist(campaigns)
                    return campaign
        raise KeyError("Campaign not found")

    def clear_log(self, campaign_id: str) -> Campaign:
        with self._lock:
            campaigns = self.list_campaigns()
            for idx, campaign in enumerate(campaigns):
                if campaign.id == campaign_id:
                    campaign.log = []
                    campaigns[idx] = campaign
                    self._persist(campaigns)
                    return campaign
        raise KeyError("Campaign not found")
