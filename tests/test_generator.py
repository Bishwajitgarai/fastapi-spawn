"""Tests for fastapi_spawn.generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from fastapi_spawn.config import ProjectConfig
from fastapi_spawn.constants import AuthType, Broker, Database, ORM, Stack
from fastapi_spawn.generator import ProjectGenerator


@pytest.fixture
def minimal_config() -> ProjectConfig:
    return ProjectConfig(
        project_name="test-project",
        db=Database.sqlite,
        orm=ORM.sqlalchemy,
        auth=AuthType.none,
        broker=Broker.none,
        stack=Stack.minimal,
        include_docker=False,
        include_tests=True,
    )


@pytest.fixture
def full_config() -> ProjectConfig:
    return ProjectConfig(
        project_name="full-project",
        db=Database.postgresql,
        orm=ORM.sqlalchemy,
        auth=AuthType.jwt,
        broker=Broker.redis,
        stack=Stack.full,
        include_docker=True,
        include_tests=True,
    )


class TestProjectGenerator:
    def test_dry_run_returns_path(self, minimal_config, tmp_path, capsys):
        minimal_config.dry_run = True
        gen = ProjectGenerator(minimal_config, tmp_path)
        path = gen.generate()
        assert path == tmp_path / "test-project"
        # Nothing should be created on disk
        assert not (tmp_path / "test-project").exists()

    def test_generates_root_files(self, minimal_config, tmp_path):
        gen = ProjectGenerator(minimal_config, tmp_path)
        project_path = gen.generate()
        assert (project_path / "main.py").exists()
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / ".env").exists()
        assert (project_path / ".env.example").exists()
        assert (project_path / ".gitignore").exists()
        assert (project_path / "README.md").exists()

    def test_generates_app_structure(self, minimal_config, tmp_path):
        gen = ProjectGenerator(minimal_config, tmp_path)
        project_path = gen.generate()
        app = project_path / "app"
        assert app.is_dir()
        assert (app / "main.py").exists()
        assert (app / "core" / "config.py").exists()
        assert (app / "core" / "logging.py").exists()
        assert (app / "api" / "v1" / "health.py").exists()

    def test_no_auth_files_when_auth_none(self, minimal_config, tmp_path):
        gen = ProjectGenerator(minimal_config, tmp_path)
        project_path = gen.generate()
        assert not (project_path / "app" / "core" / "security.py").exists()
        assert not (project_path / "app" / "api" / "v1" / "auth.py").exists()

    def test_auth_files_generated(self, full_config, tmp_path):
        gen = ProjectGenerator(full_config, tmp_path)
        project_path = gen.generate()
        assert (project_path / "app" / "core" / "security.py").exists()
        assert (project_path / "app" / "api" / "v1" / "auth.py").exists()

    def test_tasks_generated_at_root(self, full_config, tmp_path):
        gen = ProjectGenerator(full_config, tmp_path)
        project_path = gen.generate()
        tasks = project_path / "tasks"
        assert tasks.is_dir()
        assert (tasks / "celery_app.py").exists()
        assert (tasks / "sample_tasks.py").exists()

    def test_no_tasks_without_broker(self, minimal_config, tmp_path):
        gen = ProjectGenerator(minimal_config, tmp_path)
        project_path = gen.generate()
        assert not (project_path / "tasks").exists()

    def test_docker_files_generated(self, full_config, tmp_path):
        gen = ProjectGenerator(full_config, tmp_path)
        project_path = gen.generate()
        assert (project_path / "Dockerfile").exists()
        assert (project_path / "docker-compose.yml").exists()

    def test_infra_structure(self, full_config, tmp_path):
        gen = ProjectGenerator(full_config, tmp_path)
        project_path = gen.generate()
        infra = project_path / "infra"
        assert infra.is_dir()
        assert (infra / "docker").is_dir()
        assert (infra / "helm" / "Chart.yaml").exists()
        assert (infra / "terraform" / "main.tf").exists()

    def test_force_overwrites_existing(self, minimal_config, tmp_path):
        minimal_config.force = True
        gen = ProjectGenerator(minimal_config, tmp_path)
        gen.generate()
        # Second call should succeed with --force
        gen2 = ProjectGenerator(minimal_config, tmp_path)
        path = gen2.generate()
        assert path.exists()
