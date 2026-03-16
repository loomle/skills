# Repair Recipe

Use this recipe for small corrective edits to an existing Material graph.

## Best Fit
- broken or missing wire
- wrong root property connection
- one node feeding the wrong consumer
- local cleanup after a partial failed rewrite

## Preferred Mode
Use `LOOMLE mode` first.

## Steps
1. Query the current Material graph.
2. Identify the exact bad edge or missing edge.
3. Verify the source node ID, destination node ID, and pin names before mutating.
4. If the repair needs a new well-known node, call `graph.ops.resolve` first and reuse its `preferredPlan`.
5. Apply the smallest possible batch:
   - `disconnectPins` or `breakPinLinks` with `args.target = { nodeId, pin }`
   - then one or two `connectPins`
6. Re-query immediately.
7. Confirm the exact repaired edge exists.
8. Compile if the edit was structural.

## Good Example Shape
- disconnect wrong `Alpha` input
- reconnect the right source into the same `Alpha`
- query and verify only that local region

## Avoid
- deleting a large chain just to fix one edge
- trusting mutate success without readback
- guessing unary pin names on UE 5.7
- hardcoding a class path for a common node when `graph.ops.resolve` already covers it
