# Phase 1.5 — Agent Integration: Plan and Next Steps

This document defines the official next phase: a **minimal agent** that collects inputs, calls the backend, explains the scan result, and suggests follow-ups. No complex LLM logic — the agent is a thin layer on top of `POST /scan`.

---

## Current status (repo vs Voiceflow)

| Piece | Where it lives | Status |
| ----- | -------------- | ------ |
| Backend `POST /scan` + `POST /scan/voiceflow` | This repo | **Done** |
| Deploy API (e.g. Render) | Host env + `docs/DEPLOY_RENDER.md` | **Done** (example: `github-cleaner-api.onrender.com`) |
| JSON contract & errors | `docs/AGENT_INTEGRATION.md` | **Done** |
| Voiceflow runbook (Render + ngrok dev) | `docs/VOICEFLOW_AGENT.md` | **Done** |
| README pointer to agent + deploy docs | `README.md` | **Done** |
| **Voiceflow project** (API → `/scan/voiceflow`, capture, copy, **Publish**) | Voiceflow (cloud), not git | **Done** for core path; optional: 404/502 branches |
| **Option B** — CLI / Streamlit client | Optional; could live in this repo | **Not** added unless you build it |

**Navigation hub for all docs:** [`docs/README.md`](README.md).

---

## Goal

- **Phase 1.5**: Agent Integration
- **Scope**: One simple agent that:
  1. Collects 3 inputs from the user.
  2. Calls `POST /scan` or **`POST /scan/voiceflow`** (flat fields for Voiceflow).
  3. Reads the JSON response (full `ScanResponse` or flat voiceflow shape).
  4. Explains the result in plain language.
  5. Suggests a next step and offers follow-up options.

The backend (FastAPI + scoring + GitHub data) is **unchanged**. The agent only orchestrates the conversation and the single API call.

---

## What the Agent Must Do

### 1. Input collection

Collect exactly three values (from chat, form, or config):

| Input               | Allowed values                    | Default     |
| ------------------- | --------------------------------- | ----------- |
| **GitHub username** | Non-empty string (e.g. `octocat`) | Required    |
| **Review mode**     | `portfolio` \| `cleanup`          | `portfolio` |
| **Scan scope**      | `public` \| `all`                 | `public`    |

- Validate: username not empty; if scope is `all`, the user (or system) must have `GITHUB_TOKEN` set for the backend.
- No extra inputs in v1 (e.g. no repo filters, no custom thresholds).

### 2. Tool call

- **Single action**: Send one request to the backend.
- **Endpoint**: `POST {BASE_URL}/scan`
- **Body** (JSON):
  ```json
  {
    "github_username": "<collected>",
    "review_mode": "<collected>",
    "scan_scope": "<collected>"
  }
  ```
- **Handling**:
  - **200**: Use the response body as `ScanResponse` for explanation.
  - **400**: e.g. `scan_scope: "all"` without token — tell user to use `public` or set token.
  - **404**: User not found — tell user to check the username.
  - **502**: GitHub/network error — tell user to retry or check token/network.
  - **Timeout / Voiceflow**: Set a **long API timeout** (90–120s) and a **failure path** with user-friendly copy — see **`VOICEFLOW_AGENT.md` §4**.

### 3. Response explanation

Present the following from `ScanResponse` in clear, short sentences (no raw JSON to the user):

| Field                        | What to show                                                           |
| ---------------------------- | ---------------------------------------------------------------------- |
| `summary.total_repos`        | Total number of repositories scanned.                                  |
| `summary.showcase_ready`     | How many are “showcase” (strong).                                      |
| `summary.needs_cleanup`      | How many need cleanup.                                                 |
| `summary.archive_candidates` | How many are archive candidates.                                       |
| `top_issues`                 | List the most common issues (e.g. “Missing README”, “No description”). |
| `recommended_next_step`      | Show this as the main suggested next step.                             |

Optional for v1: one line per repo (name + classification + score) or only a count; keep the first version short.

### 4. Follow-up prompt

After explaining, the agent must **suggest a next step** and offer **at least one** of these (or similar) follow-ups:

- _“Do you want me to list the archive candidates?”_
- _“Do you want the top 3 repos to fix first?”_
- _“Do you want a portfolio-first plan?”_

