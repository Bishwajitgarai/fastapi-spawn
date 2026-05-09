"""Constants and enums for fastapi-spawn."""

from enum import Enum


class Database(str, Enum):
    postgresql = "postgresql"
    mysql = "mysql"
    mongodb = "mongodb"
    sqlite = "sqlite"
    none = "none"


class ORM(str, Enum):
    sqlalchemy = "sqlalchemy"
    tortoise = "tortoise"
    beanie = "beanie"
    none = "none"


class AuthType(str, Enum):
    jwt = "jwt"
    oauth2 = "oauth2"
    api_key = "api-key"
    none = "none"


class Broker(str, Enum):
    redis = "redis"
    rabbitmq = "rabbitmq"
    kafka = "kafka"
    none = "none"


class Cache(str, Enum):
    redis = "redis"
    memcached = "memcached"
    none = "none"


class Stack(str, Enum):
    minimal = "minimal"
    standard = "standard"
    full = "full"


class CIProvider(str, Enum):
    github = "github"
    gitlab = "gitlab"
    both = "both"
    none = "none"


class LogLibrary(str, Enum):
    loguru = "loguru"
    structlog = "structlog"
    standard = "standard"


class Storage(str, Enum):
    s3 = "s3"
    local = "local"
    none = "none"


class MigrationTool(str, Enum):
    alembic = "alembic"   # SQLAlchemy / relational DBs
    aerich = "aerich"     # Tortoise ORM
    none = "none"


class AIProvider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    none = "none"


# ORM ↔ Database compatibility matrix
ORM_DB_COMPAT: dict[str, list[str]] = {
    ORM.sqlalchemy: [Database.postgresql, Database.mysql, Database.sqlite],
    ORM.tortoise: [Database.postgresql, Database.mysql, Database.sqlite],
    ORM.beanie: [Database.mongodb],
    ORM.none: [Database.postgresql, Database.mysql, Database.mongodb, Database.sqlite, Database.none],
}

# Migration tool ↔ ORM compatibility
MIGRATION_ORM_COMPAT: dict[str, list[str]] = {
    MigrationTool.alembic: [ORM.sqlalchemy],
    MigrationTool.aerich: [ORM.tortoise],
    MigrationTool.none: list(ORM),
}

# Human-readable labels
DB_LABELS = {
    Database.postgresql: "PostgreSQL",
    Database.mysql: "MySQL",
    Database.mongodb: "MongoDB",
    Database.sqlite: "SQLite",
    Database.none: "No database",
}

AUTH_LABELS = {
    AuthType.jwt: "JWT (JSON Web Tokens)",
    AuthType.oauth2: "OAuth2 (Password flow)",
    AuthType.api_key: "API Key",
    AuthType.none: "No authentication",
}

BROKER_LABELS = {
    Broker.redis: "Redis (via Celery)",
    Broker.rabbitmq: "RabbitMQ (via Celery)",
    Broker.kafka: "Kafka (via aiokafka)",
    Broker.none: "No message broker",
}

STORAGE_LABELS = {
    Storage.s3: "AWS S3 (via boto3)",
    Storage.local: "Local filesystem",
    Storage.none: "No file storage",
}

AI_LABELS = {
    AIProvider.openai: "OpenAI (GPT-4o, GPT-4, embeddings)",
    AIProvider.anthropic: "Anthropic (Claude 3.x)",
    AIProvider.none: "No AI integration",
}

STACK_DESCRIPTIONS = {
    Stack.minimal: "Core app only — no Docker, no infra",
    Stack.standard: "App + Docker + GitHub CI",
    Stack.full: "App + Docker + CI + Helm + Terraform",
}

