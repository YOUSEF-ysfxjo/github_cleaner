# GitHub Cleanup AI Agent — Project Work Plan

## 1. Project Goal

Build an AI-powered agent that reviews a GitHub account and helps prepare repositories for public sharing.

The agent will:

- Audit repositories
- Detect issues (missing README, secrets, messy structure, etc.)
- Suggest improvements
- Optionally apply safe fixes after user approval

The system will operate as a **GitHub hygiene and publishing assistant**.

---

## 2. Core Objectives

The agent should be able to:

- Discover all repositories in a GitHub account
- Analyze repository quality
- Detect common problems
- Generate improvement suggestions
- Assist in preparing repositories for public release
- Provide a final **publish readiness score**

---

## 3. System Architecture

High-level architecture:

```
User
  ↓
AI Agent
  ↓
GitHub Analyzer
  ↓
Repository Scanner
  ↓
Quality Evaluation Engine
  ↓
Report Generator
```

### Main components

- GitHub Data Collector
- Repository Analyzer
- Quality Scoring System
- Recommendation Engine
- Execution Tools (optional fixes)

---

## 4. Development Phases

### Phase 1 — Repository Discovery

**Goal:** Retrieve all repositories from a GitHub account.

**Tasks:**

- Connect to GitHub API
- Fetch repositories metadata
- Store repository list locally
- Extract basic attributes

**Data to collect:**

- repository name
- visibility
- description
- stars
- last commit date
- languages used
- README existence

**Deliverable:** A structured dataset of all repositories.

---

### Phase 2 — Repository Structure Analysis

**Goal:** Inspect repository contents.

**Tasks:**

- Clone repositories locally
- Scan directory structure
- Detect important files

**Files to detect:**

- README.md
- LICENSE
- requirements.txt / package.json
- .gitignore
- documentation folder

**Deliverable:** Repository structure report.

---

### Phase 3 — Quality Evaluation Engine

**Goal:** Evaluate repository quality.

**Define scoring criteria such as:**

**Documentation**

- README exists
- README length
- usage instructions
- installation guide

**Code Structure**

- organized folders
- dependency files
- clear project structure

**Maintenance**

- recent commits
- issue activity

**Security**

- presence of .env
- exposed API keys
- secrets in code

**Deliverable:** Repository quality score.

**Example:**

```
Repo: complaint-analysis-api
Score: 72 / 100

Issues:
- Missing license
- README lacks installation guide
- Hardcoded API endpoint
```

---

### Phase 4 — AI Review Layer

**Goal:** Use an LLM to provide intelligent recommendations.

**Input to the LLM:**

- repository metadata
- repository structure
- quality evaluation

**Output:**

- improvement suggestions
- missing documentation
- structural recommendations

**Example output:**

```
Suggestions:
1. Add a LICENSE file.
2. Expand the README with setup instructions.
3. Add example usage.
4. Create a project structure section.
```

---

### Phase 5 — Cleanup Recommendation Engine

**Goal:** classify repositories.

**Possible categories:**

- Public Ready
- Needs Cleanup
- Archive
- Private Only
- Experimental

**Example:**

```
Repo: OCR-Pipeline
Status: Needs Cleanup

Required actions:
- add README
- remove debug scripts
- add license
```

---

### Phase 6 — Optional Auto-Fix Tools

**Goal:** allow the agent to apply safe improvements.

**Examples — Auto actions:**

- generate README template
- add .gitignore
- create LICENSE
- remove temporary files

**Important rule:** All modifications require **user approval**.

---

### Phase 7 — Report Generation

**Goal:** produce a complete GitHub account report.

**Example report:**

```
GitHub Account Audit

Total repositories: 24

Public ready: 6
Needs cleanup: 10
Archive recommended: 5
Private only: 3
```

Each repository includes:

- score
- issues
- suggested improvements

---

## 5. Agent Capabilities

The AI agent should support commands such as:

**Examples:**

- Analyze my GitHub account
- Show repositories that are not ready for publishing
- Generate a cleanup plan
- Prepare repository X for publishing

---

## 6. Safety Design

The system must include:

- read-only analysis mode
- approval system before modifications
- protection against deleting important files
- secret detection safeguards

---

## 7. Possible Extensions

Future improvements may include:

- **GitHub Portfolio Builder** — Automatically generate a portfolio page.
- **Project README Enhancer** — Improve README quality using AI.
- **Code Quality Analysis** — Integrate static analysis tools.
- **Automated Documentation** — Generate documentation from code.

---

## 8. Final Deliverable

The final system should provide:

- a GitHub auditing agent
- repository quality scoring
- automated improvement suggestions
- optional safe fixes
- a publish-ready report

---

## 9. Expected Outcome

After running the system, the user will know:

- which repositories are ready to share
- which repositories need improvements
- how to fix them
- how to prepare a clean GitHub profile

---

## Relation to this repository

The current **`github_cleaner`** codebase maps roughly to **early phases** of this plan (API-based discovery, metadata, scoring, classification, suggestions) in **read-only** mode. This document is the **north-star work plan**; see [BUILD_SUMMARY.md](BUILD_SUMMARY.md) for what is implemented today, and [ARCHITECTURE.md](../ARCHITECTURE.md) for the layered design used in-repo.
