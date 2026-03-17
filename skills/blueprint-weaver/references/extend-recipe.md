# Extend Recipe

Use this recipe when extending a Blueprint graph with a larger but planned addition.

## Best Fit
- add a new local branch segment
- add a reusable utility chain near an existing flow
- extend an existing graph with a small feature without reauthoring the whole graph

## Preferred Mode
Use `LOOMLE mode`.

## Steps
1. Query the graph and identify the insertion point.
2. Prefer `graph.ops.resolve` for known semantic additions and use `preferredPlan` as the default creation path.
3. If semantic planning does not cover the desired node, fall back to deterministic `addNode.byClass` only after collecting the exact current graph context.
4. Add nodes in a small local cluster.
5. If same-batch wiring through fresh `clientRef`s fails, re-query and finish with explicit `nodeId`s.
6. Connect the insertion point into the new cluster.
7. Connect the new cluster back into the existing graph.
8. Layout touched nodes.
9. Re-query and verify exact new edges.
10. Compile.

## Avoid
- extending multiple unrelated regions in one batch
- mixing too many creation and reconnection steps without an intermediate readback
- assuming semantic planning removes the need to respect Blueprint type and pin-context constraints
