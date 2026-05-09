"""Utility helpers for fastapi-spawn."""

from __future__ import annotations

import re
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case."""
    s = re.sub(r"[-\s]+", "_", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()


def to_pascal_case(name: str) -> str:
    """Convert a snake_case or kebab-case string to PascalCase."""
    return "".join(word.capitalize() for word in re.split(r"[-_\s]+", name))


def to_kebab_case(name: str) -> str:
    """Convert a string to kebab-case."""
    s = re.sub(r"[_\s]+", "-", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1-\2", s)
    return s.lower()


def render_tree(root: Path, prefix: str = "") -> str:
    """
    Recursively render a directory tree as a Rich-compatible string.
    Used in --dry-run mode.
    """
    lines: list[str] = []
    try:
        items = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return ""
    for i, item in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        lines.append(prefix + connector + item.name)
        if item.is_dir():
            extension = "    " if i == len(items) - 1 else "│   "
            lines.append(render_tree(item, prefix + extension))
    return "\n".join(filter(None, lines))


def collect_dry_run_paths(root: Path) -> list[str]:
    """
    Walk a directory and return all relative file paths as strings.
    Used by the generator in dry-run mode.
    """
    paths = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            paths.append(str(path.relative_to(root)))
    return paths
