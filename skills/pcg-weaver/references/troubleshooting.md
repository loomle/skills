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
- Cause: structural readback alone is insufficient for PCG edits.
- Fix: compile after structural edits and treat runtime validation as the final check. Compare `graph.runtime.managedResources` and `inspection` before and after regenerate.

## Symptom: A semantic op resolves but the inserted stage does not behave as intended
- Cause: the resolve result was only the first half of the rewrite, or it needed narrower pin context.
- Fix: retry `graph.ops.resolve` with `fromPin` or `toPin` when requested, execute the resolved plan, then explicitly reconnect preserved downstream edges and validate with `graph.runtime`.

## Symptom: Runtime output changed but the graph still looks structurally correct
- Cause: a parameter edge or stage behavior changed output scale without breaking the visible pipeline.
- Fix: trust the runtime evidence, especially `managedResources.totalInstanceCount`, `generatedComponentCount`, and `inspection.nodes`, and repair from the current snapshot.

## Symptom: Local rewrite made the graph harder to read
- Cause: touched nodes were added without a local layout pass.
- Fix: prefer `layoutGraph(scope=\"touched\")` and re-query positions if readability matters.
