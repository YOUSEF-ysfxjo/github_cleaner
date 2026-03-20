# Tasks — Phase 2: Repo content inspection

Work through these in order. The implementation place is **`src/data/repo_inspector.py`** (see the `# task` comments inside that file).

---

## Tasks

### Task 1 — Decide how to get repo contents
Choose one approach (or both behind an option):
- **Option A:** GitHub Contents API — list/read files without cloning (rate limits apply).
- **Option B:** Shallow clone to a temp dir, then scan the filesystem.

Document the choice in the module docstring or a short comment.

---

### Task 2 — Add a function to list root-level paths for one repo
Implement a function that, given `owner`, `repo`, and (if needed) a `GitHubClient` or clone path, returns the list of files and folders at the repo root (e.g. names only, or names + type file/dir).
- If using API: use GitHub “Contents” endpoint for the repo root.
- If using clone: list the top-level directory.

---

### Task 3 — Define the file inventory to detect
Decide which paths/signals to detect and add constants or a small config (e.g. list of filenames/folders). At minimum:
- README (README.md, README.rst, etc.)
- LICENSE (LICENSE, LICENSE.md, etc.)
- .gitignore
- Dependency files: requirements.txt, pyproject.toml, package.json, etc.
- Folders: tests/, docs/, src/

---

### Task 4 — Implement “has file / has folder” checks
Using the root-level list (and optionally one level deeper for key folders), implement logic that returns booleans or a small struct per repo: e.g. `has_readme`, `has_license`, `has_gitignore`, `has_deps`, `has_tests`, `has_docs`, `has_src_layout`.

---

### Task 5 — Build a structure report dict/dataclass
From the checks above, build a single “structure report” per repo: a dict or dataclass with all the booleans and any extra info (e.g. which README file was found). This will be the evidence object you pass to scoring later.

---

### Task 6 — Integrate with existing data flow (optional in this file)
Add a function or note: “how will the rest of the app get this report?” For example: a function `inspect_repo(owner: str, repo: str, client: GitHubClient) -> StructureReport`. Do not call it from the scan route yet; just implement the function so it can be wired later.

---

### Task 7 — Add minimal tests
In `tests/`, add a test file (e.g. `test_repo_inspector.py`) that mocks the API or a temp clone and checks that your inspector returns the expected structure report for a few cases (e.g. repo with README + LICENSE, repo with nothing).

---

## Next after this file (inspector is wired into `/scan`)

Follow the step-by-step checklist in **`TASKS_STRUCTURE_TO_SCORING.md`**: use `structure_report` in issues/suggestions/scoring first, then score breakdown and cleanup plans (see also **EVALUATION_AND_NEXT_STEPS.md**).
