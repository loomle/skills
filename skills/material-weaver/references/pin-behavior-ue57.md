# UE 5.7 Pin Behavior Notes

## Key Rule
For several unary nodes in UE 5.7 MaterialEditingLibrary, input pin name must be empty string `""`.

## Confirmed Behavior
- `MaterialExpressionComponentMask`: use input pin `""` (not `"Input"`).
- `MaterialExpressionFloor`: use input pin `""`.
- `MaterialExpressionFrac`: use input pin `""`.
- `MaterialExpressionSine`: use input pin `""`.
- `MaterialExpressionAbs`: use input pin `""`.
- `MaterialExpressionOneMinus`: use input pin `""`.
- `MaterialExpressionSaturate`: in practice, also prefer input pin `""` when direct Loomle or MaterialEditingLibrary wiring rejects `"Input"`.

## Binary / Multi-input Nodes
- `MaterialExpressionMultiply`: `A`, `B`.
- `MaterialExpressionAdd`: `A`, `B`.
- `MaterialExpressionLinearInterpolate`: `A`, `B`, `Alpha`.

## Practical Guidance
- If `connect_material_expressions(...)` returns `False`, first try pin `""` for unary nodes.
- Do not assume UI-visible label `Input` is the Python pin name.
- Do not assume `graph.query` pin labels always round-trip directly into `connectPins`; verify with a tiny probe if a connection unexpectedly fails.
- Material function input labels may differ between displayed labels and accepted connection labels.
- Keep a small probe script for uncertain node classes.
