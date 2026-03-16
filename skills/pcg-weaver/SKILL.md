---
name: pcg-weaver
description: PCG graph specialist for Unreal Engine. Use when tasks involve reading, repairing, refactoring, or extending PCG graphs. Prefer Loomle graph.query/mutate for pipeline rewrites, preserve external dataflow interfaces during local changes, and verify every structural edit with readback plus compile.
---

# PCG Weaver

## Overview
Use this skill as the strategy layer for Unreal PCG graph work.

- Default to `Loomle` for graph reading, local pipeline rewrites, verification, layout, and compile loops.
- Keep edits small and verifiable: `query -> mutate -> query -> compile`.
- Preserve external dataflow interfaces whenever replacing a local pipeline segment.
- Use `graph.runtime` as the preferred runtime validation layer whenever the edit affects generated output, spawned actors, or instanced meshes.

## Workflow
1. Confirm scope and target PCG asset plus graph name.
2. Choose the narrowest task recipe.
3. Query before mutating.
4. Execute in small verified batches.
5. Re-query and compile after each structural change.
6. Preserve dataflow readability and pipeline intent.

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

- Broken pipe, wrong downstream consumer, missing local edge, or local cleanup:
  read [references/repair-recipe.md](references/repair-recipe.md)
- Replace a local pipeline segment while preserving upstream inputs and downstream consumers:
  read [references/subgraph-replace-recipe.md](references/subgraph-replace-recipe.md)
- Extend a pipeline with a new local stage or multi-stage insert:
  read [references/extend-recipe.md](references/extend-recipe.md)

## 1) Confirm Scope
- Identify the target PCG asset path.
- Identify the exact graph name before mutating, usually `PCGGraph`.
- Identify whether the task is:
  - repair
  - local refactor
  - subgraph replacement
  - pipeline extension
- Identify what upstream inputs and downstream consumers must remain stable.

## 2) Loomle Mode
Use this path first for PCG work.

Recommended rhythm:
1. `graph.query` the target PCG graph.
2. Identify the exact pipeline boundary before mutating.
3. For known semantic stages, call `graph.ops.resolve` on the target graph and prefer the returned `preferredPlan`.
4. If adding nodes by action, fetch fresh `graph.actions` from the same asset and graph only when semantic planning does not cover the stage you need.
5. Apply a small `graph.mutate` batch.
6. `graph.query` again and verify:
   - new nodes exist
   - expected edges exist
   - removed edges are actually gone
   - preserved upstream and downstream interfaces still connect correctly
7. `compile`
8. Repeat only if the previous batch verified cleanly.

For a concrete Loomle-first edit loop, read [references/loomle-pcg-workflow.md](references/loomle-pcg-workflow.md).
Always pass `graphType="pcg"` on PCG `graph.query`, `graph.actions`, and `graph.mutate` calls.

## 3) Node Creation Guidance
Prefer the simplest node-creation path that is reliable in the current graph.

- Use `graph.ops.resolve` first when the stage is a stable semantic operation. Copy the returned `preferredPlan` into `graph.mutate` instead of hardcoding class paths.
- Treat `graph.ops.resolve` as a semantic planning layer. It can usually choose the right stage and provide first-pass settings and pins, but the skill still owns preserved interface rewiring, re-query, and downstream validation.
- Use `addNode.byAction` when the curated action set already exposes the node you want but semantic planning does not.
- Use `addNode.byClass` only when deterministic construction is easier or semantic/action discovery is incomplete.
- Re-query exact pins after introducing unfamiliar PCG nodes before wiring deeper stages.
- If `graph.ops.resolve` returns `settingsTemplate` or `verificationHints`, carry them forward. They are execution guidance, not decoration.
- For `connectPins`, use nested `args.from` and `args.to` endpoint objects with `nodeId` or `nodeRef` plus `pin`.
- If `graph.ops.resolve` or runtime diagnostics indicate a pin-context-sensitive op, retry resolve with the narrowest `fromPin` or `toPin` you have instead of guessing a class path.

## 4) Run and Verify
- Always verify with a fresh `graph.query` after every structural batch.
- Compile after structural edits.
- Treat `layoutGraph(scope=\"touched\")` as a readability helper, not as proof that the pipeline is correct.
- Trust readback over mutate optimism if there is any disagreement.
- When the pipeline drives runtime generation, capture a `graph.runtime` baseline before the edit and compare after regenerate. Prefer `managedResources` and `inspection` over static graph shape when validating spawned output.

## 5) Layout Rules
- Keep pipeline flow readable left to right.
- Keep upstream source nodes visually separated from middle-stage filters and downstream consumers.
- Preserve nearby local context; do not trigger unnecessary whole-graph churn.
- Prefer `layoutGraph(scope=\"touched\")` before any global layout.

## 6) Validation Contract
Always leave behind enough evidence that another agent could confirm the edit worked.

Minimum expectations:
- identify the target asset and graph name
- show the local pipeline boundary
- verify with a fresh `graph.query`
- compile after structural edits

For local refactors, prefer verifying:
- node count changed in the expected direction
- specific new node IDs exist
- specific old edges are gone
- specific replacement edges are present
- preserved upstream and downstream dataflow still connect as intended
- `graph.runtime` shows the expected before/after change for generated output, for example `totalInstanceCount`, `generatedComponentCount`, or executed node titles

## Troubleshooting
- If a PCG edge does not appear after a reported success, trust fresh readback and repair from the observed state.
- If adding a pipeline stage introduces an unfamiliar output pin, query the new node and use the actual returned pin name.
- If a mutate batch fails midway, assume earlier ops may already be committed unless readback proves otherwise.
- If a pipeline replacement disconnects the graph, rebuild from the current snapshot instead of replaying the original whole batch blindly.
- If compile succeeds but the pipeline still looks wrong, re-query exact node IDs and edges rather than relying on layout.
- For layout or move verification, prefer `position` or `layout.position`; `nodePosX/nodePosY` may be null.
- If a PCG graph still executes but output counts changed unexpectedly, compare `graph.runtime.managedResources.totalInstanceCount` and `inspection.nodes` before assuming the structure edit was wrong.
- `setPinDefault` is not universally supported on PCG nodes. If it fails, keep the committed part of the batch, re-query, and continue from the observed state.

For recurring failure patterns and concrete fixes, read [references/troubleshooting.md](references/troubleshooting.md).

## Scope Boundary
This skill is intentionally PCG-focused. It should not become a generic Blueprint or Material skill.

- PCG graph strategy belongs here.
- General graph protocol behavior belongs in `LOOMLE`.
- Project-specific style or naming rules should come from the current repo instructions, not be hardcoded here.
