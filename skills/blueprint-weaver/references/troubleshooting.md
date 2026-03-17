# Troubleshooting

## Symptom: Node creation still fails after semantic planning
- Cause: the node is outside the current semantic catalog, or the resolve call lacks pin/type context.
- Fix: re-query the current graph, gather narrower context, then retry resolve or fall back to deterministic `addNode.byClass`.

## Symptom: Batch fails and the graph is left half-changed
- Cause: mutate batches may partially commit before a later op fails.
- Fix: re-query immediately, trust the current snapshot, then repair from the observed state.

## Symptom: New Blueprint nodes were created, but same-batch `connectPins` could not resolve them
- Cause: a fresh `clientRef` may not always resolve cleanly for later Blueprint wiring ops in the same batch.
- Fix: re-query the graph, collect the concrete `nodeId`s for the newly created nodes, then reconnect in a follow-up batch.

## Symptom: `graph.ops.resolve` reports `requires_pin_context`
- Cause: some semantic ops, such as reroutes, depend on a narrower source-pin context than a whole-graph resolve can express.
- Fix: gather the tighter local context first, or fall back to graph-specific creation guidance instead of forcing the semantic op.

## Symptom: semantic node creation succeeded but later wiring still failed
- Cause: semantic planning helped choose the right node, but Blueprint type compatibility or pin context still rejected the connection.
- Fix: trust the failure, re-query exact pin names and types, then reconnect in a narrower follow-up batch.

## Symptom: Graph looks mostly right but behavior may still be broken
- Cause: structural readback alone is insufficient for Blueprint edits.
- Fix: run `graph.verify` after structural edits and treat verify as the required graph-level validation step.

## Symptom: Local rewrite made the graph harder to read
- Cause: touched nodes were added without a local layout pass.
- Fix: prefer `layoutGraph(scope=\"touched\")` and re-query positions if readability matters.
