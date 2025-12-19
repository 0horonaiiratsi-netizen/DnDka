from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .ai_engine import DMEngine
from .dice import DiceError, roll
from .models import (
    Campaign,
    CampaignCreate,
    DMRequest,
    DiceRequest,
    DiceResponse,
    Message,
    PlayerCreate,
)
from .state import StateStore

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "db.json"
FRONTEND_DIR = BASE_DIR / "frontend"

store = StateStore(DB_PATH)
dm = DMEngine()

app = FastAPI(title="DnDka Online", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/api/campaigns", response_model=List[Campaign])
def list_campaigns():
    return store.list_campaigns()


@app.post("/api/campaigns", response_model=Campaign, status_code=201)
def create_campaign(payload: CampaignCreate):
    return store.add_campaign(payload)


@app.get("/api/campaigns/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: str):
    campaign = store.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@app.get("/api/campaigns/{campaign_id}/log", response_model=List[Message])
def get_log(campaign_id: str):
    campaign = store.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign.log


@app.post("/api/campaigns/{campaign_id}/players", response_model=Campaign, status_code=201)
def add_player(campaign_id: str, payload: PlayerCreate):
    try:
        return store.add_player(campaign_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Campaign not found")


@app.post("/api/campaigns/{campaign_id}/messages", response_model=Campaign, status_code=201)
def add_message(campaign_id: str, message: Message):
    try:
        return store.add_message(campaign_id, message)
    except KeyError:
        raise HTTPException(status_code=404, detail="Campaign not found")


@app.post("/api/campaigns/{campaign_id}/dm")
def dm_response(campaign_id: str, request: DMRequest):
    campaign = store.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    prompt_message = Message(author="Party", text=request.prompt)
    store.add_message(campaign_id, prompt_message)
    dm_message = dm.generate_dm_entry(campaign, request)
    store.add_message(campaign_id, dm_message)
    response = dm.generate_response(campaign, request)
    return response


@app.post("/api/rolls", response_model=DiceResponse)
def roll_dice(payload: DiceRequest):
    try:
        result = roll(payload.expression)
        return DiceResponse(
            expression=payload.expression,
            rolls=result.rolls,
            modifier=result.modifier,
            total=result.total,
        )
    except DiceError as err:
        raise HTTPException(status_code=400, detail=str(err))


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
