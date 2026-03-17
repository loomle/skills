# Node Creation Fallback Notes

Blueprint node creation should stay inside the stable public graph surface.

## Practical Rules
- Prefer `graph.ops.resolve` whenever the desired node has a semantic `opId`.
- If resolve returns `resolved=false`, gather narrower pin or edge context before giving up.
- Use `addNode.byClass` only when semantic planning does not cover the node you need.
- Do not assume fallback creation also handles downstream rewiring; re-query and reconnect preserved interfaces explicitly.

## Recovery
- If semantic creation fails, re-query the current graph and collect exact pin/type context before retrying.
- If the graph context changed, discard old assumptions and resolve again from the current snapshot.
- If class-based creation succeeds but wiring still fails, trust the fresh query and continue with exact returned pin names and types.
