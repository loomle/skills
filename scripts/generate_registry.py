#!/usr/bin/env python3
"""
Generate a machine-readable registry index for all repository skills.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_skills import ROOT, iter_skill_dirs, load_yaml

REPO_URL = "https://github.com/loomle/skills"
REGISTRY_PATH = ROOT / "registry" / "index.json"


def load_frontmatter(skill_dir: Path) -> dict:
    content = (skill_dir / "SKILL.md").read_text()
    _, frontmatter_block, _ = content.split("---", 2)
    import yaml

    data = yaml.safe_load(frontmatter_block)
    if not isinstance(data, dict):
        raise ValueError(f"{skill_dir.name}: invalid SKILL.md frontmatter")
    return data


def build_skill_entry(skill_dir: Path) -> dict:
    frontmatter = load_frontmatter(skill_dir)
    openai_yaml = load_yaml(skill_dir / "agents" / "openai.yaml")
    interface = openai_yaml["interface"]
    skill_name = frontmatter["name"]

    return {
        "name": skill_name,
        "description": frontmatter["description"],
        "display_name": interface["display_name"],
        "short_description": interface["short_description"],
        "default_prompt": interface["default_prompt"],
        "path": f"skills/{skill_name}",
        "source_url": f"{REPO_URL}/tree/main/skills/{skill_name}",
    }


def build_registry() -> dict:
    skills = [build_skill_entry(skill_dir) for skill_dir in iter_skill_dirs()]
    return {
        "schema_version": 1,
        "repo": {
            "name": "loomle/skills",
            "url": REPO_URL,
            "branch": "main",
        },
        "skills": skills,
    }


def render_registry(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate registry/index.json for Loomle skills.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if registry/index.json is out of date instead of rewriting it.",
    )
    args = parser.parse_args()

    rendered = render_registry(build_registry())

    if args.check:
        if not REGISTRY_PATH.exists():
            print("registry/index.json is missing")
            return 1
        current = REGISTRY_PATH.read_text()
        if current != rendered:
            print("registry/index.json is out of date")
            return 1
        print("registry/index.json is up to date")
        return 0

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(rendered)
    print(f"Wrote {REGISTRY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
