#!/usr/bin/env python3
"""
Generates a simplified modlist.json (and modlist.md) from universal.json.

universal.json (manifest_version 3, per the Wynncraft-Overhaul installer format)
has top-level arrays: "mods", "shaderpacks", "resourcepacks", and "remote_include"
(files pulled in from outside the normal mod sources). Each entry has at least
"name" and "version".

Usage: python3 scripts/generate_modlist.py
Reads:  universal.json
Writes: modlist.json, modlist.md
"""

import json
from pathlib import Path

SRC = Path("universal.json")
OUT_JSON = Path("modlist.json")
OUT_MD = Path("modlist.md")

# Which top-level keys in universal.json map to which output section.
SECTION_MAP = {
    "mods": "mods",
    "shaderpacks": "shaders",
    "resourcepacks": "texturepacks",
    "remote_include": "other",
}


def extract_entries(items):
    """Pull just name + version from each entry, sorted alphabetically."""
    entries = []
    for item in items:
        name = item.get("name")
        version = item.get("version", "unknown")
        if not name:
            continue
        entries.append({"name": name, "version": version})
    entries.sort(key=lambda e: e["name"].lower())
    return entries


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))

    result = {
        "modpack_name": data.get("name"),
        "modpack_version": data.get("modpack_version"),
        "minecraft_version": data.get("minecraft_version"),
    }

    for src_key, out_key in SECTION_MAP.items():
        result[out_key] = extract_entries(data.get(src_key, []))

    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    # Human-readable bullet list version
    lines = [
        f"# {result['modpack_name']} — Modlist",
        "",
        f"Modpack version: `{result['modpack_version']}`  ",
        f"Minecraft version: `{result['minecraft_version']}`",
        "",
    ]
    titles = {
        "mods": "Mods",
        "shaders": "Shaders",
        "texturepacks": "Texture Packs",
        "other": "Other (added files)",
    }
    for key, title in titles.items():
        entries = result.get(key, [])
        if not entries:
            continue
        lines.append(f"## {title}")
        for e in entries:
            lines.append(f"- {e['name']} — `{e['version']}`")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
