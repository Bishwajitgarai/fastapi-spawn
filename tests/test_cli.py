"""Tests for the CLI layer."""

from __future__ import annotations

from typer.testing import CliRunner

from fastapi_spawn.cli import app

runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "fastapi-spawn" in result.output


def test_list_templates():
    result = runner.invoke(app, ["list-templates"])
    assert result.exit_code == 0
    assert "postgresql" in result.output
    assert "sqlalchemy" in result.output


def test_new_dry_run(tmp_path):
    result = runner.invoke(
        app,
        [
            "new", "my-api",
            "--db", "sqlite",
            "--orm", "sqlalchemy",
            "--auth", "none",
            "--broker", "none",
            "--cache", "none",
            "--stack", "minimal",
            "--ci", "none",
            "--log-lib", "loguru",
            "--no-docker",
            "--dry-run",
            "--output", str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "my-api" in result.output
    assert not (tmp_path / "my-api").exists()


def test_new_invalid_name():
    result = runner.invoke(
        app,
        ["new", "1invalid",
         "--db", "sqlite", "--orm", "none",
         "--auth", "none", "--broker", "none",
         "--cache", "none", "--stack", "minimal",
         "--ci", "none", "--log-lib", "standard"],
    )
    assert result.exit_code != 0


def test_new_orm_db_incompatible():
    result = runner.invoke(
        app,
        ["new", "my-api",
         "--db", "mongodb", "--orm", "sqlalchemy",
         "--auth", "none", "--broker", "none",
         "--cache", "none", "--stack", "minimal",
         "--ci", "none", "--log-lib", "standard"],
    )
    assert result.exit_code != 0
    assert "not compatible" in result.output
