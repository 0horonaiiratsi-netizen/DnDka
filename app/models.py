from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class PlayerCreate(BaseModel):
    name: str
    character_name: str
    character_class: str
    level: int = Field(ge=1, le=20, default=1)
    backstory: str = Field(default="", max_length=2000)


class Player(PlayerCreate):
    id: str = Field(default_factory=lambda: uuid4().hex)


class CampaignCreate(BaseModel):
    title: str
    summary: str = Field(default="", max_length=2000)
    tone: str = Field(default="classic fantasy", max_length=120)
    setting: str = Field(default="Forgotten Realms", max_length=120)


class CampaignUpdate(BaseModel):
    title: str | None = None
    summary: str | None = Field(default=None, max_length=2000)
    tone: str | None = Field(default=None, max_length=120)
    setting: str | None = Field(default=None, max_length=120)


class Message(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    author: str
    text: str = Field(max_length=4000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    summary: str
    tone: str
    setting: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    players: List[Player] = Field(default_factory=list)
    log: List[Message] = Field(default_factory=list)


class DMRequest(BaseModel):
    prompt: str
    campaign_state: Optional[str] = None


class DMResponse(BaseModel):
    reply: str
    guidance: str


class DiceRequest(BaseModel):
    expression: str


class DiceResponse(BaseModel):
    expression: str
    rolls: List[int]
    modifier: int
    total: int
