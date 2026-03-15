# Loomle-First Material Workflow

Use this recipe when editing an existing Material graph interactively.

## Goal
Make a local Material change with:
- explicit readback
- small-batch safety
- compile validation

## Standard Loop
1. Read current context if the Material is already open.
2. `graph.query` the root Material graph with `graphType="material"`.
3. Identify the exact node IDs and external edges around the subgraph you plan to change.
4. Apply one small `graph.mutate` batch.
5. Immediately `graph.query` again.
6. Verify:
   - new nodes exist
   - intended edges exist
   - removed edges are gone
   - total node/edge counts make sense
7. `compile`
8. Repeat only if the previous batch verified cleanly.

## Good Batch Shapes

### Safe local rewire
- disconnect one edge
- connect one replacement edge
- query and verify

### Safe subgraph replacement
- query old boundary first
- prefer the address form that already succeeds in the current session
- add replacement nodes first
- re-query exact new node IDs and pin behavior before wiring unfamiliar nodes
- reconnect preserved external inputs
- reconnect preserved external outputs
- remove the old node or small chain only after the replacement path is present
- layout touched nodes
- query and verify
- compile

## Verification Checklist
- Do not trust `changed=true` alone.
- Prefer fresh `graph.query` over mutate optimism.
- If a connection reports success but does not appear in the snapshot, treat it as a failed edit.
- For Material specifically, double-check pin names before assuming the edit logic is wrong.
- For layout or move verification, read `position` or `layout.position`; `nodePosX/nodePosY` may be null.

## Material-Specific Notes
- Unary node input pins in UE 5.7 may require `""` instead of the visible `Input` label.
- Many ordinary Material expression outputs now round-trip as `fromPin="None"` in `graph.query`; trust the fresh snapshot over remembered pin labels.
- Ordinary Material pin labels should round-trip into `connectPins`, but special unary, `None`-output, and root-property cases still deserve a tiny probe if a wire unexpectedly fails.
- Root Material properties are special targets; verify the edge lands on the intended root property.

## When To Abort This Path
Switch to `UE Python mode` if:
- you need a large graph generated from scratch
- you need a repeatable script artifact
- Loomle address or pin behavior is inconsistent for the edit
- you need actor assignment or end-to-end command-line execution
