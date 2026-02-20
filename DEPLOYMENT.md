# Postify Deployment Guide

## Overview
This guide covers deploying Postify with Gunicorn for production environments.

## Prerequisites
- Python 3.11+
- Virtual environment activated
- All environment variables configured
- SSL certificates (for HTTPS)

## Quick Start

### Development
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Start with auto-reload
cd backend
gunicorn -c gunicorn_config.py wsgi
```

### Production
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start production server
cd backend
gunicorn -c gunicorn.conf.py wsgi
```

## Configuration Files

### gunicorn.conf.py (Production)
- **Workers**: `CPU cores * 2 + 1`
- **Worker Class**: `uvicorn.workers.UvicornWorker`
- **Timeout**: 30 seconds
- **Max Requests**: 1000 per worker
- **Logging**: Structured with access/error logs

### gunicorn_config.py (Development)
- **Workers**: 1
- **Auto-reload**: Enabled
- **Logging**: Verbose for debugging

## Environment Variables

### Required for Production
```bash
# Database
DB_PATH=/app/tokens.db
UPLOAD_DIR=/app/uploads

# URLs
FRONTEND_ORIGIN=https://yourdomain.com
BACKEND_PUBLIC_BASE=https://api.yourdomain.com

# Branding
BRAND_NAME=Postify
BRAND_PRIMARY=#0f172a
BRAND_SECONDARY=#334155
BRAND_ACCENT=#22c55e

# Social Media APIs (add your actual keys)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
META_REDIRECT_URI=https://api.yourdomain.com/auth/callback?platform=facebook
IG_USER_ID=your_instagram_user_id
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_REDIRECT_URI=https://api.yourdomain.com/auth/callback?platform=twitter
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=https://api.yourdomain.com/auth/callback?platform=linkedin
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

## Deployment Options

### 1. Direct Server Deployment

#### Linux/Mac
```bash
# Clone repository
git clone https://github.com/abhishek123107/postplace.git
cd postplace

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your actual values

# Start server
cd backend
gunicorn -c gunicorn.conf.py app.main:app
```

#### Windows
```cmd
# Clone repository
git clone https://github.com/abhishek123107/postplace.git
cd postplace

# Setup virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
copy backend\.env.example backend\.env
# Edit backend\.env with your actual values

# Start server
cd backend
gunicorn -c gunicorn.conf.py app.main:app
```

### 2. Docker Deployment

#### Single Container
```bash
# Build image
docker build -t postify-backend ./backend

# Run container
docker run -d \
  --name postify-backend \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/tokens.db:/app/tokens.db \
  --env-file .env \
  postify-backend
```

#### Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f postify-backend

# Stop services
docker-compose down
```

### 3. Systemd Service (Linux)

#### Create service file
```bash
sudo nano /etc/systemd/system/postify.service
```

```ini
[Unit]
Description=Postify Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/postify
Environment=PATH=/opt/postify/.venv/bin
ExecStart=/opt/postify/.venv/bin/gunicorn -c /opt/postify/gunicorn.conf.py app.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Enable and start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable postify
sudo systemctl start postify
sudo systemctl status postify
```

## SSL/HTTPS Setup

### Using Nginx
1. **Install Nginx**: `sudo apt install nginx`
2. **Copy nginx.conf**: `sudo cp nginx.conf /etc/nginx/sites-available/postify`
3. **Enable site**: `sudo ln -s /etc/nginx/sites-available/postify /etc/nginx/sites-enabled/`
4. **Test config**: `sudo nginx -t`
5. **Reload Nginx**: `sudo systemctl reload nginx`

### Using Certbot (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Performance Tuning

### Gunicorn Settings
```python
# For high traffic sites
workers = multiprocessing.cpu_count() * 4 + 1
worker_connections = 2000
max_requests = 2000
preload_app = True
```

### System Settings
```bash
# Increase file limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize network
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" >> /etc/sysctl.conf
sysctl -p
```

## Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Gunicorn stats
curl http://localhost:8000/stats
```

### Log Monitoring
```bash
# Real-time logs
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log

# Log rotation
sudo nano /etc/logrotate.d/gunicorn
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill process
sudo kill -9 <PID>
```

#### Permission Denied
```bash
# Fix permissions
sudo chown -R www-data:www-data /opt/postify
sudo chmod -R 755 /opt/postify
```

#### Memory Issues
```bash
# Monitor memory usage
free -h
htop

# Increase swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Security

### Firewall Setup
```bash
# UFW (Ubuntu)
sudo ufw allow 8000
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### Environment Security
```bash
# Secure .env file
chmod 600 .env
chown app:app .env

# Remove debug info
export ENVIRONMENT=production
export DEBUG=False
```

## Backup Strategy

### Database Backup
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /app/tokens.db /backups/tokens_$DATE.db
find /backups -name "tokens_*.db" -mtime +7 -delete
```

### Code Backup
```bash
# Git backup
git pull origin main
git add .
git commit -m "Backup $(date)"
git push origin main
```

## Scaling

### Horizontal Scaling
```bash
# Multiple Gunicorn instances
gunicorn -c gunicorn.conf.py app.main:app --bind 0.0.0.0:8000 &
gunicorn -c gunicorn.conf.py app.main:app --bind 0.0.0.0:8001 &
gunicorn -c gunicorn.conf.py app.main:app --bind 0.0.0.0:8002 &
```

### Load Balancer (Nginx)
```nginx
upstream postify_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

This deployment guide covers all aspects of running Postify in production with Gunicorn.
