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


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"
    ),
) -> None:
    pass

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
@app.command("start", help="Create a project using a preset template.")
def start(
    preset: Optional[str] = typer.Argument(None, help="Preset name (basic, full-local, full)"),
    project_name: Optional[str] = typer.Argument(None, help="Name of the new project"),
    output: Path = typer.Option(Path("."), "--output", "-o", help="Output directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing directory"),
) -> None:
    _print_banner()
    
    if not preset:
        import questionary
        from fastapi_spawn.interactive import SPAWN_STYLE
        preset = questionary.select(
            "Which preset do you want to use?",
            choices=["custom", "basic", "full-local", "full"],
            default="custom",
            style=SPAWN_STYLE,
        ).unsafe_ask()
        
    if preset == "custom":
        from fastapi_spawn.interactive import run_interactive_flow
        opts = run_interactive_flow(project_name or "")
        project_name = opts["project_name"]
        config = ProjectConfig(
            project_name=project_name,
            db=opts["db"],
            orm=opts["orm"],
            migration=opts.get("migration", MigrationTool.none),
            auth=opts["auth"],
            broker=opts["broker"],
            cache=opts["cache"],
            storage=opts["storage"],
            ai=opts["ai"],
            api_extra=opts.get("api_extra", APIExtra.none),
            monitoring=opts["monitoring"],
            log_lib=opts["log_lib"],
            log_dest=opts.get("log_dest", LogDestination.local),
            email=opts.get("email", EmailProvider.none),
            notify=opts.get("notify", NotificationProvider.none),
            vector_db=opts["vector_db"],
            stack=opts["stack"],
            ci=opts["ci"],
            include_docker=opts["include_docker"],
            include_tests=opts["include_tests"],
            force=force,
        )
        
        _print_summary(config)
        
        import questionary
        from fastapi_spawn.interactive import SPAWN_STYLE
        
        use_current = questionary.confirm(
            "Do you want to generate files directly in the current directory? (If no, a subfolder will be created)", default=False, style=SPAWN_STYLE
        ).unsafe_ask()
        
        if use_current:
            output_dir = Path(".")
            config.create_project_folder = False
            import os
            if os.listdir("."):
                confirm = questionary.confirm(
                    "Current directory is not empty. This may overwrite files! Proceed?", default=False, style=SPAWN_STYLE
                ).unsafe_ask()
                if not confirm:
                    rprint("[yellow]Aborted.[/yellow]")
                    raise typer.Exit()
        else:
            output_dir = output / config.project_name

        try:
            generator = ProjectGenerator(config, output_dir)
            project_path = generator.generate()
            rprint(f"\n[bold green]✓ Project created:[/bold green] {project_path.resolve()}")
            _print_next_steps(config)
        except Exception as exc:
            rprint(f"\n[bold red]✗ Generation failed:[/bold red] {exc}")
            raise typer.Exit(1) from exc
            
        return
    else:
        if not project_name:
            import questionary
            from fastapi_spawn.interactive import SPAWN_STYLE
            from fastapi_spawn.validators import questionary_validator, validate_project_name
            project_name = questionary.text(
                "Project name:",
                validate=questionary_validator(validate_project_name),
                style=SPAWN_STYLE,
            ).unsafe_ask()
    assert project_name is not None
    if preset == "basic":
        config = ProjectConfig(
            project_name=project_name,
            db=Database.sqlite,
            orm=ORM.sqlalchemy,
            migration=MigrationTool.alembic,
            auth=AuthType.jwt,
            broker=Broker.none,
            cache=Cache.none,
            storage=Storage.local,
            ai=AIProvider.none,
            api_extra=APIExtra.none,
            monitoring=MonitoringProvider.none,
            log_lib=LogLibrary.loguru,
            log_dest=LogDestination.local,
            email=EmailProvider.none,
            notify=NotificationProvider.none,
            vector_db=VectorDB.none,
            stack=Stack.minimal,
            ci=CIProvider.none,
            include_docker=True,
            include_tests=True,
            force=force,
        )
    elif preset == "full-local":
        config = ProjectConfig(
            project_name=project_name,
            db=Database.postgresql,
            orm=ORM.sqlalchemy,
            migration=MigrationTool.alembic,
            auth=AuthType.jwt,
            broker=Broker.none,
            cache=Cache.none,
            storage=Storage.local,
            ai=AIProvider.none,
            api_extra=APIExtra.none,
            monitoring=MonitoringProvider.none,
            log_lib=LogLibrary.loguru,
            log_dest=LogDestination.local,
            email=EmailProvider.none,
            notify=NotificationProvider.none,
            vector_db=VectorDB.chroma,
            stack=Stack.standard,
            ci=CIProvider.none,
            include_docker=True,
            include_tests=True,
            force=force,
        )
    elif preset == "full":
        config = ProjectConfig(
            project_name=project_name,
            db=Database.postgresql,
            orm=ORM.sqlalchemy,
            migration=MigrationTool.alembic,
            auth=AuthType.jwt,
            broker=Broker.redis,
            cache=Cache.redis,
            storage=Storage.s3,
            ai=AIProvider.openai,
            api_extra=APIExtra.websockets,
            monitoring=MonitoringProvider.both,
            log_lib=LogLibrary.loguru,
            log_dest=LogDestination.local,
            email=EmailProvider.none,
            notify=NotificationProvider.none,
            vector_db=VectorDB.qdrant,
            stack=Stack.full,
            ci=CIProvider.github,
            include_docker=True,
            include_tests=True,
            force=force,
        )
    else:
        rprint(f"[bold red]✗ Error:[/bold red] Unknown preset '{preset}'. Available presets: basic, full-local, full, custom")
        raise typer.Exit(1)

    _print_summary(config)

    import questionary
    from fastapi_spawn.interactive import SPAWN_STYLE
    
    use_current = questionary.confirm(
        "Do you want to generate files directly in the current directory? (If no, a subfolder will be created)", default=False, style=SPAWN_STYLE
    ).unsafe_ask()
    
    if use_current:
        output_dir = Path(".")
        config.create_project_folder = False
        # Check if directory is not empty
        import os
        if os.listdir("."):
            confirm = questionary.confirm(
                "Current directory is not empty. This may overwrite files! Proceed?", default=False, style=SPAWN_STYLE
            ).unsafe_ask()
            if not confirm:
                rprint("[yellow]Aborted.[/yellow]")
                raise typer.Exit()
    else:
        output_dir = output / config.project_name

    try:
        generator = ProjectGenerator(config, output_dir)
        project_path = generator.generate()
        rprint(f"\n[bold green]✓ Project created:[/bold green] {project_path.resolve()}")
        _print_next_steps(config)
    except Exception as exc:
        rprint(f"\n[bold red]✗ Generation failed:[/bold red] {exc}")
        raise typer.Exit(1) from exc


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


