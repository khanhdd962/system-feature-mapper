# System Feature Mapper V1.0 — Implementation and acceptance report

Date: 2026-11-15. One implementation agent; no subagents, external LLM API, production service or database. The attached plan was read in full and treated as a product specification. Source analysis is performed by the Codex Skill; scripts do not claim to derive business semantics independently.

## Milestones

| Milestone | Delivered | Verification |
|---|---|---|
| A | Skill scaffold, concise SKILL.md, Draft 2020-12 schema, fixture, validator, pinned dependencies and CLI contracts | Initial 4 unit tests passed, including duplicate, parent/cycle, reference and path failures |
| B | Deterministic SVG layout, visible-node rendering, independent branches, pan/zoom/fit/reset, search, breadcrumb, modal tabs, related links, safe embedded Markdown, focus trap and keyboard controls | 7 tests passed at this milestone, including 3 actual Chromium interaction cases; fixture viewer completed before source-analysis pipeline |
| C | Source metadata inventory, configurable excludes, sensitive-file filtering, hashes, resume state, phase references and coverage/evidence protocol | 2 discovery tests passed; unchanged state preserved, changed source invalidates completion; source fixture inspected before business enrichment |
| D | Overview/tree/per-node merging, schema/source validation, Markdown overflow, self-contained HTML, report and artifact verifier | 9-node, 3-module, 3-level shop map generated; 2 Markdown files using caseLimit=2; no app source mutation |
| E | Malformed/partial input, missing evidence, Unicode/XSS, secret-pattern redaction, symlink boundaries, interrupted/resumed state, large/deep trees, installed package reused across two repositories | Final test suite and limitations below |

## Actual tests

Command: `python -m unittest discover -s tests -v`.

Final suite: **22 tests** (unit, CLI/pipeline integration, 3 Chromium UI cases). Python 3.12, Node 24, jsonschema 4.26.0, PyYAML 6.0.3, Playwright 1.62.0, system Chromium. Generator supports Python 3.10+; alternate interpreter versions were not separately executed.

Browser assertions cover initial root/top modules, branch expansion and collapse, deep search with Vietnamese accent folding, popup business text, tabs, child/related navigation, Markdown reading view, Escape, focus restoration/trapping, keyboard branch selection, pan, wheel/buttons zoom, fit/reset. A 357-node tree was expanded and collapsed; a 401-level structure was validated separately. These are functional checks, not a universal performance guarantee. Request interception provided the single HTML document; no additional HTTP(S) resources were requested, and no page JavaScript errors occurred. Screenshot overview and popup were generated and visually inspected.

**file:// test limitation:** the actual navigation attempt failed with `net::ERR_BLOCKED_BY_ADMINISTRATOR` before the artifact loaded. Managed Chromium policy blocks file URLs. The policy was not altered. Tests used an intercepted HTTP document with the same HTML bytes; packaging was statically checked for no resource imports, fetch, CDN or external assets. Direct disk opening remains an acceptance item to verify in the user's browser.

## Source-backed fixture review

The provided workspace had no application repository. A small executable, synthetic shop repository was created for controlled acceptance, with domain.py, routes.py and declarative UI. It is not a production application or a substitute for the user's real-repository acceptance.

| Sampled capability | Inspected evidence | Result |
|---|---|---|
| Account aggregate | domain.py:8–19; navigation.html:2–4 | Login/logout purpose and child relationship match source |
| Login | domain.py:8–15; navigation.html:3 | Required fields, invalid credentials, sign-in result match source |
| Purchase | domain.py:21–33; navigation.html:5 | Auth, positive integer, missing product, insufficient stock and order creation match source |
| History | domain.py:35–38; routes.py:6 | Auth restriction and copied in-memory order list match source |
| Cancel | domain.py:40–50; navigation.html:6 | Missing order, status restriction, cancellation and stock return match source |

All three navigation areas and all five declared routes map to canonical nodes. No invented payment, delivery, multi-user authorization or live web UI behavior is claimed. The static UI is not wired to a server. Unknown fields have explicit reasons. RuntimeObserved stays false in the generated map. Fixture-domain unit tests execute only synthetic in-memory objects and validate happy/error cases; they do not establish web/production behavior.

The install-reuse test copies the whole package once into a temporary Skill directory, then invokes its CLIs from an analyzed shop repository and an unrelated notes repository. The latter uses illustrative map input, not an asserted automatic source analysis. This validates packaging/reuse without claiming the host has loaded the Skill.

## Remaining acceptance gates and handling

1. **Codex catalog recognition:** standard SKILL.md front matter and installation layout are present, but this session cannot refresh the host Skill catalog. Install the ZIP directory in ~/.agents/skills or repository .agents/skills and reopen Codex; invoke by name. No custom slash command is promised.
2. **Real repository acceptance:** no user application repository was available. Run the installed Skill in the target repository, compare menus/routes and audit at least five nodes. The existing fixture acceptance and tests are included for reproduction.
3. **Disk URL verification:** open the generated index.html in an unrestricted local browser. If organization policy also blocks file URLs, serve that output directory locally; the artifact itself requires no server or build.
4. **Release tag:** do not mark the full final acceptance checklist complete or create v1.0.0 until the above gates pass. This deliverable is packaged as v1.0.0-rc.1. SchemaVersion remains 1.0.0.

## Known constraints

- Agent interpretation quality depends on available source. Dynamic/remote-configured behavior, inaccessible modules and metadata-only large/binary files must remain coverage gaps.
- V1 conservatively invalidates all completed nodes when inventory hashes change. It supports safe resumption, not semantic incremental updates. Large metadata-only files are tracked by size rather than content hash.
- Secrets are excluded by file patterns and defensive output redaction (keys, tokens, emails). Arbitrary personal data cannot be reliably recognized by regex; the Skill requires source selection and content review. Do not provide real customer records.
- Supplementary Markdown is generated from complete business fields and embedded as plain text, avoiding a Markdown parser/XSS dependency. It is readable with headings visible, not rich Markdown rendering.
- Discovery, evidence claim correctness, capability deduplication and contradiction review are agent responsibilities; graph/schema validators cannot prove business truth.
- Viewing needs no Python/npm/dependencies; generation needs the pinned Python dependencies; development UI tests additionally need Playwright and Chromium.

## Reproduce

1. Install requirements and development requirements in an environment with Chromium.
2. Run the test suite above.
3. `python scripts/build-mindmap.py --repo tests/fixtures/sample-shop --workspace .feature-map-workspace --case-limit 2`
4. `python scripts/verify-output.py --repo tests/fixtures/sample-shop`
5. Open tests/fixtures/sample-shop/docs/feature-map/index.html.

No global installation was performed and no production source/database was changed.

## Artifact export constraint

The chat default export path `/codex/browser/projectless/0001-files-mentioned-by-the-user-uploaded-file-pointe/output` is on a read-only root filesystem on this Cloud machine. No approval review rejection occurred; the filesystem rejected directory creation. Deliverables are retained under `/workspace/output` and the complete ZIP can be saved from the Cloud workspace. No fake file link or nonexistent export is claimed.
