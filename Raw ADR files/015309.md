# ADR-006: Deployment Architecture

## Status
**Approved** — 2024-12-21

## Context

The Reachy Home Assistant consists of multiple components that need to run reliably in a home environment:

1. **Assistant Service**: Main robot control and conversation
2. **API Server**: Web app backend
3. **Web Frontend**: React dashboard
4. **PostgreSQL Database**: Persistent storage
5. **Reachy Mini**: Robot hardware (wireless connection)

### Key Requirements
- Run on Seeed reComputer J4012 (Jetson Orin NX 16GB)
- Start automatically on boot
- Self-healing (restart on crash)
- Accessible on local network
- Easy to update and maintain
- Minimal complexity (this is a home project)

## Decision

**Systemd services for process management with direct installations (no Docker).**

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Seeed reComputer J4012                                │
│                    (Jetson Orin NX 16GB)                                 │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         Systemd                                      │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────────┐  │ │
│  │  │  reachy-    │ │  reachy-    │ │  postgresql │ │  reachy-web   │  │ │
│  │  │  assistant  │ │  api        │ │             │ │  (nginx)      │  │ │
│  │  │  .service   │ │  .service   │ │  .service   │ │  .service     │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         Network                                      │ │
│  │  Port 3000: API (FastAPI/Uvicorn)                                   │ │
│  │  Port 80: Web frontend (nginx serving React build)                  │ │
│  │  Port 5432: PostgreSQL (localhost only)                             │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         Storage                                      │ │
│  │  /home/reachy/reachy-assistant/         (application code)          │ │
│  │  /var/lib/postgresql/                    (database)                  │ │
│  │  /home/reachy/enrolled/                  (face/voice data)          │ │
│  │  /home/reachy/backups/                   (daily backups)            │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
            │                              │
            ▼                              ▼
    ┌─────────────┐                 ┌─────────────┐
    │ Reachy Mini │                 │  Home WiFi  │
    │  (Wireless) │                 │   Network   │
    └─────────────┘                 └─────────────┘
```

### Why Not Docker

| Factor | Direct Install | Docker |
|--------|----------------|--------|
| GPU access | Native, simple | nvidia-container-toolkit needed |
| Resource overhead | None | ~200MB+ per container |
| Complexity | Lower | Higher for Jetson |
| Debugging | Direct access | Extra layer |
| Updates | git pull + pip | Rebuild images |

For a single-machine home deployment, Docker adds complexity without benefit.

### Service Definitions

```ini
# /etc/systemd/system/reachy-assistant.service
[Unit]
Description=Reachy Home Assistant Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=reachy
WorkingDirectory=/home/reachy/reachy-assistant
Environment=PATH=/home/reachy/reachy-assistant/venv/bin
ExecStart=/home/reachy/reachy-assistant/venv/bin/python -m assistant.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/reachy-api.service
[Unit]
Description=Reachy API Server
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=reachy
WorkingDirectory=/home/reachy/reachy-assistant
Environment=PATH=/home/reachy/reachy-assistant/venv/bin
ExecStart=/home/reachy/reachy-assistant/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Consequences

### Positive
- **Simplicity**: Standard Linux service management
- **Reliability**: Systemd handles restarts, boot order
- **Performance**: No container overhead
- **GPU access**: Native CUDA support
- **Familiar**: Standard Jetson/Linux patterns

### Negative
- **No isolation**: Services share system Python/libs
- **Manual dependency management**: No container pinning
- **Harder to replicate**: No docker-compose up
- **System-specific**: Tied to Jetson/Ubuntu

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Dependency conflicts | Use virtual environment |
| Failed updates | Test on dev branch first |
| Service crashes | Systemd auto-restart |
| Disk full | Monitoring + log rotation |

## Implementation Notes

### Initial Setup Script

```bash
#!/bin/bash
# scripts/setup.sh - Run once on fresh Jetson

# System packages
sudo apt update && sudo apt install -y \
    postgresql postgresql-contrib \
    python3-pip python3-venv \
    nginx ffmpeg

# PostgreSQL
sudo -u postgres createuser reachy
sudo -u postgres createdb reachy_db -O reachy

# Application
cd /home/reachy
git clone https://github.com/you/reachy-assistant.git
cd reachy-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install services
sudo cp deploy/reachy-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable reachy-assistant reachy-api
sudo systemctl start reachy-assistant reachy-api
```

### Update Script

```bash
#!/bin/bash
# scripts/deploy.sh - Run to update

cd /home/reachy/reachy-assistant
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --quiet

sudo systemctl restart reachy-assistant reachy-api
echo "Deploy complete!"
```

### Backup Script (Cron)

```bash
#!/bin/bash
# scripts/backup.sh - Runs daily via cron

BACKUP_DIR=/home/reachy/backups
DATE=$(date +%Y%m%d)

# Database backup
pg_dump reachy_db | gzip > $BACKUP_DIR/db-$DATE.sql.gz

# Keep last 7 days
find $BACKUP_DIR -name "db-*.sql.gz" -mtime +7 -delete

# Optional: sync to cloud
# rclone copy $BACKUP_DIR remote:reachy-backups
```

### Network Configuration

```nginx
# /etc/nginx/sites-available/reachy
server {
    listen 80;
    server_name _;

    # React frontend
    location / {
        root /home/reachy/reachy-assistant/src/web/build;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
```

### Monitoring

```bash
# View service status
sudo systemctl status reachy-assistant reachy-api

# View logs
journalctl -u reachy-assistant -f
journalctl -u reachy-api -f

# Resource usage
htop
nvtop  # GPU monitoring
```

## Hardware Notes

### Seeed reComputer J4012 Specifications
- **CPU**: 8-core Arm Cortex-A78AE
- **GPU**: 1024-core NVIDIA Ampere (32 Tensor Cores)
- **Memory**: 16GB LPDDR5
- **Storage**: 128GB NVMe (expandable)
- **Connectivity**: Gigabit Ethernet, WiFi 6, Bluetooth 5.2

### Resource Allocation (Expected)

| Component | CPU | GPU | RAM |
|-----------|-----|-----|-----|
| PostgreSQL | 1 core | - | 1GB |
| Assistant Service | 2 cores | 4GB | 4GB |
| API Server | 1 core | - | 500MB |
| Web Server | 0.5 core | - | 100MB |
| OS + Buffer | 3.5 cores | - | 6GB |
| **Total** | 8 cores | 4GB | ~12GB |

Leaves headroom for spikes and future features.

## Future Considerations

1. **Containerization**: Consider if deploying to multiple homes
2. **Remote monitoring**: Add Prometheus/Grafana if needed
3. **OTA updates**: Automated update system
4. **Redundancy**: Backup Jetson for critical families

## Related Decisions
- ADR-001: Data storage (PostgreSQL configuration)
- ADR-005: Speech pipeline (resource requirements)
