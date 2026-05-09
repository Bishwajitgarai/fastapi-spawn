"""Core project generation engine for fastapi-spawn."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from jinja2 import Environment, PackageLoader, StrictUndefined, TemplateNotFound
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from fastapi_spawn.config import ProjectConfig
from fastapi_spawn.constants import CIProvider, MigrationTool, Stack

console = Console()


class ProjectGenerator:
    """
    Generates a FastAPI project from Jinja2 templates.

    Final generated structure:
        <project>/
        ├── app/
        │   ├── api/v1/           (health, auth?)
        │   ├── core/             (config, logging, exceptions, security?, storage?, ai?)
        │   ├── db/               (session)
        │   ├── models/
        │   ├── schemas/
        │   ├── services/
        │   └── repositories/
        ├── tasks/                (celery_app, sample_tasks) — root level
        ├── migrations/           (alembic env.py + versions/) — when alembic chosen
        ├── infra/
        │   ├── docker/
        │   ├── helm/
        │   └── terraform/
        ├── tests/
        ├── main.py               uv run entry point
        ├── alembic.ini           when alembic chosen
        ├── Dockerfile
        ├── docker-compose.yml
        ├── .env  .env.example  .gitignore  .pre-commit-config.yaml
        ├── Makefile
        └── pyproject.toml
    """

    def __init__(self, config: ProjectConfig, output_dir: Path) -> None:
        self.config = config
        self.output_dir = output_dir
        self.ctx = config.to_context()
        self._env = Environment(
            loader=PackageLoader("fastapi_spawn", "templates"),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    # ── Public API ──────────────────────────────────────────────────────────

    def generate(self) -> Path:
        if self.config.dry_run:
            self._dry_run_display()
            return self.output_dir / self.config.project_name

        project_path = self.output_dir / self.config.project_name

        if project_path.exists() and self.config.force:
            shutil.rmtree(project_path)

        with tempfile.TemporaryDirectory() as staging_root:
            staging = Path(staging_root) / self.config.project_name
            staging.mkdir(parents=True)

            with Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]{task.description}"),
                transient=True,
                console=console,
            ) as progress:
                task = progress.add_task("Writing root files...", total=None)

                self._generate_root(staging)

                progress.update(task, description="Writing app/ module...")
                self._generate_app(staging)

                if self.config.has_broker:
                    progress.update(task, description="Writing tasks/...")
                    self._generate_tasks(staging)

                if self.config.has_alembic:
                    progress.update(task, description="Writing Alembic migrations/...")
                    self._generate_alembic(staging)

                if self.config.include_tests:
                    progress.update(task, description="Writing tests/...")
                    self._generate_tests(staging)

                if self.config.has_docker:
                    progress.update(task, description="Writing Docker files...")
                    self._generate_docker(staging)

                if self.config.has_infra or self.config.stack == Stack.full:
                    progress.update(task, description="Writing infra/...")
                    self._generate_infra(staging)

                if self.config.has_ci:
                    progress.update(task, description="Writing CI/CD workflows...")
                    self._generate_ci(staging)

                if self.config.include_makefile:
                    self._render_to(staging / "Makefile", "base/Makefile.j2")

            shutil.copytree(str(staging), str(project_path))

        return project_path

    # ── Section generators ──────────────────────────────────────────────────

    def _generate_root(self, root: Path) -> None:
        self._render_to(root / "main.py", "root/main.py.j2")
        self._render_to(root / "pyproject.toml", "base/pyproject.toml.j2")
        self._render_to(root / ".env", "base/env.j2")
        self._render_to(root / ".env.example", "base/env_example.j2")
        self._render_to(root / ".gitignore", "base/gitignore.j2")
        self._render_to(root / ".pre-commit-config.yaml", "base/pre_commit.j2")
        self._render_to(root / "README.md", "base/README.md.j2")

    def _generate_app(self, root: Path) -> None:
        pkg = root / "app"
        pkg.mkdir()
        self._render_to(pkg / "__init__.py", "app/__init__.py.j2")
        self._render_to(pkg / "main.py", "app/main.py.j2")

        # core/
        core = pkg / "core"
        core.mkdir()
        self._render_to(core / "__init__.py", "app/__init__.py.j2")
        self._render_to(core / "config.py", "app/core/config.py.j2")
        self._render_to(core / "logger.py", "app/core/logger.py.j2")
        self._render_to(core / "exceptions.py", "app/core/exceptions.py.j2")
        if self.config.has_auth:
            self._render_to(core / "security.py", "app/core/security.py.j2")
        if self.config.has_s3:
            self._render_to(core / "storage.py", "app/core/storage.py.j2")
        if self.config.has_ai:
            self._render_to(core / "ai.py", "app/core/ai.py.j2")
        if self.config.has_monitoring:
            self._render_to(core / "monitoring.py", "app/core/monitoring.py.j2")
        if self.config.has_email:
            self._render_to(core / "email.py", "app/core/email.py.j2")
        if self.config.has_notify:
            self._render_to(core / "notifications.py", "app/core/notifications.py.j2")
        if self.config.has_vector_db:
            self._render_to(core / "vector_db.py", "app/core/vector_db.py.j2")

        # middleware/
        mw = pkg / "middleware"
        mw.mkdir()
        self._render_to(mw / "__init__.py", "app/middleware/__init__.py.j2")
        self._render_to(mw / "request_logger.py", "app/middleware/request_logger.py.j2")
        self._render_to(mw / "rate_limit.py", "app/middleware/rate_limit.py.j2")

        # api/
        api = pkg / "api"
        api.mkdir()
        self._render_to(api / "__init__.py", "app/__init__.py.j2")
        self._render_to(api / "deps.py", "app/api/deps.py.j2")
        v1 = api / "v1"
        v1.mkdir()
        self._render_to(v1 / "__init__.py", "app/__init__.py.j2")
        self._render_to(v1 / "router.py", "app/api/v1/router.py.j2")
        (v1 / "health").mkdir()
        self._render_to(v1 / "health" / "router.py", "app/api/v1/health/router.py.j2")
        if self.config.has_auth:
            (v1 / "auth").mkdir()
            self._render_to(v1 / "auth" / "router.py", "app/api/v1/auth/router.py.j2")
        if self.config.has_websockets:
            (v1 / "ws").mkdir()
            self._render_to(v1 / "ws" / "router.py", "app/api/v1/ws/router.py.j2")
            self._render_to(core / "ws_manager.py", "app/core/ws_manager.py.j2")
        if self.config.has_graphql:
            self._render_to(api / "graphql.py", "app/api/graphql.py.j2")

        # db/ (only when a real database is chosen)
        if self.config.db.value != "none":
            db_dir = pkg / "db"
            db_dir.mkdir()
            self._render_to(db_dir / "__init__.py", "app/__init__.py.j2")
            self._render_to(db_dir / "session.py", "app/db/session.py.j2")

        # models/, schemas/, services/, repositories/
        for sub in ("models", "schemas", "services", "repositories"):
            d = pkg / sub
            d.mkdir()
            self._render_to(d / "__init__.py", "app/__init__.py.j2")

        # frontend/ — static showcase UI
        frontend_dir = pkg / "frontend"
        frontend_dir.mkdir()
        self._render_to(frontend_dir / "index.html", "app/frontend/index.html.j2")

        # logs/ directory (for file-based logging)
        if self.config.has_log_file:
            (root / "logs").mkdir(exist_ok=True)
            (root / "logs" / ".gitkeep").write_text("", encoding="utf-8")

        # Extras rendering
        extras = self.config.extras
        if "stripe" in extras:
            (v1 / "payments").mkdir(parents=True, exist_ok=True)
            self._render_to(v1 / "payments" / "router.py", "app/api/v1/payments/router.py.j2")
            self._render_to(v1 / "payments" / "__init__.py", "app/__init__.py.j2")
        
        has_sso = any(e.startswith("sso") for e in extras)
        if has_sso:
            (v1 / "auth").mkdir(parents=True, exist_ok=True)
            self._render_to(v1 / "auth" / "sso.py", "app/api/v1/auth/sso.py.j2")
            
        if "sse" in extras:
            (v1 / "streaming").mkdir(parents=True, exist_ok=True)
            self._render_to(v1 / "streaming" / "router.py", "app/api/v1/streaming/router.py.j2")
            self._render_to(v1 / "streaming" / "__init__.py", "app/__init__.py.j2")

        if "seed" in extras:
            (root / "db").mkdir(parents=True, exist_ok=True)
            self._render_to(root / "db" / "seed.py", "db/seed.py.j2")

        if "ocr" in extras:
            self._render_to(core / "ocr.py", "app/core/ocr.py.j2")

        if "meilisearch" in extras:
            self._render_to(core / "search.py", "app/core/search.py.j2")

        if "rbac" in extras:
            self._render_to(core / "permissions.py", "app/core/permissions.py.j2")
            (v1 / "permissions").mkdir(parents=True, exist_ok=True)
            self._render_to(v1 / "permissions" / "router.py", "app/api/v1/permissions/router.py.j2")

        if "caching" in extras:
            self._render_to(core / "cache.py", "app/core/cache.py.j2")

        if "response-format" in extras:
            middleware = pkg / "middleware"
            middleware.mkdir(exist_ok=True)
            self._render_to(middleware / "response_format.py", "app/middleware/response_format.py.j2")

        if "admin" in extras:
            (pkg / "admin").mkdir(parents=True, exist_ok=True)
            self._render_to(pkg / "admin" / "setup.py", "app/admin/setup.py.j2")

        if "pagination" in extras:
            (v1 / "pagination").mkdir(parents=True, exist_ok=True)
            self._render_to(v1 / "pagination" / "router.py", "app/api/v1/pagination/router.py.j2")

        if "uploads" in extras:
            (v1 / "uploads").mkdir(parents=True, exist_ok=True)
            self._render_to(v1 / "uploads" / "router.py", "app/api/v1/uploads/router.py.j2")


    def _generate_tasks(self, root: Path) -> None:
        """Root-level tasks/ directory."""
        tasks = root / "tasks"
        tasks.mkdir()
        self._render_to(tasks / "__init__.py", "app/__init__.py.j2")
        if self.config.broker.value in ("redis", "rabbitmq"):
            self._render_to(tasks / "celery_app.py", "tasks/celery_app.py.j2")
            self._render_to(tasks / "sample_tasks.py", "tasks/sample_tasks.py.j2")
        if self.config.broker.value == "arq":
            self._render_to(tasks / "arq_worker.py", "tasks/arq_worker.py.j2")

    def _generate_alembic(self, root: Path) -> None:
        """Alembic migration setup at project root."""
        self._render_to(root / "alembic.ini", "alembic/alembic.ini.j2")
        migrations = root / "migrations"
        migrations.mkdir()
        (migrations / "versions").mkdir()
        self._render_to(migrations / "env.py", "alembic/env.py.j2")
        self._render_to(migrations / "__init__.py", "app/__init__.py.j2")

    def _generate_tests(self, root: Path) -> None:
        tests = root / "tests"
        tests.mkdir()
        self._render_to(tests / "__init__.py", "app/__init__.py.j2")
        self._render_to(tests / "conftest.py", "tests/conftest.py.j2")
        self._render_to(tests / "test_health.py", "tests/test_health.py.j2")

    def _generate_docker(self, root: Path) -> None:
        self._render_to(root / "Dockerfile", "docker/Dockerfile.j2")
        self._render_to(root / "docker-compose.yml", "docker/docker-compose.yml.j2")
        self._render_to(root / ".dockerignore", "docker/dockerignore.j2")

    def _generate_ci(self, root: Path) -> None:
        ci = self.config.ci
        if ci in (CIProvider.github, CIProvider.both):
            gha = root / ".github" / "workflows"
            gha.mkdir(parents=True)
            self._render_to(gha / "tests.yml", "ci/github/tests.yml.j2")
            self._render_to(gha / "publish.yml", "ci/github/publish.yml.j2")
        if ci in (CIProvider.gitlab, CIProvider.both):
            self._render_to(root / ".gitlab-ci.yml", "ci/gitlab/gitlab-ci.yml.j2")

    def _generate_infra(self, root: Path) -> None:
        infra = root / "infra"
        (infra / "docker").mkdir(parents=True)
        self._render_to(infra / "docker" / "docker-compose.prod.yml", "infra/docker/docker-compose.prod.yml.j2")
        helm = infra / "helm"
        helm.mkdir()
        self._render_to(helm / "Chart.yaml", "infra/helm/Chart.yaml.j2")
        self._render_to(helm / "values.yaml", "infra/helm/values.yaml.j2")
        tf = infra / "terraform"
        tf.mkdir()
        self._render_to(tf / "main.tf", "infra/terraform/main.tf.j2")
        self._render_to(tf / "variables.tf", "infra/terraform/variables.tf.j2")

    # ── Render helper ───────────────────────────────────────────────────────

    def _render_to(self, dest: Path, template_name: str) -> None:
        try:
            tmpl = self._env.get_template(template_name)
        except TemplateNotFound:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(tmpl.render(**self.ctx), encoding="utf-8")

    # ── Dry-run display ─────────────────────────────────────────────────────

    def _dry_run_display(self) -> None:
        cfg = self.config
        tree = Tree(
            f":open_file_folder: [bold green]{cfg.project_name}/[/bold green]",
            guide_style="dim",
        )

        app = tree.add("[bold blue]app/[/bold blue]")
        app.add("__init__.py  main.py")
        core_items = "config.py  logging.py  exceptions.py"
        if cfg.has_auth:       core_items += "  security.py"
        if cfg.has_s3:         core_items += "  storage.py"
        if cfg.has_ai:         core_items += "  ai.py"
        app.add(f"[blue]core/[/blue]  {core_items}")
        api = app.add("[blue]api/[/blue]  deps.py  [dim]graphql.py[/dim]?")
        v1 = api.add("[blue]v1/[/blue]  router.py")
        v1.add("[blue]health/[/blue]  router.py")
        if cfg.has_auth:
            v1.add("[blue]auth/[/blue]  router.py")
        if cfg.has_websockets:
            v1.add("[blue]ws/[/blue]  router.py")
        if cfg.db.value != "none":
            app.add("[blue]db/[/blue]  session.py")
        for sub in ("models/", "schemas/", "services/", "repositories/"):
            app.add(sub)

        if cfg.has_broker:
            t = tree.add("[blue]tasks/[/blue]")
            t.add("celery_app.py  sample_tasks.py")

        if cfg.has_alembic:
            m = tree.add("[blue]migrations/[/blue]")
            m.add("env.py  [dim]versions/[/dim]")
            tree.add("alembic.ini")

        if cfg.include_tests:
            t = tree.add("[blue]tests/[/blue]")
            t.add("conftest.py  test_health.py")

        if cfg.has_infra or cfg.stack == Stack.full:
            infra = tree.add("[blue]infra/[/blue]")
            infra.add("[blue]docker/[/blue]  docker-compose.prod.yml")
            infra.add("[blue]helm/[/blue]  Chart.yaml  values.yaml")
            infra.add("[blue]terraform/[/blue]  main.tf  variables.tf")

        if cfg.has_ci and cfg.ci in (CIProvider.github, CIProvider.both):
            ci = tree.add("[blue].github/workflows/[/blue]")
            ci.add("tests.yml  publish.yml")

        root_files = "main.py  pyproject.toml  .env  .env.example  .gitignore  .pre-commit-config.yaml  README.md"
        if cfg.has_docker:
            root_files += "  Dockerfile  docker-compose.yml  .dockerignore"
        if cfg.include_makefile:
            root_files += "  Makefile"
        tree.add(root_files)

        console.print(tree)
