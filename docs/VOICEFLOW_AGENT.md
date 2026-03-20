# Phase 1.5 — Voiceflow agent (run + connect)

This is the **documented way** to run the backend and connect a **Voiceflow** (or similar) agent. Prefer **`POST /scan/voiceflow`** for a **flat** JSON (no nested `summary` / `repos` / arrays) — see **[AGENT_INTEGRATION.md](AGENT_INTEGRATION.md)**. Use **`POST /scan`** when you need the full payload.

---

## Prerequisites

- Project installed: `pip install -e .` or `uv pip install -e .` from the repo root.
- **`.env`** at the project root with a valid GitHub token (recommended to avoid rate limits and `401 Bad credentials`):

  ```bash
  cp .env.example .env
  # Edit .env: GITHUB_TOKEN=ghp_your_real_token
  ```

  See the main [README](../README.md) — the app loads `.env` on startup via `python-dotenv`.

---

## 1. Run the API (local)

From the **project root** (`github_cleaner/`):

```bash
source .venv/bin/activate
PYTHONPATH=src uvicorn api.main:app --reload
```

Default URL: **`http://127.0.0.1:8000`**. Health check: `GET http://localhost:8000/health` → `{"status":"ok"}`.

---

## 2. Expose localhost for cloud agents (ngrok)

Voiceflow runs in the cloud; it cannot call `http://localhost:8000` on your machine unless you tunnel.

1. Install [ngrok](https://ngrok.com/) and add your [authtoken](https://dashboard.ngrok.com/get-started/your-authtoken) once: `ngrok config add-authtoken …`
2. **Use the same port as uvicorn** (default **8000**):

   ```bash
   ngrok http 8000
   ```

3. Copy the **Forwarding** HTTPS URL from the ngrok terminal (e.g. `https://rex-thatchy-ciliately.ngrok-free.dev`). Free tier may use **`.ngrok-free.dev`** — use the exact host ngrok prints.

4. Leave **both** terminals open: one for uvicorn, one for ngrok.

**Verify the tunnel** (optional):

```bash
curl -H "ngrok-skip-browser-warning: true" https://YOUR_NGROK_HOST/health
```

Or run `./scripts/check-ngrok.sh` while uvicorn and ngrok are up — it prints the live public URL and checks `/health`.

---

## 3. Configure Voiceflow (API block)

**Where in Voiceflow:** open your agent project → find the **canvas** (the diagram with blocks) → click the block that **calls your backend** (often labeled **API**, **Integrations**, or shows `POST` + a URL). Settings for that block open on the **right** — that’s where you paste the URL and body.

### Option A — Flat JSON (easiest for Voiceflow): `POST /scan/voiceflow`

| Setting | Value |
|--------|--------|
| **Method** | `POST` |
| **URL** | `https://<your-ngrok-host>/scan/voiceflow` (full URL; no space; path is `/scan/voiceflow`) |
| **Headers** | `Content-Type: application/json` |
| | `ngrok-skip-browser-warning: true` (avoids ngrok’s HTML interstitial on API calls) |

**Body (JSON),** e.g. (replace the username part with your Voiceflow variable if the editor uses `{{variable}}` or another syntax):

```json
{
  "github_username": "octocat",
  "review_mode": "portfolio",
  "scan_scope": "public"
}
```

**Capture response (map to variables):** the JSON has **no** nested `summary` — use top-level keys only, e.g. `total_repos`, `showcase_ready`, `needs_cleanup`, `archive_candidates`, `top_issue_1`, `top_issue_2`, `top_issue_3`, `recommended_next_step`, `archive_repo_1`, `archive_repo_2`, `cleanup_repo_1`, `cleanup_repo_2`. See **[AGENT_INTEGRATION.md](AGENT_INTEGRATION.md)** for the full list and error codes (**400 / 404 / 502**).

**Remove** any old mappings like `summary.total_repos` or `top_issues.0` — those only match **`/scan`**, not **`/scan/voiceflow`**.

**Example speak / text block** (variable names must match what you saved in Capture):

```text
GitHub scan results

You have {total_repos} public repositories.

- Showcase-ready: {showcase_ready}
- Need cleanup: {needs_cleanup}
- Archive candidates: {archive_candidates}

Most common issues:
1. {top_issue_1}
2. {top_issue_2}
3. {top_issue_3}

Repos to prioritize for cleanup: {cleanup_repo_1}, {cleanup_repo_2}
Repos to consider archiving: {archive_repo_1}, {archive_repo_2}

Recommended next step: {recommended_next_step}
```

### Option B — Full JSON: `POST /scan`

Same as above but URL ends with **`/scan`**. Map nested paths, e.g. `summary.total_repos`, `top_issues[0]`, `repos`, etc.

---

## 4. Troubleshooting (short)

| Symptom | Likely cause |
|--------|----------------|
| ngrok “offline” / ERR_NGROK_3200 | ngrok not running, or wrong hostname (e.g. `.app` vs `.dev`). |
| ERR_NGROK_8012 upstream `localhost:8001` | ngrok points to **8001** but API is on **8000** — run `ngrok http 8000`. |
| `502` + GitHub “Bad credentials” | Invalid `GITHUB_TOKEN` in `.env` or placeholder left in place. |
| `502` + rate limit | Set a real token in `.env`, or wait and retry. |
| Voiceflow “API tool failed”, curl works | Increase API block timeout; scan can take many seconds for large profiles. |

---

## 5. Related docs

- **[AGENT_INTEGRATION.md](AGENT_INTEGRATION.md)** — `POST /scan` request/response JSON, errors, agent behavior.
- **[PHASE_1.5_AGENT_PLAN.md](PHASE_1.5_AGENT_PLAN.md)** — Phase 1.5 goals and checklist.
- **[SETUP_UV.md](SETUP_UV.md)** — uv / ngrok notes.

---

## Phase 1.5 success (this setup)

With the API running, ngrok forwarding to **8000**, and Voiceflow calling `POST https://<ngrok-host>/scan/voiceflow` (flat) or `…/scan` (full) with the headers above, you have **one documented way** to run the agent against the running backend, as required by the Phase 1.5 plan.
