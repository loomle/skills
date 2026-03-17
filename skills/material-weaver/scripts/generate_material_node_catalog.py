#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


HEADER_ROOT = Path("/Users/Shared/Epic Games/UE_5.7/Engine/Source/Runtime/Engine/Public/Materials")
SOURCE_ROOT = Path("/Users/Shared/Epic Games/UE_5.7/Engine/Source/Runtime/Engine")


CLASS_RE = re.compile(
    r"UCLASS\((?P<meta>.*?)\)\s*class\s+(?:(?P<api>\w+)\s+)?(?P<name>UMaterialExpression[A-Za-z0-9_]+)\s*:\s*public\s+(?P<base>\w+)\s*\{(?P<body>.*?)\n\};",
    re.DOTALL,
)


def clean_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def derive_display_title(class_name: str) -> str:
    text = class_name
    if text.startswith("UMaterialExpression"):
        text = text[len("UMaterialExpression") :]
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
        rf"void\s+{class_name}::{method_name}\s*\([^)]*\)\s*const\s*\{{(?P<body>.*?)\n\}}",
        rf"FString\s+{class_name}::{method_name}\s*\([^)]*\)\s*const\s*\{{(?P<body>.*?)\n\}}",
        rf"FText\s+{class_name}::{method_name}\s*\([^)]*\)\s*const\s*\{{(?P<body>.*?)\n\}}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group("body")
    return None


def parse_keywords_from_body(body: str) -> str | None:
    match = re.search(r"GetKeywords\s*\([^)]*\)\s*const\s*\{([^}]*)\}", body, re.DOTALL)
    if not match:
        return None
    return parse_text_expr(match.group(1))


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


def parse_property_flags(meta: str) -> list[str]:
    flags = []
    for token in [
        "EditAnywhere",
        "Transient",
        "AdvancedDisplay",
        "BlueprintReadOnly",
        "BlueprintReadWrite",
        "ShowAsInputPin",
        "OverridingInputProperty",
        "RequiredInput",
    ]:
        if token in meta:
            flags.append(token)
    return flags


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
    for path in root.rglob("MaterialExpression*.cpp"):
        mapping.setdefault(path.stem, path)
    return mapping


def derive_root_hints(class_name: str) -> list[str]:
    hints = {
        "UMaterialExpressionMultiply": ["BaseColor", "Roughness", "Metallic", "EmissiveColor", "Opacity"],
        "UMaterialExpressionAdd": ["BaseColor", "Roughness", "Metallic", "EmissiveColor", "Opacity"],
        "UMaterialExpressionLinearInterpolate": ["BaseColor", "Roughness", "Metallic", "EmissiveColor", "Opacity"],
        "UMaterialExpressionOneMinus": ["BaseColor", "Roughness", "Metallic", "EmissiveColor", "Opacity"],
        "UMaterialExpressionSaturate": ["BaseColor", "Roughness", "Metallic", "EmissiveColor", "Opacity"],
        "UMaterialExpressionScalarParameter": ["Roughness", "Metallic", "Specular", "Opacity"],
        "UMaterialExpressionVectorParameter": ["BaseColor", "EmissiveColor"],
        "UMaterialExpressionTextureSample": ["BaseColor", "Normal", "EmissiveColor", "Opacity", "Roughness"],
        "UMaterialExpressionMaterialFunctionCall": ["BaseColor", "Roughness", "Metallic", "Normal", "EmissiveColor"],
    }
    return hints.get(class_name, [])


def derive_semantic_hints(class_name: str) -> dict:
    mapping = {
        "UMaterialExpressionMultiply": {"ops": ["mat.math.multiply"]},
        "UMaterialExpressionAdd": {"ops": ["mat.math.add"]},
        "UMaterialExpressionLinearInterpolate": {"ops": ["mat.math.lerp"]},
        "UMaterialExpressionOneMinus": {"ops": ["mat.math.one_minus"]},
        "UMaterialExpressionSaturate": {"ops": ["mat.math.saturate"]},
        "UMaterialExpressionScalarParameter": {"ops": ["mat.param.scalar"]},
        "UMaterialExpressionVectorParameter": {"ops": ["mat.param.vector"]},
        "UMaterialExpressionTextureSample": {"ops": ["mat.texture.sample"]},
        "UMaterialExpressionTextureSampleParameter2D": {"ops": ["mat.param.texture"]},
        "UMaterialExpressionMaterialFunctionCall": {"ops": ["mat.func.call"]},
        "UMaterialExpressionConstant": {"ops": ["mat.constant.scalar"]},
        "UMaterialExpressionConstant3Vector": {"ops": ["mat.constant.vector3"]},
    }
    hints = mapping.get(class_name, {}).copy()
    root_hints = derive_root_hints(class_name)
    if root_hints:
        hints["targetRootPins"] = root_hints
    return hints


