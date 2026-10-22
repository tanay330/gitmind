FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    HF_HOME=/opt/models/hf \
    FASTEMBED_CACHE_PATH=/opt/models/fastembed

WORKDIR /app

# 1. Install dependencies first. This layer is cached until pyproject.toml or uv.lock changes.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# 2. Add the code and install the project itself.
COPY src ./src
RUN uv sync --frozen --no-dev

# 3. Download the ML models now, so the server doesn't download them at startup.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" \
 && python -c "from fastembed import SparseTextEmbedding; SparseTextEmbedding(model_name='Qdrant/bm25')"

# 4. Run as a normal user, not root.
RUN useradd --create-home --uid 1000 app \
 && mkdir -p /app/data \
 && chown -R app:app /app /opt/models
USER app

ENV DATABASE_URL=sqlite:////app/data/gitmind.db
EXPOSE 8000

CMD ["sh", "-c", "uvicorn gitmind.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]