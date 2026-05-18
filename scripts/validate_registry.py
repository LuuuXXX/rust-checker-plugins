#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    print("Python 3.11+ is required (tomllib missing)", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "registry.toml"
PLUGINS_DIR = ROOT / "plugins"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_CATEGORIES = {"quality", "security", "deps", "perf", "compat"}
VALID_TYPES = {"string", "integer", "float", "boolean", "list"}
VALID_PARSERS = {"raw"}


def fail(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError:
        fail(f"Missing TOML file: {path.relative_to(ROOT)}")
    except tomllib.TOMLDecodeError as exc:
        fail(f"Invalid TOML in {path.relative_to(ROOT)}: {exc}")


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate_registry() -> list[dict]:
    data = load_toml(REGISTRY_PATH)
    plugins = data.get("plugin")
    expect(isinstance(plugins, list) and plugins, "registry.toml must contain at least one [[plugin]] entry")

    names = set()
    for entry in plugins:
        expect(isinstance(entry, dict), "Each [[plugin]] entry must be a table")
        name = entry.get("name")
        version = entry.get("version")
        category = entry.get("category")
        path = entry.get("path")

        expect(isinstance(name, str) and NAME_RE.match(name), f"Invalid plugin name in registry: {name!r}")
        expect(name not in names, f"Duplicate plugin name in registry: {name}")
        names.add(name)
        expect(isinstance(version, str) and version.count(".") == 2, f"Invalid version for plugin {name}")
        expect(category in VALID_CATEGORIES, f"Invalid category for plugin {name}: {category!r}")
        expect(isinstance(path, str) and path == f"plugins/{name}/plugin.toml", f"Invalid path for plugin {name}: {path!r}")
        expect((ROOT / path).is_file(), f"Registry path does not exist for plugin {name}: {path}")

    return plugins


def validate_plugin_file(registry_entry: dict) -> None:
    name = registry_entry["name"]
    path = ROOT / registry_entry["path"]
    data = load_toml(path)

    plugin = data.get("plugin")
    command = data.get("command")
    report = data.get("report")
    output_schema = data.get("output_schema")
    dependencies = data.get("dependencies")

    expect(isinstance(plugin, dict), f"[plugin] table missing in {path.relative_to(ROOT)}")
    expect(plugin.get("name") == name, f"plugin.name mismatch in {path.relative_to(ROOT)}")
    expect(plugin.get("version") == registry_entry["version"], f"plugin.version mismatch in {path.relative_to(ROOT)}")
    expect(plugin.get("category") == registry_entry["category"], f"plugin.category mismatch in {path.relative_to(ROOT)}")
    expect(isinstance(plugin.get("description"), str) and plugin["description"].strip(), f"plugin.description missing in {path.relative_to(ROOT)}")
    expect(isinstance(plugin.get("author"), str) and plugin["author"].strip(), f"plugin.author missing in {path.relative_to(ROOT)}")
    expect(isinstance(plugin.get("tags"), list), f"plugin.tags must be a list in {path.relative_to(ROOT)}")

    expect(isinstance(command, dict), f"[command] table missing in {path.relative_to(ROOT)}")
    expect(isinstance(command.get("program"), str) and command["program"].strip(), f"command.program missing in {path.relative_to(ROOT)}")
    expect(isinstance(command.get("args"), list), f"command.args must be a list in {path.relative_to(ROOT)}")
    if "env" in command:
        expect(isinstance(command["env"], dict), f"command.env must be a table in {path.relative_to(ROOT)}")

    expect(isinstance(report, dict), f"[report] table missing in {path.relative_to(ROOT)}")
    parser = report.get("parser")
    output_path = report.get("output_path")
    expect(
        isinstance(parser, str)
        and (parser.startswith("builtin::") or parser.startswith("custom::") or parser in VALID_PARSERS),
        f"Invalid report.parser in {path.relative_to(ROOT)}: {parser!r}",
    )
    expect(isinstance(output_path, str) and output_path.endswith(".md"), f"Invalid report.output_path in {path.relative_to(ROOT)}")

    expect(isinstance(output_schema, dict), f"[output_schema] table missing in {path.relative_to(ROOT)}")
    fields = output_schema.get("fields")
    expect(isinstance(fields, list) and fields, f"[[output_schema.fields]] must contain at least one entry in {path.relative_to(ROOT)}")
    field_names = set()
    for field in fields:
        expect(isinstance(field, dict), f"Each output schema field must be a table in {path.relative_to(ROOT)}")
        field_name = field.get("name")
        field_type = field.get("type")
        field_desc = field.get("description")
        expect(isinstance(field_name, str) and field_name.strip(), f"Field name missing in {path.relative_to(ROOT)}")
        expect(field_name not in field_names, f"Duplicate field name {field_name!r} in {path.relative_to(ROOT)}")
        field_names.add(field_name)
        expect(field_type in VALID_TYPES, f"Invalid field type {field_type!r} in {path.relative_to(ROOT)}")
        expect(isinstance(field_desc, str) and field_desc.strip(), f"Field description missing for {field_name} in {path.relative_to(ROOT)}")

    if dependencies is not None:
        expect(isinstance(dependencies, dict), f"[dependencies] must be a table in {path.relative_to(ROOT)}")
        for dep_kind in ("required", "optional"):
            entries = dependencies.get(dep_kind)
            if entries is None:
                continue
            expect(isinstance(entries, list), f"[[dependencies.{dep_kind}]] must be an array in {path.relative_to(ROOT)}")
            for dep in entries:
                expect(isinstance(dep, dict), f"Each dependency in {path.relative_to(ROOT)} must be a table")
                expect(isinstance(dep.get("name"), str) and dep["name"].strip(), f"Dependency name missing in {path.relative_to(ROOT)}")
                expect(isinstance(dep.get("install"), str) and dep["install"].strip(), f"Dependency install missing in {path.relative_to(ROOT)}")


def validate_directory_consistency(registry_entries: list[dict]) -> None:
    registered = {entry["name"] for entry in registry_entries}
    actual = {
        child.name
        for child in PLUGINS_DIR.iterdir()
        if child.is_dir() and (child / "plugin.toml").is_file()
    }
    missing = sorted(registered - actual)
    extra = sorted(actual - registered)
    expect(not missing, f"Plugins declared in registry but missing on disk: {', '.join(missing)}")
    expect(not extra, f"Plugins present on disk but missing in registry: {', '.join(extra)}")


def main() -> None:
    expect(REGISTRY_PATH.is_file(), "registry.toml not found")
    expect(PLUGINS_DIR.is_dir(), "plugins/ directory not found")

    registry_entries = validate_registry()
    validate_directory_consistency(registry_entries)
    for entry in registry_entries:
        validate_plugin_file(entry)

    print(f"[OK] validated {len(registry_entries)} plugin(s)")


if __name__ == "__main__":
    main()
