#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


HEADER_ROOT = Path("/Users/Shared/Epic Games/UE_5.7/Engine/Source/Editor/BlueprintGraph/Classes")
SOURCE_ROOT = Path("/Users/Shared/Epic Games/UE_5.7/Engine/Source/Editor/BlueprintGraph")


CLASS_RE = re.compile(
    r"UCLASS\((?P<meta>.*?)\)\s*class\s+(?:(?P<api>\w+)\s+)?(?P<name>UK2Node_[A-Za-z0-9_]+)\s*:\s*public\s+(?P<bases>[^{]+)\{(?P<body>.*?)\n\};",
    re.DOTALL,
)


def clean_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def derive_display_title(class_name: str) -> str:
    text = class_name
    if text.startswith("UK2Node_"):
        text = text[len("UK2Node_") :]
    text = text.replace("_", " ")
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    return clean_ws(text)


def parse_text_expr(expr: str | None) -> str | None:
    if not expr:
        return None
    patterns = [
        r'LOCTEXT\s*\(\s*"[^"]*"\s*,\s*"([^"]*)"\s*\)',
        r'NSLOCTEXT\s*\(\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"([^"]*)"\s*\)',
        r'INVTEXT\s*\(\s*"([^"]*)"\s*\)',
        r'FText::FromString\s*\(\s*TEXT\("([^"]*)"\)\s*\)',
        r'TEXT\("([^"]*)"\)',
    ]
    for pattern in patterns:
        match = re.search(pattern, expr, re.DOTALL)
        if match:
            return clean_ws(match.group(1))
    return None


