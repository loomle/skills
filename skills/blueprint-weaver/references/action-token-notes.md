# Action Token Notes

Blueprint action tokens are graph-context specific.

## Practical Rules
- Fetch `graph.actions` from the current asset and graph before using `addNode.byAction`.
- Do not reuse action tokens across different Blueprint assets.
- Do not assume a token from one graph remains valid in another graph.
- If action discovery falls back to a generic set, prefer deterministic construction only when the fallback still contains the needed action.

## Recovery
- If token-based node creation fails, refresh `graph.actions` on the current graph.
- If the graph context changed, discard old tokens and fetch new ones.
- If action discovery remains noisy, first check whether `graph.ops.resolve` already covers the semantic node you need.
- Switch to `addNode.byClass` only when semantic planning does not help and token-based discovery remains noisy.
