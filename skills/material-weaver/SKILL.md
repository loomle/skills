---
name: material-weaver
description: Material graph specialist for Unreal Engine. Use when tasks involve reading, repairing, refactoring, or generating Material graphs. Prefer Loomle graph.query plus graph.ops.resolve/mutate for interactive edits and graph.verify for final checks; fall back to bundled UE Python scripts when deterministic bulk generation, command-line execution, or direct MaterialEditingLibrary control is safer.
---

# Material Weaver

## Overview
Use this skill as the strategy layer for Unreal Material graph work.

- Default to `Loomle` for graph reading, semantic planning, small-batch rewrites, and graph-level verification.
- Use bundled `UE Python` scripts when you need deterministic batch creation, command-line reruns, actor assignment, or a fallback around Material pin/runtime quirks.
- Keep edits small and verifiable: `graph.query -> graph.ops.resolve -> graph.mutate -> graph.verify`.

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

- Need a broad Material node inventory, expression class lookup, tooltip lookup, or fallback class search:
  read [references/material-node-catalog-usage.md](references/material-node-catalog-usage.md)
- Broken or missing wires, wrong root property, small local fix:
  read [references/repair-recipe.md](references/repair-recipe.md)
- Replace an existing node chain or subgraph while preserving external inputs/outputs:
  read [references/subgraph-replace-recipe.md](references/subgraph-replace-recipe.md)
- Build a Material graph mostly from scratch or produce a reusable generator:
  read [references/generate-recipe.md](references/generate-recipe.md)

## Start Here
- Identify the target Material asset path and whether to overwrite or create a versioned copy.
- Identify whether the task is:
  - repair
  - local refactor
  - subgraph replacement
  - whole-graph generation
- If actor assignment matters, note the target actor or level explicitly before choosing `UE Python mode`.
- Default loop: `graph.query -> graph.ops.resolve -> graph.mutate -> graph.verify`.
- Add a fresh `graph.query` only when you need exact node or edge proof beyond verify output.

## Loomle Mode
Use this path first when the task is an interactive Material edit rather than a reusable batch script.

Recommended rhythm:
1. `graph.query` the Material root graph.
2. If a `MaterialFunctionCall` exposes `childGraphRef`, follow that ref or use `graph.list(includeSubgraphs=true)` before rebuilding the address manually.
3. Identify the exact subgraph boundary before mutating.
4. When adding a well-known node, call `graph.ops.resolve` first and prefer the returned `preferredPlan` over hardcoded class guesses.
5. Apply a small `graph.mutate` batch.
6. Prefer `graph.verify` as the default final check for the batch.
7. Use a fresh `graph.query` when you need exact node or edge proof beyond verify output.
8. Verify:
   - new nodes exist
   - expected edges exist
   - removed edges are actually gone
   - verify status and diagnostics are acceptable
9. Repeat only if the previous step verified cleanly

Use `graph.query` and `context` to discover graph refs instead of guessing addresses. For Material assets, prefer the address forms that already work in the current session.
Always pass `graphType="material"` on Material `graph.query`, `graph.ops`, `graph.ops.resolve`, `graph.verify`, and `graph.mutate` calls.
When `graph.ops.resolve` returns a stable `preferredPlan`, treat that as the default source of node-creation truth. Treat it as a semantic vocabulary layer, not as a full rewrite planner: it should decide what node to introduce and offer first-pass pin hints, while the skill still owns subgraph boundaries, preserved interfaces, and verification. Fall back to direct `addNode.byClass` only when:
- the op is not in the curated catalog
- resolve returns `resolved=false`
- the task needs a node shape that the semantic catalog does not express yet

Use the local Material node catalog when you need broad expression discovery, likely root-sink targets, or header/cpp lookup before choosing a fallback class.
If you want a semantic plan to emit an immediate root-sink connection shape, pass `items[*].hints.targetRootPin` before manually wiring into `__material_root__`.

Read [references/pin-behavior-ue57.md](references/pin-behavior-ue57.md) before wiring nodes in UE 5.7.
For a concrete Loomle-first edit recipe, read [references/loomle-material-workflow.md](references/loomle-material-workflow.md).

## UE Python Mode
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

## Verification
- In `Loomle mode`, prefer `graph.verify` after every structural batch. Use a fresh `graph.query` when you need exact node or edge proof or when verify output needs follow-up.
- In `UE Python mode`, use `UnrealEditor-Cmd -run=pythonscript` and enforce a done marker:
  - [scripts/run_ue_python_and_check_done.sh](scripts/run_ue_python_and_check_done.sh)
- Configure Unreal executable outside the skill:
  - set `UE_BIN` in your environment, or ensure `UnrealEditor-Cmd` is available in `PATH`
- Treat missing marker as failure even when process exit code is 0.

For local refactors, prefer leaving behind:
- the target asset path
- the graph address actually used
- the intended change boundary
- `graph.verify` output
- exact node or edge proof only when the task depends on it

For a compact mode choice table, read [references/mode-selection.md](references/mode-selection.md).

## Layout Rules
- Prefer readable left-to-right flow from upstream expressions into downstream consumers and root properties.
- For multi-input nodes, use deterministic source ordering when pin semantics exist, for example `A`, `B`, `Alpha`.
- Keep all expression nodes left of Material Output.
- Treat `layoutGraph(scope=\"touched\")` as a convenience, not as proof of correctness. Re-query and inspect positions if layout quality matters.
- For Material layout verification, prefer `position` or `layout.position` from `graph.query`; `nodePosX/nodePosY` may be null.

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
