# Loomle-First Blueprint Workflow

Use this recipe when editing an existing Blueprint graph interactively.

## Goal
Make a local Blueprint change with:
- explicit readback
- small-batch safety
- graph-level verify validation

## Standard Loop
1. Query the target Blueprint graph.
2. Identify the exact local rewrite boundary.
3. Record preserved external inputs and outputs before mutating.
4. For known semantic nodes, call `graph.ops.resolve` on the exact target graph and prefer its `preferredPlan`.
5. Apply one small `graph.mutate` batch.
6. Run `graph.verify`.
7. If you need exact node or edge proof, immediately `graph.query` again.
8. Verify:
   - new nodes exist
   - intended edges exist
   - removed edges are gone
   - preserved interfaces still connect correctly
   - verify status and diagnostics are acceptable
9. Repeat only if the previous batch verified cleanly.

## Good Batch Shapes

### Safe local repair
- disconnect or remove one bad local connection
- connect the intended replacement
- query and verify

### Safe subgraph replacement
- query old boundary first
- prefer the graph address form that already succeeds in the current session
- for stable semantic nodes like a branch, prefer `graph.ops.resolve` over hardcoded class paths
- for edge-sensitive semantic nodes like `core.reroute`, retry resolve with `fromPin` or `toPin` context before falling back
- for variable get/set ops, provide `items[*].hints.variableName` before falling back
- add replacement nodes
- treat the resolved plan as the opening move, then explicitly reconnect preserved downstream edges
- if same-batch wiring through fresh `clientRef`s fails, re-query and finish the wiring with explicit `nodeId`s
- reconnect preserved external inputs
- reconnect preserved external outputs
- remove the old node or small chain only after readback confirms the replacement path
- layout touched nodes
- query and verify

## Verification Checklist
- Do not trust `changed=true` alone.
- Prefer fresh `graph.query` over mutate optimism.
- If a batch fails, verify what was already committed before retrying.
- For Blueprint specifically, prefer `graph.verify` after structural edits even when the local snapshot looks correct.
- If `graph.query` by `graphName` is inconsistent, recover a `graphRef` from `graph.list` and continue with that.
- If `graph.ops.resolve` reports `requires_pin_context` or another incompatibility reason, gather the narrower context or fall back instead of forcing the op.
