# Tasks — After structure report (plain English + checklist)

This doc explains **where you are**, **what the new JSON means**, and **what to build next**, in small tasks like `TASKS.md` for Phase 2.

---

## Where you are (simple explanation)

**Before:** The app only used **metadata** from GitHub (stars, description, “does this repo have a README?” from a special API, etc.) to score repos.

**Now:** For **each repo**, the app also calls the **Contents API** once and builds a **`structure_report`**: booleans like “is there a `tests/` folder at root?”, “is there `pyproject.toml`?”, etc. That object is attached to each item in **`repos[]`** in the **`POST /scan`** response.

**Important:** Scoring (`score`, `issues`, `suggestions`) **still mostly ignores** `structure_report`. So the API **shows** richer evidence, but the **numbers and text recommendations** are not fully driven by it yet. The tasks below fix that gap.

---

## What is `structure_report`? (for Voiceflow / clients)

Each repo in the response can look like:

```json
"structure_report": {
  "has_files": {
    "readme": true,
    "license": false,
    "gitignore": true,
    "deps": true,
    "tests": false,
    "docs": false,
    "src_layout": true
  },
  "has_folders": { "tests": false, "docs": false, "src": true },
  "has_files_and_folders": { ... }
}
```

Or **`null`** if that repo’s contents could not be fetched (API error). Your agent can **read** these fields today; the tasks below make the **backend scoring** use them too.

---

## Task 1 — Read `structure_report` inside scoring (issues)

**Goal:** When `structure_report` is present, add **clear, user-facing issues** that match what you already computed from the file tree.

**Examples of rules (you choose the exact wording):**

| If structure says… | You might add issue… |
|--------------------|----------------------|
| `has_files.deps` is false | “No dependency manifest at repo root (e.g. requirements.txt, pyproject.toml, package.json)” |
| `has_folders.tests` is false | “No `tests/` folder at repository root” |
| `has_folders.docs` is false | “No `docs/` folder at repository root” |
| `has_files.src_layout` is false | “No `src/` layout at root (optional but common for libraries)” |

**Where to change code:**  
`src/scoring/issues.py` — extend `detect_issues(repo: RepoDTO)` to read `repo.structure_report` when it is not `None`. If `None`, keep current behavior only (metadata-based).

**Why:** Users and the agent see **consistent** messages: the JSON evidence and the **issues** list tell the same story.

**How to verify:** Add or extend tests in `tests/test_scoring.py` with a `RepoDTO` that has `structure_report` set and assert the new issue strings appear.

---

## Task 2 — Feed structure into suggestions

**Goal:** When `structure_report` flags a gap, add a **matching suggestion** (what to do next).

**Where:** `src/scoring/suggestions.py` — in `suggest_improvements`, branch on `repo.structure_report` (when not `None`) in addition to `classification`.

**Why:** “Issues” say what’s wrong; “suggestions” say how to improve. Both should align with structure when data exists.

**How to verify:** Tests in `test_scoring.py` with mocked `structure_report`.

---

## Task 3 — Optionally adjust the numeric score

**Goal:** Small **bonus or penalty** in `score_repo` based on structure (e.g. + points if `tests/` exists, small penalty if no deps file when language suggests a package).

**Where:** `src/scoring/scorer.py` — read `repo.structure_report` when not `None`. Keep changes **small** so scores stay understandable.

**Why:** Today the score might say “good” while structure says “no tests folder”; tightening the score makes the product feel honest.

**Caution:** If `structure_report` is `None`, do **not** change score based on structure (you have no evidence).

**How to verify:** Golden tests: same metadata, different `structure_report` → slightly different score.

---

## Task 4 — (Optional) Simplify the redundant report shape

**Goal:** `structure_report` currently has **`has_files`**, **`has_folders`**, and **`has_files_and_folders`** with overlap. Pick **one** canonical block (e.g. only `has_files` + `has_folders`) and deprecate or remove the duplicate in a later version, **or** document which block agents should read.

**Where:** `src/data/repo_inspector.py` + any client docs.

**Why:** Less confusion for you and for Voiceflow mappers.

---

## Task 5 — Rate limits and large profiles (later, but plan)

**Goal:** Many repos ⇒ many Contents API calls. Decide a policy:

- Cap inspected repos (e.g. first 30), or  
- Skip inspection when repo count > N, or  
- Add simple caching (same owner+name in one scan).

**Where:** `src/api/routes/scan.py` (loop over repos) or a small helper.

**Why:** Avoid **502** / rate limit on big GitHub accounts without a token.

---

## Task 6 — Score breakdown + evidence (bigger step)

**Goal:** Instead of one `score` number, expose **sub-scores** (e.g. documentation / structure / maintenance) and short **reasons** (see `docs/EVALUATION_AND_NEXT_STEPS.md`).

**Follow the step-by-step checklist:** **`TASKS_SCORE_BREAKDOWN.md`** (contracts → `scorer.py` → aggregator → tests → docs).

**Why:** Makes the product easier to explain: “why is this repo 62?”

**Do this after** Tasks 1–3 so you already use `structure_report` in one place before splitting the score.

---

## Task 7 — Repo-level “cleanup plan” (even bigger step)

**Goal:** Per repo, add fields like **blocking issues**, **quick wins**, **suggested order** (all deterministic, no LLM required at first).

**Where:** New optional fields on `RepoResult` or a nested object; built in aggregator or a new `scoring/remediation.py`.

**Why:** Moves from “diagnosis only” to “what do I do Monday morning?”

---

## Suggested order (summary)

| Order | Task | One-line purpose |
|-------|------|------------------|
| 1 | Issues from `structure_report` | Same story in JSON + issue list |
| 2 | Suggestions from structure | Actionable text aligned with evidence |
| 3 | Small score tweaks from structure | Score matches what you see in the report |
| 4 | (Optional) Flatten `structure_report` shape | Less duplication |
| 5 | (Later) Rate limit / cap strategy | Big profiles stay reliable |
| 6 | (Later) Score breakdown + evidence | Explain the number |
| 7 | (Later) Cleanup plan object | Actionable roadmap per repo |

---

## Related docs

- **`docs/TASKS.md`** — Original Phase 2 inspector tasks (mostly done).  
- **`docs/EVALUATION_AND_NEXT_STEPS.md`** — Priorities 2–3 in more detail.  
- **`docs/AGENT_INTEGRATION.md`** — `structure_report` in the API contract.