@app.command("inspect", help="Inspect and fix corrupted or missing tracking files.")
def inspect_project(
    project_dir: Path = typer.Option(Path("."), "--dir", "-d", help="Path to the existing project"),
) -> None:
    """Inspect and fix corrupted or missing tracking files."""
    import json
    _print_banner()
    
    if not project_dir.exists():
        console.print(f"[bold red]✗ Directory not found:[/bold red] {project_dir.resolve()}")
        raise typer.Exit(1)

    config_path = project_dir / ".fastapi-spawn.json"
    project_status: dict = {}
    corrupted = False

    if config_path.exists():
        try:
            project_status = json.loads(config_path.read_text(encoding="utf-8"))
            console.print("[bold green]✓ Found .fastapi-spawn.json[/bold green]")
        except Exception:
            console.print("[bold yellow]⚠ .fastapi-spawn.json is corrupted.[/bold yellow]")
            corrupted = True
    else:
        console.print("[bold yellow]⚠ .fastapi-spawn.json is missing.[/bold yellow]")
        corrupted = True

    if corrupted:
        console.print("[cyan]Attempting to reconstruct project state...[/cyan]")
        inferred_features = []
        
        # Check pyproject.toml for deps
        pyproject_path = project_dir / "pyproject.toml"
        content = ""
        if pyproject_path.exists():
            content = pyproject_path.read_text(encoding="utf-8")
            if "fastapi-sso" in content or "pyjwt" in content:
                inferred_features.append("auth")
            if "boto3" in content:
                inferred_features.append("s3")
            if "google-cloud-storage" in content:
                inferred_features.append("gcs")
            if "cloudinary" in content:
                inferred_features.append("cloudinary")
            if "openai" in content:
                inferred_features.append("openai")
            if "anthropic" in content:
                inferred_features.append("anthropic")
            if "google-genai" in content or "google-generativeai" in content:
                inferred_features.append("gemini")
            if "ollama" in content:
                inferred_features.append("ollama")
            if "alembic" in content:
                inferred_features.append("alembic")
            if "celery" in content:
                inferred_features.append("celery")
            if "arq" in content:
                inferred_features.append("arq")
            if "redis" in content:
                inferred_features.append("redis")
            if "aiokafka" in content:
                inferred_features.append("kafka")
            if "sentry-sdk" in content:
                inferred_features.append("sentry")
            if "prometheus-fastapi-instrumentator" in content:
                inferred_features.append("prometheus")
            if "opentelemetry" in content:
                inferred_features.append("opentelemetry")
            if "sendgrid" in content:
                inferred_features.append("sendgrid")
            if "resend" in content:
                inferred_features.append("resend")
            if "qdrant" in content:
                inferred_features.append("qdrant")

        # Check for files
        if (project_dir / "app" / "core" / "security.py").exists():
            if "auth" not in inferred_features:
                inferred_features.append("auth")
        if (project_dir / "migrations" / "env.py").exists():
            if "alembic" not in inferred_features:
                inferred_features.append("alembic")

        project_status["installed_features"] = list(set(inferred_features))
        project_status["project_name"] = project_dir.name
        
        # Guess DB
        if "asyncpg" in content or "psycopg" in content:
            project_status["db"] = "postgresql"
        elif "aiomysql" in content or "pymysql" in content:
            project_status["db"] = "mysql"
        elif "motor" in content:
            project_status["db"] = "mongodb"
        else:
            project_status["db"] = "sqlite"

        try:
            config_path.write_text(json.dumps(project_status, indent=2), encoding="utf-8")
            console.print("[bold green]✓ Reconstructed and saved .fastapi-spawn.json[/bold green]")
        except Exception as e:
            console.print(f"[bold red]✗ Failed to save tracking file: {e}[/bold red]")
            raise typer.Exit(1)

    console.print(f"\n[bold cyan]Project Status:[/bold cyan]")
    console.print(f"  Name: {project_status.get('project_name', 'Unknown')}")
    console.print(f"  DB: {project_status.get('db', 'Unknown')}")
    console.print(f"  Installed Features: {', '.join(project_status.get('installed_features', [])) or 'None'}")


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
    "ses":         "AWS SES email",
    "resend":      "Resend transactional email",
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
    "admin":       "Auto-generated internal admin dashboard (sqladmin)",
    "pagination":  "Automatic endpoint pagination (fastapi-pagination)",
    "uploads":     "File upload router & handling",
    "docker":      "Dockerfile + docker-compose.yml",
    "ci":          "GitHub Actions CI/CD workflows",
    "helm":        "Helm chart (infra/helm/)",
    "terraform":   "Terraform scaffold (infra/terraform/)",
}


