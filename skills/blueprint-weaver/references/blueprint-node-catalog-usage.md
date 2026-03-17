# Blueprint Node Catalog Usage

Use the local Blueprint node catalog when you need a broad node inventory or a fallback discovery map outside the current semantic `graph.ops` surface.

## Recommended Lookup Order
1. Start with `references/blueprint-node-catalog-index.json`.
2. Open `references/blueprint-node-catalog.json` only for the small matching subset that needs more detail.
3. Open the listed header or cpp file only for the final candidates.
4. Use live Loomle `graph.query` only when you need real graph-instance pins, type compatibility, or exact node wiring proof.

## Best Use Cases
- find likely Blueprint node classes when `graph.ops.resolve` does not cover the stage
- inspect whether a node class has node properties, dynamic pins, or known semantic hints
- locate the engine header/cpp that defines a node's title, tooltip, or fallback behavior
- compare nearby node classes before deciding whether to fall back to `addNode.byClass`

## What This Catalog Is Not
- It is not the final authority for live pin names.
- It is not a substitute for `graph.verify`.
- It is not a replacement for `graph.ops.resolve`; prefer semantic planning first and use this catalog as the fallback discovery layer.
