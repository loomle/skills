# Loomle-First Blueprint Workflow

Use this recipe when editing an existing Blueprint graph interactively.

## Goal
Make a local Blueprint change with:
- explicit readback
- small-batch safety
- compile validation

## Standard Loop
1. Query the target Blueprint graph.
2. Identify the exact local rewrite boundary.
3. Record preserved external inputs and outputs before mutating.
4. Apply one small `graph.mutate` batch.
5. Immediately `graph.query` again.
6. Verify:
   - new nodes exist
   - intended edges exist
   - removed edges are gone
   - preserved interfaces still connect correctly
7. Compile.
8. Repeat only if the previous batch verified cleanly.

## Good Batch Shapes

### Safe local repair
- disconnect or remove one bad local connection
- connect the intended replacement
- query and verify

### Safe subgraph replacement
- query old boundary first
- prefer the graph address form that already succeeds in the current session
- add replacement nodes
- if same-batch wiring through fresh `clientRef`s fails, re-query and finish the wiring with explicit `nodeId`s
- reconnect preserved external inputs
- reconnect preserved external outputs
- remove the old node or small chain only after readback confirms the replacement path
- layout touched nodes
- query and verify
- compile

## Verification Checklist
- Do not trust `changed=true` alone.
- Prefer fresh `graph.query` over mutate optimism.
- If a batch fails, verify what was already committed before retrying.
- For Blueprint specifically, compile after structural edits even when the local snapshot looks correct.
- If `graph.query` by `graphName` is inconsistent, recover a `graphRef` from `graph.list` and continue with that.
