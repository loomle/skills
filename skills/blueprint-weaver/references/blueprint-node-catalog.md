# Blueprint Node Catalog

Generated from local Unreal Engine BlueprintGraph headers and matching cpp files.

Use this as a local discovery map for node classes, likely titles, hints, and fallback creation paths.
Do not treat it as the final authority for live pin layouts; use Loomle `graph.query` on a real graph when pin names or type-compatibility matter.

## Search Tips

- Index source: `references/blueprint-node-catalog-index.json`
- JSON source: `references/blueprint-node-catalog.json`
- Start with the lighter index for class/title/category lookup.
- Find reroute-related nodes: `rg -n 'reroute|Knot' blueprint-node-catalog-index.json`
- Find variable nodes: `rg -n 'Variable(Set|Get)' blueprint-node-catalog.json`
- Find nodes with dynamic pins: `rg -n 'DynamicPins' blueprint-node-catalog-index.json`

## Summary

- Total node classes: `114`
- Classes with dynamic pins: `6`

## Category Hints

- `Utilities|Array`: `1`
- `uncategorized`: `113`

## Example Entries

### Add Component By Class
- Class: `UK2Node_AddComponentByClass`
- Base: `UK2Node_ConstructObjectFromClass`
- Header: `Classes/K2Node_AddComponentByClass.h`
- Cpp: `Private/K2Node_AddComponentByClass.cpp`
- Flags: `MinimalAPI`

### Add Delegate
- Class: `UK2Node_AddDelegate`
- Base: `UK2Node_BaseMCDelegate`
- Header: `Classes/K2Node_AddDelegate.h`
- Flags: `MinimalAPI`

### Add Math Expression...
- Class: `UK2Node_MathExpression`
- Base: `UK2Node_Composite`
- Header: `Classes/K2Node_MathExpression.h`
- Cpp: `Private/K2Node_MathExpression.cpp`
- Flags: `MinimalAPI`
- Key Properties:
  - `Expression`: `FString` [Expression]
  - `bMadeAfterRotChange`: `bool`

### Add Reroute Node...
- Class: `UK2Node_Knot`
- Base: `UK2Node`
- Header: `Classes/K2Node_Knot.h`
- Cpp: `Private/K2Node_Knot.cpp`
- Tooltip: Reroute Node (reroutes wires)
- Flags: `MinimalAPI`
- Semantic Hints: `{"ops": ["core.reroute"], "requiresContext": ["fromPin"]}`

### Add Return Node...
- Class: `UK2Node_FunctionResult`
- Base: `UK2Node_FunctionTerminator`
- Header: `Classes/K2Node_FunctionResult.h`
- Cpp: `Private/K2Node_FunctionResult.cpp`
- Tooltip: The node terminates the function's execution. It returns output parameters.
- Flags: `MinimalAPI, ShowsNodeProperties`

### Add Timeline...
- Class: `UK2Node_Timeline`
- Base: `UK2Node`
- Header: `Classes/K2Node_Timeline.h`
- Cpp: `Private/K2Node_Timeline.cpp`
- Tooltip: Timeline node allows values to be keyframed over time.\nDouble click to open timeline editor.
- Flags: `MinimalAPI, ShowsNodeProperties`
- Key Properties:
  - `TimelineName`: `FName`
  - `TimelineGuid`: `FGuid`

### Add {ComponentType}
- Class: `UK2Node_AddComponent`
- Base: `UK2Node_CallFunction`
- Header: `Classes/K2Node_AddComponent.h`
- Cpp: `Private/K2Node_AddComponent.cpp`
- Flags: `MinimalAPI`
- Key Properties:
  - `TemplateBlueprint`: `FString`
  - `TemplateType`: `TObjectPtr<UClass>`

### Assign
- Class: `UK2Node_AssignmentStatement`
- Base: `UK2Node`
- Header: `Classes/K2Node_AssignmentStatement.h`
- Cpp: `Private/K2Node_AssignmentStatement.cpp`
- Tooltip: Assigns Value to Variable
- Flags: `MinimalAPI`

### Assign {0}
- Class: `UK2Node_AssignDelegate`
- Base: `UK2Node_AddDelegate`
- Header: `Classes/K2Node_AssignDelegate.h`
- Cpp: `Private/K2Node_AssignDelegate.cpp`
- Flags: `MinimalAPI`

### Assign {DelegatePropertyName}
- Class: `UK2Node_DelegateSet`
- Base: `UK2Node`
- Header: `Classes/K2Node_DelegateSet.h`
- Cpp: `Private/K2Node_DelegateSet.cpp`
- Tooltip: {0}\n{1}
- Flags: `MinimalAPI`
- Key Properties:
  - `DelegatePropertyName`: `FName`
  - `DelegatePropertyClass`: `TSubclassOf<class UObject>`

### Async Action
- Class: `UK2Node_AsyncAction`
- Base: `UK2Node_BaseAsyncTask`
- Header: `Classes/K2Node_AsyncAction.h`
- Cpp: `Private/K2Node_AsyncAction.cpp`
- Flags: `MinimalAPI`

### Async Load Asset
- Class: `UK2Node_LoadAsset`
- Base: `UK2Node`
- Header: `Classes/K2Node_LoadAsset.h`
- Cpp: `Private/K2Node_LoadAsset.cpp`
- Tooltip: Asynchronously loads a Soft Object Reference and returns object of the correct type if the load succeeds
- Flags: `MinimalAPI`
