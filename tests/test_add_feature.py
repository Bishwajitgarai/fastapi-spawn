"""Tests for the automatic feature addition."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from typer.testing import CliRunner
from fastapi_spawn.cli import app

runner = CliRunner()


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Setup a mock project directory."""
    pd = tmp_path / "my-api"
    pd.mkdir()
    (pd / ".env").write_text("APP_NAME=my-api\n")
    # Pre-write an empty config
    (pd / ".fastapi-spawn.json").write_text(
        json.dumps({
            "project_name": "my-api",
            "db": "postgresql",
            "orm": "sqlalchemy",
            "installed_features": []
        })
    )
    return pd


@patch("subprocess.run")
def test_add_feature_deps_and_files(mock_run, project_dir: Path):
    """Test that adding a standard feature updates env and tracking json."""
    # Run the add command for a known feature, e.g., 'sso-github'
    result = runner.invoke(app, ["add", "sso-github", "--dir", str(project_dir)])
    
    assert result.exit_code == 0
    assert "✓ Sso-github added successfully!" in result.output
    
    # 1. Dependency check
    mock_run.assert_called_with(["uv", "add", "fastapi-sso>=0.14.0"], cwd=project_dir, check=True)
    
    # 2. Tracking file check
    status = json.loads((project_dir / ".fastapi-spawn.json").read_text())
    assert "sso-github" in status["installed_features"]
    
    # 3. Env file check
    env_content = (project_dir / ".env").read_text()
    assert "GITHUB_CLIENT_ID=" in env_content
    assert "GITHUB_CLIENT_SECRET=" in env_content


@patch("subprocess.run")
def test_add_feature_alembic_special(mock_run, project_dir: Path):
    """Test that alembic triggers its special run commands and jinja templating."""
    # Create the migrations folder so the template generator can run
    (project_dir / "migrations").mkdir()
    
    result = runner.invoke(app, ["add", "alembic", "--dir", str(project_dir)])
    
    assert result.exit_code == 0
    assert "✓ Alembic added successfully!" in result.output
    
    # Should run 'alembic init migrations'
    mock_run.assert_called_with(["uv", "run", "alembic", "init", "migrations"], cwd=project_dir, check=True)
    
    # Check that tracking file got updated
    status = json.loads((project_dir / ".fastapi-spawn.json").read_text())
    assert "alembic" in status["installed_features"]
    
    # Check that env.py was rendered over
    assert (project_dir / "migrations" / "env.py").exists()


def test_add_unknown_feature(project_dir: Path):
    result = runner.invoke(app, ["add", "something-fake", "--dir", str(project_dir)])
    assert result.exit_code == 1
    assert "Unknown feature" in result.output


def test_add_already_installed_feature(project_dir: Path):
    # Pre-install auth
    status = {"installed_features": ["auth"]}
    (project_dir / ".fastapi-spawn.json").write_text(json.dumps(status))
    
    result = runner.invoke(app, ["add", "auth", "--dir", str(project_dir)])
    assert result.exit_code == 0
    assert "already installed" in result.output
