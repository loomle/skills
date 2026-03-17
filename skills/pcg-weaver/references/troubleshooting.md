# Troubleshooting

## Symptom: A new PCG connection reports success but no edge appears
- Cause: pin name guess was wrong or the node exposes a different output than expected.
- Fix: re-query the exact node and connect using the returned pin names.

## Symptom: `connectPins` complains that it requires from/to node references
- Cause: the mutate payload used top-level node ID fields instead of nested endpoint objects.
- Fix: send `args.from` and `args.to`, each with `nodeId` or `nodeRef` plus `pin`.

## Symptom: Batch fails and the graph is left half-changed
- Cause: mutate batches may partially commit before a later op fails.
- Fix: re-query immediately, trust the current snapshot, then repair from the observed state.

## Symptom: Replacing a middle pipeline stage leaves the graph temporarily disconnected
- Cause: the old stage was removed before the replacement chain was fully introduced and verified.
- Fix: stage the rewrite in two passes:
  1. add the new nodes
  2. re-query their real pins
  3. remove the old stage and reconnect from the observed state

## Symptom: Pipeline shape looks right but behavior may still be broken
- Cause: graph-level verification and scene-level behavior are different surfaces.
- Fix: use `graph.verify` to validate the PCG asset itself, then run a separate level-instance check only if the task explicitly depends on generated world output.

## Symptom: `setPinDefault` fails after disconnecting an overridable PCG input
- Cause: this is the intended Loomle path for writing overridable PCG defaults, but current versions may still have node-specific bugs or incomplete support.
- Fix: keep the successful disconnect, re-query the node, and continue from the observed state. Do not assume the whole batch rolled back.

## Symptom: A semantic op resolves but the inserted stage does not behave as intended
- Cause: the resolve result was only the first half of the rewrite, or it needed narrower pin context.
- Fix: retry `graph.ops.resolve` with `fromPin` or `toPin` when requested, execute the resolved plan, then explicitly reconnect preserved downstream edges and validate the graph with `graph.verify`.

## Symptom: A level instance behaves differently even though the graph verifies cleanly
- Cause: the graph asset is healthy, but the scene instance, input data, or level setup changed the runtime outcome.
- Fix: keep graph repair and scene-instance debugging separate. Do not rewrite the graph unless the graph-level evidence points back to the asset itself.

## Symptom: Local rewrite made the graph harder to read
- Cause: touched nodes were added without a local layout pass.
- Fix: prefer `layoutGraph(scope=\"touched\")` and re-query positions if readability matters.
