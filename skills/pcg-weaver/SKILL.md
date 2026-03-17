---
name: pcg-weaver
description: PCG graph specialist for Unreal Engine. Use when tasks involve reading, repairing, refactoring, or extending PCG graphs. Prefer Loomle graph.query/mutate for pipeline rewrites, preserve external dataflow interfaces during local changes, and verify structural edits with graph.verify plus targeted readback when needed.
---

# PCG Weaver

## Overview
Use this skill as the strategy layer for Unreal PCG graph work.

- Default to `Loomle` for graph reading, local pipeline rewrites, layout, and graph-level verification.
- Keep edits small and verifiable: `query -> mutate -> graph.verify`.
- Preserve external dataflow interfaces whenever replacing a local pipeline segment.
- Use scene- or instance-level validation only when the task explicitly depends on spawned runtime behavior; graph tools validate the graph asset itself, not world outcomes.

## Mutation Safety
- Treat `graph.mutate` as potentially partial-commit unless readback proves otherwise.
- For middle-stage pipeline rewrites, prefer:
  1. add the replacement stages
  2. re-query exact new pin names
  3. reconnect preserved upstream inputs and downstream consumers
  4. remove the old middle stage
- Do not trust reported success if the fresh graph snapshot disagrees.

## Task Routing
Pick the narrowest recipe that matches the request.

- Need a broad PCG node inventory, class lookup, tooltip lookup, or property search:
  read [references/pcg-node-catalog-usage.md](references/pcg-node-catalog-usage.md)
- Broken pipe, wrong downstream consumer, missing local edge, or local cleanup:
  read [references/repair-recipe.md](references/repair-recipe.md)
- Replace a local pipeline segment while preserving upstream inputs and downstream consumers:
  read [references/subgraph-replace-recipe.md](references/subgraph-replace-recipe.md)
- Extend a pipeline with a new local stage or multi-stage insert:
  read [references/extend-recipe.md](references/extend-recipe.md)

## Start Here
- Identify the target PCG asset path.
- Identify the exact graph name before mutating, usually `PCGGraph`.
- If the task starts from a selected PCG actor or component in a level, read `context`, then `graph.resolve` the emitted actor or component path, and prefer the returned `graphRef` for later `graph.query`, `graph.mutate`, and `graph.verify` calls.
- Identify whether the task is:
  - repair
  - local refactor
  - subgraph replacement
  - pipeline extension
- Identify what upstream inputs and downstream consumers must remain stable.
- Default loop: `graph.query -> graph.mutate -> graph.verify`.
- Add a fresh `graph.query` only when you need exact node or edge proof beyond verify output.

## Catalog-First Discovery
When the task starts with "what PCG node should I use?" or needs a broad inventory:

1. Search `references/pcg-node-catalog-index.json` first.
2. Open `references/pcg-node-catalog.json` only for the small matching subset that needs full property detail.
3. Open the listed header only for the final candidates.
4. Use live `graph.query` only when you need real graph-instance pins or dynamic pin behavior.

Do not load the full catalog into context by default. Treat it as a local database and query it narrowly.

## Loomle Loop
Use this path first for PCG work.

Recommended rhythm:
1. Start from the target PCG graph directly, or resolve a selected level actor/component into a PCG `graphRef` first.
2. Identify the exact pipeline boundary before mutating.
3. For known semantic stages, call `graph.ops.resolve` on the target graph and prefer the returned `preferredPlan`.
4. If semantic planning does not cover the stage you need, use the local PCG node catalog and direct `addNode.byClass` as the fallback path.
5. Apply a small `graph.mutate` batch.
6. Prefer `graph.verify` as the default final check for the batch.
7. Use a fresh `graph.query` when you need exact node or edge proof beyond verify output.
8. Verify:
   - new nodes exist
   - expected edges exist
   - removed edges are actually gone
   - preserved upstream and downstream interfaces still connect correctly
   - verify status and diagnostics are acceptable
9. Repeat only if the previous batch verified cleanly.

