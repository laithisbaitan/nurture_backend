# Nurture Backend — Project Status & Roadmap

Living document. Updated at the end of every stage. The agent reads this first in
every session to stay oriented.

## Goal

v1 backend for Nurture, a personal-first health/food-tracking app:

- JWT auth (register / login / refresh / me)
- Shared global food database (manual entry + two-step photo flow, AI-ready)
- Per-user food logging and weight logging
- Per-user daily/weekly progress aggregation
- Django admin over all models, basic `APITestCase` coverage per app

Frontend is a separate Flutter app (not in this repo). No frontend work here.

## Stack

Django 6.1, DRF 3.18, SimpleJWT, PostgreSQL, python-dotenv, django-cors-headers,
Pillow. Media stored on filesystem (`media/`), served by nginx in production.

## Stage Roadmap

| Stage | Scope | Status |
|---|---|---|
| 0 | Repo, venv, project + 4 apps, .env settings, Postgres, DRF/JWT/CORS/media config | **Done & verified** |
| 1 | `accounts`: Profile model, register/login/refresh/me endpoints, admin | Not started |
| 2 | `foods`: FoodItem model, CRUD + search endpoints (manual entry only) | Not started |
| 3 | `foods`: two-step photo flow (upload photo → PATCH nutrition later) | Not started |
| 4 | `logs`: FoodLog + WeightLog models and user-scoped endpoints | Not started |
| 5 | `progress`: daily/weekly aggregation + weight-trend endpoints | Not started |

**Rule: never build ahead of the current stage. Stop after each stage and wait for
user confirmation before starting the next.**

## Current focus

Awaiting user confirmation to start Stage 1 (`accounts`: Profile model,
register/login/refresh/me endpoints, admin registration, tests).

## Environments

- **Local dev**: this machine. `.env` points at `localhost` Postgres 16
  (db/user `nurture`). Note: local `pg_hba.conf` needed a `local all postgres peer`
  rule prepended for admin access via `sudo -u postgres psql`.
- **Production VPS**: 72.61.91.102, Ubuntu, Postgres 17 (`postgresql@17-main`),
  nginx. DB + user already created by the user. Deployment guide: `docs/DEPLOYMENT.md`.

## Decision log

- 2026-08-17: Built-in Django `User` (no custom user model). Email-based login via
  SimpleJWT customization in Stage 1.
- 2026-08-17: python-dotenv with discrete `DB_*` vars (not django-environ/DATABASE_URL).
- 2026-08-17: No email verification / password reset in v1 (accepted risk, per spec).
- 2026-08-17: `FoodItem.source` enum and `micros_json` JSONField exist from Stage 2
  so later stages need no schema migrations.
- 2026-08-17: gunicorn is the one deployment-only extra package (WSGI server for
  systemd/nginx). Not needed for local dev.
