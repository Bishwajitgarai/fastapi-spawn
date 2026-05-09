"""Project configuration dataclass for fastapi-spawn."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi_spawn.constants import (
    AIProvider, APIExtra, AuthType, Broker, Cache, CIProvider,
    Database, EmailProvider, LogDestination, LogLibrary,
    MigrationTool, MonitoringProvider, NotificationProvider,
    ORM, Stack, Storage, VectorDB,
)


@dataclass
class ProjectConfig:
    """Holds all user-selected options for a new FastAPI project."""

    project_name: str
    # Core
    db: Database = Database.postgresql
    orm: ORM = ORM.sqlalchemy
    migration: MigrationTool = MigrationTool.none
    auth: AuthType = AuthType.jwt
    broker: Broker = Broker.none
    cache: Cache = Cache.none
    # Storage & AI
    storage: Storage = Storage.none
    ai: AIProvider = AIProvider.none
    # Observability
    monitoring: MonitoringProvider = MonitoringProvider.none
    log_lib: LogLibrary = LogLibrary.loguru
    log_dest: LogDestination = LogDestination.local
    # Communication
    email: EmailProvider = EmailProvider.none
    notify: NotificationProvider = NotificationProvider.none
    # Data
    vector_db: VectorDB = VectorDB.none
    # Deployment
    stack: Stack = Stack.standard
    ci: CIProvider = CIProvider.github
    # API extras
    api_extra: APIExtra = APIExtra.none
    # Flags
    include_docker: bool = True
    include_tests: bool = True
    include_makefile: bool = True
    dry_run: bool = False
    force: bool = False
    extras: list[str] = field(default_factory=list)
    # Derived (post-init)
    package_name: str = field(default="", init=False)
    slug: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.slug = self.project_name.lower().replace("-", "_").replace(" ", "_")
        self.package_name = self.slug

    # ── Predicates ─────────────────────────────────────────────────────────

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
    def has_s3(self) -> bool:
        return self.storage == Storage.s3

    @property
    def has_storage(self) -> bool:
        return self.storage != Storage.none

    @property
    def has_migration(self) -> bool:
        return self.migration != MigrationTool.none

    @property
    def has_alembic(self) -> bool:
        return self.migration == MigrationTool.alembic

    @property
    def has_ai(self) -> bool:
        return self.ai != AIProvider.none

    @property
    def has_monitoring(self) -> bool:
        return self.monitoring != MonitoringProvider.none

    @property
    def has_sentry(self) -> bool:
        return self.monitoring in (MonitoringProvider.sentry, MonitoringProvider.both)

    @property
    def has_prometheus(self) -> bool:
        return self.monitoring in (MonitoringProvider.prometheus, MonitoringProvider.both)

    @property
    def has_email(self) -> bool:
        return self.email != EmailProvider.none

    @property
    def has_notify(self) -> bool:
        return self.notify != NotificationProvider.none

    @property
    def has_vector_db(self) -> bool:
        return self.vector_db != VectorDB.none

    @property
    def has_log_file(self) -> bool:
        return self.log_dest in (LogDestination.local, LogDestination.cloudwatch, LogDestination.datadog)

    @property
    def has_websockets(self) -> bool:
        return self.api_extra in (APIExtra.websockets, APIExtra.both)

    @property
    def has_graphql(self) -> bool:
        return self.api_extra in (APIExtra.graphql, APIExtra.both)

    # ── Template context ───────────────────────────────────────────────────

    def to_context(self) -> dict:
        return {
            "project_name": self.project_name,
            "package_name": self.package_name,
            "slug": self.slug,
            "db": self.db.value,
            "orm": self.orm.value,
            "migration": self.migration.value,
            "auth": self.auth.value,
            "broker": self.broker.value,
            "cache": self.cache.value,
            "storage": self.storage.value,
            "ai": self.ai.value,
            "monitoring": self.monitoring.value,
            "log_lib": self.log_lib.value,
            "log_dest": self.log_dest.value,
            "email": self.email.value,
            "notify": self.notify.value,
            "vector_db": self.vector_db.value,
            "stack": self.stack.value,
            "ci": self.ci.value,
            # booleans
            "api_extra": self.api_extra.value,
            "has_websockets": self.has_websockets,
            "has_graphql": self.has_graphql,
            "has_relational_db": self.has_relational_db,
            "has_mongo": self.has_mongo,
            "has_auth": self.has_auth,
            "has_broker": self.has_broker,
            "has_cache": self.has_cache,
            "has_docker": self.has_docker,
            "has_infra": self.has_infra,
            "has_ci": self.has_ci,
            "has_s3": self.has_s3,
            "has_storage": self.has_storage,
            "has_migration": self.has_migration,
            "has_alembic": self.has_alembic,
            "has_ai": self.has_ai,
            "has_monitoring": self.has_monitoring,
            "has_sentry": self.has_sentry,
            "has_prometheus": self.has_prometheus,
            "has_email": self.has_email,
            "has_notify": self.has_notify,
            "has_vector_db": self.has_vector_db,
            "has_log_file": self.has_log_file,
            "include_tests": self.include_tests,
            "include_makefile": self.include_makefile,
            "extras": self.extras,
        }

    def summary_lines(self) -> list[tuple[str, str]]:
        return [
            ("Project",      self.project_name),
            ("Package",      self.package_name),
            ("Database",     self.db.value),
            ("ORM",          self.orm.value),
            ("Migrations",   self.migration.value),
            ("Auth",         self.auth.value),
            ("Broker",       self.broker.value),
            ("Cache",        self.cache.value),
            ("Storage",      self.storage.value),
            ("AI",           self.ai.value),
            ("Monitoring",   self.monitoring.value),
            ("Email",        self.email.value),
            ("Notify",       self.notify.value),
            ("Vector DB",    self.vector_db.value),
            ("Log lib",      self.log_lib.value),
            ("Log dest",     self.log_dest.value),
            ("Stack",        self.stack.value),
            ("CI/CD",        self.ci.value),
            ("API extras",   self.api_extra.value),
            ("Docker",       "yes" if self.has_docker else "no"),
            ("Tests",        "yes" if self.include_tests else "no"),
            ("Extras",       ", ".join(self.extras) if self.extras else "none"),
            ("Dry-run",      "yes" if self.dry_run else "no"),
        ]
