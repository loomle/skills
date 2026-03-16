---
name: material-weaver
description: Material graph specialist for Unreal Engine. Use when tasks involve reading, repairing, refactoring, or generating Material graphs. Prefer Loomle graph.query/mutate for interactive edits and verification; fall back to bundled UE Python scripts when deterministic bulk generation, command-line execution, or direct MaterialEditingLibrary control is safer.
---

# Material Weaver

## Overview
Use this skill as the strategy layer for Unreal Material graph work.

- Default to `Loomle` for graph reading, small-batch rewrites, verification, and compile loops.
- Use bundled `UE Python` scripts when you need deterministic batch creation, command-line reruns, actor assignment, or a fallback around Material pin/runtime quirks.
- Keep edits small and verifiable: `query -> mutate -> query -> compile`.

## Workflow
1. Confirm scope and target Material asset.
2. Choose editing mode:
   - `LOOMLE mode` for interactive repair/refactor.
   - `UE Python mode` for deterministic generation or fallback.
3. Execute in small verified batches.
4. Re-query and compile after each structural change.
5. Preserve project style and readability.

## Mutation Safety
- Treat `graph.mutate` as potentially partial-commit unless readback proves otherwise.
- Prefer two-pass replacement for risky rewires:
  1. add the new nodes
  2. re-query exact pins and graph refs
  3. reconnect preserved interfaces
  4. remove the old chain
- Do not trust `changed=true` alone; always confirm with a fresh `graph.query`.

## Task Routing
Pick the narrowest recipe that matches the request.

- Broken or missing wires, wrong root property, small local fix:
  read [references/repair-recipe.md](references/repair-recipe.md)
- Replace an existing node chain or subgraph while preserving external inputs/outputs:
  read [references/subgraph-replace-recipe.md](references/subgraph-replace-recipe.md)
- Build a Material graph mostly from scratch or produce a reusable generator:
  read [references/generate-recipe.md](references/generate-recipe.md)

## 1) Confirm Scope
- Identify the target Material asset path and whether to overwrite or create a versioned copy.
- Identify whether the task is:
  - repair
  - local refactor
  - subgraph replacement
  - whole-graph generation
- If actor assignment matters, note the target actor or level explicitly before choosing `UE Python mode`.

## 2) Loomle Mode
Use this path first when the task is an interactive Material edit rather than a reusable batch script.

Recommended rhythm:
1. `graph.query` the Material root graph.
2. Identify the exact subgraph boundary before mutating.
3. When adding a well-known node, call `graph.ops.resolve` first and prefer the returned `preferredPlan` over hardcoded class guesses.
4. Apply a small `graph.mutate` batch.
5. `graph.query` again and verify:
   - new nodes exist
   - expected edges exist
   - removed edges are actually gone
6. `compile`
7. Repeat only if the previous step verified cleanly

Use `graph.query` and `context` to discover graph refs instead of guessing addresses. For Material assets, prefer the address forms that already work in the current session.
Always pass `graphType="material"` on Material `graph.query`, `graph.actions`, and `graph.mutate` calls.
When `graph.ops.resolve` returns a stable `preferredPlan`, treat that as the default source of node-creation truth. Treat it as a semantic vocabulary layer, not as a full rewrite planner: it should decide what node to introduce and offer first-pass pin hints, while the skill still owns subgraph boundaries, preserved interfaces, and verification. Fall back to direct `addNode.byClass` only when:
- the op is not in the curated catalog
- resolve returns `resolved=false`
- the task needs a node shape that the semantic catalog does not express yet

Read [references/pin-behavior-ue57.md](references/pin-behavior-ue57.md) before wiring nodes in UE 5.7.
For a concrete Loomle-first edit recipe, read [references/loomle-material-workflow.md](references/loomle-material-workflow.md).

## 3) UE Python Mode
Use this path when one of these is true:

- you are generating a large deterministic Material graph from scratch
- you want a rerunnable artifact committed as a script
- you need command-line execution through `UnrealEditor-Cmd`
- you are assigning the Material to actors/assets as part of the workflow
- Loomle pin or graph-addressing behavior is blocking reliable progress

