<div align="center">

# ⚡ fastapi-spawn

**The most complete FastAPI project scaffolding CLI — built for modern Python development.**

[![PyPI version](https://img.shields.io/pypi/v/fastapi-spawn.svg?color=cyan&style=flat-square)](https://pypi.org/project/fastapi-spawn/)
[![Python](https://img.shields.io/pypi/pyversions/fastapi-spawn.svg?style=flat-square)](https://pypi.org/project/fastapi-spawn/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/Bishwajitgarai/fastapi-spawn/tests.yml?label=tests&style=flat-square)](https://github.com/Bishwajitgarai/fastapi-spawn/actions)

</div>

---

## Why fastapi-spawn?

`fastapi-spawn` generates **production-ready** FastAPI projects in seconds. No boilerplate, no guesswork — just run one command and get a fully structured, configured project with the exact stack you need.

| Feature | scaffold-fastapi | **fastapi-spawn** |
|---|---|---|
| Interactive TUI | Basic prompts | ✅ Rich questionary TUI |
| Databases | PostgreSQL, MongoDB, SQLite | ✅ + MySQL |
| ORM | None | ✅ SQLAlchemy 2.x, Tortoise, Beanie |
| Migrations | ❌ | ✅ Alembic (async), Aerich |
| Auth | ❌ | ✅ JWT, OAuth2, API Key |
| Message brokers | Redis, RabbitMQ | ✅ + Kafka |
| File storage | ❌ | ✅ AWS S3 (boto3) |
| AI integration | ❌ | ✅ OpenAI, Anthropic |
| Config style | Single URL | ✅ Individual fields + `@property` URL |
| Entry point | app/main.py | ✅ Root `main.py` (`uv run main.py`) |
| CI/CD | GitHub Actions | ✅ GitHub Actions + GitLab CI |
| Observability | ❌ | ✅ /health /readiness /liveness |
| Logging | None | ✅ loguru / structlog / standard |
| Package manager | uv | ✅ uv (with `[tool.uv]` config) |
| Dry-run mode | ❌ | ✅ Preview tree before generating |

---

## Installation

```bash
pip install fastapi-spawn
# or
uv pip install fastapi-spawn
```

---

## Quick Start

```bash
# Fully interactive — guided TUI
fastapi-spawn new my-api

# One-liner (all flags)
fastapi-spawn new my-api \
  --db postgresql \
  --orm sqlalchemy \
  --migration alembic \
  --auth jwt \
  --broker redis \
  --storage s3 \
  --ai openai \
  --stack full \
  --ci github \
  --log-lib loguru

# Preview without writing files
fastapi-spawn new my-api --dry-run
```

---

## Generated Project Structure

```
my-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── health.py        # /health  /readiness  /liveness
│   │       └── auth.py          # JWT login + refresh
│   ├── core/
│   │   ├── config.py            # Pydantic Settings v2 (individual env fields)
│   │   ├── logging.py           # loguru / structlog / standard
│   │   ├── exceptions.py        # Custom exception hierarchy
│   │   ├── security.py          # JWT + bcrypt (when auth enabled)
│   │   ├── storage.py           # AWS S3 utils (when s3 chosen)
│   │   └── ai.py                # OpenAI / Anthropic client (when AI chosen)
│   ├── db/
│   │   └── session.py           # Async SQLAlchemy / Tortoise / Beanie
│   ├── models/                  # ORM models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic layer
│   └── repositories/            # Data access layer
├── tasks/                       # Celery workers (root-level)
│   ├── celery_app.py
│   └── sample_tasks.py
├── migrations/                  # Alembic migrations
│   ├── env.py                   # Async-compatible env
│   └── versions/
├── infra/
│   ├── docker/
│   ├── helm/
│   └── terraform/
├── tests/
│   ├── conftest.py
│   └── test_health.py
├── main.py                      # uv run main.py entry point
├── alembic.ini
├── Dockerfile                   # Uses uv for fast builds
├── docker-compose.yml           # All services pre-configured
├── .env                         # gitignored
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
└── pyproject.toml               # uv-compatible
```

---

## Environment Variables

`fastapi-spawn` generates **individual env fields** (not URL strings) for every service, assembled into URLs via `@property`:

```env
# PostgreSQL — assembled into DATABASE_URL by settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=my_api_db

# OpenAI — supports custom base URL for Azure / LM Studio
OPENAI_API_KEY=sk-placeholder
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=                # blank = api.openai.com

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

---

## All Options

```
fastapi-spawn new [OPTIONS] PROJECT_NAME

  --db           postgresql | mysql | mongodb | sqlite | none
  --orm          sqlalchemy | tortoise | beanie | none
  --migration    alembic | aerich | none
  --auth         jwt | oauth2 | api-key | none
  --broker       redis | rabbitmq | kafka | none
  --cache        redis | memcached | none
  --storage      s3 | local | none
  --ai           openai | anthropic | none
  --stack        minimal | standard | full
  --ci           github | gitlab | both | none
  --log-lib      loguru | structlog | standard
  --no-docker    Skip Docker files
  --no-tests     Skip test suite
  --dry-run      Preview file tree only
  --force / -f   Overwrite existing directory
  --output / -o  Output directory (default: .)
```

### Subcommands

```bash
fastapi-spawn list-templates   # Show all options + ORM/DB compatibility
fastapi-spawn validate FILE    # Validate a .fastapi-spawn.toml
```

---

## After Scaffolding

```bash
cd my-api
uv sync                        # Install all dependencies
uv run alembic upgrade head    # Run DB migrations (if alembic)
docker compose up --build      # Start all services
# or
uv run main.py                 # Run locally
```

---

## ORM ↔ Database Compatibility

| ORM | Compatible Databases |
|---|---|
| `sqlalchemy` | postgresql, mysql, sqlite |
| `tortoise` | postgresql, mysql, sqlite |
| `beanie` | mongodb |
| `none` | any |

---

## Contributing

```bash
git clone https://github.com/Bishwajitgarai/fastapi-spawn
cd fastapi-spawn
uv sync --all-extras
uv run pytest
```

PRs are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT © [Bishwajit Garai](https://github.com/Bishwajitgarai)