For a concrete Loomle-first edit loop, read [references/loomle-pcg-workflow.md](references/loomle-pcg-workflow.md).
Always pass `graphType="pcg"` on PCG `graph.query`, `graph.verify`, and `graph.mutate` calls.

## Node Creation Guidance
Prefer the simplest node-creation path that is reliable in the current graph.

- Use the local PCG node catalog when you need to discover likely node classes, titles, or editable properties before choosing an op or node creation path.
- Use `graph.ops.resolve` first when the stage is a stable semantic operation. Copy the returned `preferredPlan` into `graph.mutate` instead of hardcoding class paths.
- Treat `graph.ops.resolve` as a semantic planning layer. It can usually choose the right stage and provide first-pass settings and pins, but the skill still owns preserved interface rewiring, re-query, and downstream validation.
- Use `addNode.byClass` when deterministic construction is easier or semantic discovery is incomplete.
- Re-query exact pins after introducing unfamiliar PCG nodes before wiring deeper stages.
- If `graph.ops.resolve` returns `settingsTemplate` or `verificationHints`, carry them forward. They are execution guidance, not decoration.
- For `connectPins`, use nested `args.from` and `args.to` endpoint objects with `nodeId` or `nodeRef` plus `pin`.
- If `graph.ops.resolve` indicates a pin-context-sensitive op, retry resolve with the narrowest `fromPin` or `toPin` you have instead of guessing a class path.

## Verification
- Prefer `graph.verify` after every structural batch. Use a fresh `graph.query` when you need exact node or edge proof or when verify diagnostics need local inspection.
- Treat `layoutGraph(scope=\"touched\")` as a readability helper, not as proof that the pipeline is correct.
- Trust readback over mutate optimism if there is any disagreement.
- If the task explicitly cares about world results, perform a separate scene- or instance-level validation pass after graph verification.

For local refactors, prefer verifying:
- specific new node IDs or edges exist when they matter to the task
- specific old edges are gone when a replacement removed them
- preserved upstream and downstream dataflow still connect as intended
- scene-level validation is only required when the task explicitly cares about generated runtime behavior

## Layout Rules
- Keep pipeline flow readable left to right.
- Keep upstream source nodes visually separated from middle-stage filters and downstream consumers.
- Preserve nearby local context; do not trigger unnecessary whole-graph churn.
- Prefer `layoutGraph(scope=\"touched\")` before any global layout.

## Troubleshooting
- If a PCG edge does not appear after a reported success, trust fresh readback and repair from the observed state.
- If adding a pipeline stage introduces an unfamiliar output pin, query the new node and use the actual returned pin name.
- If a mutate batch fails midway, assume earlier ops may already be committed unless readback proves otherwise.
- If a pipeline replacement disconnects the graph, rebuild from the current snapshot instead of replaying the original whole batch blindly.
- If `graph.verify` succeeds but the pipeline still looks wrong, re-query exact node IDs and edges rather than relying on layout.
- For layout or move verification, prefer `position` or `layout.position`; `nodePosX/nodePosY` may be null.
- If the verified graph still behaves unexpectedly in a level, treat that as a separate scene-instance problem rather than proof that the graph asset is invalid.
- For overridable PCG input pins, `setPinDefault` is the intended follow-up path after disconnecting the input, but current Loomle builds may still fail or behave inconsistently on some nodes. If that happens, keep the committed part of the batch, re-query, and continue from the observed state.
- `graph.verify` can return graph-level diagnostics even when the compile step itself succeeds; treat those diagnostics as authoritative for the asset.

For recurring failure patterns and concrete fixes, read [references/troubleshooting.md](references/troubleshooting.md).

## Scope Boundary
This skill is intentionally PCG-focused. It should not become a generic Blueprint or Material skill.

- PCG graph strategy belongs here.
- General graph protocol behavior belongs in `LOOMLE`.
- Project-specific style or naming rules should come from the current repo instructions, not be hardcoded here.
