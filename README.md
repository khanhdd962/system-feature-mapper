# System Feature Mapper V1.0

## Download / Tải xuống

- [Complete export ZIP](downloads/system-feature-mapper-complete-export.zip?raw=true) — Skill, offline HTML demo, report, test results and screenshots.
- [Installable Skill ZIP](downloads/system-feature-mapper-v1.0.0-rc.1.zip?raw=true)
- [Release and acceptance report](RELEASE-REPORT.md)
- [Viewer demo source](demo/index.html) — download and open locally; supplementary Markdown is in demo/details/.

This is v1.0.0-rc.1. Host recognition, unrestricted file:// opening and real-user-repository acceptance remain gates; see the release report.


Reusable single-agent Codex Skill. It produces an offline HTML business feature map with accessible detail dialogs. AI interprets source; deterministic Python scripts inventory, validate, merge and render. No API keys, external LLMs, CDN or viewer installation.

## Install

Copy this whole directory to `~/.agents/skills/system-feature-mapper/` for reuse, or `.agents/skills/system-feature-mapper/` inside a repository. Do not copy just SKILL.md. Install generator dependencies with `python -m pip install -r requirements.txt` (Python 3.10+). Reopen Codex if its Skill catalog does not refresh.

Ask Codex: “Use system-feature-mapper to analyze this repository and generate a complete interactive feature mind map.” Codex does the source interpretation and intermediate authoring; scripts alone do not infer business semantics. Open `docs/feature-map/index.html` directly, including offline via file://.

## Generator CLI

Every script supports `--help`, rejects invalid input with nonzero status, and uses repository-relative output paths. See references for workflow and state contracts. Example fixture: `python scripts/build-mindmap.py --repo /path/to/repo --input /path/to/example-feature-map.json`.

## Upgrade

Replace the installed package with the new version, retain repository analysis workspaces, run validation and review changed source hashes before rebuilding. Version 1.0 schema is independent from display names.

## Limits

Source reading does not prove runtime behavior. Dynamic routes, remote configuration, inaccessible modules and very large/binary sources must be recorded as gaps. No automatic application E2E, production access or deployment. AI analysis runs inside Codex, not a standalone Python analyzer. YAML and JSON config are supported. Offline viewing needs a modern browser with SVG and dialog support.

## Troubleshooting

Validation failures identify the node/path; repair evidence or mark uncertainty. Missing dependencies: install requirements. Skill absent from catalog: verify front matter, installation directory, reopen Codex. Stale workspace: rescan and review affected nodes. Output path/symlink rejection: choose a directory inside the repository. Keep target source unmodified.

## Development checks

`python -m unittest discover -s tests -v` runs validator, generator, inventory/resume, install reuse and viewer tests. Viewer tests require development-only Playwright and Chromium (`python -m pip install -r requirements-dev.txt`); set `CHROMIUM_EXECUTABLE` if Chromium is elsewhere. The test serves HTML through Playwright request interception because the implementation environment blocks file:// by managed browser policy. No external assets or app services are used. See RELEASE-REPORT.md for measured results and unverified acceptance items.
