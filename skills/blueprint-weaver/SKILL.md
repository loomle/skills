---
name: blueprint-weaver
description: Blueprint graph specialist for Unreal Engine. Use when tasks involve reading, repairing, refactoring, or extending Blueprint graphs. Prefer Loomle graph.query/mutate for interactive edits, preserve external exec/data interfaces during local rewrites, and verify every structural change with readback plus compile.
---

# Blueprint Weaver

## Overview
Use this skill as the strategy layer for Unreal Blueprint graph work.

- Default to `Loomle` for graph reading, local rewrites, layout, and graph-level verification.
- Keep edits small and verifiable: `query -> mutate -> graph.verify`.
- Preserve external graph interfaces whenever replacing a local node chain or branch segment.

## Workflow
1. Confirm scope and target Blueprint asset plus graph name.
2. Choose the narrowest task recipe.
3. Query before mutating.
4. Execute in small verified batches.
5. Re-query or `graph.verify` after each structural change.
6. Preserve project style and graph readability.

## Mutation Safety
- Treat `graph.mutate` as potentially partial-commit unless readback proves otherwise.
- For local branch or chain replacement, prefer:
  1. identify the preserved upstream and downstream interfaces
  2. add the replacement nodes
  3. reconnect the preserved interfaces
  4. remove the old local chain
- Refresh `graph.actions` in the current asset and graph before reusing `actionToken` values.

## Task Routing
Pick the narrowest recipe that matches the request.

- Broken exec flow, bad data wire, missing node connection, or local cleanup:
  read [references/repair-recipe.md](references/repair-recipe.md)
- Replace a branch segment, insert a local control flow chain, or preserve external interfaces during rewrite:
  read [references/subgraph-replace-recipe.md](references/subgraph-replace-recipe.md)
- Build or extend a Blueprint graph with a larger planned addition:
  read [references/extend-recipe.md](references/extend-recipe.md)

## 1) Confirm Scope
- Identify the target Blueprint asset path.
- Identify the exact graph name before mutating, for example `EventGraph` or `ToggleJetpack`.
- Identify whether the task is:
  - repair
  - local refactor
  - subgraph replacement
  - graph extension
- Identify what external inputs and outputs must remain stable.

## 2) Loomle Mode
Use this path first for Blueprint work.

Recommended rhythm:
1. `graph.query` the target Blueprint graph.
2. Identify the exact rewrite boundary before mutating.
3. For known semantic nodes, call `graph.ops.resolve` on the exact target graph and prefer the returned `preferredPlan`.
4. If adding nodes by action, fetch fresh `graph.actions` from the same asset and graph only when semantic planning does not cover the desired node.
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

## 3) Node Creation Guidance
Prefer the simplest node-creation path that is reliable in the current graph.

- Use `graph.ops.resolve` first for stable semantic ops such as common control-flow nodes. Reuse the returned `preferredPlan` instead of hardcoding class paths when possible.
- For edge-sensitive semantic ops such as `core.reroute`, include the narrowest available pin context. If resolve succeeds with pin context, treat the returned steps as the opening move and let the skill finish downstream reconnects and verification.
- Use `addNode.byAction` when you already have a valid action token for the current graph context and semantic planning does not cover the node you need.
- Use `addNode.byClass` when deterministic construction is easier or action discovery is noisy.
- Do not reuse Blueprint `actionToken` values across different assets or graph contexts.
- If `graph.ops.resolve` returns `resolved=false` with reasons like `requires_pin_context`, treat that as a signal to gather more context or fall back to graph-specific creation guidance rather than forcing the semantic op.
- Do not assume a semantic plan fully inserts a node into an existing edge. Re-query after the planned steps and explicitly restore downstream connections before deleting old local wiring.

Read [references/action-token-notes.md](references/action-token-notes.md) before caching or reusing node-creation context.

## 4) Run and Verify
- Prefer `graph.verify` after every structural batch. Use a fresh `graph.query` when you need exact node or edge proof or when verify returns unexpected diagnostics.
- Treat `layoutGraph(scope=\"touched\")` as a readability helper, not as proof that the structure is correct.
- Trust readback over mutate optimism if there is any disagreement.

## 5) Layout Rules
- Keep exec flow readable left to right.
- Keep `then` / `else` fanout visually separated when possible.
- Preserve nearby local context; do not trigger unnecessary whole-graph churn.
- Prefer `layoutGraph(scope=\"touched\")` before any global layout.

## 6) Validation Contract
Always leave behind enough evidence that another agent could confirm the edit worked.

Minimum expectations:
- identify the target asset and graph name
- show the local rewrite boundary
- use `graph.verify` after structural edits

For local refactors, prefer verifying:
- node count changed in the expected direction
- specific new node IDs exist
- specific old edges are gone
- specific replacement edges are present
- preserved upstream and downstream interfaces still connect as intended

## Troubleshooting
- If node creation fails, refresh `graph.actions` on the current asset and graph before retrying.
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