Implementation rules:
- Prefer deterministic constants for node placement.
- Build graph in small composable functions:
  - `connect_expr(...)`
  - `connect_property(...)`
  - `layout_nodes(...)`
  - `apply_to_actor(...)`
- Always write a unique done marker string.
- Fail fast on any connection call that returns `False` or raises.
- Save and compile only when all mandatory connections succeed.
- Log structured report lines with key counts and booleans.

Use [scripts/material_graph_helpers.py](scripts/material_graph_helpers.py) helpers directly or copy patterns from it.

## 4) Run and Verify
- In `Loomle mode`, always verify with a fresh `graph.query` after every structural batch.
- In `UE Python mode`, use `UnrealEditor-Cmd -run=pythonscript` and enforce a done marker:
  - [scripts/run_ue_python_and_check_done.sh](scripts/run_ue_python_and_check_done.sh)
- Configure Unreal executable outside the skill:
  - set `UE_BIN` in your environment, or ensure `UnrealEditor-Cmd` is available in `PATH`
- Treat missing marker as failure even when process exit code is 0.

## 5) Layout Rules
- Prefer readable left-to-right flow from upstream expressions into downstream consumers and root properties.
- For multi-input nodes, use deterministic source ordering when pin semantics exist, for example `A`, `B`, `Alpha`.
- Keep all expression nodes left of Material Output.
- Treat `layoutGraph(scope=\"touched\")` as a convenience, not as proof of correctness. Re-query and inspect positions if layout quality matters.
- For Material layout verification, prefer `position` or `layout.position` from `graph.query`; `nodePosX/nodePosY` may be null.

## 6) Choosing Between LOOMLE And UE Python
Choose `Loomle` when:
- editing an existing Material graph interactively
- doing local rewires or subgraph replacement
- you want readback and compile validation after every batch

Choose `UE Python` when:
- creating a graph from scratch
- you need a reusable script artifact
- you need direct MaterialEditingLibrary control
- Loomle addressing or pin-resolution becomes unreliable for the task

For a compact decision table, read [references/mode-selection.md](references/mode-selection.md).

## 7) Validation Contract
Always leave behind enough evidence that another agent could confirm the edit worked.

Minimum expectations:
- identify the target asset path
- record the graph address actually used
- show the intended change boundary
- verify with a fresh `graph.query`
- compile after structural edits

For local refactors, prefer verifying:
- node count changed in the expected direction
- specific new node IDs exist
- specific old edges are gone
- specific replacement edges are present

If the task used `UE Python mode`, also require:
- save confirmation
- compile confirmation
- explicit done marker or equivalent structured success line

## Troubleshooting
- If wires appear missing with no obvious runtime failure, check pin names first.
- If `graph.ops.resolve` returns pin hints that disagree with fresh readback, trust the fresh `graph.query` snapshot and continue with the actual returned pins.
- If a unary node refuses to connect, try the UE 5.7 empty-pin rule from the reference file.
- If selection returns `/Engine/Transient...` paths, prefer `resolvedGraphRefs` or a direct root-asset query over transient node-path resolution.
- Material Function node selection is expected to come through in current Loomle builds; if it does not, fall back to direct function-asset query and continue from returned graph refs.
- If Material Output appears inside the graph cluster, left-shift rightmost expression columns.
- If lines still cross, enforce deterministic ordering for multi-input node sources and increase row spacing.
- If Loomle returns success but the graph snapshot does not match, trust the fresh `graph.query` snapshot over assumptions.
- If coordinates do not apply in `UE Python mode`, log write-back node positions and re-run with wider spacing.

## Scope Boundary
This skill is intentionally Material-focused. It should not become a generic Blueprint or PCG skill.

- Material graph strategy belongs here.
- General graph protocol behavior belongs in `LOOMLE`.
- Project-specific style or naming rules should come from the current repo instructions, not be hardcoded here.

For recurring failure patterns and concrete fixes, read [references/troubleshooting.md](references/troubleshooting.md).
