# Phase 2 — README & structure depth (your implementation)

**No code was added for behavior** — only stubs under `src/phase2/` and this checklist. You implement tasks in the order below.

## Files map

| File | Role |
| ---- | ---- |
| **`docs/TASKS_PHASE2.md`** (this file) | Master order + links |
| **`src/phase2/readme_client.py`** | Fetch README text from GitHub API |
| **`src/phase2/readme_signals.py`** | Rule-based signals from README text |
| **`src/phase2/scan_integration.py`** | Where/how to plug into `RepoDTO`, issues, scorer, scan route |
| **`src/phase2/__init__.py`** | Package marker |

## Suggested order

1. Read module docstrings in **`readme_client.py`** → implement tasks there.
2. Read **`readme_signals.py`** → implement (can unit-test with fake strings without network).
3. Read **`scan_integration.py`** → wire into existing pipeline (`repo_fetcher`, `issues`, `aggregator`, contracts).

## Constraints (from MVP)

- Read-only; no writes to GitHub.
- Respect **rate limits**: cap how many repos get README fetch per scan (similar idea to `MAX_REPOS_TO_INSPECT`).
- Truncate stored excerpt (e.g. max chars) — do not return full megabyte READMEs in JSON by default.

## When done

- Update **`docs/BUILD_SUMMARY.md`** and **`docs/AGENT_INTEGRATION.md`** if response shape changes.
- Add **`tests/test_phase2_*.py`** (or extend existing tests).
