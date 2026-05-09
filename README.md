<div align="center">

# ⚡ fastapi-spawn

**The most complete FastAPI project scaffolding CLI — built for modern Python development.**

[![PyPI version](https://img.shields.io/pypi/v/fastapi-spawn.svg?color=cyan&style=flat-square)](https://pypi.org/project/fastapi-spawn/)
[![Python](https://img.shields.io/pypi/pyversions/fastapi-spawn.svg?style=flat-square)](https://pypi.org/project/fastapi-spawn/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/Bishwajitgarai/fastapi-spawn/tests.yml?label=tests&style=flat-square)](https://github.com/Bishwajitgarai/fastapi-spawn/actions)

Generate production-ready FastAPI projects in seconds — with exactly the stack you need.

</div>

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
# Interactive TUI — guided step-by-step
fastapi-spawn new my-api

# Full stack one-liner
fastapi-spawn new my-api \
  --db postgresql \
  --orm sqlalchemy \
  --migration alembic \
  --auth jwt \
  --broker redis \
  --storage s3 \
  --ai openai \
  --monitoring sentry \
  --email sendgrid \
  --notify slack \
  --log-lib loguru \
  --log-dest local \
  --vector-db qdrant \
  --api-extra both \
  --stack full \
  --ci github

# Preview file tree without writing
fastapi-spawn new my-api --dry-run

# Add a feature to an existing project
fastapi-spawn add openai
fastapi-spawn add alembic
fastapi-spawn add sentry
```

---

## Generated Project Structure

```
my-api/
├── app/
│   ├── api/
│   │   ├── graphql.py           # Strawberry GraphQL schema + IDE (if graphql)
│   │   └── v1/
│   │       ├── router.py        # Central API router aggregating sub-routers
│   │       ├── health/
│   │       │   └── router.py    # GET /health  /readiness  /liveness
│   │       ├── auth/
│   │       │   └── router.py    # POST /auth/login  /auth/refresh (if auth)
│   │       └── ws/
│   │           └── router.py    # WebSocket /ws/connect (if websockets)
│   ├── core/
│   │   ├── config.py            # Pydantic Settings v2 — individual env fields + @property URLs
│   │   ├── logger.py            # Context-var logger — request ID, client IP, file rotation
│   │   ├── exceptions.py        # Custom exception hierarchy + handlers
│   │   ├── security.py          # JWT / bcrypt
│   │   ├── ws_manager.py        # WebSocket connection manager — broadcast, rooms
│   │   ├── storage.py           # AWS S3/MinIO | GCS | Cloudinary
│   │   ├── ai.py                # OpenAI | Anthropic | Gemini | Ollama | LangChain | LlamaIndex
│   │   ├── monitoring.py        # Sentry | Prometheus | OpenTelemetry
│   │   ├── email.py             # SendGrid | SMTP | AWS SES
│   │   ├── notifications.py     # Slack | Discord webhooks
│   │   └── vector_db.py         # Qdrant | ChromaDB | Pinecone | Supabase | Elasticsearch
│   ├── middleware/
│   │   ├── request_logger.py    # X-Request-ID, response time, structured logs
│   │   └── rate_limit.py        # slowapi — 200/min default, 429 + Retry-After
│   ├── db/
│   │   └── session.py           # Async SQLAlchemy / SQLModel / Tortoise / Beanie
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── repositories/
├── tasks/
│   ├── celery_app.py            # Celery (Redis / RabbitMQ)
│   ├── sample_tasks.py
│   └── arq_worker.py            # Arq async task queue (if arq)
├── migrations/                  # Alembic async
│   ├── env.py
│   └── versions/
├── infra/
│   ├── docker/
│   ├── helm/
│   └── terraform/
├── tests/
├── logs/                        # Local rotating logs
├── main.py                      # uv run main.py
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env                         # gitignored
├── .env.example                 # full reference of every supported variable
├── .gitignore
├── .pre-commit-config.yaml
└── pyproject.toml               # [tool.uv.scripts] pre-wired
```

---

## All Options

```
fastapi-spawn new [OPTIONS] PROJECT_NAME

Database & ORM
  --db           postgresql | mysql | mongodb | sqlite | supabase | duckdb | none
  --orm          sqlalchemy | sqlmodel | tortoise | beanie | none
  --migration    alembic | aerich | none

Auth & Security
  --auth         jwt | oauth2 | api-key | auth0 | none

Messaging & Cache
  --broker       redis | rabbitmq | kafka | arq | none
  --cache        redis | memcached | none

Storage
  --storage      s3 | gcs | cloudinary | local | none

AI / LLM
  --ai           openai | anthropic | gemini | ollama | langchain | llamaindex | none

API Extras
  --api-extra    websockets | graphql | both | none

Monitoring
  --monitoring   sentry | prometheus | opentelemetry | both | none

Email
  --email        sendgrid | smtp | ses | none

Notifications
  --notify       slack | discord | none

Logging
  --log-lib      loguru | structlog | standard
  --log-dest     local | cloudwatch | datadog | none

Vector Database
  --vector-db    qdrant | chroma | pinecone | supabase | elasticsearch | none

Deployment
  --stack        minimal | standard | full
  --ci           github | gitlab | both | none

Flags
  --no-docker    Skip Docker files
  --no-tests     Skip test suite
  --dry-run      Preview file tree without writing
  --force / -f   Overwrite existing directory
  --output / -o  Output directory (default: .)
```

---

## uv run Scripts

Every generated project has `[tool.uv.scripts]` pre-wired:

```bash
uv run dev        # uvicorn --reload
uv run start      # python main.py
uv run test       # pytest --cov
uv run lint       # ruff check
uv run format     # ruff format
uv run typecheck  # mypy
uv run migrate    # alembic upgrade head    (if alembic)
uv run rollback   # alembic downgrade -1    (if alembic)
uv run makemig    # alembic revision --autogenerate (if alembic)
uv run worker     # celery worker           (if celery)
uv run beat       # celery beat             (if celery)
```

---

## Environment Variables

**Individual fields per service — no URL strings.** All connection URLs are assembled via `@property` in `app/core/config.py`. Your `.env.example` includes every supported variable:

```env
# ── Application ──────────────────────────────────────────────────────────────
APP_NAME=my-api
ENVIRONMENT=dev                      # dev | staging | production
SECRET_KEY=CHANGE_ME                 # openssl rand -hex 32
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_BACKUP_DAYS=30

# ── PostgreSQL ─────────────────────────────────────────────────────────────
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=my_api_db
# → assembled as: postgresql+asyncpg://USER:PASS@HOST:PORT/DB

# ── MySQL ─────────────────────────────────────────────────────────────────
MYSQL_USER=root
MYSQL_PASSWORD=CHANGE_ME
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=my_api_db
# → assembled as: mysql+aiomysql://USER:PASS@HOST:PORT/DB

# ── MongoDB ───────────────────────────────────────────────────────────────
MONGODB_USER=mongo
MONGODB_PASSWORD=CHANGE_ME
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=my_api_db
# → assembled as: mongodb://USER:PASS@HOST:PORT

# ── Supabase ──────────────────────────────────────────────────────────────
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=CHANGE_ME               # anon or service role key

# ── DuckDB ────────────────────────────────────────────────────────────────
DUCKDB_FILE=my_api.duckdb

# ── Redis ─────────────────────────────────────────────────────────────────
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
# → assembled as: redis://:PASS@HOST:PORT/DB

# ── RabbitMQ ─────────────────────────────────────────────────────────────
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=CHANGE_ME
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_VHOST=/
# → assembled as: amqp://USER:PASS@HOST:PORT/VHOST

# ── Kafka ────────────────────────────────────────────────────────────────
KAFKA_HOST=localhost
KAFKA_PORT=9092
# → assembled as: HOST:PORT

# ── Auth / JWT ───────────────────────────────────────────────────────────
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# ── Auth0 ────────────────────────────────────────────────────────────────
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=CHANGE_ME
AUTH0_CLIENT_SECRET=CHANGE_ME
AUTH0_AUDIENCE=https://your-api.example.com

# ── AWS (S3 / SES / CloudWatch) ──────────────────────────────────────────
AWS_ACCESS_KEY_ID=CHANGE_ME
AWS_SECRET_ACCESS_KEY=CHANGE_ME
AWS_REGION=us-east-1
AWS_S3_BUCKET=my-api-bucket
AWS_S3_ENDPOINT_URL=               # http://localhost:9000 for MinIO

# ── Google Cloud Storage ─────────────────────────────────────────────────
GCS_PROJECT_ID=CHANGE_ME
GCS_BUCKET=my-api-bucket
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

# ── Cloudinary ───────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME=CHANGE_ME
CLOUDINARY_API_KEY=CHANGE_ME
CLOUDINARY_API_SECRET=CHANGE_ME

# ── OpenAI ───────────────────────────────────────────────────────────────
OPENAI_API_KEY=sk-placeholder
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_BASE_URL=                   # blank = api.openai.com
                                   # Azure: https://<resource>.openai.azure.com/
                                   # LM Studio: http://localhost:1234/v1

# ── Anthropic ────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-placeholder
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# ── Google Gemini ────────────────────────────────────────────────────────
GEMINI_API_KEY=CHANGE_ME
GEMINI_MODEL=gemini-1.5-pro

# ── Ollama (local LLM — no API key) ─────────────────────────────────────
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3
# → assembled as: http://HOST:PORT

# ── Sentry ───────────────────────────────────────────────────────────────
SENTRY_DSN=https://xxx@sentry.io/yyy

# ── Datadog ──────────────────────────────────────────────────────────────
DD_API_KEY=CHANGE_ME
DD_SITE=datadoghq.com

# ── SendGrid ─────────────────────────────────────────────────────────────
SENDGRID_API_KEY=SG.placeholder
SENDGRID_FROM_EMAIL=noreply@example.com

# ── SMTP ─────────────────────────────────────────────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=CHANGE_ME
SMTP_PASSWORD=CHANGE_ME
SMTP_FROM_EMAIL=noreply@example.com
SMTP_STARTTLS=true
SMTP_SSL=false

# ── AWS SES ──────────────────────────────────────────────────────────────
SES_FROM_EMAIL=noreply@example.com  # uses AWS_* credentials above

# ── Slack ────────────────────────────────────────────────────────────────
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/CHANGE_ME

# ── Discord ──────────────────────────────────────────────────────────────
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/CHANGE_ME

# ── Qdrant ───────────────────────────────────────────────────────────────
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=                    # blank for local Docker Qdrant
# → assembled as: http://HOST:PORT

# ── Pinecone ─────────────────────────────────────────────────────────────
PINECONE_API_KEY=CHANGE_ME
PINECONE_INDEX_NAME=my-api-index

# ── Elasticsearch ────────────────────────────────────────────────────────
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_API_KEY=
# → assembled as: http://HOST:PORT
```

> All variables are assembled into connection URLs inside `app/core/config.py` via `@property`. Your code always reads from structured fields — never a fragile connection string.

---

## Middleware (always included)

| Middleware | Behaviour |
|---|---|
| `RequestLoggingMiddleware` | Assigns `X-Request-ID`, logs `→ METHOD /path` + `✓ status Xms` with client IP |
| `RateLimitMiddleware` | 200 req/min default via `slowapi`, returns `429` + `Retry-After: 60` |
| `CORSMiddleware` | Configurable origins via `CORS_ORIGINS` env var |

Every response carries `X-Request-ID` and `X-Response-Time` headers automatically.

---

## WebSockets

```python
# Connect: ws://host/api/v1/ws/connect
# Room:    ws://host/api/v1/ws/connect/{room_id}

# Client protocol
{"type": "broadcast", "data": "hello everyone"}
{"type": "ping"}   # → {"type": "pong"}
```

---

## GraphQL

Strawberry schema with **Query + Mutation + Subscription** is mounted at `/graphql`.  
GraphiQL IDE is enabled in `dev` mode. Subscriptions use `graphql-transport-ws`.

---

## Add Features to Existing Projects

```bash
fastapi-spawn add sentry       # Sentry error tracking
fastapi-spawn add openai       # OpenAI async client
fastapi-spawn add alembic      # Alembic async migrations
fastapi-spawn add s3           # AWS S3 / MinIO storage
fastapi-spawn add celery       # Celery worker + tasks/
fastapi-spawn add websockets   # WebSocket connection manager
fastapi-spawn add graphql      # Strawberry GraphQL schema
fastapi-spawn add qdrant       # Qdrant vector DB
fastapi-spawn add chroma       # ChromaDB local vector DB
fastapi-spawn add helm         # Helm chart in infra/helm/
fastapi-spawn add terraform    # Terraform in infra/terraform/
```

---

## ORM ↔ Database Compatibility

| ORM | Compatible Databases |
|---|---|
| `sqlalchemy` | postgresql, mysql, sqlite, supabase |
| `sqlmodel` | postgresql, mysql, sqlite, supabase |
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

---

## License

MIT © [Bishwajit Garai](https://github.com/Bishwajitgarai)
