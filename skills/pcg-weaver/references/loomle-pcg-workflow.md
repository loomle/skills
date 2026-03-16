# Loomle-First PCG Workflow

Use this recipe when editing an existing PCG graph interactively.

## Goal
Make a local PCG pipeline change with:
- explicit readback
- small-batch safety
- compile validation
- runtime validation when generated output matters

## Standard Loop
1. Query the target PCG graph with `graphType="pcg"`.
2. Identify the exact local pipeline boundary.
3. Record preserved upstream inputs and downstream consumers before mutating.
4. For known stages, call `graph.ops.resolve` and prefer its `preferredPlan`, `settingsTemplate`, and `verificationHints`.
5. Apply one small `graph.mutate` batch.
6. Immediately `graph.query` again.
7. Verify:
   - new nodes exist
   - intended edges exist
   - removed edges are gone
   - preserved interfaces still connect correctly
8. Compile.
9. If the edit affects generated runtime output, capture `graph.runtime` before and after regenerate and compare counts or executed node summaries.
10. Repeat only if the previous batch verified cleanly.

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
- compile

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
- For runtime-sensitive PCG edits, prefer `graph.runtime.managedResources` and `inspection` as the final acceptance check.