@app.command("add", help="Add a feature to an [bold]existing[/bold] fastapi-spawn project.")
def add_feature(
    feature: Optional[str] = typer.Argument(None, help="Feature to add. Leave blank to see all available features."),
    project_dir: Path = typer.Option(Path("."), "--dir", "-d", help="Path to the existing project"),
) -> None:
    import json
    import shlex
    import subprocess
    from jinja2 import Environment, PackageLoader, StrictUndefined, TemplateNotFound
    from fastapi_spawn.steps import FEATURE_ACTIONS

    _print_banner()

    # Load tracking config
    config_path = project_dir / ".fastapi-spawn.json"
    project_status: dict = {}
    if config_path.exists():
        try:
            project_status = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            console.print("[dim yellow]⚠ Could not parse .fastapi-spawn.json — starting fresh[/dim yellow]")

    # Show feature table if no feature given
    if not feature:
        installed = set(project_status.get("installed_features", []))
        table = Table(title="Available Features", box=None)
        table.add_column("Feature", style="bold green", justify="left")
        table.add_column("Description", style="white", justify="left")
        table.add_column("Status", justify="center")
        for k, v in _ADDABLE_FEATURES.items():
            status = "[bold green]✓ installed[/bold green]" if k in installed else "[dim]—[/dim]"
            table.add_row(k, v, status)
        console.print(table)
        console.print("\n[dim]Run: fastapi-spawn add <feature>[/dim]\n")
        raise typer.Exit(0)

    if feature not in _ADDABLE_FEATURES:
        console.print(
            f"[bold red]✗ Unknown feature:[/bold red] '{feature}'\n"
            f"[dim]Available: {', '.join(_ADDABLE_FEATURES)}[/dim]"
        )
        raise typer.Exit(1)

    if not project_dir.exists():
        console.print(f"[bold red]✗ Directory not found:[/bold red] {project_dir.resolve()}")
        raise typer.Exit(1)

    installed_features: list = project_status.get("installed_features", [])
    if feature in installed_features:
        console.print(f"[bold yellow]⚠ '{feature}' already installed in this project.[/bold yellow]")
        raise typer.Exit(0)

    action = FEATURE_ACTIONS.get(feature)
    if not action:
        console.print(f"[bold yellow]⚠ No automation defined for '{feature}'.[/bold yellow]")
        raise typer.Exit(0)

    console.print(Panel.fit(
        f"[bold cyan]→ Adding:[/bold cyan] [bold]{feature}[/bold]\n[dim]{_ADDABLE_FEATURES[feature]}[/dim]",
        border_style="cyan", padding=(0, 2),
    ))

    # [1/4] Install deps
    deps = action.get("deps", [])
    if deps:
        console.print("\n[bold cyan][1/4] Installing dependencies...[/bold cyan]")
        for d in deps:
            console.print(f"  [dim]uv add {d}[/dim]")
        try:
            subprocess.run(["uv", "add"] + deps, cwd=project_dir, check=True)
            console.print("  [bold green]✓ Dependencies installed[/bold green]")
        except subprocess.CalledProcessError:
            console.print(f"  [bold red]✗ Failed to install deps[/bold red]")
            raise typer.Exit(1)
    else:
        console.print("\n[bold cyan][1/4] No extra dependencies needed.[/bold cyan]")

    # [2/4] Generate files from templates
    files = action.get("files", [])
    if files:
        console.print("\n[bold cyan][2/4] Generating files...[/bold cyan]")
        jinja_env = Environment(
            loader=PackageLoader("fastapi_spawn", "templates"),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        ctx = {
            "project_name": project_status.get("project_name", project_dir.name),
            "db": project_status.get("db", "postgresql"),
            "orm": project_status.get("orm", "sqlalchemy"),
            "has_auth": feature == "auth" or "auth" in installed_features,
            "has_alembic": feature == "alembic" or "alembic" in installed_features,
            "has_broker": feature in ("celery", "arq") or any(f in installed_features for f in ("celery", "arq")),
            "has_s3": feature in ("s3", "gcs", "cloudinary") or any(f in installed_features for f in ("s3", "gcs", "cloudinary")),
            "has_ai": feature in ("openai", "anthropic", "gemini", "ollama", "langchain", "llamaindex"),
            "ai_provider": feature if feature in ("openai", "anthropic", "gemini", "ollama", "langchain", "llamaindex") else project_status.get("ai", "none"),
            "storage_provider": feature if feature in ("s3", "gcs", "cloudinary") else project_status.get("storage", "none"),
            "email_provider": feature if feature in ("sendgrid", "smtp", "ses", "resend") else project_status.get("email", "none"),
            "notify_provider": feature if feature in ("slack", "discord") else project_status.get("notify", "none"),
            "vector_db": feature if feature in ("qdrant", "chroma", "pinecone", "elasticsearch") else project_status.get("vector_db", "none"),
            "monitoring": feature if feature in ("sentry", "prometheus", "opentelemetry") else project_status.get("monitoring", "none"),
        }
        for template_path, dest_rel in files:
            dest = project_dir / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                tmpl = jinja_env.get_template(template_path)
                dest.write_text(tmpl.render(**ctx), encoding="utf-8")
                console.print(f"  [bold green]✓[/bold green] {dest_rel}")
            except TemplateNotFound:
                console.print(f"  [dim yellow]⚠ No template for {dest_rel} — skipping[/dim yellow]")
            except Exception as exc:
                console.print(f"  [bold red]✗ {dest_rel}: {exc}[/bold red]")
    else:
        console.print("\n[bold cyan][2/4] No files to generate.[/bold cyan]")

    # [3/4] Append env vars to .env
    env_vars = action.get("env_vars", [])
    if env_vars:
        console.print("\n[bold cyan][3/4] Updating .env...[/bold cyan]")
        env_file = project_dir / ".env"
        existing_env = env_file.read_text(encoding="utf-8") if env_file.exists() else ""
        new_lines = [v for v in env_vars if v.split("=")[0].strip() not in existing_env]
        if new_lines:
            with env_file.open("a", encoding="utf-8") as f:
                f.write(f"\n# Added by fastapi-spawn add {feature}\n")
                for line in new_lines:
                    f.write(line + "\n")
            console.print(f"  [bold green]✓[/bold green] Added {len(new_lines)} env var(s)")
        else:
            console.print("  [dim]All env vars already in .env[/dim]")
    else:
        console.print("\n[bold cyan][3/4] No env vars needed.[/bold cyan]")

    # [4/4] Run init commands / special handling
    if action.get("_special") == "alembic":
        console.print("\n[bold cyan][4/4] Initializing Alembic...[/bold cyan]")
        try:
            subprocess.run(["uv", "run", "alembic", "init", "migrations"], cwd=project_dir, check=True)
            console.print("  [bold green]✓ alembic init migrations[/bold green]")
            db_val = project_status.get("db", "postgresql")
            cfg = ProjectConfig(project_name=project_dir.name, db=Database(db_val), orm=ORM.sqlalchemy, migration=MigrationTool.alembic)
            gen = ProjectGenerator(cfg, project_dir)
            gen._render_to(project_dir / "migrations" / "env.py", "alembic/env.py.j2")
            console.print("  [bold green]✓ Rendered async env.py[/bold green]")
        except subprocess.CalledProcessError:
            console.print("  [bold red]✗ alembic init failed[/bold red]")
    elif action.get("run_cmds"):
        console.print("\n[bold cyan][4/4] Running commands...[/bold cyan]")
        for cmd_str in action["run_cmds"]:
            console.print(f"  [dim]{cmd_str}[/dim]")
            try:
                subprocess.run(shlex.split(cmd_str), cwd=project_dir, check=True)
                console.print(f"  [bold green]✓[/bold green] done")
            except subprocess.CalledProcessError:
                console.print(f"  [bold red]✗ Failed: {cmd_str}[/bold red]")
    else:
        console.print("\n[bold cyan][4/4] No init commands needed.[/bold cyan]")

    # Update tracking file
    installed_features.append(feature)
    project_status["installed_features"] = installed_features
    try:
        config_path.write_text(json.dumps(project_status, indent=2), encoding="utf-8")
        console.print("\n[dim]ℹ .fastapi-spawn.json updated[/dim]")
    except Exception:
        pass

    note = action.get("note")
    msg = f"[bold green]✓ {feature.capitalize()} added successfully![/bold green]"
    if note:
        msg += f"\n[dim]{note}[/dim]"
    console.print(Panel(msg, border_style="green", padding=(0, 2)))


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
    steps = []
    if config.create_project_folder:
        steps.append(f"  [bold cyan]cd {config.project_name}[/bold cyan]")
    steps.append("  [bold cyan]uv sync[/bold cyan]")
    if config.has_alembic:
        steps.append("  [bold cyan]uv run alembic upgrade head[/bold cyan]")
    if config.has_docker:
        steps.append("  [bold cyan]docker compose up --build -d[/bold cyan]")
    else:
        steps.append("  [bold cyan]uv run uvicorn app.main:app --reload[/bold cyan]")

    console.print(Panel(
        "\n".join(steps),
        title="[bold green]Next Steps[/bold green]",
        border_style="green",
        padding=(0, 1),
    ))


if __name__ == "__main__":
    app()
