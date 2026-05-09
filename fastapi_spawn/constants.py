"""Constants and enums for fastapi-spawn — the complete FastAPI ecosystem."""

from enum import Enum


# ── Database ───────────────────────────────────────────────────────────────

class Database(str, Enum):
    postgresql = "postgresql"
    mysql      = "mysql"
    mongodb    = "mongodb"
    sqlite     = "sqlite"
    supabase   = "supabase"   # managed Postgres + realtime
    duckdb     = "duckdb"     # analytical / OLAP queries
    none       = "none"


class ORM(str, Enum):
    sqlalchemy = "sqlalchemy"
    sqlmodel   = "sqlmodel"   # Pydantic v2 + SQLAlchemy — type-safe
    tortoise   = "tortoise"
    beanie     = "beanie"     # MongoDB ODM
    none       = "none"


class MigrationTool(str, Enum):
    alembic = "alembic"
    aerich  = "aerich"
    none    = "none"


# ── Auth ───────────────────────────────────────────────────────────────────

class AuthType(str, Enum):
    jwt      = "jwt"
    oauth2   = "oauth2"
    api_key  = "api-key"
    auth0    = "auth0"    # managed identity (Auth0 / Okta)
    none     = "none"


# ── Messaging ──────────────────────────────────────────────────────────────

class Broker(str, Enum):
    redis    = "redis"    # Celery + Redis
    rabbitmq = "rabbitmq" # Celery + RabbitMQ
    kafka    = "kafka"    # aiokafka
    arq      = "arq"      # lightweight async Redis task queue
    none     = "none"


class Cache(str, Enum):
    redis     = "redis"
    memcached = "memcached"
    none      = "none"


# ── Storage ────────────────────────────────────────────────────────────────

class Storage(str, Enum):
    s3         = "s3"         # AWS S3 or MinIO
    gcs        = "gcs"        # Google Cloud Storage
    cloudinary = "cloudinary" # image/video CDN
    local      = "local"
    none       = "none"


# ── AI / LLM ──────────────────────────────────────────────────────────────

class AIProvider(str, Enum):
    openai     = "openai"
    anthropic  = "anthropic"
    gemini     = "gemini"
    ollama     = "ollama"      # local, no API key
    langchain  = "langchain"   # framework (wraps any LLM)
    llamaindex = "llamaindex"  # RAG-focused framework
    none       = "none"


# ── Monitoring ─────────────────────────────────────────────────────────────

class MonitoringProvider(str, Enum):
    sentry        = "sentry"
    prometheus    = "prometheus"
    opentelemetry = "opentelemetry"  # vendor-neutral OTEL tracing
    both          = "both"           # sentry + prometheus
    none          = "none"


# ── Email ─────────────────────────────────────────────────────────────────

class EmailProvider(str, Enum):
    sendgrid = "sendgrid"
    smtp     = "smtp"
    ses      = "ses"
    none     = "none"


# ── Notifications ──────────────────────────────────────────────────────────

class NotificationProvider(str, Enum):
    slack   = "slack"
    discord = "discord"
    none    = "none"


# ── Logging ────────────────────────────────────────────────────────────────

class LogLibrary(str, Enum):
    loguru   = "loguru"
    structlog = "structlog"
    standard = "standard"


class LogDestination(str, Enum):
    local      = "local"
    cloudwatch = "cloudwatch"  # AWS CloudWatch Logs
    datadog    = "datadog"
    none       = "none"


# ── Vector database ────────────────────────────────────────────────────────

class VectorDB(str, Enum):
    qdrant        = "qdrant"
    chroma        = "chroma"         # ChromaDB — local dev
    pinecone      = "pinecone"
    supabase      = "supabase"       # pgvector on Supabase
    elasticsearch = "elasticsearch"
    none          = "none"


# ── Deployment ─────────────────────────────────────────────────────────────

class Stack(str, Enum):
    minimal  = "minimal"
    standard = "standard"
    full     = "full"


class CIProvider(str, Enum):
    github  = "github"
    gitlab  = "gitlab"
    both    = "both"
    none    = "none"


class APIExtra(str, Enum):
    websockets = "websockets"  # WebSocket endpoint + connection manager
    graphql    = "graphql"     # Strawberry GraphQL schema + router
    both       = "both"        # WebSockets + GraphQL
    none       = "none"


# ── Compatibility matrices ─────────────────────────────────────────────────

ORM_DB_COMPAT: dict[str, list[str]] = {
    ORM.sqlalchemy: [Database.postgresql, Database.mysql, Database.sqlite, Database.supabase],
    ORM.sqlmodel:   [Database.postgresql, Database.mysql, Database.sqlite, Database.supabase],
    ORM.tortoise:   [Database.postgresql, Database.mysql, Database.sqlite],
    ORM.beanie:     [Database.mongodb],
    ORM.none:       list(Database),
}

