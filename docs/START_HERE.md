# Start Here — How the Codebase Fits Together

Use this as a reading map: **where to start** and **how data flows** from request to response.

---

## 1. Entry point: the API

**Start with:** `src/api/main.py`

- This is the FastAPI app. It mounts the scan router and exposes `GET /health` and `POST /scan`.
- The only real endpoint you use is **POST /scan**.

---

## 2. What happens when you call POST /scan

**Read next:** `src/api/routes/scan.py`

This file is the **orchestrator**. It:

1. Receives the request body and validates it (Pydantic turns it into a `ScanRequest`).
2. Calls the **data layer** to fetch repos from GitHub.
3. Passes the list of repos to the **scoring** layer.
4. Returns a `ScanResponse` (summary, top issues, per-repo results, recommended next step).

So the flow is:

```
Request (JSON) → scan.py → data layer (fetch repos) → scoring layer (score, classify, suggest) → Response (JSON)
```

---

## 3. Input and output shapes (contracts)

**Read:** `src/contracts/`

- **scan_request.py** — What the client sends: `github_username`, `review_mode`, `scan_scope`.
- **scan_response.py** — What the API returns: `Summary`, `RepoResult`, `ScanResponse`.
- **repo_dto.py** — The **internal** shape of one repo (what we get from GitHub and pass to scoring). Not the same as the public response.

Contracts have **no business logic**. They only define data shapes and validation.

---

## 4. Data layer (GitHub)

**Read:** `src/data/repo_fetcher.py` then `src/data/github_client.py`

- **github_client.py** — Talks to GitHub REST API: list user repos (paginated), check if a repo has a README. **Read-only.**
- **repo_fetcher.py** — Uses the client to fetch all repos for a username, maps each raw GitHub object to a **RepoDTO**, and returns `list[RepoDTO]`.

So: **scan.py** calls `fetch_repos_for_user(...)` and gets back a list of `RepoDTO`s. No scoring happens here.

---

## 5. Scoring engine (all logic lives here)

**Read in this order:**

1. **src/scoring/scorer.py** — Computes a 0–100 score for one repo (documentation, activity, structure, naming, portfolio value). **Deterministic.**
2. **src/scoring/classifier.py** — Maps score + repo (e.g. empty?) to `showcase` | `cleanup` | `archive`.
3. **src/scoring/issues.py** — Detects issues per repo (e.g. missing README, no description, inactive >12 months).
4. **src/scoring/suggestions.py** — Suggests improvements per repo (e.g. add README, add description).
5. **src/scoring/aggregator.py** — **Ties it all together**: for each repo it calls scorer, classifier, issues, suggestions; then builds the **Summary** (counts), **top_issues** (most common issues), and **recommended_next_step**.

So: **scan.py** calls `build_scan_result(repos)` and gets back a full `ScanResponse`. The aggregator is the only place that uses scorer, classifier, issues, and suggestions together.

---

## 6. Dependency injection

**Read:** `src/api/dependencies.py`

- Provides `get_github_client()`. The scan route uses this so the GitHub client can be swapped in tests (or for different configs) without changing the route code.

---

## Visual flow (same as above, in one picture)

```
┌─────────────────────────────────────────────────────────────────┐
│  Client (e.g. Agent)                                            │
│  POST /scan  { "github_username": "octocat", ... }              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  api/routes/scan.py                                              │
│  1. Validate body → ScanRequest (contracts)                       │
│  2. fetch_repos_for_user(...)  ← data layer                      │
│  3. build_scan_result(repos)  ← scoring layer                    │
│  4. Return ScanResponse (contracts)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
┌─────────────────────┐               ┌─────────────────────────────┐
│  data/repo_fetcher  │               │  scoring/aggregator.py      │
│  + github_client    │               │  For each repo:             │
│  → list[RepoDTO]   │               │  - score_repo()              │
└─────────────────────┘               │  - classify_repo()           │
                                      │  - detect_issues()           │
                                      │  - suggest_improvements()   │
                                      │  → Summary, top_issues,     │
                                      │    recommended_next_step   │
                                      └─────────────────────────────┘
```

---

## Where to start reading (short list)

| Order | File | Why |
|-------|------|-----|
| 1 | `src/api/main.py` | Entry point of the app |
| 2 | `src/api/routes/scan.py` | Where the scan flow is orchestrated |
| 3 | `src/contracts/scan_request.py` + `scan_response.py` | Input/output contract |
| 4 | `src/contracts/repo_dto.py` | Shape of one repo between data and scoring |
| 5 | `src/data/repo_fetcher.py` | How we get repos from GitHub |
| 6 | `src/data/github_client.py` | Low-level GitHub API calls |
| 7 | `src/scoring/aggregator.py` | How scoring is wired (you have this open) |
| 8 | `src/scoring/scorer.py` | How the 0–100 score is computed |
| 9 | `src/scoring/classifier.py` | showcase / cleanup / archive |
| 10 | `src/scoring/issues.py` + `suggestions.py` | Issue detection and suggestions |

If you only read **two files** to get the big picture: **`api/routes/scan.py`** (orchestration) and **`scoring/aggregator.py`** (how the result is built).
