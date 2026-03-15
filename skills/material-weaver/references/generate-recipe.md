# Generate Recipe

Use this recipe when creating most or all of a Material graph from scratch.

## Best Fit
- new Material authored from a design spec
- repeatable generation from a known template
- graph creation that should live as a script artifact

## Preferred Mode
Use `UE Python mode` by default.

## Steps
1. Decide whether to create a new asset or versioned copy.
2. Build or update a Python generator script.
3. Use deterministic node placement and helper functions.
4. Create nodes in stable groups:
   - parameters and constants
   - core math chains
   - root-property hookups
5. Fail fast on any bad connection.
6. Save and compile only after mandatory edges succeed.
7. Emit a unique done marker.
8. If useful, query the result afterward with Loomle for an independent semantic check.

## Minimum Script Features
- explicit asset path
- helper functions for connect and layout
- compile and save
- structured success output
- unique done marker

## Avoid
- interactive ad hoc generation for large graphs
- relying on manual editor state
- leaving the script without any success marker