The user can answer yes/no or choose an option. In Phase 1.5, the agent does **not** perform a second API call for these; it only uses the same `ScanResponse` (e.g. filter `repos` by `classification` or score) to answer. No new endpoints required.

---

## Implementation Options (Pick One for v1)

### Option A — Voiceflow (or similar no-code agent)

- **Steps**:
  1. Create a project in Voiceflow (or equivalent).
  2. Add a block to collect: GitHub username (required), review mode (default `portfolio`), scan scope (default `public`).
  3. Add an API/Integration block: `POST {BACKEND_URL}/scan` with body from collected variables.
  4. Map response to variables (e.g. `summary`, `top_issues`, `recommended_next_step`).
  5. Add a response block that:
     - Explains total repos, showcase/cleanup/archive counts, top issues, recommended next step.
     - Asks one of the follow-up questions above.
  6. (Optional) Add a simple intent/button flow for “list archive candidates” / “top 3 to fix” / “portfolio plan” that uses the same stored response to reply (no new API call).
- **Deliverable**: Link to the Voiceflow project or export + short doc: “How to run the agent (Voiceflow) and connect it to the backend.”

### Option B — Simple script (e.g. Python CLI or minimal web form)

- **Steps**:
  1. One script or tiny app (e.g. Flask/Streamlit or `input()` in Python).
  2. Collect the 3 inputs (prompts or form fields).
  3. Call `POST /scan` with `httpx` or `requests`.
  4. Parse JSON; print or render: total repos, showcase/cleanup/archive, top issues, recommended next step.
  5. Print one of the follow-up questions (e.g. “Do you want the top 3 repos to fix first?”).
  6. (Optional) If user says “yes”, filter `response["repos"]` by classification/score and print the list (still no new API call).
- **Deliverable**: Single file or small app + one-line run instructions (e.g. “Start backend, then run `python agent_cli.py`”).

### Recommended for “next step”

- **Prefer Option A** if the goal is to later plug in a real conversational UI (Voiceflow, Slack, etc.) and reuse the same backend.
- **Prefer Option B** if the goal is to validate the flow quickly with minimal tooling and no external platform.

---

## Concrete Plan (Checklist)

1. **Decide**
   - [ ] Choose: Voiceflow (or similar) **or** simple script/app.

2. **Backend**
   - [ ] Ensure backend is running: `PYTHONPATH=src uvicorn api.main:app` and `POST /scan` returns `ScanResponse` (already done).
   - [ ] Document `BASE_URL` (e.g. `http://localhost:8000` for local).

3. **Inputs**
   - [ ] Implement collection for: GitHub username, review mode, scan scope (with defaults above).
   - [ ] If scope is `all`, document or warn that `GITHUB_TOKEN` must be set on the server.

4. **Tool call**
   - [ ] Implement `POST {BASE_URL}/scan` with the JSON body.
   - [ ] Handle 200, 400, 404, 502 and map to user-facing messages.

5. **Explanation**
   - [ ] From `ScanResponse`: show total repos, showcase_ready, needs_cleanup, archive_candidates, top_issues, recommended_next_step in plain language.

6. **Follow-up**
   - [ ] After the explanation, show at least one follow-up line:
         “Do you want me to review the archive candidates?” / “Do you want the top 3 repos to fix first?” / “Do you want a portfolio-first plan?”
   - [ ] (Optional) If user accepts, use `repos` from the same response to list archive candidates or top 3 to fix — no second `/scan` call.

7. **Document**
   - [ ] Add a short “Phase 1.5 Agent” section to the main README or docs: how to run the agent and connect it to `/scan`.

---

## What Stays Out of Phase 1.5

- No new backend endpoints.
- No database or scan history.
- No write actions (archive, rename, etc.).
- No “conversation memory” beyond the current scan result (optional later).
- No custom scoring or config from the agent; backend logic remains as is.

---

## Success Criteria

Phase 1.5 is done when:

1. User can give **GitHub username** (+ optional review mode and scope).
2. Agent calls **POST /scan** and receives **ScanResponse**.
3. Agent **explains** summary counts, top issues, and recommended next step.
4. Agent **suggests** at least one follow-up (e.g. “review archive candidates?”, “top 3 to fix?”, “portfolio plan?”).
5. There is **one** documented way to run the agent (Voiceflow project or script/app) against the running backend.

This file is the single reference for **what to do next** and **how to implement** Phase 1.5 — Agent Integration.
