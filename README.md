# GitHub Cleaner AI Agent

Production-grade AI system that analyzes GitHub profiles, evaluates repository quality, and provides structured recommendations to improve portfolio quality.

## Architecture

- **Layer 1 — Agent**: Conversation, tool calls (Voiceflow / LLM).
- **Layer 2 — Backend API**: FastAPI; orchestration and response shaping.
- **Layer 3 — Scoring Engine**: Deterministic scoring and classification.
- **Layer 4 — Data**: GitHub API client (read-only in MVP).

See [ARCHITECTURE.md](ARCHITECTURE.md) and [docs/MODULES.md](docs/MODULES.md). **Full project work plan (vision & phases 1–7):** [docs/PROJECT_WORK_PLAN.md](docs/PROJECT_WORK_PLAN.md). **Docs map:** [docs/README.md](docs/README.md).

**Phase 1.5 — Voiceflow agent:** how to run the API, ngrok, and connect Voiceflow to `POST /scan` is documented in **[docs/VOICEFLOW_AGENT.md](docs/VOICEFLOW_AGENT.md)** (JSON contract: [docs/AGENT_INTEGRATION.md](docs/AGENT_INTEGRATION.md)).

## MVP (Phase 1)

- Read-only GitHub scan
- Repository scoring (0–100)
- Classification: showcase / cleanup / archive
- Issue detection and suggestions
- No write actions

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

**GitHub token (recommended):** Copy `.env.example` to `.env`, put your real token in `GITHUB_TOKEN=...`, and restart the API. The app loads `.env` automatically. Never commit `.env` (it is in `.gitignore`).

## Run API

From project root (after `pip install -e .`):

```bash
PYTHONPATH=src uvicorn api.main:app --reload
```

Or run from `src`: `uvicorn api.main:app --reload`

POST `/scan` with JSON:

```json
{
  "github_username": "octocat",
  "review_mode": "portfolio",
  "scan_scope": "public"
}
```

## Save scan result to JSON

From project root, with the API running:

```bash
chmod +x scripts/scan-and-save.sh
./scripts/scan-and-save.sh Mjeedbakr
```

Result is saved to **`output/scan_Mjeedbakr.json`**. Use any username:

```bash
./scripts/scan-and-save.sh octocat    # → output/scan_octocat.json
./scripts/scan-and-save.sh YOUR_USER  # → output/scan_YOUR_USER.json
```

Or with curl only (saves formatted JSON):

```bash
curl -s -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"github_username":"Mjeedbakr","review_mode":"portfolio","scan_scope":"public"}' \
  | python3 -c "import sys,json; json.dump(json.load(sys.stdin), open('output/scan_Mjeedbakr.json','w'), indent=2)"
```

## Project Layout

```
src/
  api/          # FastAPI app and routes
  contracts/    # Pydantic input/output and DTOs
  data/         # GitHub API client
  scoring/      # Scoring, classification, issues, suggestions
docs/           # Architecture and module docs
tests/          # Tests
```

## License

MIT
