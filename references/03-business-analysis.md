# Deep business analysis

After full structural discovery, process each node, one module at a time. Write features/<stable-id>.json following schemas/feature-map.schema.json. Required fields: id, parentId, kind, name, shortDescription, purpose, actors, preconditions, usageSteps, inputs, outputs, mainFlow, alternativeFlows, exceptionCases, relatedFeatureIds, documentationPath, verification.

All arrays contain business prose strings, except relatedFeatureIds (stable IDs). documentationPath is null unless needed. Unknown arrays are empty with `unknowns:{field:"reason"}`; unknown purpose must explicitly say insufficient evidence. Preserve parent abstraction: aggregate purpose and children rather than fabricated form instructions.

Inspect UI affordances AND backend validation, permission checks, side effects and available tests. Write concrete steps, inputs, visible results and evidenced alternatives/errors only. Distinguish user actions from scheduled/system triggers. Reuse common auth explanations via related links. Do not copy sensitive records, code snippets, implementation paths or technical jargon into business prose.

verification: `{status:"source_confirmed|inferred|unknown|runtime_observed",runtimeObserved:false,evidence:[{path,startLine,endLine,type,summary}],notes:"...",claims:{purpose:[0],usageSteps:[0,1],exceptionCases:[1]}}`. Evidence types: ui, route, authorization, domain, test, docs. `claims` maps each substantive field to evidence indexes, supporting claim-level audits. Claim summaries should identify supported individual cases/steps when a field contains several claims. Inferred claims must say why. Runtime observed is reserved for authorized, actually executed observation. Existing tests corroborate intent, not production results.

Set analysisComplete=true per processed node, including blocked nodes with explicit unknown content and reasons. Save evidence-index.json as `{featureId:[evidence...]}`. Never change app source.
