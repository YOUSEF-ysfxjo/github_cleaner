# Tasks — Priority 2: Score breakdown + evidence

Step-by-step work to expose **why** each repo has its **overall `score`**, aligned with `**docs/EVALUATION_AND_NEXT_STEPS.md**` and your **PROJECT_WORK_PLAN** (stronger “quality evaluation” without LLM yet).

---

## Goal (plain English)

Today each repo returns one number `**score`\** (0–100). Users and agents ask: *Why 62?\*

**After this work**, each repo also returns:

- `**score_breakdown*`\* — sub-scores **0–100** for a few **dimensions** that match how you already compute the total (documentation, activity, structure, naming, portfolio).
- `**score_evidence`** (or similar) — short **human-readable bullets\*\* that explain the biggest drivers (e.g. “Documentation: strong README and license”, “Activity: last commit over 12 months ago”, “Structure penalty: −12 from root listing (capped)”).

The **top-level `score`** stays the **single source of truth** for classification; breakdown + evidence are **explanatory**, not a second scoring system.

---

## Design choices (decide once, then implement)

1. **Dimensions** — Use the **same five** pillars already in `scorer.py`:
   `documentation`, `activity`, `structure`, `naming`, `portfolio`
   (names can be snake_case in JSON).
2. **Structure penalties** — Today penalties are applied **after** the weighted sum. For transparency, either:

- **Option A (recommended):** In the API, show **raw dimension scores** (0–100 each), then a field `**structure_penalty_applied`** (number, 0–25) and a line in `**score_evidence\*_` like _“Overall score reduced by up to 25 points from root structure checklist (see issues).”\*
- **Option B:** Bake penalty only into a separate pseudo-dimension `structure_from_listing` — more work and duplicates `structure_report`.

3. **Evidence strings** — Keep them **deterministic** (if/else from `RepoDTO` + breakdown values), not LLM-generated in this phase.

---

## Task 1 — Add API types (`contracts/scan_response.py`)

**What:** New Pydantic model, e.g. `**ScoreBreakdown*`\*, with five float fields **0–100**:

- `documentation`
- `activity`
- `structure`
- `naming`
- `portfolio`

Optional (recommended):

- `structure_penalty_applied: float` — **0** if no report or no penalty; else the **actual** penalty before cap (or the **applied** amount after cap — pick one and document it).

**On `RepoResult`, add:**

- `score_breakdown: ScoreBreakdown` (or optional with defaults if you want backward compat — prefer **required** once shipped).
- `score_evidence: list[str]` — short strings, max ~5–8 items per repo.

**Why:** Stable JSON contract for Voiceflow and other clients.

**Verify:** Model validates; OpenAPI shows new fields under `RepoResult`.

---

## Task 2 — Centralize scoring in `scorer.py`

**What:** Add a function, e.g. `**score_repo_with_breakdown(repo: RepoDTO) -> tuple[float, ScoreBreakdown, float, list[str]]`**
(or return a small `**dataclass`/`TypedDict\*\*` internally, then map to Pydantic in the aggregator).

It should:

1. Call the existing `**_score_documentation**`, `**_score_activity**`, `**_score_structure**`, `**_score_naming**`, `**_score_portfolio_value**` (do **not** duplicate formulas).
2. Build `**ScoreBreakdown`\*\* (or dict) from those five numbers.
3. Compute **weighted total** = same formula as today’s `**score_repo`\*\* (before structure penalty).
4. Compute **structure penalty** (same logic as now: sum of per-flag penalties, **cap 25**).
5. **Final score** = `clamp(weighted_total - penalty, 0, 100)` — must **match** current `**score_repo`\*\* behavior for every `RepoDTO` (regression tests).
6. Build `**score_evidence**`:

