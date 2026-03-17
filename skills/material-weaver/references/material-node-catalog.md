# Material Node Catalog

Generated from local Unreal Engine Material expression headers and matching cpp files.

Use this as a discovery map for expression classes, likely captions, semantic op coverage, and common root-sink hints.
Do not treat it as the final authority for live pin names; use Loomle `graph.query` on a real material graph when pin round-trip or function-subgraph behavior matters.

## Search Tips

- Index source: `references/material-node-catalog-index.json`
- JSON source: `references/material-node-catalog.json`
- Start with the lighter index for class/title/root-sink lookup.
- Find multiply-like expressions: `rg -n 'Multiply|mat.math.multiply' material-node-catalog-index.json`
- Find parameter nodes: `rg -n 'Parameter' material-node-catalog.json`
- Find nodes with root pin hints: `rg -n 'targetRootPins' material-node-catalog-index.json`

## Summary

- Total expression classes: `308`
- Classes with semantic hints: `12`
- Classes with root pin hints: `9`

## Example Entries

### Abs
- Class: `UMaterialExpressionAbs`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionAbs.h`
- Key Properties:
  - `Input`: `FExpressionInput`

### Absorption Medium Material Output
- Class: `UMaterialExpressionAbsorptionMediumMaterialOutput`
- Base: `UMaterialExpressionCustomOutput`
- Header: `Public/Materials/MaterialExpressionAbsorptionMediumMaterialOutput.h`
- Key Properties:
  - `TransmittanceColor`: `FExpressionInput`

### Actor Position WS
- Class: `UMaterialExpressionActorPositionWS`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionActorPositionWS.h`
- Key Properties:
  - `OriginType`: `EPositionOrigin` [UMaterialExpressionActorPositionWS] (EditAnywhere, ShowAsInputPin)

### Add
- Class: `UMaterialExpressionAdd`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionAdd.h`
- Semantic Hints: `{"ops": ["mat.math.add"], "targetRootPins": ["BaseColor", "Roughness", "Metallic", "EmissiveColor", "Opacity"]}`
- Key Properties:
  - `A`: `FExpressionInput` (RequiredInput)
  - `B`: `FExpressionInput` (RequiredInput)
  - `ConstA`: `float` [MaterialExpressionAdd] (EditAnywhere, OverridingInputProperty)
  - `ConstB`: `float` [MaterialExpressionAdd] (EditAnywhere, OverridingInputProperty)

### Aggregate
- Class: `UMaterialExpressionAggregate`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionAggregate.h`
- Key Properties:
  - `Kind`: `EMaterialExpressionMakeAggregateKind` [MaterialAggregate] (EditAnywhere)
  - `UserAggregate`: `TObjectPtr<UMaterialAggregate>` [MaterialAggregate] (EditAnywhere)
  - `AttributeNames`: `TArray<FName>` [MaterialAggregate] (EditAnywhere)
  - `PrototypeInput`: `FExpressionInput`
  - `Entries`: `TArray<FMaterialExpressionAggregateEntry>`

### Antialiased Texture Mask
- Class: `UMaterialExpressionAntialiasedTextureMask`
- Base: `UMaterialExpressionTextureSampleParameter2D`
- Header: `Public/Materials/MaterialExpressionAntialiasedTextureMask.h`
- Key Properties:
  - `Threshold`: `float` [MaterialExpressionAntialiasedTextureMask] (EditAnywhere)
  - `Channel`: `TEnumAsByte<enum ETextureColorChannel>` [MaterialExpressionAntialiasedTextureMask] (EditAnywhere)

### Append Vector
- Class: `UMaterialExpressionAppendVector`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionAppendVector.h`
- Key Properties:
  - `A`: `FExpressionInput`
  - `B`: `FExpressionInput`

### Arccosine
- Class: `UMaterialExpressionArccosine`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionArccosine.h`
- Key Properties:
  - `Input`: `FExpressionInput`

### Arccosine Fast
- Class: `UMaterialExpressionArccosineFast`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionArccosineFast.h`
- Key Properties:
  - `Input`: `FExpressionInput`

### Arcsine
- Class: `UMaterialExpressionArcsine`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionArcsine.h`
- Key Properties:
  - `Input`: `FExpressionInput`

### Arcsine Fast
- Class: `UMaterialExpressionArcsineFast`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionArcsineFast.h`
- Key Properties:
  - `Input`: `FExpressionInput`

### Arctangent
- Class: `UMaterialExpressionArctangent`
- Base: `UMaterialExpression`
- Header: `Public/Materials/MaterialExpressionArctangent.h`
- Key Properties:
  - `Input`: `FExpressionInput`
