# Deployment Guide

## Local Deployment

### Prerequisites

- Rust 1.75+
- Node.js 18+
- Git

### Build

```bash
# Clone repository
git clone https://github.com/kiss-kedaya/openclaw-observational-memory.git
cd openclaw-observational-memory

# Build backend (release mode)
cargo build --release

# Build frontend
cd frontend
npm install
npm run build
cd ..
```

### Run

```bash
# Run the server
./target/release/observational-memory

# Server will start on http://localhost:3000
```

## Docker Deployment

### Dockerfile

```dockerfile
# Build stage
FROM rust:1.75 as rust-builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

# Frontend build stage
FROM node:18 as frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend ./
RUN npm run build

# Runtime stage
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=rust-builder /app/target/release/observational-memory /usr/local/bin/
COPY --from=frontend-builder /app/dist ./frontend/dist

EXPOSE 3000
CMD ["observational-memory"]
```

### Build and Run

```bash
# Build image
docker build -t observational-memory:latest .

# Run container
docker run -p 3000:3000 -v $(pwd)/data:/app/data observational-memory:latest
```

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/observational-memory.service`:

```ini
[Unit]
Description=Observational Memory Service
After=network.target

[Service]
Type=simple
User=observational-memory
WorkingDirectory=/opt/observational-memory
ExecStart=/opt/observational-memory/observational-memory
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable observational-memory
sudo systemctl start observational-memory
sudo systemctl status observational-memory
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name observational-memory.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## GitHub Actions Auto-Build

### Workflow Configuration

The project includes `.github/workflows/build.yml` for automatic builds.

### Supported Platforms

- Windows (x64)
- macOS (x64)
- macOS (ARM64)
- Linux (x64)

### Trigger Build

```bash
# Create and push tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Build for all platforms
# 2. Run tests
# 3. Create release
# 4. Upload artifacts
```

## Environment Variables

```bash
# Database path (default: ./memory.db)
export DATABASE_PATH=/path/to/memory.db

# Server port (default: 3000)
export PORT=3000

# Log level (default: info)
export RUST_LOG=info
```

## Performance Tuning

### Database

```bash
# Increase SQLite cache size
export SQLITE_CACHE_SIZE=10000

# Enable WAL mode
export SQLITE_WAL_MODE=1
```

### Server

```bash
# Increase worker threads
export TOKIO_WORKER_THREADS=8

# Increase connection pool
export DB_POOL_SIZE=20
```

## Monitoring

### Health Check

```bash
curl http://localhost:3000/api/sessions
```

### Logs

```bash
# View logs
journalctl -u observational-memory -f

# Or with Docker
docker logs -f observational-memory
```

### Metrics (Planned)

- Prometheus endpoint: `/metrics`
- Grafana dashboard
- Alert rules

## Backup

### Database Backup

```bash
# Backup SQLite database
cp memory.db memory.db.backup

# Or use SQLite backup command
sqlite3 memory.db ".backup memory.db.backup"
```

### Automated Backup

```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-observational-memory.sh
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Database Locked

```bash
# Check for stale locks
fuser memory.db

# Remove lock file
rm memory.db-shm memory.db-wal
```

### High Memory Usage

```bash
# Check memory usage
ps aux | grep observational-memory

# Restart service
sudo systemctl restart observational-memory
```

## Security

### Firewall

```bash
# Allow port 3000
sudo ufw allow 3000/tcp
```

### SSL/TLS

Use Let's Encrypt with Nginx:

```bash
sudo certbot --nginx -d observational-memory.example.com
```

## Upgrade

```bash
# Pull latest code
git pull origin master

# Rebuild
cargo build --release
cd frontend && npm run build && cd ..

# Restart service
sudo systemctl restart observational-memory
```

## Rollback

```bash
# Checkout previous version
git checkout v0.9.0

# Rebuild and restart
cargo build --release
sudo systemctl restart observational-memory
```
