# Material Node Catalog Usage

Use the local Material node catalog when you need a broad expression inventory or a fallback discovery map outside the current semantic `graph.ops` surface.

## Recommended Lookup Order
1. Start with `references/material-node-catalog-index.json`.
2. Open `references/material-node-catalog.json` only for the small matching subset that needs more detail.
3. Open the listed header or cpp file only for the final candidates.
4. Use live Loomle `graph.query` only when you need real graph-instance pins, `childGraphRef`, or exact root-sink wiring proof.

## Best Use Cases
- find likely Material expression classes when `graph.ops.resolve` does not cover the stage
- inspect whether a node usually participates in a common root property path
- locate the engine header/cpp that defines a node's caption, keywords, or fallback behavior
- compare nearby expression classes before deciding whether to fall back to `addNode.byClass`

## What This Catalog Is Not
- It is not the final authority for live pin names.
- It is not a substitute for `graph.verify`.
- It is not a replacement for `graph.ops.resolve`; prefer semantic planning first and use this catalog as the fallback discovery layer.