def extract_method_body(text: str, class_name: str, method_name: str) -> str | None:
    patterns = [
        rf"FText\s+{class_name}::{method_name}\s*\([^)]*\)\s*const\s*\{{(?P<body>.*?)\n\}}",
        rf"FText\s+{class_name}::{method_name}\s*\([^)]*\)\s*\{{(?P<body>.*?)\n\}}",
        rf"bool\s+{class_name}::{method_name}\s*\([^)]*\)\s*const\s*\{{(?P<body>.*?)\n\}}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group("body")
    return None


def parse_category(meta: str) -> str | None:
    patterns = [
        r'Category\s*=\s*"([^"]+)"',
        r'Category\s*=\s*([A-Za-z0-9_|]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, meta)
        if match:
            return match.group(1)
    return None


def parse_keywords(meta: str) -> list[str]:
    keywords = []
    match = re.search(r'Keywords\s*=\s*"([^"]+)"', meta)
    if match:
        keywords.extend([clean_ws(x) for x in match.group(1).split() if clean_ws(x)])
    return keywords


def parse_class_flags(meta: str, bases: list[str], body: str) -> list[str]:
    flags = []
    if "MinimalAPI" in meta:
        flags.append("MinimalAPI")
    if "abstract" in meta.lower():
        flags.append("Abstract")
    if "BlueprintInternalUseOnly" in meta:
        flags.append("BlueprintInternalUseOnly")
    if "DeprecatedNode" in meta:
        flags.append("DeprecatedNode")
    if "IK2Node_AddPinInterface" in bases:
        flags.append("DynamicPins")
    if "ShouldShowNodeProperties() const override { return true; }" in body:
        flags.append("ShowsNodeProperties")
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


def collect_cpp_map(root: Path) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for path in root.rglob("K2Node*.cpp"):
        mapping.setdefault(path.stem, path)
    return mapping


def derive_semantic_hints(class_name: str, bases: list[str]) -> dict:
    hints: dict[str, list[str] | bool] = {}
    if class_name == "UK2Node_Knot":
        hints["ops"] = ["core.reroute"]
        hints["requiresContext"] = ["fromPin"]
    elif class_name == "UK2Node_IfThenElse":
        hints["ops"] = ["bp.flow.branch"]
        hints["requiresContext"] = ["fromPin"]
    elif class_name == "UK2Node_ExecutionSequence":
        hints["ops"] = ["bp.flow.sequence"]
        hints["requiresContext"] = ["fromPin"]
    elif class_name == "UK2Node_VariableGet":
        hints["ops"] = ["bp.var.get"]
        hints["requiresHints"] = ["variableName"]
    elif class_name == "UK2Node_VariableSet":
        hints["ops"] = ["bp.var.set"]
        hints["requiresHints"] = ["variableName"]

    if "IK2Node_AddPinInterface" in bases:
        hints["hasDynamicPins"] = True
    return hints


def parse_header(path: Path, cpp_map: dict[str, Path]) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: list[dict] = []
    for match in CLASS_RE.finditer(text):
        meta = clean_ws(match.group("meta"))
        class_name = match.group("name")
        bases = [clean_ws(part.split()[-1]) for part in match.group("bases").split(",")]
        body = match.group("body")
        rel = path.relative_to(SOURCE_ROOT).as_posix()
        cpp_path = cpp_map.get(path.stem)
        cpp_text = cpp_path.read_text(encoding="utf-8", errors="ignore") if cpp_path and cpp_path.exists() else ""

        title_body = extract_method_body(cpp_text, class_name, "GetNodeTitle") or extract_method_body(body, class_name, "GetNodeTitle")
        tooltip_body = extract_method_body(cpp_text, class_name, "GetTooltipText") or extract_method_body(body, class_name, "GetTooltipText")

        properties = []
        for raw_meta, raw_decl in extract_uproperty_entries(body):
            prop_meta = clean_ws(raw_meta)
            decl = clean_ws(raw_decl)
            prop_name = parse_property_name(decl)
            if not prop_name:
                continue
            properties.append(
                {
                    "name": prop_name,
                    "cppType": parse_property_type(decl, prop_name),
                    "category": parse_category(prop_meta),
                    "meta": prop_meta,
                }
            )

        entries.append(
            {
                "className": class_name,
                "baseClassName": bases[0] if bases else None,
                "baseClasses": bases,
                "relativeHeaderPath": rel,
                "headerPath": str(path),
                "relativeCppPath": cpp_path.relative_to(SOURCE_ROOT).as_posix() if cpp_path else None,
                "displayTitleHint": parse_text_expr(title_body) or derive_display_title(class_name),
                "tooltipHint": parse_text_expr(tooltip_body),
                "categoryHint": parse_category(meta),
                "keywords": parse_keywords(meta),
                "flags": parse_class_flags(meta, bases, body),
                "semanticHints": derive_semantic_hints(class_name, bases),
                "hasGetMenuActions": "GetMenuActions(" in body,
                "hasAllocateDefaultPins": "AllocateDefaultPins(" in body,
                "hasExpandNode": "ExpandNode(" in body,
                "hasValidateNodeDuringCompilation": "ValidateNodeDuringCompilation(" in body,
                "hasNodeProperties": "ShouldShowNodeProperties() const override { return true; }" in body,
                "properties": properties,
            }
        )
    return entries


def build_index(nodes: list[dict]) -> dict:
    return {
        "summary": {
            "totalNodes": len(nodes),
            "dynamicPinNodes": sum(1 for node in nodes if node["semanticHints"].get("hasDynamicPins")),
            "categories": dict(Counter(node["categoryHint"] or "uncategorized" for node in nodes)),
        },
        "nodes": [
            {
                "className": node["className"],
                "baseClassName": node["baseClassName"],
                "displayTitleHint": node["displayTitleHint"],
                "categoryHint": node["categoryHint"],
                "relativeHeaderPath": node["relativeHeaderPath"],
                "relativeCppPath": node["relativeCppPath"],
                "flags": node["flags"],
                "semanticHints": node["semanticHints"],
                "propertyCount": len(node["properties"]),
                "propertyNames": [prop["name"] for prop in node["properties"]],
            }
            for node in nodes
        ],
    }


def build_markdown(catalog: dict) -> str:
    lines = [
        "# Blueprint Node Catalog",
        "",
        "Generated from local Unreal Engine BlueprintGraph headers and matching cpp files.",
        "",
        "Use this as a local discovery map for node classes, likely titles, hints, and fallback creation paths.",
        "Do not treat it as the final authority for live pin layouts; use Loomle `graph.query` on a real graph when pin names or type-compatibility matter.",
        "",
        "## Search Tips",
        "",
        f"- Index source: `{catalog['indexPath']}`",
        f"- JSON source: `{catalog['jsonPath']}`",
        "- Start with the lighter index for class/title/category lookup.",
        "- Find reroute-related nodes: `rg -n 'reroute|Knot' blueprint-node-catalog-index.json`",
        "- Find variable nodes: `rg -n 'Variable(Set|Get)' blueprint-node-catalog.json`",
        "- Find nodes with dynamic pins: `rg -n 'DynamicPins' blueprint-node-catalog-index.json`",
        "",
        "## Summary",
        "",
        f"- Total node classes: `{catalog['summary']['totalNodes']}`",
        f"- Classes with dynamic pins: `{catalog['summary']['dynamicPinNodes']}`",
        "",
        "## Category Hints",
        "",
    ]
    for category, count in sorted(catalog["summary"]["categories"].items()):
        lines.append(f"- `{category}`: `{count}`")

    lines.extend(["", "## Example Entries", ""])
    for entry in catalog["nodes"][:12]:
        lines.append(f"### {entry['displayTitleHint']}")
        lines.append(f"- Class: `{entry['className']}`")
        lines.append(f"- Base: `{entry['baseClassName']}`")
        lines.append(f"- Header: `{entry['relativeHeaderPath']}`")
        if entry.get("relativeCppPath"):
            lines.append(f"- Cpp: `{entry['relativeCppPath']}`")
        if entry.get("tooltipHint"):
            lines.append(f"- Tooltip: {entry['tooltipHint']}")
        if entry.get("categoryHint"):
            lines.append(f"- Category: `{entry['categoryHint']}`")
        if entry["flags"]:
            lines.append(f"- Flags: `{', '.join(entry['flags'])}`")
        if entry["semanticHints"]:
            lines.append(f"- Semantic Hints: `{json.dumps(entry['semanticHints'], ensure_ascii=False)}`")
        if entry["properties"]:
            lines.append("- Key Properties:")
            for prop in entry["properties"][:5]:
                category = f" [{prop['category']}]" if prop.get("category") else ""
                lines.append(f"  - `{prop['name']}`: `{prop['cppType']}`{category}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cpp_map = collect_cpp_map(SOURCE_ROOT)
    nodes: list[dict] = []
    for header in sorted(HEADER_ROOT.glob("K2Node*.h")):
        nodes.extend(parse_header(header, cpp_map))

    nodes.sort(key=lambda node: (node["displayTitleHint"] or node["className"], node["className"]))
    index = build_index(nodes)
    catalog = {
        "summary": index["summary"],
        "indexPath": "references/blueprint-node-catalog-index.json",
        "jsonPath": "references/blueprint-node-catalog.json",
        "nodes": nodes,
    }

    (output_dir / "blueprint-node-catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "blueprint-node-catalog-index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "blueprint-node-catalog.md").write_text(
        build_markdown(catalog),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
