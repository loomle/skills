#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


SETTINGS_ROOTS = {
    "UPCGSettings",
    "UPCGBaseSubgraphSettings",
    "UPCGSettingsWithDynamicInputs",
}


CLASS_RE = re.compile(
    r"class\s+(?P<name>\w+)\s*:\s*public\s+(?P<base>\w+)\s*\{(?P<body>.*?)\n\};",
    re.DOTALL,
)

def clean_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_nsloctext_arg(expr: str) -> str | None:
    match = re.search(r'NSLOCTEXT\s*\(\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"([^"]*)"\s*\)', expr)
    if match:
        return match.group(1)
    match = re.search(r'FText::FromString\s*\(\s*TEXT\("([^"]*)"\)\s*\)', expr)
    if match:
        return match.group(1)
    return None


def parse_fname_arg(expr: str) -> str | None:
    match = re.search(r'FName\s*\(\s*TEXT\("([^"]*)"\)\s*\)', expr)
    if match:
        return match.group(1)
    match = re.search(r'FName\s*\(\s*"([^"]*)"\s*\)', expr)
    if match:
        return match.group(1)
    return None


def parse_category(meta: str) -> str | None:
    for pattern in [
        r'Category\s*=\s*"([^"]+)"',
        r'Category\s*=\s*([A-Za-z0-9_|]+)',
    ]:
        match = re.search(pattern, meta)
        if match:
            return match.group(1)
    return None


def parse_metadata_flags(meta: str) -> list[str]:
    flags = []
    if "PCG_Overridable" in meta:
        flags.append("PCG_Overridable")
    if "AdvancedDisplay" in meta:
        flags.append("AdvancedDisplay")
    if "BlueprintReadWrite" in meta:
        flags.append("BlueprintReadWrite")
    if "BlueprintReadOnly" in meta:
        flags.append("BlueprintReadOnly")
    if "EditAnywhere" in meta:
        flags.append("EditAnywhere")
    if "VisibleAnywhere" in meta:
        flags.append("VisibleAnywhere")
    if "Transient" in meta:
        flags.append("Transient")
    return flags


def parse_property_name(decl: str) -> str | None:
    line = clean_ws(decl.rstrip(";"))
    if "=" in line:
        line = line.split("=", 1)[0].strip()
    match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", line)
    return match.group(1) if match else None


def parse_property_type(decl: str, prop_name: str | None) -> str:
    line = clean_ws(decl.rstrip(";"))
    if "=" in line:
        line = line.split("=", 1)[0].strip()
    line = line.lstrip(") ").strip()
    if prop_name and line.endswith(prop_name):
        return line[: -len(prop_name)].strip()
    return line


