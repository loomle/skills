# Troubleshooting

## Symptom: Node creation fails with token-related errors
- Cause: stale or cross-context `actionToken`.
- Fix: refresh `graph.actions` on the current asset and graph, then retry.

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
- Fix: compile after structural edits and treat compile as required validation.

## Symptom: Local rewrite made the graph harder to read
- Cause: touched nodes were added without a local layout pass.
- Fix: prefer `layoutGraph(scope=\"touched\")` and re-query positions if readability matters.
