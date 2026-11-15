# Build and output

Run `python "$SKILL/scripts/build-mindmap.py" --repo "$REPO" --workspace .feature-map-workspace`. It merges overview/tree/features, checks final queue status, validates, generates Markdown overflow (>5 alternative/error cases, >12 usage steps, or >1200 words, thresholds configurable), embeds safe data, and writes index.html, feature-map.json, analysis-report.md. --input is for already validated complete fixture/data input; it does not replace source analysis.

Run `python "$SKILL/scripts/verify-output.py" --repo "$REPO"`. Review warnings and reports. Rebuild twice to check determinism: keep generatedAt from original overview stable during an unchanged run. Open HTML using available browser tooling if feasible; distinguish actual browser results from static verification. Browser tooling is a development dependency, never a viewing requirement.

The final link is docs/feature-map/index.html (or configured directory). Supplementary Markdown lives in details/ and is also embedded as escaped text in the popup; it needs no fetch. Keep diagnostics in JSON/report. build-manifest.json records output hashes. Deliver concise counts, known gaps, source-confirmed versus inferred distinctions and runtime limits. Users do not manually construct the tree or JSON.
