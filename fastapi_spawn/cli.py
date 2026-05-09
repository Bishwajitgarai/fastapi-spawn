"""Main CLI entry point for fastapi-spawn."""

from __future__ import annotations

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


# ── `new` command ─────────────────────────────────────────────────────────────

@app.command("new", help="Create a new FastAPI project.")
def new(
    project_name: Optional[str] = typer.Argument(None, help="Name of the new project"),
    db: Optional[Database] = typer.Option(None, "--db", help="Database backend"),
    orm: Optional[ORM] = typer.Option(None, "--orm", help="ORM / ODM"),
    migration: Optional[MigrationTool] = typer.Option(None, "--migration", help="Migration tool (alembic, aerich, none)"),
    auth: Optional[AuthType] = typer.Option(None, "--auth", help="Auth strategy"),
    broker: Optional[Broker] = typer.Option(None, "--broker", help="Message broker"),
    cache: Optional[Cache] = typer.Option(None, "--cache", help="Cache layer"),
    storage: Optional[Storage] = typer.Option(None, "--storage", help="File storage (s3, local, none)"),
    ai: Optional[AIProvider] = typer.Option(None, "--ai", help="AI provider (openai, anthropic, none)"),
    stack: Optional[Stack] = typer.Option(None, "--stack", help="Deployment stack"),
    ci: Optional[CIProvider] = typer.Option(None, "--ci", help="CI/CD provider"),
    log_lib: Optional[LogLibrary] = typer.Option(None, "--log-lib", help="Logging library"),
    no_docker: bool = typer.Option(False, "--no-docker", help="Skip Docker files"),
    no_tests: bool = typer.Option(False, "--no-tests", help="Skip test suite"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview structure without writing files"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing directory"),
    output: Path = typer.Option(Path("."), "--output", "-o", help="Output directory"),
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"
    ),
) -> None:
    _print_banner()

    needs_interactive = any(
        x is None for x in [project_name, db, orm, migration, auth, broker, cache, storage, ai, stack, ci, log_lib]
    )

    if needs_interactive:
        console.print("[dim]Some options are missing — launching interactive mode...[/dim]\n")
        opts = run_interactive_flow(project_name or "")
        project_name = project_name or opts["project_name"]
        db = db or opts["db"]
        orm = orm or opts["orm"]
        migration = migration or opts["migration"]
        auth = auth or opts["auth"]
        broker = broker or opts["broker"]
        cache = cache or opts["cache"]
        storage = storage or opts["storage"]
        ai = ai or opts["ai"]
        stack = stack or opts["stack"]
        ci = ci or opts["ci"]
        log_lib = log_lib or opts["log_lib"]
        include_docker = (not no_docker) and opts["include_docker"]
        include_tests = (not no_tests) and opts["include_tests"]
    else:
        include_docker = not no_docker
        include_tests = not no_tests

    # Validate
    try:
        validate_project_name(project_name)  # type: ignore[arg-type]
        validate_orm_db_compat(orm, db)  # type: ignore[arg-type]
        if not dry_run:
            validate_output_dir(output / project_name, force)  # type: ignore[operator]
    except ValueError as exc:
        console.print(f"[bold red]✗ Error:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    config = ProjectConfig(
        project_name=project_name,  # type: ignore[arg-type]
        db=db,  # type: ignore[arg-type]
        orm=orm,  # type: ignore[arg-type]
        migration=migration,  # type: ignore[arg-type]
        auth=auth,  # type: ignore[arg-type]
        broker=broker,  # type: ignore[arg-type]
        cache=cache,  # type: ignore[arg-type]
        storage=storage,  # type: ignore[arg-type]
        ai=ai,  # type: ignore[arg-type]
        stack=stack,  # type: ignore[arg-type]
        ci=ci,  # type: ignore[arg-type]
        log_lib=log_lib,  # type: ignore[arg-type]
        include_docker=include_docker,
        include_tests=include_tests,
        dry_run=dry_run,
        force=force,
    )

    _print_summary(config)

    if dry_run:
        console.print("\n[bold yellow]🔍 Dry-run mode — no files will be written.[/bold yellow]\n")

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

    table.add_row("--db", ", ".join(d.value for d in Database))
    table.add_row("--orm", ", ".join(o.value for o in ORM))
    table.add_row("--migration", ", ".join(m.value for m in MigrationTool))
    table.add_row("--auth", ", ".join(a.value for a in AuthType))
    table.add_row("--broker", ", ".join(b.value for b in Broker))
    table.add_row("--cache", ", ".join(c.value for c in Cache))
    table.add_row("--storage", ", ".join(s.value for s in Storage))
    table.add_row("--ai", ", ".join(a.value for a in AIProvider))
    table.add_row("--stack", ", ".join(s.value for s in Stack))
    table.add_row("--ci", ", ".join(c.value for c in CIProvider))
    table.add_row("--log-lib", ", ".join(l.value for l in LogLibrary))
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


