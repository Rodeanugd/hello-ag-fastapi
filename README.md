# hello-archgen-fastapi

Minimal FastAPI + Postgres app used to demonstrate ArchGen's deployment
tools. Not intended for production use.

## Endpoints

- `GET /healthcheck` → `{"ok": true}`
- `POST /guestbook` with body `{"text": "..."}` → `{"id": N, "text": "..."}`
- `GET /guestbook` → `[{"id": N, "text": "...", "created_at": "..."}]`

## Environment

- `DATABASE_URL` — Postgres connection string. DO App Platform injects this
  automatically when bound to a managed Postgres component. Both
  `postgres://`, `postgresql://`, and `postgresql+asyncpg://` URL forms are
  tolerated; the app rewrites to the async driver at startup.
- `SENTRY_DSN` — optional; tolerated whether real or bogus. Read but never
  validated.

## Local run

```bash
docker build -t hello-archgen-fastapi .
docker run \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e SENTRY_DSN=https://dummy@sentry.io/0 \
  -p 8000:8000 hello-archgen-fastapi
```

## Deploy

This repo is consumed by ArchGen's deployment tooling. The app spec lives
in the consuming side; this repo only ships the application code.
