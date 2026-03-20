# Evaluation & Next Steps — What to Do Now

This document summarizes where the project stands versus the [PROJECT_WORK_PLAN](PROJECT_WORK_PLAN.md), the main gaps, and a **prioritized action list** in English only.

---

## 1. Overall Verdict

- **Current state:** Strong **Phase 1 MVP** backend + agent integration foundation; not yet the full system described in the Work Plan.
- **Strengths:** Solid base, clear architecture, good docs, real implementation (API, scoring, Voiceflow path), read-only-by-design.
- **Gap:** Today = repository audit from **metadata** + scoring + reporting + Voiceflow hookup. Not yet = full repository **content** inspection + deep AI review + safe auto-fix execution.

---

## 2. Phase-by-Phase Status vs Work Plan

| Phase | Work plan goal | Status | Notes |
| ----- | ----------------- | ------ | ----- |
| **1 — Repository Discovery** | Connect to GitHub API, fetch metadata, store list, extract attributes | **Done** | GitHubClient, fetch_repos_for_user, RepoDTO, POST /scan, summary, classification, token, public/all. |
| **2 — Repository Structure Analysis** | Clone repos, scan directory structure, detect important files (README, LICENSE, deps, docs/) | **Not done** | Current analysis is metadata-based (e.g. README existence via API). No cloning, no file-tree or content inspection. ~10–20% if only surface file checks exist. |
| **3 — Quality Evaluation Engine** | Multi-dimensional scoring (documentation, structure, maintenance, security) | **MVP done, ~60%** | Single 0–100 score, classification, issues, suggestions exist. Missing: dimension breakdown (doc/structure/maintenance/safety), evidence per signal, richer heuristics. |
| **4 — AI Review Layer** | LLM uses metadata + structure + quality → intelligent, contextual recommendations | **Not implemented** | Current behavior is rule-based/templated (e.g. “add license”, “add README”). No LLM reading README or project type, no tailored suggestions. |
| **5 — Cleanup Recommendation Engine** | Classify repos (Public Ready, Needs Cleanup, Archive, etc.) + remediation plan per class | **Partially done, ~65%** | Showcase / cleanup / archive classification works. Missing: finer categories, per-repo action plans, priority and effort. |
| **6 — Optional Auto-Fix Tools** | Generate README/.gitignore/LICENSE, remove temp files; all with user approval | **Intentionally deferred** | Read-only MVP; no write endpoints. Correct for current stage. |
| **7 — Report Generation** | Full account audit, totals by category, score/issues per repo | **Done for MVP** | Summary, top_issues, repos list, recommended_next_step, save-to-JSON. Possible later: markdown/PDF/HTML export, dashboard, scan history. |

---

## 3. Main Gaps (What’s Missing)

1. **Analysis is still shallow**  
   Audit is metadata-first. Need move from **profile audit** to **repository content audit** (files, structure, README content, risk signals).

2. **No clear evidence per judgment**  
   For each classification/score, users need: why, which signals, which rules. Add factors, penalties, evidence snippets.

3. **Single aggregate score can be misleading**  
   One number hides dimensions. Add sub-scores (e.g. Documentation, Structure, Maintenance, Safety, Portfolio fit) then total.

4. **No real remediation engine**  
   Suggestions exist but not **action plans**: quick wins vs blockers, order of work, estimated effort, publish status per repo.

5. **Agent is not interactive enough**  
   Flow is: username → /scan → summary. Missing: “Which 3 repos to fix first?”, “Why is this not showcase-ready?”, “Cleanup plan for repo X”, “Only security issues”, etc.

6. **No persistence / scan history**  
   Each run is one-off. Later: scan history, diff between scans, progress and readiness trend over time.

---

## 4. What to Do Now — Prioritized List

### Priority 1 — Deep repository inspection (Phase 2 for real)

**Goal:** Move from profile metadata audit to **repo content inspection**.

- **File inventory per repo (for selected repos):**  
  Detect README, LICENSE, .gitignore, pyproject.toml/requirements.txt/package.json, tests/, docs/, src/, notebooks, env/example files.
- **Structure signals:**  
  Clear layout (e.g. src/), tests present, root not cluttered, temp/junk files.
- **Documentation signals:**  
  Inspect README: title, what it does, installation, usage, examples, tech stack, status.
