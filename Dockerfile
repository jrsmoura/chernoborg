# Full-stack image: Next.js frontend (port 3000) + ADK backend (internal 8000).
# The FAISS index must be built before building this image (make build).
# GOOGLE_API_KEY is injected at runtime — never baked into the image.
#
# Build:  docker compose build
# Run:    docker compose up

# ── Stage 1: Build Next.js standalone bundle ─────────────────────────────────
FROM node:22-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --quiet
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Runtime image ───────────────────────────────────────────────────
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    INDEX_DIR=/app/index \
    HOSTNAME=0.0.0.0 \
    PORT=3000

# Node.js 22 (runtime for Next.js) + supervisor (process manager)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg2 ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get purge -y --auto-remove curl gnupg2 && \
    pip install --no-cache-dir supervisor && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (google-adk, google-genai, faiss-cpu, pydantic, numpy)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ADK agent source + pre-built FAISS index
COPY ingest/           ingest/
COPY assistente_iesb/  assistente_iesb/
COPY index/            index/

# Next.js standalone server + static assets + public files (images, favicon…)
COPY --from=frontend-builder /frontend/.next/standalone/   ./frontend/
COPY --from=frontend-builder /frontend/.next/static/       ./frontend/.next/static/
COPY --from=frontend-builder /frontend/public/             ./frontend/public/

# Process manager config
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Non-root user — also grant write to ADK's browser config dir so it can
# write runtime-config.json on startup without a permission error.
RUN useradd --no-create-home --shell /bin/false app && \
    chown -R app /app && \
    chown -R app /usr/local/lib/python3.13/site-packages/google/adk/cli/browser/
USER app

EXPOSE 3000

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
