# Deploying nurture_backend to the VPS

Target: Ubuntu VPS at 72.61.91.102 with Postgres 17 and nginx already installed.
The app runs as gunicorn behind nginx, managed by systemd.

## 1. Get the code onto the VPS

`/var/www` is fine. Clone via git so updates are just `git pull`:

```bash
sudo mkdir -p /var/www
cd /var/www
sudo git clone <repo-url> nurture_backend
sudo chown -R www-data:www-data /var/www/nurture_backend
```

## 2. Python environment

```bash
cd /var/www/nurture_backend
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install -r requirements.txt gunicorn
```

gunicorn is the WSGI server systemd runs; it is deployment-only and intentionally
not in `requirements.txt`.

## 3. Production .env

Create `/var/www/nurture_backend/.env` (never committed):

```
SECRET_KEY=<generate a fresh one, do NOT reuse the dev key>
DEBUG=False
ALLOWED_HOSTS=72.61.91.102
DB_NAME=nurture
DB_USER=nurture
DB_PASSWORD=<the password you set when creating the VPS db user>
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=
```

Generate a key: `./venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

When a domain is added later, put it in `ALLOWED_HOSTS` and add the Flutter web
origin (if any) to `CORS_ALLOWED_ORIGINS`. Native mobile apps don't need CORS.

## 4. Migrate and collect static files

```bash
sudo -u www-data ./venv/bin/python manage.py migrate
sudo -u www-data ./venv/bin/python manage.py collectstatic --noinput
sudo -u www-data ./venv/bin/python manage.py createsuperuser
```

## 5. systemd unit

Create `/etc/systemd/system/nurture.service`:

```ini
[Unit]
Description=Nurture Django backend (gunicorn)
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/nurture_backend
ExecStart=/var/www/nurture_backend/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/nurture.sock \
    nurture.wsgi:application
RuntimeDirectory=nurture
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nurture
sudo systemctl status nurture
```

## 6. nginx site

Create `/etc/nginx/sites-available/nurture`:

```nginx
server {
    listen 80;
    server_name 72.61.91.102;

    client_max_body_size 10M;  # food photo uploads

    location /static/ {
        alias /var/www/nurture_backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/nurture_backend/media/;
    }

    location / {
        proxy_pass http://unix:/run/nurture.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/nurture /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 7. Updating after each stage

```bash
cd /var/www/nurture_backend
sudo -u www-data git pull
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo -u www-data ./venv/bin/python manage.py migrate
sudo -u www-data ./venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart nurture
```

## Later (when a domain exists)

- Point DNS at the VPS, add the domain to `server_name` and `ALLOWED_HOSTS`.
- Add HTTPS with certbot: `sudo certbot --nginx -d yourdomain.com`.
