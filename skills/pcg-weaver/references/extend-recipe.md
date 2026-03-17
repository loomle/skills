# Extend Recipe

Use this recipe when extending a PCG graph with a new local pipeline stage or small stage cluster.

## Best Fit
- add one filter stage
- add a tag or transform stage between existing nodes
- extend a local pipeline without redesigning the whole graph

## Preferred Mode
Use `Loomle mode`.

## Steps
1. Query the graph and identify the insertion point.
2. Prefer `graph.ops.resolve` for known stages and use `preferredPlan` as the default node-creation path.
3. If semantic planning does not cover the needed stage, pick the class from the local PCG node catalog and add it directly with `addNode.byClass`.
4. Add nodes in a small local cluster.
5. If semantic planning returned `verificationHints`, re-query new stages before wiring downstream outputs.
6. Connect the insertion point into the new cluster.
7. Connect the new cluster back into the existing graph.
8. Layout touched nodes.
9. Run `graph.verify`.
10. Re-query exact new edges only when verify output is not enough.

## Avoid
- extending multiple unrelated regions in one batch
- mixing too many creation and reconnection steps without an intermediate readback
- hardcoding a class path for a common PCG stage when `graph.ops.resolve` already knows it
