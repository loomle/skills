# Subgraph Replacement Recipe

Use this recipe when replacing an existing Blueprint node chain or branch segment while preserving external interfaces.

## Best Fit
- replace one branch with a richer local control segment
- insert local reroutes around a branch or function call
- replace a short exec/data segment without changing graph entry points

## Preferred Mode
Use `LOOMLE mode`.

## Steps
1. Query the graph.
2. Identify the replacement boundary:
   - external exec inputs to preserve
   - external data inputs to preserve
   - external downstream consumers to preserve
   - nodes to remove
3. Write down the preserved edges before changing anything.
4. Prefer the graph address form that already succeeds in the current session.
5. Add the replacement nodes first.
6. Reconnect preserved exec and data inputs into the new subgraph.
7. Reconnect preserved downstream outputs from the new subgraph.
8. Remove the old node or small chain only after the replacement path is present.
9. Run `layoutGraph(scope=\"touched\")`.
10. Re-query and verify the preserved interface plus new internal edges.
11. Compile.

## Verification Checklist
- old internal nodes are gone
- preserved upstream connections still land where intended
- preserved downstream consumers are still fed
- the new internal chain is fully connected
- compile succeeds
