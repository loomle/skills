---
name: blueprint-weaver
description: Blueprint graph specialist for Unreal Engine. Use when tasks involve reading, repairing, refactoring, or extending Blueprint graphs. Prefer Loomle graph.query plus graph.ops.resolve/mutate for interactive edits, preserve external exec/data interfaces during local rewrites, and verify every structural change with graph.verify plus readback.
---

# Blueprint Weaver

## Overview
Use this skill as the strategy layer for Unreal Blueprint graph work.

- Default to `Loomle` for graph reading, semantic planning, local rewrites, layout, and graph-level verification.
- Keep edits small and verifiable: `graph.query -> graph.ops.resolve -> graph.mutate -> graph.verify`.
- Preserve external graph interfaces whenever replacing a local node chain or branch segment.

## Mutation Safety
- Treat `graph.mutate` as potentially partial-commit unless readback proves otherwise.
- For local branch or chain replacement, prefer:
  1. identify the preserved upstream and downstream interfaces
  2. add the replacement nodes
  3. reconnect the preserved interfaces
  4. remove the old local chain

## Task Routing
Pick the narrowest recipe that matches the request.

- Need a broad Blueprint node inventory, class lookup, tooltip lookup, or fallback class search:
  read [references/blueprint-node-catalog-usage.md](references/blueprint-node-catalog-usage.md)
- Broken exec flow, bad data wire, missing node connection, or local cleanup:
  read [references/repair-recipe.md](references/repair-recipe.md)
- Replace a branch segment, insert a local control flow chain, or preserve external interfaces during rewrite:
  read [references/subgraph-replace-recipe.md](references/subgraph-replace-recipe.md)
- Build or extend a Blueprint graph with a larger planned addition:
  read [references/extend-recipe.md](references/extend-recipe.md)

## Start Here
- Identify the target Blueprint asset path.
- Identify the exact graph name before mutating, for example `EventGraph` or `ToggleJetpack`.
- Identify whether the task is:
  - repair
  - local refactor
  - subgraph replacement
  - graph extension
- Identify what external inputs and outputs must remain stable.
- Default loop: `graph.query -> graph.ops.resolve -> graph.mutate -> graph.verify`.
- Add a fresh `graph.query` only when you need exact node or edge proof beyond verify output.

## Loomle Mode
Use this path first for Blueprint work.

Recommended rhythm:
1. `graph.query` the target Blueprint graph.
2. Identify the exact rewrite boundary before mutating.
3. For known semantic nodes, call `graph.ops.resolve` on the exact target graph and prefer the returned `preferredPlan`.
4. If semantic planning does not cover the desired node, fall back to deterministic `addNode.byClass` from the exact current graph context.
5. Apply a small `graph.mutate` batch.
6. Prefer `graph.verify` as the default final check for the batch.
7. Use a fresh `graph.query` when you need exact node or edge proof beyond verify output.
8. Verify:
   - new nodes exist
   - expected edges exist
   - removed edges are actually gone
   - preserved external interfaces still land where intended
   - verify status and diagnostics are acceptable
9. Repeat only if the previous batch verified cleanly.

For a concrete Loomle-first edit loop, read [references/loomle-blueprint-workflow.md](references/loomle-blueprint-workflow.md).

## Node Creation Guidance
Prefer the simplest node-creation path that is reliable in the current graph.

- Use the local Blueprint node catalog when you need broad class discovery, likely node titles, fallback header lookup, or a quick check of whether a node exposes properties or dynamic pins.
- Use `graph.ops.resolve` first for stable semantic ops such as common control-flow nodes. Reuse the returned `preferredPlan` instead of hardcoding class paths when possible.
- For edge-sensitive semantic ops such as `core.reroute`, include the narrowest available pin context. If resolve succeeds with pin context, treat the returned steps as the opening move and let the skill finish downstream reconnects and verification.
- For variable get/set ops, pass `items[*].hints.variableName` before falling back to deterministic class-based creation.
- Use `addNode.byClass` when deterministic construction is easier or semantic planning does not cover the node you need.
- If `graph.ops.resolve` returns `resolved=false` with reasons like `requires_pin_context`, treat that as a signal to gather more context or fall back to graph-specific creation guidance rather than forcing the semantic op.
- Do not assume a semantic plan fully inserts a node into an existing edge. Re-query after the planned steps and explicitly restore downstream connections before deleting old local wiring.

Read [references/action-token-notes.md](references/action-token-notes.md) before choosing a fallback creation path for uncovered nodes.

## Verification
- Prefer `graph.verify` after every structural batch. Use a fresh `graph.query` when you need exact node or edge proof or when verify returns unexpected diagnostics.
- Treat `layoutGraph(scope=\"touched\")` as a readability helper, not as proof that the structure is correct.
- Trust readback over mutate optimism if there is any disagreement.

For local refactors, prefer leaving behind:
- the target asset and graph name
- the local rewrite boundary
- `graph.verify` output
- exact proof that preserved upstream and downstream interfaces still connect as intended when the task depends on it

## Layout Rules
- Keep exec flow readable left to right.
- Keep `then` / `else` fanout visually separated when possible.
- Preserve nearby local context; do not trigger unnecessary whole-graph churn.
- Prefer `layoutGraph(scope=\"touched\")` before any global layout.

## Troubleshooting
- If node creation fails, re-query the current graph context and retry with either narrower resolve context or deterministic class-based creation.
- If a mutate batch fails midway, assume earlier ops may already be committed unless proven otherwise by readback.
- If a local replacement risks disconnecting exec flow, stage the new path first and delete the old nodes only after readback confirms the new edges.
- If a connection reports success but the graph snapshot disagrees, trust the fresh query and repair from there.
- If `graph.verify` returns `status=\"ok\"` but the graph still looks wrong, re-query exact node IDs and edges rather than relying on layout.
- If a reroute or similar op resolves only after adding `fromPin` or `toPin`, keep that context in the log so later repair batches can reproduce the same resolve path.

For recurring failure patterns and concrete fixes, read [references/troubleshooting.md](references/troubleshooting.md).

## Scope Boundary
This skill is intentionally Blueprint-focused. It should not become a generic Material or PCG skill.

- Blueprint graph strategy belongs here.
- General graph protocol behavior belongs in `LOOMLE`.
- Project-specific style or naming rules should come from the current repo instructions, not be hardcoded here.
