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

## Symptom: Graph looks mostly right but behavior may still be broken
- Cause: structural readback alone is insufficient for Blueprint edits.
- Fix: compile after structural edits and treat compile as required validation.

## Symptom: Local rewrite made the graph harder to read
- Cause: touched nodes were added without a local layout pass.
- Fix: prefer `layoutGraph(scope=\"touched\")` and re-query positions if readability matters.
