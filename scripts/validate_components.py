#!/usr/bin/env python3
"""Validate distributable Claude Code components under src/claude/.

This script is a boundary validator: it holds no rules of its own. Every frontmatter
constraint lives in schemas/skill.json and schemas/agent.json, which are the
single authorities and carry their source citations. The checks implemented here are
the ones a per-file JSON Schema cannot express:

- a skill's `name` must equal its directory name (the directory is the /command);
- an agent's filename stem must equal its `name` (identity comes only from `name`);
- agent names must be unique across the whole tree (the harness otherwise loads one
  by filesystem read order);
- a SKILL.md body stays within the documented 500-line guidance, which this contract
  makes a hard limit;
- a skill directory must contain SKILL.md (the required entrypoint);
- component classes without a contract (anything besides skills/ and agents/) are
  rejected until a contract exists — the class that was 'commands' is rejected by
  name, because custom commands were merged into skills.

Frontmatter parsing is shared via scripts/frontmatter_lib.py.

src/claude/ may not exist yet: the contract precedes the first component by design
(docs/adr/0009). That state is reported and exits 0 — it is a declared commitment,
not a validation failure.

Declared dependencies: PyYAML, jsonschema. Both are required; the script exits with a
named error rather than degrading silently if either is missing.

Usage:  scripts/validate_components.py [source_root]   (default: src/claude)
Exit:   0 all components valid (or tree absent), 1 validation failures, 2 cannot run
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from generator_lib import REPO_ROOT, display
from frontmatter_lib import split_frontmatter
from cli import cannot_run

SKILL_SCHEMA_PATH = REPO_ROOT / "schemas" / "skill.json"
AGENT_SCHEMA_PATH = REPO_ROOT / "schemas" / "agent.json"

# Documented guidance ("Keep SKILL.md under 500 lines"), made a hard limit here —
# the rationale is recorded in docs/adr/0009-component-contracts-from-anthropic-documentation.md.
MAX_SKILL_BODY_LINES = 500

HOOK_SCHEMA_PATH = REPO_ROOT / "schemas" / "hook.json"
HOOK_DECLARATION = "hooks.declaration.json"

PLUGIN_SCHEMA_PATH = REPO_ROOT / "schemas" / "plugin.json"
PLUGIN_DIR = ".claude-plugin"
PLUGIN_MANIFEST = "plugin.json"

COMMANDS_MERGED = (
    "custom commands were merged into skills "
    "(https://code.claude.com/docs/en/skills, retrieved 2026-07-29) — "
    "author src/claude/skills/<name>/SKILL.md instead"
)

try:
    import yaml
except ImportError:
    cannot_run("cannot run: PyYAML is not installed (pip install pyyaml)")

try:
    from jsonschema import Draft202012Validator
except ImportError:
    cannot_run("cannot run: jsonschema is not installed (pip install jsonschema)")


def load_validator(schema_path: Path) -> Draft202012Validator:
    if not schema_path.is_file():
        cannot_run(f"cannot run: schema {schema_path} does not exist")
    return Draft202012Validator(json.loads(schema_path.read_text()))


def parse(path: Path, failures: list[str]) -> tuple[dict, str] | None:
    rel = display(path)
    try:
        return split_frontmatter(path.read_text())
    except ValueError as exc:
        failures.append(f"{rel}: {exc}")
    except yaml.YAMLError as exc:
        failures.append(f"{rel}: frontmatter is not valid YAML: {exc}")
    return None


def schema_errors(validator: Draft202012Validator, data: dict, rel: str, failures: list[str]) -> bool:
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    seen: set[str] = set()
    for err in errors:
        where = ".".join(str(p) for p in err.path) or "(root)"
        message = err.message
        # A dependentSchemas failure reports against the document root, hiding which
        # field triggered it. Name the trigger from the schema path — this reads the
        # schema's own structure, it encodes no rule of its own. Two trigger fields
        # can demand the same thing; the dedup below collapses the repeat.
        schema_path = list(err.absolute_schema_path)
        if schema_path and schema_path[0] == "dependentSchemas":
            message = f"{message} (required by the presence of '{schema_path[1]}')"
            where = str(schema_path[1])
        line = f"{rel}: {where}: {message}"
        if line not in seen:
            seen.add(line)
            failures.append(line)
    return bool(errors)


# Directories under the framework source that carry payload rather than a Claude Code
# component. The harness never reads them: foundation/0008 calls them "Siegard's own", resolved
# through ${CLAUDE_PLUGIN_ROOT}. They have contracts of their own — check_contract_versions.py
# locks the schemas and scaffold.py expands the templates — so a component contract here would
# be a second authority over a file that already has one.
PAYLOAD_DIRS = frozenset({"bin", "schemas", "templates"})


def check_skills(root: Path, failures: list[str]) -> int:
    validator = load_validator(SKILL_SCHEMA_PATH)
    checked = 0
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            failures.append(
                f"{display(entry)}: skills/ holds one directory per skill; a loose file is not a skill"
            )
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.is_file():
            failures.append(f"{display(entry)}: skill directory has no SKILL.md, the required entrypoint")
            continue
        checked += 1
        rel = display(skill_md)
        parsed = parse(skill_md, failures)
        if parsed is None:
            continue
        data, body = parsed
        if schema_errors(validator, data, rel, failures):
            continue
        if data["name"] != entry.name:
            failures.append(
                f"{rel}: name '{data['name']}' must equal the directory name '{entry.name}' — "
                f"the directory name is what becomes the /command"
            )
        body_lines = len(body.splitlines())
        if body_lines > MAX_SKILL_BODY_LINES:
            failures.append(
                f"{rel}: body is {body_lines} lines, over the {MAX_SKILL_BODY_LINES}-line limit — "
                f"move detail into supporting files the skill references"
            )
    return checked


def check_agents(root: Path, failures: list[str]) -> int:
    validator = load_validator(AGENT_SCHEMA_PATH)
    checked = 0
    seen_names: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        rel = display(path)
        if path.suffix != ".md":
            failures.append(f"{rel}: an agent definition is a .md file; nothing else belongs under agents/")
            continue
        checked += 1
        parsed = parse(path, failures)
        if parsed is None:
            continue
        data, _body = parsed
        if schema_errors(validator, data, rel, failures):
            continue
        name = data["name"]
        if name in seen_names:
            failures.append(
                f"{rel}: name '{name}' already used by {seen_names[name]} — the harness would "
                f"load only one of them, chosen by filesystem read order"
            )
        else:
            seen_names[name] = rel
        if path.stem != name:
            failures.append(f"{rel}: filename must be '{name}.md' to match the name field")
    return checked


def check_hooks(root: Path, failures: list[str]) -> int:
    """Validate the hook declaration, and hold it to the files beside it.

    A hook is a script rather than a frontmatter artifact, so what a per-file schema can check is
    its declaration: `foundation/0010` R10 requires a hook to state its event, its matcher, and its
    guarantee, and R11 its own timeout. `schemas/hook.json` is that contract.

    The cross-file half is the correspondence. A declared hook with no script would install a
    `hooks.json` pointing at nothing, and a script nobody declared would sit in `src/claude/hooks/`
    looking installed while the harness never loads it — the silent failure `foundation/0008` R8 names
    for a different directory and which applies here for the same reason.
    """
    declaration = root / HOOK_DECLARATION
    if not declaration.is_file():
        failures.append(
            f"{display(root)}: hooks/ holds no {HOOK_DECLARATION}, so nothing states what these "
            f"scripts bind (foundation/0010 R10)"
        )
        return 0

    try:
        data = json.loads(declaration.read_text())
    except json.JSONDecodeError as exc:
        failures.append(f"{display(declaration)}: not valid JSON: {exc}")
        return 0

    validator = load_validator(HOOK_SCHEMA_PATH)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    for err in errors:
        where = ".".join(str(p) for p in err.path) or "(root)"
        failures.append(f"{display(declaration)}: {where}: {err.message}")
    if errors:
        return 0

    declared = {entry["file"] for entry in data["hooks"]}
    present = {p.name for p in root.iterdir() if p.is_file() and p.name != HOOK_DECLARATION}
    for name in sorted(declared - present):
        failures.append(
            f"{display(declaration)}: declares {name}, which hooks/ does not hold — the "
            f"installation would point at a script that is not there"
        )
    for name in sorted(present - declared):
        failures.append(
            f"{display(root / name)}: no entry in {HOOK_DECLARATION} declares it, so it would "
            f"never be loaded (foundation/0010 R10)"
        )
    return len(declared & present)


def check_plugin_manifest(entry: Path, failures: list[str]) -> int:
    """Validate `.claude-plugin/plugin.json`, and refuse anything else in that directory.

    The manifest is not a component and has no frontmatter, so it is checked here rather than
    beside skills and agents. `foundation/0008` R8 states that only `plugin.json` goes inside
    `.claude-plugin/`, and that a component placed there is not loaded at all — a failure that
    is silent at run time, which is why it is loud here.
    """
    manifest = entry / PLUGIN_MANIFEST
    for stray in sorted(entry.iterdir()):
        if stray.name != PLUGIN_MANIFEST:
            failures.append(
                f"{display(stray)}: only {PLUGIN_MANIFEST} goes inside {PLUGIN_DIR}/ — anything "
                f"else placed there is not loaded (foundation/0008 R8)"
            )
    if not manifest.is_file():
        failures.append(f"{display(entry)}: {PLUGIN_MANIFEST} is missing — a plugin root requires it")
        return 0

    try:
        data = json.loads(manifest.read_text())
    except json.JSONDecodeError as exc:
        failures.append(f"{display(manifest)}: not valid JSON: {exc}")
        return 0

    validator = load_validator(PLUGIN_SCHEMA_PATH)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "(root)"
        failures.append(f"{display(manifest)}: {where}: {err.message}")
    return 1


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "src" / "claude"
    if not root.is_dir():
        print(
            f"components checked: 0 — {display(root)} does not exist yet; the contract "
            f"precedes the first component (the build plan)"
        )
        return 0

    failures: list[str] = []
    skills = agents = hooks = manifests = 0

    for entry in sorted(root.iterdir()):
        if entry.name == "skills" and entry.is_dir():
            skills = check_skills(entry, failures)
        elif entry.name == "agents" and entry.is_dir():
            agents = check_agents(entry, failures)
        elif entry.name == "hooks" and entry.is_dir():
            hooks = check_hooks(entry, failures)
        elif entry.name == PLUGIN_DIR and entry.is_dir():
            manifests = check_plugin_manifest(entry, failures)
        elif entry.name == "commands":
            failures.append(f"{display(entry)}: {COMMANDS_MERGED}")
        elif entry.name in PAYLOAD_DIRS and entry.is_dir():
            continue
        else:
            failures.append(
                f"{display(entry)}: no contract exists for this component class — add the "
                f"schema and wire it here before shipping the class (CLAUDE.md, Commands)"
            )

    print(
        f"components checked: {skills + agents + hooks} ({skills} skill(s), {agents} agent(s), "
        f"{hooks} hook(s)), "
        f"plugin manifests: {manifests}  "
        f"schemas: {display(SKILL_SCHEMA_PATH)}, {display(AGENT_SCHEMA_PATH)}, "
        f"{display(PLUGIN_SCHEMA_PATH)}, {display(HOOK_SCHEMA_PATH)}"
    )
    if failures:
        print(f"FAILED: {len(failures)} problem(s)\n")
        for f in failures:
            print(f"  {f}")
        return 1
    print("all components valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
