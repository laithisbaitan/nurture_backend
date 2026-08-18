# nurture_backend

Django + DRF backend for **Nurture**, a personal-first health/food-tracking app.

**Stack:** Django, Django REST Framework, PostgreSQL, SimpleJWT.

## Setup

1. Clone the repo and enter it:

   ```bash
   git clone <repo-url> nurture_backend
   cd nurture_backend
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create the PostgreSQL database and user (once):

   ```bash
   sudo -u postgres psql -c "CREATE USER nurture WITH PASSWORD 'your-db-password';"
   sudo -u postgres psql -c "CREATE DATABASE nurture OWNER nurture;"
   ```

4. Create a `.env` file in the project root (see `.env.example`):

   ```bash
   cp .env.example .env
   # then edit .env: set SECRET_KEY, DB_PASSWORD, etc.
   ```

   Generate a secret key with:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. Run migrations and create an admin user:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Run the dev server:

   ```bash
   python manage.py runserver
   ```

Admin is at `http://127.0.0.1:8000/admin/`. API endpoints live under `/api/`.

## Environment variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key (required) |
| `DEBUG` | `True`/`False`, default `False` |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL connection |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins; if empty and `DEBUG=True`, all origins are allowed |

## Media files

Uploaded images (food photos) are stored under `media/` (`MEDIA_ROOT`). In local
dev Django serves them at `/media/...`; in production nginx serves that directory.
