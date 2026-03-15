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
2. Fetch fresh `graph.actions` if node creation by action is needed.
3. Add nodes in a small local cluster.
4. Connect the insertion point into the new cluster.
5. Connect the new cluster back into the existing graph.
6. Layout touched nodes.
7. Re-query and verify exact new edges.
8. Compile.

## Avoid
- extending multiple unrelated regions in one batch
- mixing too many creation and reconnection steps without an intermediate readback
