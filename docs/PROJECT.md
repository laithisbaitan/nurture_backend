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
| 1 | `accounts`: Profile model, register/login/refresh/me endpoints, admin | **Done & verified** (10 tests pass) |
| 2 | `foods`: FoodItem model, CRUD + search endpoints (manual entry only) | **Done** (21 tests pass, awaiting user confirmation) |
| 3 | `foods`: two-step photo flow (upload photo → PATCH nutrition later) | **Done** (27 tests pass, awaiting user confirmation) |
| 4 | `logs`: FoodLog + WeightLog models and user-scoped endpoints | **Done** (38 tests pass, awaiting user confirmation) |
| 5 | `progress`: daily/weekly aggregation + weight-trend endpoints | **Done** (44 tests pass, awaiting user confirmation) |

**Rule: never build ahead of the current stage. Stop after each stage and wait for
user confirmation before starting the next.**

## Git workflow

Commit day-to-day work on the `develop` branch. When a release is ready for the
VPS, merge `develop` into `main`; production only ever pulls `main`.

## Current focus

All planned stages (0-5) are implemented and tested. Awaiting user review
and deployment steps (push `develop`, then merge to `main` when ready).

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
- 2026-08-17: `User.username` is set to the email at registration; login serializer
  accepts `email` and maps it to `username` internally. Emails stored lowercase.
- 2026-08-17: JWT lifetimes: access 1h, refresh 30d (mobile-friendly; SimpleJWT
  defaults of 5min/1d would force constant refreshes).
- 2026-08-17: `name` maps to `User.first_name`; returned/editable via `/api/auth/me/`.
- 2026-08-17: Foods list paginated (20/page, viewset-level so other endpoints stay
  unpaginated). Search capped at 25 lightweight results, empty query returns [].
- 2026-08-17: `photo` is read-only in the main serializer; it only enters via
  `POST /api/foods/photo/`. `created_by` always comes from `request.user`.
  No DELETE on foods.
- 2026-08-17: Photo flow keeps nutrition columns NOT NULL (per Stage 2 spec):
  step 1 creates a placeholder row (empty names, zero macros,
  source=photo_pending_ai); step 2 PATCHes real values and sets source=manual.
  `source` is writable on PATCH only; regular POST forces manual in the view.
- 2026-08-17: FoodLog.food_item uses on_delete=PROTECT so deleting a food can't
  silently wipe users' diary history. Log lists are unpaginated (per-day, small).
  Date filtering uses logged_at__date in UTC (no per-user timezones in v1).
  FoodLog responses include flat read-only food_* fields (names, calories,
  serving) so the app needs no second request to render a day's log.
- 2026-08-18: Progress endpoints are read-only and user-scoped:
  `/api/progress/daily/`, `/api/progress/weekly/`, `/api/progress/weight-trend/`.
  Daily/weekly totals multiply food nutrients by log quantity and merge
  numeric `micros_json` keys across foods; weekly returns a fixed 7-day array.
