# loomle skills

Official Loomle skills for Codex-style local skill runtimes.

This repository currently hosts the first-party `weaver` family:

- `material-weaver`
- `blueprint-weaver`
- `pcg-weaver`

## Layout

```text
skills/
  material-weaver/
  blueprint-weaver/
  pcg-weaver/
```

Each skill is self-contained and follows the standard local skill shape:

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- optional `scripts/`

## Current install model

Until a dedicated Loomle skill registry exists, install by copying a skill folder into the local Codex skills directory:

```bash
cp -R skills/material-weaver ~/.codex/skills/
cp -R skills/blueprint-weaver ~/.codex/skills/
cp -R skills/pcg-weaver ~/.codex/skills/
```

You can also use the repository installer:

```bash
python scripts/install_skill.py list
python scripts/install_skill.py install material-weaver
```

By default the installer downloads just one skill from `loomle/skills` and writes it to `~/.codex/skills/`.
It fetches the skill directory file-by-file from GitHub, so you do not need a full repository clone or a prebuilt zip per skill.

## Validation

This repository includes a minimal GitHub Actions workflow that validates every skill on push and pull request.

You can run the same check locally:

```bash
python scripts/validate_skills.py
```

## Registry Index

The repository also publishes a generated machine-readable index at `registry/index.json`.

Regenerate it locally after adding or editing skills:

```bash
python scripts/generate_registry.py
```

## Included skills

### material-weaver
Material graph specialist for Unreal Engine Material editing with a Loomle-first workflow.

### blueprint-weaver
Blueprint graph specialist for local rewires, repairs, and subgraph replacement.

### pcg-weaver
PCG graph specialist for pipeline rewrites and validation-driven graph edits.
