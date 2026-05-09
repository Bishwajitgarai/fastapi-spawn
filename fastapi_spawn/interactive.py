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
    Storage,
    AIProvider,
    MonitoringProvider,
    VectorDB,
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
        questionary.Choice(title=f"{i}) {label}", value=db)
        for i, (db, label) in enumerate(DB_LABELS.items(), 1)
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
    choices = [questionary.Choice(title=f"{i}) {o.value}", value=o) for i, o in enumerate(valid_orms, 1)]
    if not choices:
        return ORM.none
    return questionary.select(
        "ORM / ODM:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_auth() -> AuthType:
    choices = [
        questionary.Choice(title=f"{i}) {label}", value=auth)
        for i, (auth, label) in enumerate(AUTH_LABELS.items(), 1)
    ]
    return questionary.select(
        "Authentication strategy:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_broker() -> Broker:
    choices = [
        questionary.Choice(title=f"{i}) {label}", value=broker)
        for i, (broker, label) in enumerate(BROKER_LABELS.items(), 1)
    ]
    return questionary.select(
        "Message broker:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_cache() -> Cache:
    choices = [
        questionary.Choice(title=f"{i}) {c.value}", value=c)
        for i, c in enumerate(Cache, 1)
    ]
    return questionary.select(
        "Cache layer:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_stack() -> Stack:
    choices = [
        questionary.Choice(title=f"{i}) {s.value}  —  {STACK_DESCRIPTIONS[s]}", value=s)
        for i, s in enumerate(Stack, 1)
    ]
    return questionary.select(
        "Deployment stack:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_ci() -> CIProvider:
    choices = [
        questionary.Choice(title=f"{i}) {c.value}", value=c)
        for i, c in enumerate(CIProvider, 1)
    ]
    return questionary.select(
        "CI/CD provider:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_log_lib() -> LogLibrary:
    choices = [
        questionary.Choice(title=f"{i}) {l.value}", value=l)
        for i, l in enumerate(LogLibrary, 1)
    ]
    return questionary.select(
        "Logging library:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_storage() -> Storage:
    use_storage = questionary.confirm(
        "Do you need file storage?", default=False, style=SPAWN_STYLE
    ).unsafe_ask()
    if not use_storage:
        return Storage.none
    choices = [
        questionary.Choice(title=f"{i}) {s.value}", value=s)
        for i, s in enumerate(Storage, 1) if s != Storage.none
    ]
    return questionary.select(
        "Storage provider:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_ai() -> AIProvider:
    use_ai = questionary.confirm(
        "Do you need AI/LLM integration?", default=False, style=SPAWN_STYLE
    ).unsafe_ask()
    if not use_ai:
        return AIProvider.none
    choices = [
        questionary.Choice(title=f"{i}) {a.value}", value=a)
        for i, a in enumerate(AIProvider, 1) if a != AIProvider.none
    ]
    return questionary.select(
        "AI provider:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_vector_db() -> VectorDB:
    use_vdb = questionary.confirm(
        "Do you need a Vector Database?", default=False, style=SPAWN_STYLE
    ).unsafe_ask()
    if not use_vdb:
        return VectorDB.none
    choices = [
        questionary.Choice(title=f"{i}) {v.value}", value=v)
        for i, v in enumerate(VectorDB, 1) if v != VectorDB.none
    ]
    return questionary.select(
        "Vector database:",
        choices=choices,
        style=SPAWN_STYLE,
    ).unsafe_ask()


def prompt_monitoring() -> MonitoringProvider:
    use_mon = questionary.confirm(
        "Do you need Monitoring?", default=False, style=SPAWN_STYLE
    ).unsafe_ask()
    if not use_mon:
        return MonitoringProvider.none
    choices = [
        questionary.Choice(title=f"{i}) {m.value}", value=m)
        for i, m in enumerate(MonitoringProvider, 1) if m != MonitoringProvider.none
    ]
    return questionary.select(
        "Monitoring provider:",
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
    storage = prompt_storage()
    ai = prompt_ai()
    vector_db = prompt_vector_db()
    monitoring = prompt_monitoring()
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
        "storage": storage,
        "ai": ai,
        "vector_db": vector_db,
        "monitoring": monitoring,
        "include_docker": include_docker,
        "include_tests": include_tests,
    }
