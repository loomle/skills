# Loomle-First PCG Workflow

Use this recipe when editing an existing PCG graph interactively.

## Goal
Make a local PCG pipeline change with:
- explicit readback
- small-batch safety
- graph-level verify validation
- optional scene-level validation when generated output in a level matters

## Standard Loop
1. Query the target PCG graph with `graphType="pcg"`, or if you started from a selected level actor/component, use `context` then `graph.resolve` and continue with the returned PCG `graphRef`.
2. Identify the exact local pipeline boundary.
3. Record preserved upstream inputs and downstream consumers before mutating.
4. For known stages, call `graph.ops.resolve` and prefer its `preferredPlan`, `settingsTemplate`, and `verificationHints`.
5. Apply one small `graph.mutate` batch.
6. Run `graph.verify`.
7. If you need exact node or edge proof, immediately `graph.query` again.
8. Verify:
   - new nodes exist
   - intended edges exist
   - removed edges are gone
   - preserved interfaces still connect correctly
   - verify status and diagnostics are acceptable
9. If the task explicitly depends on world results, do a separate level-instance validation pass after graph verification.
10. Repeat only if the previous batch verified cleanly.

For overridable input pins, the intended edit path is often:
- disconnect the incoming edge
- use `setPinDefault` on that input
- read back the node settings and run `graph.verify`

Treat that path as version-sensitive. If `setPinDefault` currently fails or behaves inconsistently, keep the committed part of the batch, re-query, and continue from the observed state instead of replaying the whole edit blindly.

## Good Batch Shapes

### Safe local repair
- disconnect one bad edge
- reconnect the intended replacement
- query and verify

### Safe pipeline replacement
- query old boundary first
- prefer `graph.ops.resolve` for known stages such as `Add Tag` or `Filter By Tag`
- if resolve asks for narrower context, retry with `fromPin` or `toPin` rather than guessing the stage class path
- add replacement nodes first
- re-query exact new node IDs and pin names if any stage is unfamiliar
- remove the old middle stage or short chain only after the replacement nodes exist
- reconnect preserved upstream inputs
- reconnect preserved downstream outputs
- layout touched nodes
- query and verify

## Connection Shape Reminder
For `connectPins`, use nested endpoint objects instead of top-level `fromNodeId` or `toNodeId`.

Preferred shape:

```json
{
  "op": "connectPins",
  "args": {
    "from": {
      "nodeId": "/Game/Path/Asset.Asset:NodeA",
      "pin": "Out"
    },
    "to": {
      "nodeId": "/Game/Path/Asset.Asset:NodeB",
      "pin": "In"
    }
  }
}
```

You can also use `nodeRef` for nodes created earlier in the same batch.

## Verification Checklist
- Do not trust `changed=true` alone.
- Prefer fresh `graph.query` over mutate optimism.
- If a batch fails, verify what was already committed before retrying.
- For PCG specifically, confirm output pin names from the returned snapshot when introducing unfamiliar nodes.
- If `graph.ops.resolve` supplied `verificationHints`, treat them as required follow-up work, not optional advice.
- For layout or move verification, read `position` or `layout.position`; `nodePosX/nodePosY` may be null.
- Treat `graph.verify` as the default graph-level acceptance check. Any world-instance check happens separately and answers a different question.