def extract_uproperty_entries(body: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    cursor = 0
    while True:
        start = body.find("UPROPERTY(", cursor)
        if start == -1:
            break
        i = start + len("UPROPERTY(")
        depth = 1
        while i < len(body) and depth > 0:
            char = body[i]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            i += 1
        meta = body[start + len("UPROPERTY(") : i - 1]
        while i < len(body) and body[i].isspace():
            i += 1
        decl_start = i
        while i < len(body) and body[i] != ";":
            i += 1
        decl = body[decl_start : i + 1]
        entries.append((meta, decl))
        cursor = i + 1
    return entries


def parse_header(path: Path, root: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries = []
    for match in CLASS_RE.finditer(text):
        name = match.group("name")
        base = match.group("base")
        body = match.group("body")
        rel = path.relative_to(root).as_posix()
        source_group = rel.split("/", 1)[0] if "/" in rel else rel
        title_match = re.search(r"GetDefaultNodeTitle\s*\(\)\s*const\s*override\s*\{([^}]*)\}", body, re.DOTALL)
        tooltip_match = re.search(r"GetNodeTooltipText\s*\(\)\s*const\s*override\s*\{([^}]*)\}", body, re.DOTALL)
        name_match = re.search(r"GetDefaultNodeName\s*\(\)\s*const\s*override\s*\{([^}]*)\}", body, re.DOTALL)

        properties = []
        for raw_meta, raw_decl in extract_uproperty_entries(body):
            meta = clean_ws(raw_meta)
            decl = clean_ws(raw_decl)
            prop_name = parse_property_name(decl)
            properties.append(
                {
                    "name": prop_name,
                    "cppType": parse_property_type(decl, prop_name),
                    "declaration": decl,
                    "category": parse_category(meta),
                    "flags": parse_metadata_flags(meta),
                    "meta": meta,
                }
            )

        entries.append(
            {
                "className": name,
                "baseClassName": base,
                "headerPath": str(path),
                "relativeHeaderPath": rel,
                "sourceGroup": source_group,
                "defaultNodeName": parse_fname_arg(name_match.group(1)) if name_match else None,
                "defaultNodeTitle": parse_nsloctext_arg(title_match.group(1)) if title_match else None,
                "nodeTooltip": parse_nsloctext_arg(tooltip_match.group(1)) if tooltip_match else None,
                "hasDynamicPins": "HasDynamicPins() const override { return true; }" in body,
                "implementsInputPinProperties": "InputPinProperties() const override" in body,
                "implementsOutputPinProperties": "OutputPinProperties() const override" in body,
                "implementsCreateElement": "CreateElement() const override" in body,
                "implementsSupportsBasePointDataInputs": "SupportsBasePointDataInputs" in body,
                "properties": [p for p in properties if p.get("name")],
            }
        )
    return entries


def derive_settings_classes(classes: dict[str, dict]) -> dict[str, dict]:
    derived = {}
    changed = True
    while changed:
        changed = False
        for name, info in classes.items():
            base = info["baseClassName"]
            if name in derived:
                continue
            if base in SETTINGS_ROOTS or base in derived:
                derived[name] = info
                changed = True
    return derived


def build_markdown(catalog: dict) -> str:
    lines = [
        "# PCG Node Catalog",
        "",
        "Generated from local Unreal Engine PCG source headers.",
        "",
        "Use this file as a discovery map, not as the only source of truth for live pin behavior.",
        "For exact runtime pin names or dynamic pin shapes, follow up with Loomle `graph.query` on a real graph or inspect the specific header/cpp implementation.",
        "",
        "## Search Tips",
        "",
        f"- Index source: `{catalog['indexPath']}`",
        f"- JSON source: `{catalog['jsonPath']}`",
        "- Start with the lighter index when you only need class/title/category lookup.",
        "- Find by node title: `rg -n '\"defaultNodeTitle\": \".*Add Tags' pcg-node-catalog.json`",
        "- Find by class: `rg -n 'UPCGAddTagSettings' pcg-node-catalog.json`",
        "- Find overridable properties: `rg -n 'PCG_Overridable' pcg-node-catalog.json`",
        "",
        "## Summary",
        "",
        f"- Total settings classes: `{catalog['summary']['totalSettingsClasses']}`",
        f"- Classes with dynamic pins: `{catalog['summary']['dynamicPinClasses']}`",
        "",
        "## Source Groups",
        "",
    ]

    for group, count in sorted(catalog["summary"]["sourceGroups"].items()):
        lines.append(f"- `{group}`: `{count}`")

    lines.extend(["", "## Example Entries", ""])
    for entry in catalog["nodes"][:12]:
        lines.append(f"### {entry['defaultNodeTitle'] or entry['className']}")
        lines.append(f"- Class: `{entry['className']}`")
        lines.append(f"- Header: `{entry['relativeHeaderPath']}`")
        if entry.get("defaultNodeName"):
            lines.append(f"- Node Name: `{entry['defaultNodeName']}`")
        if entry.get("nodeTooltip"):
            lines.append(f"- Tooltip: {entry['nodeTooltip']}")
        lines.append(f"- Dynamic Pins: `{entry['hasDynamicPins']}`")
        lines.append(f"- Interface Hooks: `Input={entry['implementsInputPinProperties']}` `Output={entry['implementsOutputPinProperties']}`")
        if entry["properties"]:
            lines.append("- Key Properties:")
            for prop in entry["properties"][:5]:
                flag_text = f" ({', '.join(prop['flags'])})" if prop["flags"] else ""
                category_text = f" [{prop['category']}]" if prop.get("category") else ""
                lines.append(f"  - `{prop['name']}`: `{prop['cppType']}`{category_text}{flag_text}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def build_index(nodes: list[dict]) -> dict:
    index_nodes = []
    for node in nodes:
        index_nodes.append(
            {
                "className": node["className"],
                "baseClassName": node["baseClassName"],
                "defaultNodeName": node["defaultNodeName"],
                "defaultNodeTitle": node["defaultNodeTitle"],
                "nodeTooltip": node["nodeTooltip"],
                "sourceGroup": node["sourceGroup"],
                "relativeHeaderPath": node["relativeHeaderPath"],
                "hasDynamicPins": node["hasDynamicPins"],
                "propertyCount": len(node["properties"]),
                "propertyNames": [prop["name"] for prop in node["properties"]],
                "propertyCategories": sorted(
                    {
                        prop["category"]
                        for prop in node["properties"]
                        if prop.get("category")
                    }
                ),
                "flags": sorted(
                    {
                        flag
                        for prop in node["properties"]
                        for flag in prop.get("flags", [])
                    }
                ),
            }
        )
    return {"nodes": index_nodes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--engine-root",
        default="/Users/Shared/Epic Games/UE_5.7/Engine",
        help="Path to Unreal Engine root",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "references"),
        help="Directory for generated outputs",
    )
    args = parser.parse_args()

    public_root = Path(args.engine_root) / "Plugins/PCG/Source/PCG/Public"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    classes: dict[str, dict] = {}
    for header in sorted(public_root.rglob("*.h")):
        for entry in parse_header(header, public_root):
            classes[entry["className"]] = entry

    settings_classes = derive_settings_classes(classes)
    nodes = sorted(
        settings_classes.values(),
        key=lambda item: (
            item["sourceGroup"],
            item["defaultNodeTitle"] or item["className"],
            item["className"],
        ),
    )

    source_groups = Counter(node["sourceGroup"] for node in nodes)
    catalog = {
        "engineRoot": str(Path(args.engine_root)),
        "sourceRoot": str(public_root),
        "indexPath": str(output_dir / "pcg-node-catalog-index.json"),
        "jsonPath": str(output_dir / "pcg-node-catalog.json"),
        "summary": {
            "totalSettingsClasses": len(nodes),
            "dynamicPinClasses": sum(1 for node in nodes if node["hasDynamicPins"]),
            "sourceGroups": dict(sorted(source_groups.items())),
        },
        "nodes": nodes,
    }

    index_path = output_dir / "pcg-node-catalog-index.json"
    json_path = output_dir / "pcg-node-catalog.json"
    md_path = output_dir / "pcg-node-catalog.md"
    index_path.write_text(json.dumps(build_index(nodes), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    md_path.write_text(build_markdown(catalog), encoding="utf-8")
    print(f"Wrote {index_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
