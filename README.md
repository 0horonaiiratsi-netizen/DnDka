# DnDka – AI Dungeon Master

DnDka is a lightweight FastAPI web app that hosts online Dungeons & Dragons sessions with an AI-driven Dungeon Master. It includes campaign creation, player rosters, a chat-style log, an offline-friendly AI DM brain, and a dice roller.

## Features
- **Campaigns**: Create and list adventures with tone, setting, and summary.
- **Players**: Track party members with names, classes, levels, and backstories; remove them when needed.
- **AI DM**: Ask for narration and scene guidance; prompts are stored in the log automatically.
- **Session log**: View, refresh, clear, or download the chronological history of DM responses and prompts.
- **Dice roller**: Resolve checks with expressions like `2d6+1` (tolerates spaces).
- **Campaign management**: Update or delete campaigns via the API.

## Getting started
1. Install dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Launch the server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
3. Open the UI at http://127.0.0.1:8000/.

Data persists to `data/db.json` so you can stop and restart the server without losing your campaign log.

## API overview
- `POST /api/campaigns` – create a campaign (`title`, `summary`, `tone`, `setting`).
- `PUT /api/campaigns/{id}` – update a campaign (any of `title`, `summary`, `tone`, `setting`).
- `DELETE /api/campaigns/{id}` – delete a campaign.
- `GET /api/campaigns` – list campaigns.
- `GET /api/campaigns/{id}` – get a campaign.
- `POST /api/campaigns/{id}/players` – add a player (`name`, `character_name`, `character_class`, `level`, `backstory`).
- `DELETE /api/campaigns/{id}/players/{player_id}` – remove a player.
- `POST /api/campaigns/{id}/dm` – ask the AI DM for a reply (`prompt`, optional `campaign_state`).
- `GET /api/campaigns/{id}/log` – retrieve chronological session messages.
- `DELETE /api/campaigns/{id}/log` – clear the session log.
- `POST /api/rolls` – roll dice (`expression` like `1d20+3`).

## AI behavior
The bundled DM engine is offline-friendly and crafts narrative + guidance based on the campaign tone, setting, and roster. You can replace `DMEngine.generate_response` with calls to your preferred LLM if you have an API key.

## Development notes
- Static frontend files live in `frontend/` and are served automatically by FastAPI.
- The backend persists to `data/db.json`; delete the file to reset state.
- The UI uses vanilla JS with fetch calls to the REST endpoints.
