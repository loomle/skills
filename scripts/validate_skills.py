#!/usr/bin/env python3
"""
Validate all skills in this repository.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MAX_SKILL_NAME_LENGTH = 64
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
}


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text())


def validate_frontmatter(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{skill_dir.name}: SKILL.md not found"]

    content = skill_md.read_text()
    if not content.startswith("---"):
        return [f"{skill_dir.name}: no YAML frontmatter found"]

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return [f"{skill_dir.name}: invalid frontmatter format"]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"{skill_dir.name}: invalid YAML in frontmatter: {exc}"]

    if not isinstance(frontmatter, dict):
        return [f"{skill_dir.name}: frontmatter must be a YAML dictionary"]

    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        errors.append(
            f"{skill_dir.name}: unexpected frontmatter keys: {', '.join(sorted(unexpected))}"
        )

    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str) or not name.strip():
        errors.append(f"{skill_dir.name}: missing or invalid frontmatter name")
    else:
        if name != skill_dir.name:
            errors.append(
                f"{skill_dir.name}: frontmatter name '{name}' does not match directory name"
            )
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"{skill_dir.name}: name must be hyphen-case")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append(f"{skill_dir.name}: name cannot start/end with hyphen or contain --")
        if len(name) > MAX_SKILL_NAME_LENGTH:
            errors.append(
                f"{skill_dir.name}: name too long ({len(name)} > {MAX_SKILL_NAME_LENGTH})"
            )

    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_dir.name}: missing or invalid frontmatter description")
    else:
        if "<" in description or ">" in description:
            errors.append(f"{skill_dir.name}: description cannot contain angle brackets")
        if len(description) > 1024:
            errors.append(f"{skill_dir.name}: description exceeds 1024 characters")

    return errors


def validate_openai_yaml(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    path = skill_dir / "agents" / "openai.yaml"
    if not path.exists():
        return [f"{skill_dir.name}: agents/openai.yaml not found"]

    try:
        data = load_yaml(path)
    except yaml.YAMLError as exc:
        return [f"{skill_dir.name}: invalid YAML in agents/openai.yaml: {exc}"]

    if not isinstance(data, dict):
        return [f"{skill_dir.name}: agents/openai.yaml must be a YAML dictionary"]

    interface = data.get("interface")
    if not isinstance(interface, dict):
        return [f"{skill_dir.name}: agents/openai.yaml missing interface mapping"]

    display_name = interface.get("display_name")
    short_description = interface.get("short_description")
    default_prompt = interface.get("default_prompt")

    if not isinstance(display_name, str) or not display_name.strip():
        errors.append(f"{skill_dir.name}: interface.display_name is required")

    if not isinstance(short_description, str) or not short_description.strip():
        errors.append(f"{skill_dir.name}: interface.short_description is required")
    else:
        if not (25 <= len(short_description) <= 64):
            errors.append(
                f"{skill_dir.name}: interface.short_description must be 25-64 chars"
            )

    if not isinstance(default_prompt, str) or not default_prompt.strip():
        errors.append(f"{skill_dir.name}: interface.default_prompt is required")

    return errors


def iter_skill_dirs() -> list[Path]:
    if not SKILLS_DIR.exists():
        return []
    return sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())


def main() -> int:
    skill_dirs = iter_skill_dirs()
    if not skill_dirs:
        print("No skills found under skills/")
        return 1

    errors: list[str] = []
    for skill_dir in skill_dirs:
        errors.extend(validate_frontmatter(skill_dir))
        errors.extend(validate_openai_yaml(skill_dir))

    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(skill_dirs)} skill(s):")
    for skill_dir in skill_dirs:
        print(f"- {skill_dir.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
