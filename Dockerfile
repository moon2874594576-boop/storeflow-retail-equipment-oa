FROM node:24-bookworm-slim AS frontend
WORKDIR /ui
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM postgres:16-bookworm AS pgtools

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    STOREFLOW_DATA_DIR=/app/runtime STOREFLOW_DEMO=0 \
    STOREFLOW_ALLOWED_HOSTS=localhost,127.0.0.1,app
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 liblz4-1 libzstd1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 storeflow
COPY --from=pgtools /usr/lib/postgresql/16/bin/pg_dump /usr/local/bin/pg_dump
COPY --from=pgtools /usr/lib/postgresql/16/bin/pg_restore /usr/local/bin/pg_restore
COPY --from=pgtools /usr/lib/postgresql/16/bin/createdb /usr/local/bin/createdb
COPY backend/requirements.txt /app/backend/requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=storeflow:storeflow . /app/
COPY --from=frontend --chown=storeflow:storeflow /ui/dist /app/frontend/dist
RUN mkdir -p /app/runtime && chown storeflow:storeflow /app/runtime
USER storeflow
EXPOSE 8765
HEALTHCHECK --interval=10s --timeout=5s --start-period=60s --retries=6 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/health/', timeout=4)" || exit 1
ENTRYPOINT ["python", "main.py"]
CMD ["--host", "0.0.0.0", "--no-browser"]