MIGRATION_ORM_COMPAT: dict[str, list[str]] = {
    MigrationTool.alembic: [ORM.sqlalchemy, ORM.sqlmodel],
    MigrationTool.aerich:  [ORM.tortoise],
    MigrationTool.none:    list(ORM),
}

# ── Human-readable labels ──────────────────────────────────────────────────

DB_LABELS = {
    Database.postgresql: "PostgreSQL — production SQL",
    Database.mysql:      "MySQL / MariaDB",
    Database.mongodb:    "MongoDB",
    Database.sqlite:     "SQLite — local dev",
    Database.supabase:   "Supabase — managed Postgres + realtime",
    Database.duckdb:     "DuckDB — analytical / OLAP",
    Database.none:       "No database",
}

ORM_LABELS = {
    ORM.sqlalchemy: "SQLAlchemy 2.x async",
    ORM.sqlmodel:   "SQLModel — Pydantic v2 + SQLAlchemy (type-safe)",
    ORM.tortoise:   "Tortoise ORM",
    ORM.beanie:     "Beanie — async MongoDB ODM",
    ORM.none:       "No ORM",
}

AUTH_LABELS = {
    AuthType.jwt:     "JWT (python-jose + passlib)",
    AuthType.oauth2:  "OAuth2 Password flow",
    AuthType.api_key: "API Key header",
    AuthType.auth0:   "Auth0 / Okta — managed identity",
    AuthType.none:    "No authentication",
}

BROKER_LABELS = {
    Broker.redis:    "Redis — Celery broker + result backend",
    Broker.rabbitmq: "RabbitMQ — Celery broker",
    Broker.kafka:    "Kafka — aiokafka streams",
    Broker.arq:      "Arq — lightweight async Redis task queue",
    Broker.none:     "No message broker",
}

STORAGE_LABELS = {
    Storage.s3:         "AWS S3 / MinIO (boto3)",
    Storage.gcs:        "Google Cloud Storage",
    Storage.cloudinary: "Cloudinary — image/video CDN",
    Storage.local:      "Local filesystem",
    Storage.none:       "No file storage",
}

AI_LABELS = {
    AIProvider.openai:     "OpenAI — GPT-4o, embeddings (custom base URL supported)",
    AIProvider.anthropic:  "Anthropic — Claude 3.x",
    AIProvider.gemini:     "Google Gemini — multi-modal",
    AIProvider.ollama:     "Ollama — local LLM, no API key",
    AIProvider.langchain:  "LangChain — LLM orchestration framework",
    AIProvider.llamaindex: "LlamaIndex — RAG / data-to-LLM framework",
    AIProvider.none:       "No AI integration",
}

MONITORING_LABELS = {
    MonitoringProvider.sentry:        "Sentry — error tracking + performance",
    MonitoringProvider.prometheus:    "Prometheus — metrics via instrumentator",
    MonitoringProvider.opentelemetry: "OpenTelemetry — vendor-neutral tracing",
    MonitoringProvider.both:          "Sentry + Prometheus",
    MonitoringProvider.none:          "No monitoring",
}

EMAIL_LABELS = {
    EmailProvider.sendgrid: "SendGrid",
    EmailProvider.smtp:     "SMTP (fastapi-mail)",
    EmailProvider.ses:      "AWS SES",
    EmailProvider.none:     "No email",
}

NOTIFICATION_LABELS = {
    NotificationProvider.slack:   "Slack — incoming webhooks",
    NotificationProvider.discord: "Discord — webhooks",
    NotificationProvider.none:    "No notifications",
}

LOG_DEST_LABELS = {
    LogDestination.local:      "Local — rotating file (daily, configurable retention)",
    LogDestination.cloudwatch: "AWS CloudWatch Logs",
    LogDestination.datadog:    "Datadog Logs",
    LogDestination.none:       "Console only",
}

VECTOR_DB_LABELS = {
    VectorDB.qdrant:        "Qdrant — local Docker or Qdrant Cloud",
    VectorDB.chroma:        "ChromaDB — local open-source vector DB",
    VectorDB.pinecone:      "Pinecone — managed cloud",
    VectorDB.supabase:      "Supabase pgvector",
    VectorDB.elasticsearch: "Elasticsearch — kNN search",
    VectorDB.none:          "No vector database",
}

STACK_DESCRIPTIONS = {
    Stack.minimal:  "Core app only — no Docker, no infra",
    Stack.standard: "App + Docker + GitHub CI",
    Stack.full:     "App + Docker + CI + Helm + Terraform",
}
