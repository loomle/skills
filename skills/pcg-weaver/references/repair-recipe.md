# Repair Recipe

Use this recipe for small corrective edits to an existing PCG graph.

## Best Fit
- broken dataflow edge
- wrong downstream consumer
- missing local connection
- cleanup after a partially failed rewrite

## Preferred Mode
Use `LOOMLE mode`.

## Steps
1. Query the current graph.
2. Identify the exact bad edge or missing edge.
3. Verify source node ID, destination node ID, and pin names before mutating.
4. If the repair needs a standard stage, call `graph.ops.resolve` first and reuse its `preferredPlan` or `verificationHints`.
5. Apply the smallest possible batch:
   - `disconnectPins` or `breakPinLinks` with `args.target = { nodeId, pin }`
   - then one or two `connectPins`
6. Re-query immediately.
7. Confirm the repaired local structure exists.
8. Compile if the repair changed structure.

## Avoid
- deleting a large chain just to fix one edge
- trusting mutate success without readback
- assuming a guessed PCG output pin is correct without verification
- skipping `verificationHints` when semantic planning already warned that pin names need readback
