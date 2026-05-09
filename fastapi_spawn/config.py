"""Project configuration dataclass for fastapi-spawn."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi_spawn.constants import (
    AIProvider,
    AuthType,
    Broker,
    Cache,
    CIProvider,
    Database,
    LogLibrary,
    MigrationTool,
    ORM,
    Stack,
    Storage,
)


@dataclass
class ProjectConfig:
    """Holds all user-selected options for a new FastAPI project."""

    project_name: str
    db: Database = Database.postgresql
    orm: ORM = ORM.sqlalchemy
    auth: AuthType = AuthType.jwt
    broker: Broker = Broker.none
    cache: Cache = Cache.none
    stack: Stack = Stack.standard
    ci: CIProvider = CIProvider.github
    log_lib: LogLibrary = LogLibrary.loguru
    storage: Storage = Storage.none
    migration: MigrationTool = MigrationTool.none
    ai: AIProvider = AIProvider.none
    include_docker: bool = True
    include_tests: bool = True
    include_makefile: bool = True
    dry_run: bool = False
    force: bool = False
    # Derived fields (set post-init)
    package_name: str = field(default="", init=False)
    slug: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.slug = self.project_name.lower().replace("-", "_").replace(" ", "_")
        self.package_name = self.slug

    # ── Convenience predicates ─────────────────────────────────────────────

    @property
    def has_relational_db(self) -> bool:
        return self.db in (Database.postgresql, Database.mysql, Database.sqlite)

    @property
    def has_mongo(self) -> bool:
        return self.db == Database.mongodb

    @property
    def has_auth(self) -> bool:
        return self.auth != AuthType.none

    @property
    def has_broker(self) -> bool:
        return self.broker != Broker.none

    @property
    def has_cache(self) -> bool:
        return self.cache != Cache.none

    @property
    def has_docker(self) -> bool:
        return self.include_docker and self.stack != Stack.minimal

    @property
    def has_infra(self) -> bool:
        return self.stack == Stack.full

    @property
    def has_ci(self) -> bool:
        return self.ci != CIProvider.none

    @property
    def has_storage(self) -> bool:
        return self.storage != Storage.none

    @property
    def has_s3(self) -> bool:
        return self.storage == Storage.s3

    @property
    def has_migration(self) -> bool:
        return self.migration != MigrationTool.none

    @property
    def has_alembic(self) -> bool:
        return self.migration == MigrationTool.alembic

    @property
    def has_ai(self) -> bool:
        return self.ai != AIProvider.none

    # ── Template context ───────────────────────────────────────────────────

    def to_context(self) -> dict:
        """Return a Jinja2-ready template context dict."""
        return {
            "project_name": self.project_name,
            "package_name": self.package_name,
            "slug": self.slug,
            "db": self.db.value,
            "orm": self.orm.value,
            "auth": self.auth.value,
            "broker": self.broker.value,
            "cache": self.cache.value,
            "stack": self.stack.value,
            "ci": self.ci.value,
            "log_lib": self.log_lib.value,
            "storage": self.storage.value,
            "migration": self.migration.value,
            "ai": self.ai.value,
            # Booleans for easy Jinja2 conditionals
            "has_relational_db": self.has_relational_db,
            "has_mongo": self.has_mongo,
            "has_auth": self.has_auth,
            "has_broker": self.has_broker,
            "has_cache": self.has_cache,
            "has_docker": self.has_docker,
            "has_infra": self.has_infra,
            "has_ci": self.has_ci,
            "has_storage": self.has_storage,
            "has_s3": self.has_s3,
            "has_migration": self.has_migration,
            "has_alembic": self.has_alembic,
            "has_ai": self.has_ai,
            "include_tests": self.include_tests,
            "include_makefile": self.include_makefile,
        }

    def summary_lines(self) -> list[tuple[str, str]]:
        """Return key-value pairs for display in the rich summary panel."""
        rows = [
            ("Project", self.project_name),
            ("Package", self.package_name),
            ("Database", self.db.value),
            ("ORM", self.orm.value),
            ("Migrations", self.migration.value),
            ("Auth", self.auth.value),
            ("Broker", self.broker.value),
            ("Cache", self.cache.value),
            ("Storage", self.storage.value),
            ("AI", self.ai.value),
            ("Stack", self.stack.value),
            ("CI/CD", self.ci.value),
            ("Logging", self.log_lib.value),
            ("Docker", "yes" if self.has_docker else "no"),
            ("Tests", "yes" if self.include_tests else "no"),
            ("Dry-run", "yes" if self.dry_run else "no"),
        ]
        return rows
