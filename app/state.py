import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import Campaign, CampaignCreate, Message, Player, PlayerCreate


class StateStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
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

    def save_campaigns(self, campaigns: List[Campaign]) -> None:
        self._write({"campaigns": [c.model_dump() for c in campaigns]})

    def add_campaign(self, payload: CampaignCreate) -> Campaign:
        campaigns = self.list_campaigns()
        campaign = Campaign(**payload.model_dump())
        campaigns.append(campaign)
        self.save_campaigns(campaigns)
        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        for campaign in self.list_campaigns():
            if campaign.id == campaign_id:
                return campaign
        return None

    def add_player(self, campaign_id: str, payload: PlayerCreate) -> Campaign:
        campaigns = self.list_campaigns()
        for idx, campaign in enumerate(campaigns):
            if campaign.id == campaign_id:
                campaign.players.append(Player(**payload.model_dump()))
                campaigns[idx] = campaign
                self.save_campaigns(campaigns)
                return campaign
        raise KeyError("Campaign not found")

    def add_message(self, campaign_id: str, message: Message) -> Campaign:
        campaigns = self.list_campaigns()
        for idx, campaign in enumerate(campaigns):
            if campaign.id == campaign_id:
                campaign.log.append(message)
                campaigns[idx] = campaign
                self.save_campaigns(campaigns)
                return campaign
        raise KeyError("Campaign not found")
