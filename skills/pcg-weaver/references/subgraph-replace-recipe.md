# Subgraph Replacement Recipe

Use this recipe when replacing an existing PCG pipeline segment while preserving external dataflow interfaces.

## Best Fit
- replace one middle stage with a richer filter/tag/transform chain
- preserve multiple upstream inputs into a replacement subgraph
- insert a local pipeline while keeping the same downstream consumer

## Preferred Mode
Use `Loomle mode`.

## Steps
1. Query the graph.
2. Identify the replacement boundary:
   - upstream inputs to preserve
   - downstream consumers to preserve
   - nodes to remove
3. Write down the preserved edges before changing anything.
4. Prefer `graph.ops.resolve` for known stages and carry forward any returned `settingsTemplate` or `verificationHints`.
5. Add the replacement nodes first.
6. Re-query exact new node IDs and pin names if any stage is unfamiliar.
7. Reconnect preserved upstream inputs into the new subgraph.
8. Reconnect preserved downstream consumers from the new subgraph.
9. Remove the old node or short chain only after the replacement path is present.
10. Run `layoutGraph(scope=\"touched\")`.
11. Run `graph.verify`.
12. Re-query and verify the preserved interface plus new internal edges when verify output is not enough.

## Verification Checklist
- old internal nodes are gone
- preserved upstream connections still land where intended
- preserved downstream consumers are still fed
- the new internal chain is fully connected
- `graph.verify` status and diagnostics are acceptable
