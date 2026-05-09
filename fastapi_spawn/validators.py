"""Input validators for fastapi-spawn."""

from __future__ import annotations

import re
from pathlib import Path

from fastapi_spawn.constants import ORM, ORM_DB_COMPAT, Database


def validate_project_name(name: str) -> str:
    """
    Validate that a project name is a valid Python package identifier
    (allows hyphens which are converted to underscores).
    Returns the cleaned name or raises ValueError.
    """
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Project name cannot be empty.")
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", cleaned):
        raise ValueError(
            f"Invalid project name '{cleaned}'. "
            "Use letters, numbers, hyphens, or underscores. Must start with a letter."
        )
    if len(cleaned) > 64:
        raise ValueError("Project name must be 64 characters or fewer.")
    return cleaned


def validate_orm_db_compat(orm: ORM, db: Database) -> None:
    """
    Raise ValueError if the selected ORM is not compatible with the selected DB.
    """
    compatible_dbs = ORM_DB_COMPAT.get(orm, [])
    if db not in compatible_dbs:
        compat_str = ", ".join(d.value for d in compatible_dbs)
        raise ValueError(
            f"ORM '{orm.value}' is not compatible with database '{db.value}'. "
            f"Compatible databases: {compat_str}"
        )


def validate_output_dir(path: Path, force: bool) -> None:
    """
    Validate that the output directory can be safely created.
    Raises ValueError if the directory exists and --force was not passed.
    """
    if path.exists() and not force:
        raise ValueError(
            f"Directory '{path}' already exists. Use --force to overwrite."
        )


def questionary_validator(validate_fn):  # type: ignore[no-untyped-def]
    """
    Wrap a validation function for use as a questionary validator.
    Returns a callable that returns True on success or an error string on failure.
    """

    def _inner(val: str):  # type: ignore[no-untyped-def]
        try:
            validate_fn(val)
            return True
        except ValueError as exc:
            return str(exc)

    return _inner
