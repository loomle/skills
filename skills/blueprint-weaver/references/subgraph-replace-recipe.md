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
5. For stable semantic nodes like a branch, call `graph.ops.resolve` and prefer returned `preferredPlan` entries over hardcoded class paths.
6. If semantic planning reports `requires_pin_context`, gather narrower context or fall back instead of forcing the op.
7. Add the replacement nodes first.
8. Reconnect preserved exec and data inputs into the new subgraph.
9. Reconnect preserved downstream outputs from the new subgraph.
10. Remove the old node or small chain only after the replacement path is present.
11. Run `layoutGraph(scope=\"touched\")`.
12. Re-query and verify the preserved interface plus new internal edges.
13. Compile.

## Verification Checklist
- old internal nodes are gone
- preserved upstream connections still land where intended
- preserved downstream consumers are still fed
- the new internal chain is fully connected
- compile succeeds