- **Risk signals:**  
  Secrets patterns, committed .env, large binaries, debug/cache artifacts.

**Outcome:** Per-repo, **evidence-backed structure report** (not only API metadata).

---

### Priority 2 — Score breakdown + evidence

**Goal:** Make scoring more credible and explainable.

- Split score into **dimensions**, e.g.:
  - Documentation (e.g. 30%)
  - Structure (e.g. 25%)
  - Maintenance (e.g. 20%)
  - Safety (e.g. 15%)
  - Portfolio fit (e.g. 10%)
- Expose **sub-scores**, **penalties**, and **explanations** in the API and report.
- For each conclusion (e.g. “archive”, “needs_cleanup”), attach **factors**, **matched rules**, and **evidence** (e.g. “no README”, “last commit 2 years ago”).

---

### Priority 3 — Repo-level cleanup plan

**Goal:** Turn output from “diagnostic” to **actionable**.

- Per repo, provide:
  - **Blocking issues** (must fix before publish)
  - **Quick wins**
  - **Recommended order of fixes**
  - **Rough effort** (e.g. quick / medium / large)
  - **Publish status** (e.g. ready / after N fixes / archive)
- Example logic: missing README → blocker; no license → moderate; short description → quick win; inactive fork → archive candidate.

---

### Priority 4 — Interactive follow-up agent flows

**Goal:** Make the Voiceflow agent a **guided assistant**, not only a single-shot scanner.

- Add intents/flows for:
  - “Show archive candidates”
  - “Explain repo X” / “Why is this not showcase-ready?”
  - “Show highest-impact fixes”
  - “Generate cleanup plan for top 5 repos”
  - “Prepare repo X for publishing”
  - “Only show repos missing README”
  - “Only show repos with security risks”
- Reuse the same scan response where possible; add endpoints only when needed (e.g. repo detail, plan).

---

### Priority 5 — LLM enhancement layer (Phase 4)

**Goal:** Use an LLM where it adds value, **after** you have good structured data.

- Use LLM for:
  - Richer, contextual suggestions
  - Repo description drafts
  - README outline suggestions
  - Summarizing repo purpose
  - Explaining why a repo is showcase vs archive
- Keep **deterministic**: scoring, repo existence, basic security checks, raw signals. LLM on top, not replacing core logic.

---

### Priority 6 — Safe auto-fix preview (Phase 6 later)

**Goal:** Preview only first; no direct writes yet.

- Support **preview** for:
  - README draft
  - License suggestion
  - Topics suggestion
  - Short description
  - .gitignore proposal
- User reviews and approves; **apply** in a later phase with explicit approval and safeguards.

---

## 5. Architecture and Process Suggestions (Later)

- **Orchestration layer:** Move /scan orchestration into a clear service (e.g. `ScanService`, `RepoAuditService`) instead of keeping it only in the route.
- **API evolution:** When needed: async job + `/scan/{job_id}`, `/repos/{repo_name}/details`, `/repos/{repo_name}/recommendations`, `/plans/cleanup`, `/fix/preview`, `/fix/apply` with approval.
- **Contracts:** Add fields such as `score_breakdown`, `evidence`, `confidence`, `remediation_priority` where they help both the agent and the user.

---

## 6. What You Need to Do Now (Summary)

| Order | Action |
| ----- | ------ |
| **1** | Implement **deep repository inspection** (Phase 2): file inventory, structure/docs/risk signals, evidence-backed structure report. |
| **2** | Add **score breakdown + evidence** to the scoring engine and API (dimensions, subtotals, explanations). |
| **3** | Build **repo-level cleanup plan** (blockers, quick wins, order, effort, publish status). |
| **4** | Design and implement **interactive follow-up flows** in the agent (Voiceflow intents + backend support if needed). |
| **5** | Introduce **LLM layer** for suggestions and explanations once data quality is high. |
| **6** | Add **safe auto-fix preview** (no apply yet), then approval-based apply later. |

Start with **Priority 1 (deep repo inspection)**; the rest builds on better data and clearer evidence.

For full vision and phase definitions, see [PROJECT_WORK_PLAN.md](PROJECT_WORK_PLAN.md). For what is implemented today, see [BUILD_SUMMARY.md](BUILD_SUMMARY.md).
