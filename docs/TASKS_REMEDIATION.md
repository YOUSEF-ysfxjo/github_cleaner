# Tasks — Remediation plan (implemented)

Per-repo **`remediation`** is implemented in code and tests; this file is the **checklist pointer** for docs that reference `TASKS_REMEDIATION.md`.

## Delivered

| Area | Location |
| ---- | -------- |
| Contract | `RemediationPlan`, `EffortHint`, `PublishReadiness` in `contracts/scan_response.py` |
| Builder | `build_remediation_plan` in `scoring/remediation.py` (aligned with `issues.py` strings) |
| Wiring | `aggregator.py` sets `remediation` on each `RepoResult` |
| Tests | `tests/test_remediation.py` |
| Full JSON only | `POST /scan` includes `remediation`; **`POST /scan/voiceflow`** does not (flat payload) |

## Voiceflow

Use **`POST /scan`** from a custom client if you need remediation JSON; for no-code agents, extend **`VoiceflowScanResponse`** in `contracts/voiceflow_scan_response.py` if you want flat remediation slots later.

## See also

- **`BUILD_SUMMARY.md`** — inventory  
- **`AGENT_INTEGRATION.md`** — `RepoResult.remediation` shape  
