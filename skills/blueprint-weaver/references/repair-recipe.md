# Repair Recipe

Use this recipe for small corrective edits to an existing Blueprint graph.

## Best Fit
- broken exec flow
- wrong data wire
- missing local connection
- cleanup after a partially failed rewrite

## Preferred Mode
Use `LOOMLE mode`.

## Steps
1. Query the current graph.
2. Identify the exact bad edge or missing edge.
3. Verify source node ID, destination node ID, and pin names before mutating.
4. If the repair needs a stable semantic node, call `graph.ops.resolve` first and reuse its `preferredPlan`.
5. Apply the smallest possible batch:
   - `disconnectPins` or `breakPinLinks` with `args.target = { nodeId, pin }`
   - then one or two `connectPins`
6. Re-query immediately.
7. Confirm the repaired local structure exists.
8. Compile if the repair changed structure.

## Avoid
- deleting a large chain just to fix one edge
- trusting mutate success without readback
- mutating before confirming the exact graph name
- forcing a semantic op that reports `requires_pin_context`; narrow the context or fall back