def parse_header(path: Path, cpp_map: dict[str, Path]) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: list[dict] = []
    for match in CLASS_RE.finditer(text):
        meta = clean_ws(match.group("meta"))
        class_name = match.group("name")
        base = match.group("base")
        body = match.group("body")
        rel = path.relative_to(SOURCE_ROOT).as_posix()
        cpp_path = cpp_map.get(path.stem)
        cpp_text = cpp_path.read_text(encoding="utf-8", errors="ignore") if cpp_path and cpp_path.exists() else ""

        caption_body = extract_method_body(cpp_text, class_name, "GetCaption")
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
                    "flags": parse_property_flags(prop_meta),
                    "meta": prop_meta,
                }
            )

        entries.append(
            {
                "className": class_name,
                "baseClassName": base,
                "relativeHeaderPath": rel,
                "headerPath": str(path),
                "relativeCppPath": cpp_path.relative_to(SOURCE_ROOT).as_posix() if cpp_path else None,
                "displayTitleHint": parse_text_expr(caption_body) or derive_display_title(class_name),
                "keywordsHint": parse_keywords_from_body(body),
                "classFlags": [flag for flag in ["MinimalAPI", "collapsecategories", "hidecategories=Object"] if flag in meta],
                "semanticHints": derive_semantic_hints(class_name),
                "hasInputsView": "GetInputsView()" in body,
                "hasInputNames": "GetInputName(" in body,
                "hasConnectorTooltips": "GetConnectorToolTip(" in body,
                "hasMatchesSearchQuery": "MatchesSearchQuery(" in body,
                "properties": properties,
            }
        )
    return entries


def build_index(nodes: list[dict]) -> dict:
    return {
        "summary": {
            "totalNodes": len(nodes),
            "withSemanticHints": sum(1 for node in nodes if node["semanticHints"]),
            "withRootPinHints": sum(1 for node in nodes if node["semanticHints"].get("targetRootPins")),
            "baseClasses": dict(Counter(node["baseClassName"] or "unknown" for node in nodes)),
        },
        "nodes": [
            {
                "className": node["className"],
                "baseClassName": node["baseClassName"],
                "displayTitleHint": node["displayTitleHint"],
                "relativeHeaderPath": node["relativeHeaderPath"],
                "relativeCppPath": node["relativeCppPath"],
                "semanticHints": node["semanticHints"],
                "propertyCount": len(node["properties"]),
                "propertyNames": [prop["name"] for prop in node["properties"]],
            }
            for node in nodes
        ],
    }


def build_markdown(catalog: dict) -> str:
    lines = [
        "# Material Node Catalog",
        "",
        "Generated from local Unreal Engine Material expression headers and matching cpp files.",
        "",
        "Use this as a discovery map for expression classes, likely captions, semantic op coverage, and common root-sink hints.",
        "Do not treat it as the final authority for live pin names; use Loomle `graph.query` on a real material graph when pin round-trip or function-subgraph behavior matters.",
        "",
        "## Search Tips",
        "",
        f"- Index source: `{catalog['indexPath']}`",
        f"- JSON source: `{catalog['jsonPath']}`",
        "- Start with the lighter index for class/title/root-sink lookup.",
        "- Find multiply-like expressions: `rg -n 'Multiply|mat.math.multiply' material-node-catalog-index.json`",
        "- Find parameter nodes: `rg -n 'Parameter' material-node-catalog.json`",
        "- Find nodes with root pin hints: `rg -n 'targetRootPins' material-node-catalog-index.json`",
        "",
        "## Summary",
        "",
        f"- Total expression classes: `{catalog['summary']['totalNodes']}`",
        f"- Classes with semantic hints: `{catalog['summary']['withSemanticHints']}`",
        f"- Classes with root pin hints: `{catalog['summary']['withRootPinHints']}`",
        "",
        "## Example Entries",
        "",
    ]
    for entry in catalog["nodes"][:12]:
        lines.append(f"### {entry['displayTitleHint']}")
        lines.append(f"- Class: `{entry['className']}`")
        lines.append(f"- Base: `{entry['baseClassName']}`")
        lines.append(f"- Header: `{entry['relativeHeaderPath']}`")
        if entry.get("relativeCppPath"):
            lines.append(f"- Cpp: `{entry['relativeCppPath']}`")
        if entry.get("keywordsHint"):
            lines.append(f"- Keywords: `{entry['keywordsHint']}`")
        if entry["semanticHints"]:
            lines.append(f"- Semantic Hints: `{json.dumps(entry['semanticHints'], ensure_ascii=False)}`")
        if entry["properties"]:
            lines.append("- Key Properties:")
            for prop in entry["properties"][:5]:
                category = f" [{prop['category']}]" if prop.get("category") else ""
                flags = f" ({', '.join(prop['flags'])})" if prop["flags"] else ""
                lines.append(f"  - `{prop['name']}`: `{prop['cppType']}`{category}{flags}")
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
    for header in sorted(HEADER_ROOT.glob("MaterialExpression*.h")):
        nodes.extend(parse_header(header, cpp_map))

    nodes.sort(key=lambda node: (node["displayTitleHint"] or node["className"], node["className"]))
    index = build_index(nodes)
    catalog = {
        "summary": index["summary"],
        "indexPath": "references/material-node-catalog-index.json",
        "jsonPath": "references/material-node-catalog.json",
        "nodes": nodes,
    }

    (output_dir / "material-node-catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "material-node-catalog-index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "material-node-catalog.md").write_text(
        build_markdown(catalog),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
