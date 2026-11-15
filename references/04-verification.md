# Coverage and consistency

Reconcile route list, UI/menu list, roles/permissions and user-visible domain operations against canonical nodes. Record each surface's inspected source paths, mapped IDs and unresolved gaps in discovery-progress.json coverageSurfaces. Check missing actors, duplicate capabilities, impossible/contradictory flows and unexpanded parents manually. Return only affected branches to discovery/enrichment when gaps emerge.

Run validate-features.py on merged feature-map.json with --repo. It checks schema, graph, references, relative paths and actual evidence file/line existence. Review claim mappings and unknown reasons. Evidence paths are maintainer-only in JSON/report, not ordinary UI. Secrets and personal data require human/agent review as well as defensive redaction; pattern matching cannot guarantee detection of arbitrary personal information.

Before building verify every node has final complete/blocked discovery status and analysisComplete=true; blocked entries need reason. Preserve runtimeObserved=false unless observed. Review five representative nodes against actual source, including a parent, a restricted capability and an error case. Record comparisons and remaining dynamic/inaccessible behaviors in acceptance notes. No automatic application startup or runtime E2E.
