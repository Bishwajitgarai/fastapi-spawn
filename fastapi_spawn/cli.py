"""Main CLI entry point for fastapi-spawn."""

from __future__ import annotations

import os
import sys

# Force UTF-8 output on Windows (cp1252 chokes on emoji)
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fastapi_spawn import __version__
from fastapi_spawn.config import ProjectConfig
from fastapi_spawn.constants import (
    AIProvider,
    APIExtra,
    AuthType,
    Broker,
    Cache,
    CIProvider,
    Database,
    EmailProvider,
    LogDestination,
    LogLibrary,
    MigrationTool,
    MonitoringProvider,
    NotificationProvider,
    ORM,
    Stack,
    Storage,
    VectorDB,
)
from fastapi_spawn.generator import ProjectGenerator
from fastapi_spawn.interactive import run_interactive_flow
from fastapi_spawn.validators import validate_orm_db_compat, validate_output_dir, validate_project_name

app = typer.Typer(
    name="fastapi-spawn",
    help="[bold cyan]fastapi-spawn[/bold cyan] — Scaffold production-ready FastAPI projects in seconds.",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        rprint(f"[bold cyan]fastapi-spawn[/bold cyan] version [bold]{__version__}[/bold]")
        raise typer.Exit()


@app.command("help", help="Show this help message and exit.")
def show_help(ctx: typer.Context) -> None:
    """Print the global CLI help."""
    # We leverage Click's internal help formatting to render the same as --help
    rprint(ctx.parent.get_help())



# ── `new` command ──────────────────────────────────────────────────────────────

@app.command("new", help="Create a new FastAPI project.")
def new(
    project_name: Optional[str] = typer.Argument(None, help="Name of the new project"),
    # Database
    db: Optional[Database] = typer.Option(None, "--db", help="Database backend"),
    orm: Optional[ORM] = typer.Option(None, "--orm", help="ORM / ODM"),
    migration: Optional[MigrationTool] = typer.Option(None, "--migration", help="Migration tool"),
    # Auth
    auth: Optional[AuthType] = typer.Option(None, "--auth", help="Auth strategy"),
    # Messaging
    broker: Optional[Broker] = typer.Option(None, "--broker", help="Message broker"),
    cache: Optional[Cache] = typer.Option(None, "--cache", help="Cache layer"),
    # Storage & AI
    storage: Optional[Storage] = typer.Option(None, "--storage", help="File storage (s3, gcs, cloudinary, local, none)"),
    ai: Optional[AIProvider] = typer.Option(None, "--ai", help="AI provider"),
    # API extras
    api_extra: Optional[APIExtra] = typer.Option(None, "--api-extra", help="WebSockets / GraphQL"),
    # Observability
    monitoring: Optional[MonitoringProvider] = typer.Option(None, "--monitoring", help="Monitoring (sentry, prometheus, opentelemetry, both, none)"),
    log_lib: Optional[LogLibrary] = typer.Option(None, "--log-lib", help="Logging library"),
    log_dest: Optional[LogDestination] = typer.Option(None, "--log-dest", help="Log destination (local, cloudwatch, datadog, none)"),
    # Communication
    email: Optional[EmailProvider] = typer.Option(None, "--email", help="Email provider"),
    notify: Optional[NotificationProvider] = typer.Option(None, "--notify", help="Notification provider"),
    # Vector DB
    vector_db: Optional[VectorDB] = typer.Option(None, "--vector-db", help="Vector database"),
    # Deployment
    stack: Optional[Stack] = typer.Option(None, "--stack", help="Deployment stack"),
    ci: Optional[CIProvider] = typer.Option(None, "--ci", help="CI/CD provider"),
    # Flags
    no_docker: bool = typer.Option(False, "--no-docker", help="Skip Docker files"),
    no_tests: bool = typer.Option(False, "--no-tests", help="Skip test suite"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview structure without writing files"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing directory"),
    extra: Optional[list[str]] = typer.Option(None, "--extra", help="Extra integrations (e.g. stripe, sso, sse, seed, ocr, meilisearch)"),
    output: Path = typer.Option(Path("."), "--output", "-o", help="Output directory"),
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"
    ),
) -> None:
    _print_banner()

    needs_interactive = any(
        x is None for x in [
            project_name, db, orm, migration, auth, broker, cache,
            storage, ai, api_extra, monitoring, log_lib, log_dest,
            email, notify, vector_db, stack, ci,
        ]
    )

    if needs_interactive:
        console.print("[dim]Some options are missing — launching interactive mode...[/dim]\n")
        opts = run_interactive_flow(project_name or "")
        project_name  = project_name  or opts["project_name"]
        db            = db            or opts.get("db", Database.postgresql)
        orm           = orm           or opts.get("orm", ORM.sqlalchemy)
        migration     = migration     or opts.get("migration", MigrationTool.none)
        auth          = auth          or opts.get("auth", AuthType.jwt)
        broker        = broker        or opts.get("broker", Broker.none)
        cache         = cache         or opts.get("cache", Cache.none)
        storage       = storage       or opts.get("storage", Storage.none)
        ai            = ai            or opts.get("ai", AIProvider.none)
        api_extra     = api_extra     or opts.get("api_extra", APIExtra.none)
        monitoring    = monitoring    or opts.get("monitoring", MonitoringProvider.none)
        log_lib       = log_lib       or opts.get("log_lib", LogLibrary.loguru)
        log_dest      = log_dest      or opts.get("log_dest", LogDestination.local)
        email         = email         or opts.get("email", EmailProvider.none)
        notify        = notify        or opts.get("notify", NotificationProvider.none)
        vector_db     = vector_db     or opts.get("vector_db", VectorDB.none)
        stack         = stack         or opts.get("stack", Stack.standard)
        ci            = ci            or opts.get("ci", CIProvider.github)
        include_docker = (not no_docker) and opts.get("include_docker", True)
        include_tests  = (not no_tests)  and opts.get("include_tests", True)
    else:
        include_docker = not no_docker
        include_tests  = not no_tests

    # Safe defaults for non-interactive path
    db         = db         or Database.postgresql
    orm        = orm        or ORM.sqlalchemy
    migration  = migration  or MigrationTool.none
    auth       = auth       or AuthType.jwt
    broker     = broker     or Broker.none
    cache      = cache      or Cache.none
    storage    = storage    or Storage.none
    ai         = ai         or AIProvider.none
    api_extra  = api_extra  or APIExtra.none
    monitoring = monitoring or MonitoringProvider.none
    log_lib    = log_lib    or LogLibrary.loguru
    log_dest   = log_dest   or LogDestination.local
    email      = email      or EmailProvider.none
    notify     = notify     or NotificationProvider.none
    vector_db  = vector_db  or VectorDB.none
    stack      = stack      or Stack.standard
    ci         = ci         or CIProvider.github

    # Validate
    try:
        validate_project_name(project_name)  # type: ignore[arg-type]
        validate_orm_db_compat(orm, db)
        if not dry_run:
            validate_output_dir(output / project_name, force)  # type: ignore[operator]
    except ValueError as exc:
        console.print(f"[bold red]✗ Error:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    config = ProjectConfig(
        project_name=project_name,   # type: ignore[arg-type]
        db=db,
        orm=orm,
        migration=migration,
        auth=auth,
        broker=broker,
        cache=cache,
        storage=storage,
        ai=ai,
        api_extra=api_extra,
        monitoring=monitoring,
        log_lib=log_lib,
        log_dest=log_dest,
        email=email,
        notify=notify,
        vector_db=vector_db,
        stack=stack,
        ci=ci,
        include_docker=include_docker,
        include_tests=include_tests,
        dry_run=dry_run,
        force=force,
        extras=extra or [],
    )

    _print_summary(config)

    if dry_run:
        console.print("\n[bold yellow]Dry-run mode -- no files will be written.[/bold yellow]\n")

    try:
        generator = ProjectGenerator(config, output)
        project_path = generator.generate()
    except Exception as exc:
        console.print(f"\n[bold red]✗ Generation failed:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    if not dry_run:
        console.print(f"\n[bold green]✓ Project created:[/bold green] {project_path.resolve()}")
        _print_next_steps(config)


# ── `list-templates` command ───────────────────────────────────────────────────

@app.command("list-templates", help="List all available options and compatible combinations.")
def list_templates() -> None:
    _print_banner()
    table = Table(title="Available Options", border_style="cyan", show_lines=True)
    table.add_column("Flag", style="bold cyan")
    table.add_column("Choices", style="white")

    table.add_row("--db",         ", ".join(d.value for d in Database))
    table.add_row("--orm",        ", ".join(o.value for o in ORM))
    table.add_row("--migration",  ", ".join(m.value for m in MigrationTool))
    table.add_row("--auth",       ", ".join(a.value for a in AuthType))
    table.add_row("--broker",     ", ".join(b.value for b in Broker))
    table.add_row("--cache",      ", ".join(c.value for c in Cache))
    table.add_row("--storage",    ", ".join(s.value for s in Storage))
    table.add_row("--ai",         ", ".join(a.value for a in AIProvider))
    table.add_row("--api-extra",  ", ".join(a.value for a in APIExtra))
    table.add_row("--monitoring", ", ".join(m.value for m in MonitoringProvider))
    table.add_row("--log-lib",    ", ".join(l.value for l in LogLibrary))
    table.add_row("--log-dest",   ", ".join(l.value for l in LogDestination))
    table.add_row("--email",      ", ".join(e.value for e in EmailProvider))
    table.add_row("--notify",     ", ".join(n.value for n in NotificationProvider))
    table.add_row("--vector-db",  ", ".join(v.value for v in VectorDB))
    table.add_row("--stack",      ", ".join(s.value for s in Stack))
    table.add_row("--ci",         ", ".join(c.value for c in CIProvider))
    console.print(table)


# ── `validate` command ─────────────────────────────────────────────────────────

@app.command("validate", help="Validate a .fastapi-spawn.toml config file.")
def validate_config(
    config_file: Path = typer.Argument(..., help="Path to .fastapi-spawn.toml"),
) -> None:
    if not config_file.exists():
        console.print(f"[bold red]✗ File not found:[/bold red] {config_file}")
        raise typer.Exit(1)
    console.print(f"[bold green]✓ Config file found:[/bold green] {config_file}")
    console.print("[dim]Full TOML validation coming in a future release.[/dim]")


# ── `add` command ──────────────────────────────────────────────────────────────

_ADDABLE_FEATURES = {
    "auth":        "Authentication (JWT / OAuth2 / API Key / Auth0)",
    "s3":          "AWS S3 / MinIO file storage (boto3)",
    "gcs":         "Google Cloud Storage",
    "cloudinary":  "Cloudinary image/video CDN",
    "openai":      "OpenAI integration (chat + embeddings)",
    "anthropic":   "Anthropic Claude integration",
    "gemini":      "Google Gemini integration",
    "ollama":      "Ollama local LLM",
    "langchain":   "LangChain LLM framework",
    "llamaindex":  "LlamaIndex RAG framework",
    "alembic":     "Alembic async database migrations",
    "celery":      "Celery worker + sample tasks",
    "arq":         "Arq async Redis task queue",
    "redis":       "Redis cache / broker support",
    "kafka":       "Kafka broker support (aiokafka)",
    "sentry":      "Sentry error tracking + performance",
    "prometheus":  "Prometheus metrics (/metrics endpoint)",
    "opentelemetry": "OpenTelemetry distributed tracing",
    "sendgrid":    "SendGrid email",
    "smtp":        "SMTP email (fastapi-mail)",
    "slack":       "Slack webhook notifications",
    "discord":     "Discord webhook notifications",
    "qdrant":      "Qdrant vector database",
    "chroma":      "ChromaDB local vector database",
    "pinecone":    "Pinecone managed vector database",
    "elasticsearch": "Elasticsearch KNN search",
    "meilisearch": "Meilisearch ultra-fast typo-tolerant search",
    "opensearch":  "OpenSearch vector and text search",
    "vespa":       "Vespa big data serving engine",
    "websockets":  "WebSocket connection manager + endpoints",
    "sse":         "Server-Sent Events (SSE) streaming endpoint",
    "graphql":     "Strawberry GraphQL schema + subscriptions",
    "stripe":      "Stripe payments & webhook signature validation",
    "sso":         "FastAPI SSO (Google, GitHub, Microsoft)",
    "sso-google":  "FastAPI SSO (Google only)",
    "sso-github":  "FastAPI SSO (GitHub only)",
    "sso-microsoft": "FastAPI SSO (Microsoft only)",
    "seed":        "Database seeding script using Faker",
    "ocr":         "PDF & OCR data pipeline (PyMuPDF / Tesseract)",
    "rbac":        "Role-Based Access Control (Permissions) boilerplate",
    "caching":     "Redis-based response caching (fastapi-cache2)",
    "response-format": "Global JSON response formatting middleware",
    "docker":      "Dockerfile + docker-compose.yml",
    "ci":          "GitHub Actions CI/CD workflows",
    "helm":        "Helm chart (infra/helm/)",
    "terraform":   "Terraform scaffold (infra/terraform/)",
}


@app.command("add", help="Add a feature to an [bold]existing[/bold] fastapi-spawn project.")
def add_feature(
    feature: str = typer.Argument(..., help=f"Feature to add. Run 'fastapi-spawn add --help' to list all."),
    project_dir: Path = typer.Option(Path("."), "--dir", "-d", help="Path to the existing project"),
) -> None:
    _print_banner()

    if feature not in _ADDABLE_FEATURES:
        console.print(
            f"[bold red]✗ Unknown feature:[/bold red] '{feature}'\n"
            f"[dim]Available: {', '.join(_ADDABLE_FEATURES)}[/dim]"
        )
        raise typer.Exit(1)

    if not project_dir.exists():
        console.print(f"[bold red]✗ Directory not found:[/bold red] {project_dir.resolve()}")
        raise typer.Exit(1)

    console.print(f"[bold cyan]→ Adding feature:[/bold cyan] [bold]{feature}[/bold] — {_ADDABLE_FEATURES[feature]}")
    console.print(f"[dim]Target project:[/dim] {project_dir.resolve()}\n")
    _feature_guidance(feature, project_dir)


def _feature_guidance(feature: str, _project_dir: Path) -> None:
    """Print actionable steps for each addable feature."""
    _STEPS: dict[str, list[str]] = {
        "auth":      ["Add deps: python-jose[cryptography], passlib[bcrypt], python-multipart", "Add app/core/security.py (JWT helpers)", "Add auth endpoints: app/api/v1/auth.py", "Add to .env: SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES=30, ALGORITHM=HS256"],
        "s3":        ["Add dep: boto3>=1.34.0", "Create app/core/storage.py (upload, presigned_url, delete)", "Add to .env: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_S3_BUCKET, AWS_S3_ENDPOINT_URL (MinIO: http://localhost:9000)"],
        "gcs":       ["Add dep: google-cloud-storage>=2.16.0", "Create app/core/storage.py (GCS client)", "Add to .env: GCS_PROJECT_ID, GCS_BUCKET, GOOGLE_APPLICATION_CREDENTIALS=./service-account.json"],
        "cloudinary":["Add dep: cloudinary>=1.40.0", "Create app/core/storage.py (Cloudinary upload/CDN)", "Add to .env: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET"],
        "openai":    ["Add dep: openai>=1.30.0", "Create app/core/ai.py (chat_completion, get_embedding)", "Add to .env: OPENAI_API_KEY, OPENAI_MODEL=gpt-4o, OPENAI_EMBEDDING_MODEL, OPENAI_BASE_URL="],
        "anthropic": ["Add dep: anthropic>=0.28.0", "Create app/core/ai.py (chat_completion)", "Add to .env: ANTHROPIC_API_KEY, ANTHROPIC_MODEL=claude-3-5-sonnet-20241022"],
        "gemini":    ["Add dep: google-generativeai>=0.7.0", "Create app/core/ai.py (chat_completion, get_embedding)", "Add to .env: GEMINI_API_KEY, GEMINI_MODEL=gemini-1.5-pro"],
        "ollama":    ["No API key needed — run: docker run -p 11434:11434 ollama/ollama", "Create app/core/ai.py (chat via httpx)", "Add to .env: OLLAMA_HOST=localhost, OLLAMA_PORT=11434, OLLAMA_MODEL=llama3"],
        "langchain": ["Add deps: langchain>=0.2.0, langchain-openai>=0.1.0", "Create app/core/ai.py (LangChain ChatOpenAI + embeddings)", "Add to .env: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL"],
        "llamaindex":["Add deps: llama-index>=0.10.0, llama-index-llms-openai, llama-index-embeddings-openai", "Create app/core/ai.py (LlamaIndex VectorStoreIndex)", "Add to .env: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDING_MODEL"],
        "alembic":   ["Add dep: alembic>=1.13.0", "Run: alembic init migrations", "Replace migrations/env.py with async-compatible version", "Add to [tool.uv.scripts]: migrate = 'alembic upgrade head'", "Run: uv run migrate"],
        "celery":    ["Add dep: celery[redis]>=5.3.6", "Create tasks/celery_app.py + tasks/sample_tasks.py", "Add to .env: REDIS_HOST, REDIS_PORT, REDIS_DB", "Add to [tool.uv.scripts]: worker = 'celery -A tasks.celery_app worker --loglevel=info'"],
        "arq":       ["Add deps: arq>=0.25.0, redis[hiredis]>=5.0.0", "Create tasks/arq_worker.py (WorkerSettings, task defs)", "Run with: arq tasks.arq_worker.WorkerSettings"],
        "redis":     ["Add dep: redis[hiredis]>=5.0.0", "Add to .env: REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB", "Add redis_url @property to Settings in app/core/config.py"],
        "kafka":     ["Add dep: aiokafka>=0.10.0", "Add to .env: KAFKA_HOST=localhost, KAFKA_PORT=9092"],
        "sentry":    ["Add dep: sentry-sdk[fastapi]>=2.0.0", "Create app/core/monitoring.py (init_sentry)", "Add to .env: SENTRY_DSN=https://xxx@sentry.io/yyy", "Call init_sentry() in app/main.py on startup"],
        "prometheus":["Add dep: prometheus-fastapi-instrumentator>=7.0.0", "Create app/core/monitoring.py (init_prometheus)", "Call init_prometheus(app) in app/main.py — exposes /metrics"],
        "opentelemetry": ["Add dep: opentelemetry-sdk, opentelemetry-instrumentation-fastapi", "Set OTEL_EXPORTER_OTLP_ENDPOINT in .env or compose"],
        "sendgrid":  ["Add dep: sendgrid>=6.11.0", "Create app/core/email.py", "Add to .env: SENDGRID_API_KEY, SENDGRID_FROM_EMAIL"],
        "smtp":      ["Add dep: fastapi-mail>=1.4.1", "Create app/core/email.py", "Add to .env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL"],
        "ses":       ["Add dep: boto3>=1.34.0", "Create app/core/email.py", "Add to .env: AWS_* credentials, SES_FROM_EMAIL"],
        "resend":    ["Add dep: resend>=2.1.0", "Create app/core/email.py (Resend client)", "Add to .env: RESEND_API_KEY"],
        "slack":     ["No extra dep (uses httpx)", "Create app/core/notifications.py", "Add to .env: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/..."],
        "discord":   ["No extra dep (uses httpx)", "Create app/core/notifications.py", "Add to .env: DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/..."],
        "qdrant":    ["Add dep: qdrant-client[fastembed]>=1.9.0", "Create app/core/vector_db.py", "Add to .env: QDRANT_HOST=localhost, QDRANT_PORT=6333, QDRANT_API_KEY= (blank for local)"],
        "chroma":    ["Add dep: chromadb>=0.5.0", "Create app/core/vector_db.py (persistent local client)", "No env vars needed — data stored in ./chroma_data"],
        "pinecone":  ["Add dep: pinecone-client>=3.2.0", "Create app/core/vector_db.py", "Add to .env: PINECONE_API_KEY, PINECONE_INDEX_NAME"],
        "elasticsearch": ["Add dep: elasticsearch[async]>=8.13.0", "Create app/core/vector_db.py (kNN search)", "Add to .env: ELASTICSEARCH_HOST, ELASTICSEARCH_PORT, ELASTICSEARCH_API_KEY"],
        "meilisearch": ["Add dep: meilisearch>=0.30.0", "Create app/core/search.py (Meilisearch client)", "Add to .env: MEILISEARCH_HOST=http://localhost:7700, MEILISEARCH_API_KEY"],
        "opensearch": ["Add dep: opensearch-py[async]>=2.5.0", "Create app/core/search.py (OpenSearch client)", "Add to .env: OPENSEARCH_HOST, OPENSEARCH_PORT, OPENSEARCH_USER, OPENSEARCH_PASSWORD"],
        "vespa":     ["Add dep: pyvespa>=0.40.0", "Create app/core/search.py (Vespa client)", "Add to .env: VESPA_ENDPOINT"],
        "websockets":["No extra dep (built into FastAPI)", "Create app/core/ws_manager.py (ConnectionManager)", "Create app/api/v1/ws/router.py — /ws/connect, /ws/connect/{room_id}"],
        "sse":       ["Add dep: sse-starlette>=2.1.0", "Create app/api/v1/streaming/router.py", "Return EventSourceResponse(async_generator)"],
        "graphql":   ["Add dep: strawberry-graphql[fastapi]>=0.227.0", "Create app/api/graphql.py (Query + Mutation + Subscription)", "Mount: app.include_router(graphql_router, prefix='/graphql')"],
        "stripe":    ["Add dep: stripe>=9.0.0", "Create app/api/v1/payments/router.py (webhook endpoint)", "Add to .env: STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET"],
        "sso":       ["Add dep: fastapi-sso>=0.14.0", "Create app/api/v1/auth/sso.py (Google/Github/Microsoft SSO)", "Add to .env: GOOGLE_CLIENT_ID, GITHUB_CLIENT_ID, etc."],
        "sso-google": ["1. Use 'fastapi-spawn new temp_app --extra sso-google' and copy the resulting sso.py"],
        "sso-github": ["1. Use 'fastapi-spawn new temp_app --extra sso-github' and copy the resulting sso.py"],
        "sso-microsoft": ["1. Use 'fastapi-spawn new temp_app --extra sso-microsoft' and copy the resulting sso.py"],
        "seed":      ["Add dep: faker>=25.0.0", "Create db/seed.py (generate 100 mock users/posts)", "Run: uv run python db/seed.py"],
        "ocr":       ["Add deps: pymupdf>=1.24.0, pytesseract>=0.3.10", "Create app/core/ocr.py (PDF parsing pipeline)", "Install system deps: sudo apt install tesseract-ocr"],
        "rbac":      ["Create app/core/permissions.py and app/api/v1/permissions/router.py", "Add app.include_router(permissions.router) to main.py"],
        "caching":   ["Add dep: fastapi-cache2[redis]>=0.2.1", "Create app/core/cache.py", "Initialize cache in lifespan and use @cache(expire=60) on endpoints"],
        "response-format": ["Create app/middleware/response_format.py", "Add app.add_middleware(ResponseFormattingMiddleware) to main.py"],
        "docker":    ["Create Dockerfile (multi-stage, uv-based)", "Create docker-compose.yml with all selected services", "Create .dockerignore"],
        "ci":        ["Create .github/workflows/tests.yml (matrix: 3.10, 3.11, 3.12)", "Create .github/workflows/publish.yml (v* tags → PyPI)", "Add PYPI_API_TOKEN to GitHub repo secrets"],
        "helm":      ["Create infra/helm/Chart.yaml", "Create infra/helm/values.yaml (replicas, image, resources)", "Run: helm install my-release ./infra/helm"],
        "terraform": ["Create infra/terraform/main.tf (AWS ECR + ECS)", "Create infra/terraform/variables.tf", "Run: terraform -chdir=infra/terraform init && terraform apply"],
    }

    steps = _STEPS.get(feature, [])
    if steps:
        content = "\n".join(f"  [dim]{i+1}.[/dim] {s}" for i, s in enumerate(steps))
        console.print(Panel(content, title=f"[bold cyan]Steps to add '{feature}'[/bold cyan]", border_style="cyan", padding=(0, 1)))
    console.print(f"\n[dim]Preview files:[/dim] [bold cyan]fastapi-spawn new <name> --{feature} --dry-run[/bold cyan]")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _print_banner() -> None:
    import os
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    console.print(Panel.fit(
        f"[bold cyan]fastapi-spawn[/bold cyan]  [dim]v{__version__}[/dim]\n"
        "[dim]Production-ready FastAPI project scaffolding[/dim]",
        border_style="cyan", padding=(0, 2),
    ))


def _print_summary(config: ProjectConfig) -> None:
    table = Table(title="Project Configuration", border_style="dim", show_header=False, show_lines=False)
    table.add_column("Key", style="bold dim")
    table.add_column("Value", style="cyan")
    for key, val in config.summary_lines():
        table.add_row(key, val)
    console.print(table)


def _print_next_steps(config: ProjectConfig) -> None:
    steps = [
        f"  [bold cyan]cd {config.project_name}[/bold cyan]",
        "  [bold cyan]uv sync[/bold cyan]",
    ]
    if config.has_alembic:
        steps.append("  [bold cyan]uv run migrate[/bold cyan]")
    if config.has_docker:
        steps.append("  [bold cyan]docker compose up --build[/bold cyan]")
    else:
        steps.append("  [bold cyan]uv run dev[/bold cyan]")

    console.print(Panel(
        "\n".join(steps),
        title="[bold green]Next Steps[/bold green]",
        border_style="green",
        padding=(0, 1),
    ))


if __name__ == "__main__":
    app()
