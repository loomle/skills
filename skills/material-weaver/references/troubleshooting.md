# Troubleshooting

## Symptom: Node exists but wire is missing
- Cause: wrong pin name for `connect_material_expressions`.
- Fix: use `""` for unary-node input pins in UE 5.7.

## Symptom: Loomle reports success but the graph still looks wrong
- Cause: mutate success does not replace readback verification.
- Fix: run a fresh `graph.query` immediately and verify the exact expected edges and nodes.

## Symptom: Reconnect fails even though the output pin looked obvious before
- Cause: many Material expression outputs now read back as `None`.
- Fix: trust the latest `graph.query` snapshot and reuse the returned `fromPin` verbatim instead of guessing labels like `Output` or `DefaultValue`.

## Symptom: Material graph address works in query but not in list/discovery
- Cause: current Loomle entry behavior can differ between Material read paths.
- Fix: prefer the address form that already succeeds in the active session and use `context` to recover graph refs.

## Symptom: Command succeeded but result is wrong
- Cause: only process exit code was checked.
- Fix: require a unique `DONE` marker line in log output.

## Symptom: Output node overlaps graph cluster
- Cause: layout anchors too far right.
- Fix: move the rightmost expression column left.

## Symptom: Minor overlap remains
- Cause: single-pass layout.
- Fix: run second column-wise anti-overlap pass with node-height estimates.

## Symptom: Crossed lines near multi-input nodes
- Cause: non-deterministic vertical order of source nodes.
- Fix: enforce deterministic input-source ordering (for example by pin priority), then rerun column anti-overlap.