- One line per **weak** dimension (e.g. activity < 40 → “Activity: repository looks inactive (last commit > 12 months).”).
- One line for **strong** dimensions if useful (optional, keep list short).
- If `**structure_penalty_applied` > 0**, add a single evidence line summarizing the penalty (refer to `**structure_report`\*\* / issues for detail).

**Refactor:** Make `**score_repo(repo)`** call `**score_repo_with_breakdown**` and return only the **final float** so **one\*\* implementation exists.

**Where:** `src/scoring/scorer.py` only for math; evidence helpers can live in the same file or `**scoring/evidence.py`\*\* if it grows.

**Verify:** Unit tests: same repo → `**score_repo`\*\* == first element of breakdown result.

---

## Task 3 — Wire aggregator (`scoring/aggregator.py`)

**What:** In `**build_scan_result`\*\*, for each repo:

- Call `**score_repo_with_breakdown**` (or your chosen name) **once**.
- Pass `**score`**, `**score_breakdown**`, `**score_evidence**`into`**RepoResult\*\*`.
- Keep `**classify_repo(score, repo)**` using the **same final `score`**.

**Why:** No double scoring per repo.

**Verify:** Integration-style test: `**build_scan_result`\*\* returns repos with populated breakdown + evidence.

---

## Task 4 — Tests (`tests/test_scoring.py` + optional `tests/test_api_scan.py`)

**What:**

- `**test_score_repo_matches_breakdown_final`\*\* — `score_repo(r) == score_repo_with_breakdown(r)[0]` (or `.final_score`).
- `**test_score_breakdown_ranges**` — each dimension in **0–100**.
- `**test_score_evidence_not_empty_for_weak_repo`\*\* — e.g. empty repo or no README → at least one evidence string (adjust to your rules).
- Optionally extend `**test_scan_success**` in `**test_api_scan.py**` to assert JSON contains `**score_breakdown**` keys (after you implement — mock can stay as today for `inspect_repo`).

**Why:** Prevents drift between `score_repo` and breakdown path.

---

## Task 5 — Documentation

**What:**

- `**docs/AGENT_INTEGRATION.md`** — Document `**score_breakdown**`and`**score_evidence**`under the example`**repos[]**`item; state that`**score**`is final after structure penalty; mention how`**structure_penalty_applied**`relates to`**structure_report\*\*` / issues.
- `**docs/BUILD_SUMMARY.md**` (optional row) — “Score breakdown + evidence on `RepoResult`.”

**Why:** Agents and future you know how to explain scores to users.

---

## Task 6 — Voiceflow / client mapping (no code in repo)

**What:** In Voiceflow (or your client), map:

- `repos[].score_breakdown.documentation` (etc.) to variables.
- `repos[].score_evidence` → join with newlines or bullets in a single message block.

**Why:** Product UX; lives outside this repository.

---

## Suggested implementation order

| Step | Task                                                | File(s)                                             |
| ---- | --------------------------------------------------- | --------------------------------------------------- |
| 1    | `ScoreBreakdown` + `RepoResult` fields              | `contracts/scan_response.py`                        |
| 2    | `score_repo_with_breakdown` + refactor `score_repo` | `scoring/scorer.py`                                 |
| 3    | `build_scan_result` wiring                          | `scoring/aggregator.py`                             |
| 4    | Tests                                               | `tests/test_scoring.py`, `tests/test_api_scan.py`   |
| 5    | Docs                                                | `AGENT_INTEGRATION.md`, optional `BUILD_SUMMARY.md` |

---

## After this phase (reminder)

Next in the plan: **remediation / cleanup plan** per repo (Priority 3), then **LLM layer** (Phase 4) **after** breakdown is stable.

## Related docs

- `**EVALUATION_AND_NEXT_STEPS.md`\*\* — Priority 2 context.
- `**TASKS_STRUCTURE_TO_SCORING.md**` — Structure → issues/suggestions/penalties (done).
- `**PROJECT_WORK_PLAN.md**` — Phase 3 “quality evaluation” direction.
