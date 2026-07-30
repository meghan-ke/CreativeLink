# CreativeLink

Flask app connecting young artists with organisations and opportunities.

**Stack:** Flask, MySQL (SQLAlchemy), Gunicorn, Nginx, systemd, Cloudinary (media storage)

---

## Prerequisites

- Python 3.8+, `pip`, `git`
- MySQL Server
- Nginx (production only)

---

## Project Structure

```
CreativeLink/
├── app/
│   ├── __init__.py      # App factory, extensions, blueprint registration
│   ├── models.py        # SQLAlchemy models
│   ├── routes/          # Blueprints
│   └── templates/
├── static/
├── run.py               # Dev entry point
├── wsgi.py               # Production entry point (gunicorn)
├── requirements.txt
└── .env                 # Not committed to git
```

---

## Local Setup

```bash
git clone <your-repo-url>
cd CreativeLink

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` is missing:
```bash
pip install flask flask_sqlalchemy flask_jwt_extended flask_bcrypt flask_cors python-dotenv gunicorn cloudinary pymysql cryptography
pip freeze > requirements.txt
```

### `.env`

```
DATABASE_URL=mysql+pymysql://<db_user>:<db_password>@localhost/<db_name>
JWT_SECRET_KEY=<random-secret>
CLOUDINARY_CLOUD_NAME=<cloud-name>
CLOUDINARY_API_KEY=<api-key>
CLOUDINARY_API_SECRET=<api-secret>
```

Generate `JWT_SECRET_KEY`:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Cloudinary credentials: [cloudinary.com/console](https://cloudinary.com/console)

### Database

```bash
sudo apt install -y mysql-server
sudo systemctl enable --now mysql
sudo mysql
```
```sql
CREATE DATABASE creativelink;
CREATE USER 'creativelink_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON creativelink.* TO 'creativelink_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```
Match `DATABASE_URL` in `.env` to the credentials above. Tables are created automatically on first run.

### Run

```bash
source venv/bin/activate
python3 run.py
```
Visit `http://127.0.0.1:5000`.

---

## Production Deployment

### 1. Server setup

Repeat [Local Setup](#local-setup) on the server. Run `python3 run.py` once to create tables, then `Ctrl+C` — Gunicorn takes over from here.

### 2. Test Gunicorn

```bash
gunicorn --bind 127.0.0.1:8000 wsgi:app
curl http://127.0.0.1:8000/   # in a second terminal
```

### 3. systemd service

```bash
sudo tee /etc/systemd/system/creativelink.service > /dev/null << 'SVC'
[Unit]
Description=Gunicorn instance for CreativeLink
After=network.target mysql.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/CreativeLink
Environment="PATH=/home/ubuntu/CreativeLink/venv/bin"
ExecStart=/home/ubuntu/CreativeLink/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
SVC

sudo systemctl daemon-reload
sudo systemctl enable --now creativelink
sudo systemctl status creativelink
```

Adjust `User`, `Group`, and paths to match your setup.

### 4. Nginx

```bash
sudo tee /etc/nginx/sites-available/creativelink > /dev/null << 'NGINX'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 100M;

    location /static/ {
        alias /home/ubuntu/CreativeLink/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

sudo ln -s /etc/nginx/sites-available/creativelink /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

Use `server_name _;` if you don't have a domain yet.

### 5. Domain

Add an A record at your registrar:
- `@` → server's public IP
- `www` → server's public IP

Check propagation:
```bash
dig +short your-domain.com
```

### 6. HTTPS

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 7. Verify

```bash
sudo systemctl status creativelink
sudo systemctl status mysql
sudo systemctl status nginx
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'pymysql'` | `pip install pymysql` |
| `RuntimeError: 'cryptography' package is required...` | `pip install cryptography` |
| `Can't connect to MySQL server on 'localhost'` | Check `sudo systemctl status mysql` and `DATABASE_URL` |
| `413 Request Entity Too Large` | Add `client_max_body_size 100M;` to the nginx server block |
| App changes not showing up | `sudo systemctl restart creativelink` (not needed for templates/CSS) |
| `venv/` showing up in `git status` | Add `venv/`, `__pycache__/`, `*.pyc`, `.env`, `*.log`, `*.swp` to `.gitignore` |

Logs:
```bash
sudo journalctl -u creativelink -n 80 --no-pager
```

---

Website deployment url: [http://](http://18.205.151.247/)
