# SprintFlow Backend - Deployment Guide

## Production Deployment

### Prerequisites

- Linux server (Ubuntu 20.04+ or CentOS 8+)
- Docker and Docker Compose
- PostgreSQL 14+ (managed or self-hosted)
- Python 3.10+ (if deploying without Docker)

## Option 1: Docker Deployment (Recommended)

### 1. Create Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: sprintflow_db
      POSTGRES_USER: sprintflow
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sprintflow"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://sprintflow:${DB_PASSWORD}@db:5432/sprintflow_db
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "False"
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

### 2. Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/app/
COPY alembic/ /app/alembic/
COPY alembic.ini .

# Create logs directory
RUN mkdir -p logs

# Run migrations and start app
CMD ["bash", "-c", "alembic upgrade head && python -m app.scripts.seed_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### 3. Create Environment File

Create `.env.production`:

```env
DATABASE_URL=postgresql+asyncpg://sprintflow:your-secure-password@db:5432/sprintflow_db
SECRET_KEY=your-very-long-random-secret-key-minimum-32-characters
DEBUG=False
API_TITLE=SprintFlow
API_VERSION=1.0.0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 4. Deploy with Docker Compose

```bash
# Copy environment file
cp .env.production .env

# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api

# Run migrations (if not in CMD)
docker-compose exec api alembic upgrade head

# Seed database
docker-compose exec api python -m app.scripts.seed_db
```

## Option 2: Traditional Server Deployment

### 1. Prepare Server

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.10+
sudo apt-get install -y python3.10 python3.10-venv python3.10-dev

# Install PostgreSQL client
sudo apt-get install -y postgresql-client

# Create application user
sudo useradd -m -s /bin/bash sprintflow
sudo mkdir -p /var/www/sprintflow
sudo chown sprintflow:sprintflow /var/www/sprintflow
```

### 2. Deploy Application

```bash
# Switch to application directory
cd /var/www/sprintflow

# Clone repository
sudo -u sprintflow git clone <repo-url> .

# Create virtual environment
sudo -u sprintflow python3.10 -m venv venv

# Activate venv and install dependencies
sudo -u sprintflow bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Create .env file
sudo -u sprintflow cp .env.example .env
# Edit .env with production values
sudo nano .env
```

### 3. Database Setup

```bash
# Create PostgreSQL database and user
sudo -u postgres psql -c "CREATE USER sprintflow WITH PASSWORD 'your-secure-password';"
sudo -u postgres psql -c "CREATE DATABASE sprintflow_db OWNER sprintflow;"

# Run migrations
sudo -u sprintflow bash -c "source venv/bin/activate && alembic upgrade head"

# Seed database
sudo -u sprintflow bash -c "source venv/bin/activate && python -m app.scripts.seed_db"
```

### 4. Systemd Service

Create `/etc/systemd/system/sprintflow.service`:

```ini
[Unit]
Description=SprintFlow API Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=sprintflow
WorkingDirectory=/var/www/sprintflow
Environment="PATH=/var/www/sprintflow/venv/bin"
ExecStart=/var/www/sprintflow/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sprintflow
sudo systemctl start sprintflow
sudo systemctl status sprintflow
```

### 5. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/sprintflow`:

```nginx
upstream sprintflow_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    client_max_body_size 10M;

    location / {
        proxy_pass http://sprintflow_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    location /docs {
        proxy_pass http://sprintflow_api/docs;
    }

    location /openapi.json {
        proxy_pass http://sprintflow_api/openapi.json;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/sprintflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Monitoring & Logging

### Application Logs

```bash
# View service logs
sudo journalctl -u sprintflow -f

# Logs to file
tail -f /var/www/sprintflow/logs/app.log
```

### Database Monitoring

```bash
# Connect to database
psql -U sprintflow -d sprintflow_db

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check slow queries
SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

### Health Checks

```bash
# Application health
curl https://yourdomain.com/health

# API documentation
curl https://yourdomain.com/docs
```

## Scaling

### Horizontal Scaling

Use multiple application instances with load balancer:

```nginx
upstream sprintflow_api {
    server api-1.internal:8000;
    server api-2.internal:8000;
    server api-3.internal:8000;
}
```

### Database Replication

For high availability, configure PostgreSQL replication:
- Primary (read/write) server
- Standby (read-only) replicas
- Connection pooler (PgBouncer)

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/sprintflow"
DB_NAME="sprintflow_db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U sprintflow $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

Cron job:

```bash
# Run daily at 2 AM
0 2 * * * /var/www/sprintflow/backup.sh
```

### Database Restore

```bash
# Restore from backup
gunzip -c /backups/sprintflow/db_20240101_020000.sql.gz | psql -U sprintflow sprintflow_db
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u sprintflow -n 50

# Verify configuration
source venv/bin/activate
python -m app.main

# Check port availability
sudo lsof -i :8000
```

### Database Connection Issues

```bash
# Test connection
psql -h localhost -U sprintflow -d sprintflow_db -c "SELECT 1"

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql.log
```

### Performance Issues

```bash
# Check CPU/Memory
top

# Check disk usage
df -h

# Check database query performance
EXPLAIN ANALYZE SELECT ...;
```

## Security Checklist

- [ ] Set strong SECRET_KEY (min 32 chars)
- [ ] Use HTTPS with valid SSL certificate
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Update CORS origins
- [ ] Enable database authentication
- [ ] Set up firewall rules
- [ ] Enable audit logging
- [ ] Regular backups configured
- [ ] Monitor logs for errors
- [ ] Update dependencies regularly

## Rollback Procedure

If deployment fails:

```bash
# Stop current version
sudo systemctl stop sprintflow

# Revert code
cd /var/www/sprintflow
git revert <commit-hash>

# Rollback database
alembic downgrade -1

# Start service
sudo systemctl start sprintflow
```

## Support & Documentation

- API Documentation: https://yourdomain.com/docs
- Database Schema: See `alembic/versions/`
- Application Logs: `/var/www/sprintflow/logs/`
- PostgreSQL Logs: `/var/log/postgresql/`
