"""Interactive TUI prompts using questionary."""

from __future__ import annotations

import questionary
from questionary import Style

from fastapi_spawn.constants import (
    AUTH_LABELS,
    BROKER_LABELS,
    DB_LABELS,
    STACK_DESCRIPTIONS,
    AuthType,
    Broker,
    Cache,
    CIProvider,
    Database,
    LogLibrary,
    ORM,
    ORM_DB_COMPAT,
    Stack,
)
from fastapi_spawn.validators import questionary_validator, validate_project_name

SPAWN_STYLE = Style(
    [
        ("qmark", "fg:#7c3aed bold"),
        ("question", "bold"),
        ("answer", "fg:#22d3ee bold"),
        ("pointer", "fg:#7c3aed bold"),
        ("highlighted", "fg:#7c3aed bold"),
        ("selected", "fg:#22d3ee"),
        ("separator", "fg:#6b7280"),
        ("instruction", "fg:#6b7280"),
    ]
)


def prompt_project_name(default: str = "") -> str:
    return questionary.text(
        "Project name:",
        default=default,
        validate=questionary_validator(validate_project_name),
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_database() -> Database:
    choices = [
        questionary.Choice(title=label, value=db)
        for db, label in DB_LABELS.items()
    ]
    return questionary.select(
        "Database backend:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_orm(db: Database) -> ORM:
    compatible = ORM_DB_COMPAT.get(ORM.none, [])
    valid_orms = [
        orm for orm in ORM
        if db in ORM_DB_COMPAT.get(orm, []) or orm == ORM.none
    ]
    # Filter ORMs truly compatible with the chosen DB
    valid_orms = [
        orm for orm in ORM
        if db in ORM_DB_COMPAT.get(orm, compatible)
    ]
    choices = [questionary.Choice(title=o.value, value=o) for o in valid_orms]
    if not choices:
        return ORM.none
    return questionary.select(
        "ORM / ODM:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_auth() -> AuthType:
    choices = [
        questionary.Choice(title=label, value=auth)
        for auth, label in AUTH_LABELS.items()
    ]
    return questionary.select(
        "Authentication strategy:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_broker() -> Broker:
    choices = [
        questionary.Choice(title=label, value=broker)
        for broker, label in BROKER_LABELS.items()
    ]
    return questionary.select(
        "Message broker:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_cache() -> Cache:
    choices = [
        questionary.Choice(title=c.value, value=c)
        for c in Cache
    ]
    return questionary.select(
        "Cache layer:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_stack() -> Stack:
    choices = [
        questionary.Choice(title=f"{s.value}  —  {STACK_DESCRIPTIONS[s]}", value=s)
        for s in Stack
    ]
    return questionary.select(
        "Deployment stack:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_ci() -> CIProvider:
    choices = [
        questionary.Choice(title=c.value, value=c)
        for c in CIProvider
    ]
    return questionary.select(
        "CI/CD provider:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_log_lib() -> LogLibrary:
    choices = [
        questionary.Choice(title=l.value, value=l)
        for l in LogLibrary
    ]
    return questionary.select(
        "Logging library:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_flags() -> tuple[bool, bool]:
    """Returns (include_docker, include_tests)."""
    include_docker = questionary.confirm(
        "Include Docker files?", default=True, style=SPAWN_STYLE
    ).unsafe_ask()
    include_tests = questionary.confirm(
        "Include test suite?", default=True, style=SPAWN_STYLE
    ).unsafe_ask()
    return include_docker, include_tests


def run_interactive_flow(project_name: str = "") -> dict:
    """
    Run the full interactive TUI and return a dict of selected options
    suitable for passing to ProjectConfig.
    """
    name = prompt_project_name(project_name)
    db = prompt_database()
    orm = prompt_orm(db)
    auth = prompt_auth()
    broker = prompt_broker()
    cache = prompt_cache()
    stack = prompt_stack()
    ci = prompt_ci()
    log_lib = prompt_log_lib()
    include_docker, include_tests = prompt_flags()

    return {
        "project_name": name,
        "db": db,
        "orm": orm,
        "auth": auth,
        "broker": broker,
        "cache": cache,
        "stack": stack,
        "ci": ci,
        "log_lib": log_lib,
        "include_docker": include_docker,
        "include_tests": include_tests,
    }
