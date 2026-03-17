# PCG Node Catalog

Generated from local Unreal Engine PCG source headers.

Use this file as a discovery map, not as the only source of truth for live pin behavior.
For exact runtime pin names or dynamic pin shapes, follow up with Loomle `graph.query` on a real graph or inspect the specific header/cpp implementation.

## Search Tips

- Index source: `/Users/xartest/dev/skills/skills/pcg-weaver/references/pcg-node-catalog-index.json`
- JSON source: `/Users/xartest/dev/skills/skills/pcg-weaver/references/pcg-node-catalog.json`
- Start with the lighter index when you only need class/title/category lookup.
- Find by node title: `rg -n '"defaultNodeTitle": ".*Add Tags' pcg-node-catalog.json`
- Find by class: `rg -n 'UPCGAddTagSettings' pcg-node-catalog.json`
- Find overridable properties: `rg -n 'PCG_Overridable' pcg-node-catalog.json`

## Summary

- Total settings classes: `178`
- Classes with dynamic pins: `38`

## Source Groups

- `Elements`: `173`
- `PCGInputOutputSettings.h`: `1`
- `PCGSettings.h`: `1`
- `PCGSettingsWithDynamicInputs.h`: `1`
- `PCGSubgraph.h`: `2`

## Example Entries

### Add Component
- Class: `UPCGAddComponentSettings`
- Header: `Elements/PCGAddComponent.h`
- Node Name: `AddComponent`
- Tooltip: Adds component(s) to specified target actor(s).
- Dynamic Pins: `False`
- Interface Hooks: `Input=True` `Output=True`
- Key Properties:
  - `bUseClassAttribute`: `bool` [Settings] (BlueprintReadWrite, EditAnywhere)
  - `ClassAttribute`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `TemplateComponentClass`: `TSubclassOf<UActorComponent>` [Settings] (BlueprintReadOnly, EditAnywhere)
  - `bAllowTemplateComponentEditing`: `bool` [Settings] (BlueprintReadWrite, EditAnywhere)
  - `TemplateComponent`: `TObjectPtr<UActorComponent>` [Settings] (BlueprintReadWrite, EditAnywhere)

### Add Tags
- Class: `UPCGAddTagSettings`
- Header: `Elements/PCGAddTag.h`
- Node Name: `AddTags`
- Tooltip: Applies the specified tags on the output data.
- Dynamic Pins: `True`
- Interface Hooks: `Input=False` `Output=True`
- Key Properties:
  - `TagsToAdd`: `FString` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `Prefix`: `FString` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `Suffix`: `FString` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `bIgnoreTagValueParsing`: `bool` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `bTokenizeOnWhiteSpace`: `bool` [Settings] (EditAnywhere)

### Apply Hierarchy
- Class: `UPCGApplyHierarchySettings`
- Header: `Elements/PCGApplyHierarchy.h`
- Node Name: `ApplyHierarchy`
- Dynamic Pins: `False`
- Interface Hooks: `Input=True` `Output=True`
- Key Properties:
  - `PointKeyAttributes`: `TArray<FPCGAttributePropertyInputSelector>` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `ParentKeyAttributes`: `TArray<FPCGAttributePropertyInputSelector>` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `HierarchyDepthAttribute`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `RelativeTransformAttribute`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `ApplyParentRotation`: `EPCGApplyHierarchyOption` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)

### Apply On Object
- Class: `UPCGApplyOnActorSettings`
- Header: `Elements/PCGApplyOnActor.h`
- Node Name: `ApplyOnActor`
- Tooltip: Applies property overrides and executes functions on a target object.
- Dynamic Pins: `True`
- Interface Hooks: `Input=True` `Output=True`
- Key Properties:
  - `ObjectReferenceAttribute`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `TargetActor`: `TSoftObjectPtr<AActor>` [Settings] (BlueprintReadWrite)
  - `PropertyOverrideDescriptions`: `TArray<FPCGObjectPropertyOverrideDescription>` [Settings] (BlueprintReadWrite, EditAnywhere)
  - `PostProcessFunctionNames`: `TArray<FName>` [Settings] (BlueprintReadWrite, EditAnywhere)
  - `bSilenceErrorOnEmptyObjectPath`: `bool` [Settings] (AdvancedDisplay, BlueprintReadWrite, EditAnywhere)

