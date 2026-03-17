# Subgraph Replacement Recipe

Use this recipe when replacing an existing Material node chain with a new structure while preserving external graph interfaces.

## Best Fit
- replace one parameter fanout with a small control tree
- replace one math chain with another
- insert helper nodes between an upstream producer and multiple downstream consumers

## Preferred Mode
Use `LOOMLE mode` first.

## Steps
1. Query the graph.
2. Identify the replacement boundary:
   - external inputs to preserve
   - external outputs to preserve
   - nodes to remove
3. Write down the exact preserved edges before changing anything.
4. Prefer the graph address form that already succeeds in the current session.
5. For common replacement nodes, call `graph.ops.resolve` and convert returned `preferredPlan` entries directly into `graph.mutate` ops.
6. Add the replacement nodes first.
7. Re-query exact new node IDs and pin behavior if any node is unfamiliar.
8. Reconnect preserved external inputs into the new subgraph.
9. Reconnect preserved external outputs from the new subgraph.
10. Remove the old node or subgraph only after the replacement path is present.
11. Run `layoutGraph(scope=\"touched\")`.
12. Re-query and verify the preserved interface plus new internal edges.

## Verification Checklist
- old internal nodes are gone
- preserved upstream connections still land in the new subgraph
- preserved downstream consumers are still fed
- the new internal chain is fully connected
- `graph.verify` status and diagnostics are acceptable

## Escalation Rule
If the replacement gets larger than one local cluster or starts needing repeated pin probing, consider switching to `UE Python mode`.
