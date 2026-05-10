"""
Structured action manifest for every addable feature in fastapi-spawn.

Each entry is a dict with:
  deps      - list of PyPI packages to install via `uv add`
  files     - list of (template_path, dest_path) tuples relative to project root
  env_vars  - list of env var hints to append to .env if missing
  run_cmds  - list of shell commands to run after file/dep installation
  note      - optional human-readable note shown after success
"""

from __future__ import annotations

FEATURE_ACTIONS: dict[str, dict] = {
    "auth": {
        "deps": ["python-jose[cryptography]", "passlib[bcrypt]", "python-multipart"],
        "files": [
            ("app/core/security.py.j2", "app/core/security.py"),
        ],
        "env_vars": ["SECRET_KEY=changeme", "ACCESS_TOKEN_EXPIRE_MINUTES=30", "ALGORITHM=HS256"],
        "run_cmds": [],
        "note": "Add your login/register endpoints in app/api/v1/auth.py",
    },
    "s3": {
        "deps": ["boto3>=1.34.0"],
        "files": [
            ("app/core/storage.py.j2", "app/core/storage.py"),
        ],
        "env_vars": ["AWS_ACCESS_KEY_ID=", "AWS_SECRET_ACCESS_KEY=", "AWS_REGION=us-east-1", "AWS_S3_BUCKET=", "AWS_S3_ENDPOINT_URL="],
        "run_cmds": [],
        "note": "For MinIO set AWS_S3_ENDPOINT_URL=http://localhost:9000",
    },
    "gcs": {
        "deps": ["google-cloud-storage>=2.16.0"],
        "files": [
            ("app/core/storage.py.j2", "app/core/storage.py"),
        ],
        "env_vars": ["GCS_PROJECT_ID=", "GCS_BUCKET=", "GOOGLE_APPLICATION_CREDENTIALS=./service-account.json"],
        "run_cmds": [],
        "note": "Place your GCP service account JSON at ./service-account.json",
    },
    "cloudinary": {
        "deps": ["cloudinary>=1.40.0"],
        "files": [
            ("app/core/storage.py.j2", "app/core/storage.py"),
        ],
        "env_vars": ["CLOUDINARY_CLOUD_NAME=", "CLOUDINARY_API_KEY=", "CLOUDINARY_API_SECRET="],
        "run_cmds": [],
        "note": None,
    },
    "openai": {
        "deps": ["openai>=1.30.0"],
        "files": [
            ("app/core/ai.py.j2", "app/core/ai.py"),
        ],
        "env_vars": ["OPENAI_API_KEY=", "OPENAI_MODEL=gpt-4o", "OPENAI_EMBEDDING_MODEL=text-embedding-3-small", "OPENAI_BASE_URL="],
        "run_cmds": [],
        "note": None,
    },
    "anthropic": {
        "deps": ["anthropic>=0.28.0"],
        "files": [
            ("app/core/ai.py.j2", "app/core/ai.py"),
        ],
        "env_vars": ["ANTHROPIC_API_KEY=", "ANTHROPIC_MODEL=claude-3-5-sonnet-20241022"],
        "run_cmds": [],
        "note": None,
    },
    "gemini": {
        "deps": ["google-generativeai>=0.7.0"],
        "files": [
            ("app/core/ai.py.j2", "app/core/ai.py"),
        ],
        "env_vars": ["GEMINI_API_KEY=", "GEMINI_MODEL=gemini-1.5-pro"],
        "run_cmds": [],
        "note": None,
    },
    "ollama": {
        "deps": [],
        "files": [
            ("app/core/ai.py.j2", "app/core/ai.py"),
        ],
        "env_vars": ["OLLAMA_HOST=localhost", "OLLAMA_PORT=11434", "OLLAMA_MODEL=llama3"],
        "run_cmds": [],
        "note": "Run Ollama locally: docker run -p 11434:11434 ollama/ollama",
    },
    "langchain": {
        "deps": ["langchain>=0.2.0", "langchain-openai>=0.1.0"],
        "files": [
            ("app/core/ai.py.j2", "app/core/ai.py"),
        ],
        "env_vars": ["OPENAI_API_KEY=", "OPENAI_MODEL=gpt-4o", "OPENAI_BASE_URL="],
        "run_cmds": [],
        "note": None,
    },
    "llamaindex": {
        "deps": ["llama-index>=0.10.0", "llama-index-llms-openai", "llama-index-embeddings-openai"],
        "files": [
            ("app/core/ai.py.j2", "app/core/ai.py"),
        ],
        "env_vars": ["OPENAI_API_KEY=", "OPENAI_MODEL=gpt-4o", "OPENAI_EMBEDDING_MODEL=text-embedding-3-small"],
        "run_cmds": [],
        "note": None,
    },
    "alembic": {
        "deps": ["alembic>=1.13.0"],
        "files": [],  # handled specially: alembic init then overwrite env.py
        "env_vars": [],
        "run_cmds": ["uv run alembic init migrations"],
        "note": "Run: uv run alembic revision --autogenerate -m 'init'  then  uv run alembic upgrade head",
        "_special": "alembic",   # trigger special post-processing
    },
    "celery": {
        "deps": ["celery[redis]>=5.3.6"],
        "files": [
            ("tasks/celery_app.py.j2", "tasks/celery_app.py"),
            ("tasks/sample_tasks.py.j2", "tasks/sample_tasks.py"),
        ],
        "env_vars": ["CELERY_BROKER_URL=redis://localhost:6379/0", "CELERY_RESULT_BACKEND=redis://localhost:6379/0"],
        "run_cmds": [],
        "note": "Start worker: uv run celery -A tasks.celery_app worker --loglevel=info",
    },
    "arq": {
        "deps": ["arq>=0.25.0", "redis[hiredis]>=5.0.0"],
        "files": [],
        "env_vars": ["REDIS_HOST=localhost", "REDIS_PORT=6379"],
        "run_cmds": [],
        "note": "Run worker: arq tasks.arq_worker.WorkerSettings",
    },
    "redis": {
        "deps": ["redis[hiredis]>=5.0.0"],
        "files": [
            ("app/core/cache.py.j2", "app/core/cache.py"),
        ],
        "env_vars": ["REDIS_HOST=localhost", "REDIS_PORT=6379", "REDIS_PASSWORD=", "REDIS_DB=0"],
        "run_cmds": [],
        "note": None,
    },
    "kafka": {
        "deps": ["aiokafka>=0.10.0"],
        "files": [],
        "env_vars": ["KAFKA_HOST=localhost", "KAFKA_PORT=9092"],
        "run_cmds": [],
        "note": None,
    },
    "sentry": {
        "deps": ["sentry-sdk[fastapi]>=2.0.0"],
        "files": [
            ("app/core/monitoring.py.j2", "app/core/monitoring.py"),
        ],
        "env_vars": ["SENTRY_DSN="],
        "run_cmds": [],
        "note": "Call init_sentry() in your app lifespan startup",
    },
    "prometheus": {
        "deps": ["prometheus-fastapi-instrumentator>=7.0.0"],
        "files": [
            ("app/core/monitoring.py.j2", "app/core/monitoring.py"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Metrics exposed at /metrics",
    },
    "opentelemetry": {
        "deps": ["opentelemetry-sdk", "opentelemetry-instrumentation-fastapi"],
        "files": [],
        "env_vars": ["OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317"],
        "run_cmds": [],
        "note": None,
    },
    "sendgrid": {
        "deps": ["sendgrid>=6.11.0"],
        "files": [
            ("app/core/email.py.j2", "app/core/email.py"),
        ],
        "env_vars": ["SENDGRID_API_KEY=", "SENDGRID_FROM_EMAIL="],
        "run_cmds": [],
        "note": None,
    },
    "smtp": {
        "deps": ["fastapi-mail>=1.4.1"],
        "files": [
            ("app/core/email.py.j2", "app/core/email.py"),
        ],
        "env_vars": ["SMTP_HOST=", "SMTP_PORT=587", "SMTP_USER=", "SMTP_PASSWORD=", "SMTP_FROM_EMAIL="],
        "run_cmds": [],
        "note": None,
    },
    "ses": {
        "deps": ["boto3>=1.34.0"],
        "files": [
            ("app/core/email.py.j2", "app/core/email.py"),
        ],
        "env_vars": ["AWS_ACCESS_KEY_ID=", "AWS_SECRET_ACCESS_KEY=", "AWS_REGION=us-east-1", "SES_FROM_EMAIL="],
        "run_cmds": [],
        "note": None,
    },
    "resend": {
        "deps": ["resend>=2.1.0"],
        "files": [
            ("app/core/email.py.j2", "app/core/email.py"),
        ],
        "env_vars": ["RESEND_API_KEY="],
        "run_cmds": [],
        "note": None,
    },
    "slack": {
        "deps": [],
        "files": [
            ("app/core/notifications.py.j2", "app/core/notifications.py"),
        ],
        "env_vars": ["SLACK_WEBHOOK_URL=https://hooks.slack.com/services/..."],
        "run_cmds": [],
        "note": None,
    },
    "discord": {
        "deps": [],
        "files": [
            ("app/core/notifications.py.j2", "app/core/notifications.py"),
        ],
        "env_vars": ["DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/..."],
        "run_cmds": [],
        "note": None,
    },
    "qdrant": {
        "deps": ["qdrant-client[fastembed]>=1.9.0"],
        "files": [
            ("app/core/vector_db.py.j2", "app/core/vector_db.py"),
        ],
        "env_vars": ["QDRANT_HOST=localhost", "QDRANT_PORT=6333", "QDRANT_API_KEY="],
        "run_cmds": [],
        "note": None,
    },
    "chroma": {
        "deps": ["chromadb>=0.5.0"],
        "files": [
            ("app/core/vector_db.py.j2", "app/core/vector_db.py"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Data stored locally in ./chroma_data",
    },
    "pinecone": {
        "deps": ["pinecone-client>=3.2.0"],
        "files": [
            ("app/core/vector_db.py.j2", "app/core/vector_db.py"),
        ],
        "env_vars": ["PINECONE_API_KEY=", "PINECONE_INDEX_NAME="],
        "run_cmds": [],
        "note": None,
    },
    "elasticsearch": {
        "deps": ["elasticsearch[async]>=8.13.0"],
        "files": [
            ("app/core/vector_db.py.j2", "app/core/vector_db.py"),
        ],
        "env_vars": ["ELASTICSEARCH_HOST=localhost", "ELASTICSEARCH_PORT=9200", "ELASTICSEARCH_API_KEY="],
        "run_cmds": [],
        "note": None,
    },
    "meilisearch": {
        "deps": ["meilisearch>=0.30.0"],
        "files": [
            ("app/core/search.py.j2", "app/core/search.py"),
        ],
        "env_vars": ["MEILISEARCH_HOST=http://localhost:7700", "MEILISEARCH_API_KEY="],
        "run_cmds": [],
        "note": None,
    },
    "opensearch": {
        "deps": ["opensearch-py[async]>=2.5.0"],
        "files": [
            ("app/core/search.py.j2", "app/core/search.py"),
        ],
        "env_vars": ["OPENSEARCH_HOST=localhost", "OPENSEARCH_PORT=9200", "OPENSEARCH_USER=admin", "OPENSEARCH_PASSWORD="],
        "run_cmds": [],
        "note": None,
    },
    "vespa": {
        "deps": ["pyvespa>=0.40.0"],
        "files": [
            ("app/core/search.py.j2", "app/core/search.py"),
        ],
        "env_vars": ["VESPA_ENDPOINT=http://localhost:8080"],
        "run_cmds": [],
        "note": None,
    },
    "websockets": {
        "deps": [],
        "files": [
            ("app/core/ws_manager.py.j2", "app/core/ws_manager.py"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "WebSocket endpoint available at /ws/connect",
    },
    "sse": {
        "deps": ["sse-starlette>=2.1.0"],
        "files": [],
        "env_vars": [],
        "run_cmds": [],
        "note": "Return EventSourceResponse(async_generator) from your endpoint",
    },
    "graphql": {
        "deps": ["strawberry-graphql[fastapi]>=0.227.0"],
        "files": [],
        "env_vars": [],
        "run_cmds": [],
        "note": "Mount GraphQL router in app/main.py with prefix='/graphql'",
    },
    "stripe": {
        "deps": ["stripe>=9.0.0"],
        "files": [],
        "env_vars": ["STRIPE_API_KEY=", "STRIPE_WEBHOOK_SECRET="],
        "run_cmds": [],
        "note": "Add webhook endpoint in app/api/v1/payments/router.py",
    },
    "sso": {
        "deps": ["fastapi-sso>=0.14.0"],
        "files": [],
        "env_vars": ["GOOGLE_CLIENT_ID=", "GOOGLE_CLIENT_SECRET=", "GITHUB_CLIENT_ID=", "GITHUB_CLIENT_SECRET="],
        "run_cmds": [],
        "note": "Add SSO routes in app/api/v1/auth/sso.py",
    },
    "seed": {
        "deps": ["faker>=25.0.0"],
        "files": [],
        "env_vars": [],
        "run_cmds": [],
        "note": "Create db/seed.py and run: uv run python db/seed.py",
    },
    "ocr": {
        "deps": ["pymupdf>=1.24.0", "pytesseract>=0.3.10"],
        "files": [
            ("app/core/ocr.py.j2", "app/core/ocr.py"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Requires system dep: tesseract-ocr (sudo apt install tesseract-ocr)",
    },
    "rbac": {
        "deps": [],
        "files": [
            ("app/core/permissions.py.j2", "app/core/permissions.py"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Include permissions router in app/main.py",
    },
    "caching": {
        "deps": ["fastapi-cache2[redis]>=0.2.1"],
        "files": [
            ("app/core/cache.py.j2", "app/core/cache.py"),
        ],
        "env_vars": ["REDIS_HOST=localhost", "REDIS_PORT=6379"],
        "run_cmds": [],
        "note": "Use @cache(expire=60) decorator on endpoints",
    },
    "admin": {
        "deps": ["sqladmin[full]>=0.16.1"],
        "files": [
            ("app/admin/setup.py.j2", "app/admin/setup.py"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Call setup_admin(app, engine) in your lifespan",
    },
    "pagination": {
        "deps": ["fastapi-pagination>=0.12.0"],
        "files": [],
        "env_vars": [],
        "run_cmds": [],
        "note": "Call add_pagination(app) in main.py and use Page[Model] as response type",
    },
    "response-format": {
        "deps": [],
        "files": [
            ("app/middleware/response_format.py.j2", "app/middleware/response_format.py"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Add app.add_middleware(ResponseFormattingMiddleware) in main.py",
    },
    "uploads": {
        "deps": ["python-multipart>=0.0.9"],
        "files": [
            ("app/api/v1/uploads/router.py.j2", "app/api/v1/uploads/router.py"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Include uploads router in app/api/v1/router.py",
    },
    "sso-google": {
        "deps": ["fastapi-sso>=0.14.0"],
        "files": [],
        "env_vars": ["GOOGLE_CLIENT_ID=", "GOOGLE_CLIENT_SECRET="],
        "run_cmds": [],
        "note": "Add Google SSO routes in app/api/v1/auth/sso.py",
    },
    "sso-github": {
        "deps": ["fastapi-sso>=0.14.0"],
        "files": [],
        "env_vars": ["GITHUB_CLIENT_ID=", "GITHUB_CLIENT_SECRET="],
        "run_cmds": [],
        "note": "Add GitHub SSO routes in app/api/v1/auth/sso.py",
    },
    "sso-microsoft": {
        "deps": ["fastapi-sso>=0.14.0"],
        "files": [],
        "env_vars": ["MICROSOFT_CLIENT_ID=", "MICROSOFT_CLIENT_SECRET=", "MICROSOFT_TENANT_ID="],
        "run_cmds": [],
        "note": "Add Microsoft SSO routes in app/api/v1/auth/sso.py",
    },
    "docker": {
        "deps": [],
        "files": [
            ("docker/Dockerfile.j2", "Dockerfile"),
            ("docker/docker-compose.yml.j2", "docker-compose.yml"),
            ("docker/dockerignore.j2", ".dockerignore"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Run: docker compose up --build -d",
    },
    "ci": {
        "deps": [],
        "files": [
            ("ci/github/tests.yml.j2", ".github/workflows/tests.yml"),
            ("ci/github/publish.yml.j2", ".github/workflows/publish.yml"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Add PYPI_API_TOKEN to your GitHub repo secrets",
    },
    "helm": {
        "deps": [],
        "files": [
            ("infra/helm/Chart.yaml.j2", "infra/helm/Chart.yaml"),
            ("infra/helm/values.yaml.j2", "infra/helm/values.yaml"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Run: helm install my-release ./infra/helm",
    },
    "terraform": {
        "deps": [],
        "files": [
            ("infra/terraform/main.tf.j2", "infra/terraform/main.tf"),
            ("infra/terraform/variables.tf.j2", "infra/terraform/variables.tf"),
        ],
        "env_vars": [],
        "run_cmds": [],
        "note": "Run: terraform -chdir=infra/terraform init && terraform apply",
    },
}