### Apply Scale To Bounds
- Class: `UPCGApplyScaleToBoundsSettings`
- Header: `Elements/PCGApplyScaleToBounds.h`
- Node Name: `ApplyScaleToBounds`
- Tooltip: Applies the scale of each point to its bounds and resets the scale.
- Dynamic Pins: `False`
- Interface Hooks: `Input=True` `Output=True`

### Attract
- Class: `UPCGAttractSettings`
- Header: `Elements/PCGAttractElement.h`
- Node Name: `AttractElement`
- Dynamic Pins: `False`
- Interface Hooks: `Input=True` `Output=True`
- Key Properties:
  - `Mode`: `EPCGAttractMode` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `AttractorIndexAttribute`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `Distance`: `double` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `bRemoveUnattractedPoints`: `bool` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `TargetAttribute`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)

### Attribute Cast
- Class: `UPCGAttributeCastSettings`
- Header: `Elements/Metadata/PCGAttributeCast.h`
- Node Name: `AttributeCast`
- Dynamic Pins: `True`
- Interface Hooks: `Input=False` `Output=False`
- Key Properties:
  - `InputSource`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `OutputType`: `EPCGMetadataTypes` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `OutputTarget`: `FPCGAttributePropertyOutputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)

### Attribute Noise
- Class: `UPCGAttributeNoiseSettings`
- Header: `Elements/PCGAttributeNoise.h`
- Node Name: `AttributeNoise`
- Dynamic Pins: `True`
- Interface Hooks: `Input=True` `Output=True`
- Key Properties:
  - `InputSource`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `OutputTarget`: `FPCGAttributePropertyOutputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `Mode`: `EPCGAttributeNoiseMode` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `NoiseMin`: `float` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `NoiseMax`: `float` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)

### Attribute Partition
- Class: `UPCGMetadataPartitionSettings`
- Header: `Elements/Metadata/PCGMetadataPartition.h`
- Node Name: `AttributePartition`
- Dynamic Pins: `True`
- Interface Hooks: `Input=False` `Output=True`
- Key Properties:
  - `PartitionAttributeSelectors`: `TArray<FPCGAttributePropertyInputSelector>` [Settings] (BlueprintReadWrite, EditAnywhere)
  - `PartitionAttributeNames`: `FString` (PCG_Overridable)
  - `bTokenizeOnWhiteSpace`: `bool` [Settings] (EditAnywhere)
  - `bAssignIndexPartition`: `bool` [Settings] (PCG_Overridable, EditAnywhere)
  - `bDoNotPartition`: `bool` [Settings] (PCG_Overridable, EditAnywhere)

### Attribute Remove Duplicates
- Class: `UPCGAttributeRemoveDuplicatesSettings`
- Header: `Elements/PCGAttributeRemoveDuplicates.h`
- Dynamic Pins: `True`
- Interface Hooks: `Input=False` `Output=True`
- Key Properties:
  - `AttributeSelectors`: `TArray<FPCGAttributePropertyInputSelector>` [Settings] (BlueprintReadWrite, EditAnywhere)
  - `AttributeNamesToRemoveDuplicates`: `FString` (PCG_Overridable)

### Attribute Rename
- Class: `UPCGMetadataRenameSettings`
- Header: `Elements/Metadata/PCGMetadataRenameElement.h`
- Node Name: `AttributeRename`
- Dynamic Pins: `True`
- Interface Hooks: `Input=False` `Output=True`
- Key Properties:
  - `AttributeToRename`: `FPCGAttributePropertyInputSelector` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `NewAttributeName`: `FName` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)

### Attribute Set To Point
- Class: `UPCGConvertToPointDataSettings`
- Header: `Elements/PCGCollapseElement.h`
- Node Name: `AttributeSetToPoint`
- Dynamic Pins: `False`
- Interface Hooks: `Input=True` `Output=False`
- Key Properties:
  - `bMatchAttributeNamesWithPropertyNames`: `bool` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `AttributeToConvert`: `TMap<FPCGAttributePropertyInputSelector, FPCGAttributePropertyOutputSelector>` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
  - `bDeleteOriginalRemappedAttribute`: `bool` [Settings] (PCG_Overridable, BlueprintReadWrite, EditAnywhere)