# ── `add` command ────────────────────────────────────────────────────────────

_ADDABLE_FEATURES = {
    "auth":      "Authentication (JWT / OAuth2 / API Key)",
    "s3":        "AWS S3 file storage (boto3)",
    "openai":    "OpenAI integration (chat + embeddings)",
    "anthropic": "Anthropic Claude integration",
    "alembic":   "Alembic async database migrations",
    "celery":    "Celery worker + sample tasks",
    "redis":     "Redis cache / broker support",
    "kafka":     "Kafka broker support (aiokafka)",
    "docker":    "Dockerfile + docker-compose.yml",
    "ci":        "GitHub Actions CI/CD workflows",
    "helm":      "Helm chart (infra/helm/)",
    "terraform": "Terraform scaffold (infra/terraform/)",
}


@app.command(
    "add",
    help="Add a feature to an [bold]existing[/bold] fastapi-spawn project.",
)
def add_feature(
    feature: str = typer.Argument(
        ...,
        help=f"Feature to add. Choices: {', '.join(_ADDABLE_FEATURES)}",
    ),
    project_dir: Path = typer.Option(
        Path("."),
        "--dir", "-d",
        help="Path to the existing project (default: current directory)",
    ),
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

    console.print(
        f"[bold cyan]→ Adding feature:[/bold cyan] [bold]{feature}[/bold] — "
        f"{_ADDABLE_FEATURES[feature]}"
    )
    console.print(
        f"[dim]Target project:[/dim] {project_dir.resolve()}"
    )
    console.print()

    # Feature-specific guidance
    _feature_guidance(feature, project_dir)


def _feature_guidance(feature: str, project_dir: Path) -> None:
    """Print actionable instructions for each addable feature."""
    steps: list[str] = []

    if feature == "auth":
        steps = [
            "Add to pyproject.toml deps: python-jose[cryptography], passlib[bcrypt], python-multipart",
            "Copy app/core/security.py — run: fastapi-spawn new <name> --auth jwt --dry-run to preview",
            "Add auth endpoints to app/api/v1/auth.py",
            "Add ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY to .env",
        ]
    elif feature == "s3":
        steps = [
            "Add to pyproject.toml deps: boto3>=1.34.0",
            "Create app/core/storage.py with boto3 helpers",
            "Add to .env: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_S3_BUCKET, AWS_S3_ENDPOINT_URL",
            "Add to app/core/config.py: AWS_* individual fields + (optional) s3_endpoint property",
        ]
    elif feature == "openai":
        steps = [
            "Add to pyproject.toml deps: openai>=1.30.0",
            "Create app/core/ai.py with AsyncOpenAI client",
            "Add to .env: OPENAI_API_KEY=sk-placeholder, OPENAI_MODEL=gpt-4o, OPENAI_BASE_URL= ",
        ]
    elif feature == "anthropic":
        steps = [
            "Add to pyproject.toml deps: anthropic>=0.28.0",
            "Create app/core/ai.py with AsyncAnthropic client",
            "Add to .env: ANTHROPIC_API_KEY=sk-ant-placeholder, ANTHROPIC_MODEL=claude-3-5-sonnet-20241022",
        ]
    elif feature == "alembic":
        steps = [
            "Add to pyproject.toml deps: alembic>=1.13.0",
            "Run: alembic init migrations",
            "Replace migrations/env.py with async-compatible version",
            "Add to [tool.uv.scripts]: migrate = 'alembic upgrade head'",
            "Run: uv run migrate",
        ]
    elif feature == "celery":
        steps = [
            "Add to pyproject.toml deps: celery[redis]>=5.3.6",
            "Create tasks/celery_app.py and tasks/sample_tasks.py",
            "Add to .env: REDIS_HOST, REDIS_PORT, REDIS_DB",
            "Add to [tool.uv.scripts]: worker = 'celery -A tasks.celery_app worker --loglevel=info'",
            "Run: uv run worker",
        ]
    elif feature == "redis":
        steps = [
            "Add to pyproject.toml deps: redis[hiredis]>=5.0.0",
            "Add to .env: REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB",
            "Add redis_url @property to Settings in app/core/config.py",
        ]
    elif feature == "kafka":
        steps = [
            "Add to pyproject.toml deps: aiokafka>=0.10.0",
            "Add to .env: KAFKA_HOST=localhost, KAFKA_PORT=9092",
            "Create tasks/ producer/consumer modules",
        ]
    elif feature == "docker":
        steps = [
            "Create Dockerfile (uses uv for fast builds)",
            "Create docker-compose.yml with all services",
            "Create .dockerignore",
            "Run: docker compose up --build",
        ]
    elif feature == "ci":
        steps = [
            "Create .github/workflows/tests.yml (matrix: py3.10, 3.11, 3.12)",
            "Create .github/workflows/publish.yml (triggered on v* tags)",
            "Add PYPI_API_TOKEN to GitHub repo secrets",
        ]
    elif feature == "helm":
        steps = [
            "Create infra/helm/Chart.yaml",
            "Create infra/helm/values.yaml with replica, image, resource config",
            "Run: helm install my-release ./infra/helm",
        ]
    elif feature == "terraform":
        steps = [
            "Create infra/terraform/main.tf (AWS ECR + ECS scaffold)",
            "Create infra/terraform/variables.tf",
            "Run: terraform -chdir=infra/terraform init && terraform apply",
        ]

    if steps:
        panel_content = "\n".join(f"  [dim]{i+1}.[/dim] {s}" for i, s in enumerate(steps))
        console.print(
            Panel(
                panel_content,
                title=f"[bold cyan]Steps to add '{feature}'[/bold cyan]",
                border_style="cyan",
                padding=(0, 1),
            )
        )
        console.print(
            "\n[dim]Tip: Re-scaffold with --dry-run to preview exact file contents:[/dim]\n"
            f"  [bold cyan]fastapi-spawn new <name> --{feature if feature not in ('s3','openai','anthropic','celery','redis','kafka') else 'storage s3 --ai openai'} --dry-run[/bold cyan]"
        )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _print_banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]⚡ fastapi-spawn[/bold cyan]  [dim]v{}[/dim]\n"
            "[dim]Production-ready FastAPI project scaffolding[/dim]".format(__version__),
            border_style="cyan",
            padding=(0, 2),
        )
    )


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
        steps.append("  [bold cyan]uv run alembic upgrade head[/bold cyan]")
    if config.has_docker:
        steps.append("  [bold cyan]docker compose up --build[/bold cyan]")
    else:
        steps.append("  [bold cyan]uv run main.py[/bold cyan]")

    console.print(
        Panel(
            "\n".join(steps),
            title="[bold green]Next Steps[/bold green]",
            border_style="green",
            padding=(0, 1),
        )
    )


if __name__ == "__main__":
    app()
