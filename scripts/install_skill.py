#!/usr/bin/env python3
"""
Install a single skill from this repository into a local skills directory.

Supports:
- local installs from a checked-out repo
- remote installs from github.com/loomle/skills without packaging each skill
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_URL = "https://github.com/loomle/skills"
RAW_BASE = "https://raw.githubusercontent.com/loomle/skills/main"
TREE_API = "https://api.github.com/repos/loomle/skills/git/trees/main?recursive=1"
ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "index.json"
DEFAULT_DEST = Path.home() / ".codex" / "skills"
USER_AGENT = "loomle-skills-installer/0.1"
HTTP_TIMEOUT = 20
MAX_RETRIES = 3


def fetch_url(url: str) -> bytes:
    last_error: Exception | None = None
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
        },
    )
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(request, timeout=HTTP_TIMEOUT) as response:  # nosec - public read-only fetch
                return response.read()
        except (HTTPError, URLError) as exc:
            last_error = exc
            if attempt == MAX_RETRIES:
                break
            time.sleep(0.5 * attempt)
    assert last_error is not None
    raise last_error


def load_json_from_url(url: str) -> dict:
    return json.loads(fetch_url(url).decode("utf-8"))


def load_text_from_url(url: str) -> str:
    return fetch_url(url).decode("utf-8")


def load_registry(registry_path: Path) -> dict:
    return json.loads(registry_path.read_text())


def get_registry_entry(registry: dict, skill_name: str) -> dict:
    for entry in registry.get("skills", []):
        if entry.get("name") == skill_name:
            return entry
    known = ", ".join(sorted(entry.get("name", "") for entry in registry.get("skills", [])))
    raise ValueError(f"Unknown skill '{skill_name}'. Available skills: {known}")


def list_skills(registry: dict) -> int:
    for entry in registry.get("skills", []):
        print(f"{entry['name']}: {entry['short_description']}")
    return 0


def install_local(skill_name: str, skill_path: str, dest_root: Path, force: bool) -> Path:
    source = ROOT / skill_path
    if not source.exists():
        raise FileNotFoundError(f"Skill path not found in repository: {source}")
    dest = dest_root / skill_name
    if dest.exists():
        if not force:
            raise FileExistsError(f"{dest} already exists. Re-run with --force to replace it.")
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    return dest


def fetch_remote_tree() -> list[dict]:
    tree_data = load_json_from_url(TREE_API)
    return tree_data.get("tree", [])


def install_remote(skill_name: str, skill_path: str, dest_root: Path, force: bool) -> Path:
    dest = dest_root / skill_name
    if dest.exists():
        if not force:
            raise FileExistsError(f"{dest} already exists. Re-run with --force to replace it.")
        shutil.rmtree(dest)

    prefix = f"{skill_path.rstrip('/')}/"
    entries = [entry for entry in fetch_remote_tree() if entry.get("path", "").startswith(prefix)]
    if not entries:
        raise FileNotFoundError(f"No files found for remote skill path '{skill_path}'")

    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{skill_name}-install-") as tmp:
        tmp_root = Path(tmp)
        for entry in entries:
            if entry.get("type") != "blob":
                continue
            relative = Path(entry["path"]).relative_to(skill_path)
            target = tmp_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            raw_url = f"{RAW_BASE}/{entry['path']}"
            target.write_text(load_text_from_url(raw_url))
            if entry.get("mode") == "100755":
                target.chmod(target.stat().st_mode | 0o111)
        shutil.copytree(tmp_root, dest, dirs_exist_ok=True)
    return dest


def validate_install(dest: Path) -> None:
    skill_md = dest / "SKILL.md"
    if not skill_md.exists():
        raise RuntimeError(f"Installed skill is missing SKILL.md: {dest}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install skills from loomle/skills.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available skills from the local registry.")

    install = subparsers.add_parser("install", help="Install one skill.")
    install.add_argument("skill_name", help="Skill name to install.")
    install.add_argument(
        "--dest",
        default=str(DEFAULT_DEST),
        help=f"Destination root for installed skills (default: {DEFAULT_DEST})",
    )
    install.add_argument(
        "--source",
        choices=("local", "remote"),
        default="remote",
        help="Install from the local checkout or from GitHub (default: remote).",
    )
    install.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing installed skill with the same name.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    registry = load_registry(REGISTRY_PATH)

    if args.command == "list":
        return list_skills(registry)

    entry = get_registry_entry(registry, args.skill_name)
    dest_root = Path(os.path.expanduser(args.dest)).resolve()
    dest_root.mkdir(parents=True, exist_ok=True)

    try:
        if args.source == "local":
            installed = install_local(args.skill_name, entry["path"], dest_root, args.force)
        else:
            installed = install_remote(args.skill_name, entry["path"], dest_root, args.force)
        validate_install(installed)
    except (FileExistsError, FileNotFoundError, ValueError, RuntimeError, HTTPError, URLError) as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1

    print(f"Installed {args.skill_name} to {installed}")
    print(f"Source: {entry['source_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
