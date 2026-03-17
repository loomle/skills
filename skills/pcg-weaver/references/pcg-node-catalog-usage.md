# PCG Node Catalog Usage

Use this reference when the task needs:
- a broad PCG node inventory
- node titles, tooltips, or source file lookup
- property discovery before deeper graph edits

Start with the index, not the full catalog, unless you already know the exact node you want.

Preferred workflow:
1. Search `pcg-node-catalog-index.json` first for class, title, category, or rough property lookup.
2. Open `pcg-node-catalog.json` only for the small set of matching nodes that need full property detail.
3. Open the listed header only for the final candidate nodes that matter.
4. Use live `graph.query` only when you need real graph-instance pin behavior or dynamic pin names.

Important boundaries:
- The generated catalog is source-derived, not graph-instance-derived.
- It is strong for node identity, tooltip text, source grouping, and editable properties.
- It is not the final authority for dynamic pin layouts or scene/runtime outcomes.
- Treat the full catalog as a second-step lookup, not as default reading material.

Useful patterns:
- Find likely matches fast:
  `rg -n 'Add Tags|Filter Data By Tag|Spawn Actor' /Users/xartest/dev/skills/skills/pcg-weaver/references/pcg-node-catalog-index.json`
- Find by title:
  `rg -n '"defaultNodeTitle": "Add Tags"' /Users/xartest/dev/skills/skills/pcg-weaver/references/pcg-node-catalog.json`
- Find by class:
  `rg -n 'UPCGAddTagSettings' /Users/xartest/dev/skills/skills/pcg-weaver/references/pcg-node-catalog.json`
- Find overridable properties:
  `rg -n 'PCG_Overridable' /Users/xartest/dev/skills/skills/pcg-weaver/references/pcg-node-catalog.json`
