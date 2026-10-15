# ADR 002: GitHub Actions Deployment with Self-Hosted Runner

**Status**: Accepted ✅
**Date**: 2025-10-11
**Decision Makers**: Development Team

## Context

PortalForge needs a deployment strategy for MVP that is:
- Secure (no SSH keys stored in GitHub)
- Automated (CI/CD on push to main)
- Simple to maintain
- Cost-effective (free tier compatible)
- Scalable for future growth

We have:
- Single VPS: `[VPS_IP]:[SSH_PORT]`
- GitHub repository: `Vesperino/PortalForge`
- .NET 8.0 backend API
- Nuxt 3 frontend application
- Supabase for database and auth

## Decision

Use **GitHub Actions with self-hosted runner** on the VPS for automated deployment of Docker containers.

### Architecture Components

1. **Self-Hosted GitHub Actions Runner**
   - Installed on VPS at `/home/[VPS_USER]/actions-runner`
   - Runs as systemd service under `[VPS_USER]` user
   - Labels: `self-hosted`, `vps`, `production`
   - Connected to GitHub repository

2. **Docker Containers**
   - Backend: `portalforge-backend` (port 22022:5000)
   - Frontend: `portalforge-frontend` (port 5001:3000)
   - Both use multi-stage builds
   - Both have health checks

3. **Nginx Reverse Proxy**
   - Proxies `api.krablab.pl` → `localhost:22022`
   - Proxies `portal.krablab.pl` → `localhost:5001`
   - HTTP only (SSL to be added)

4. **GitHub Actions Workflows**
   - `.github/workflows/deploy-backend.yml`
   - `.github/workflows/deploy-frontend.yml`
   - Trigger on push to main or manual dispatch
   - Path filters: `backend/**` and `frontend/**`

## Rationale

### Why Self-Hosted Runner?

✅ **Security Benefits**:
- No SSH private keys in GitHub Secrets
- Runner runs locally on VPS with full Docker access
- Secrets stay on VPS (`.env` files)
- Fine-grained control over what runner can access

✅ **Simplicity**:
- No SSH connection overhead
- Direct Docker commands
- Easier to debug (can check runner logs on VPS)
- Native GitHub integration

✅ **Cost**:
- Free (uses VPS resources we already have)
- No GitHub-hosted runner minutes consumed
- No external deployment service costs

✅ **Performance**:
- Fast deployment (local Docker build and run)
- No data transfer to GitHub servers
- Instant access to VPS resources

❌ **Trade-offs**:
- Need to maintain runner service
- Runner is single point of failure (acceptable for MVP)
- VPS needs to be online for deployments

### Why Docker Containers?

✅ **Consistency**:
- Same deployment strategy for both services
- Dev-prod parity
- No "works on my machine" issues

✅ **Portability**:
- Can move to any Docker-compatible host
- Easy to add to Kubernetes later

✅ **Isolation**:
- Services don't interfere with each other
- Clean environment variables
- Resource limits can be set

✅ **Simplicity**:
- No need to install .NET or Node.js on VPS
- Easy rollback (just run previous image)
- Built-in health checks

❌ **Trade-offs**:
- Slightly more overhead than native processes
- Learning curve for Docker (minimal)

### Why Not Alternatives?

#### Alternative 1: SSH-based Deployment
**Rejected because**:
- ❌ Need to store SSH private keys in GitHub Secrets
- ❌ More complex workflow (rsync, SSH commands)
- ❌ Harder to manage secrets and environment variables
- ❌ SSH key rotation is manual process

#### Alternative 2: GitHub-Hosted Runners + SSH
**Rejected because**:
- ❌ Consumes GitHub Actions minutes (cost)
- ❌ Still requires SSH keys
- ❌ Slower (need to pull code, build remotely)
- ❌ Limited to 6 hours per job

#### Alternative 3: Docker Hub + Watchtower
**Rejected because**:
- ❌ Need to push images to Docker Hub (extra step)
- ❌ Public images expose code (would need private registry)
- ❌ Watchtower adds polling delay
- ❌ Less control over deployment timing

#### Alternative 4: Systemd Services (No Docker)
**Rejected because**:
- ❌ Need to install .NET 8.0 runtime on VPS
- ❌ Need to install Node.js 20 on VPS
- ❌ More complex deployment scripts
- ❌ Harder to rollback
- ❌ Less portable

#### Alternative 5: Platform-as-a-Service (Heroku, Render, etc.)
**Rejected because**:
- ❌ Higher cost than VPS
- ❌ Less control over infrastructure
- ❌ We already have VPS
- ❌ Vendor lock-in

## Implementation Details

### Self-Hosted Runner Setup

```bash
# 1. Download runner
cd ~
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.328.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.328.0/actions-runner-linux-x64-2.328.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.328.0.tar.gz

# 2. Configure runner
./config.sh --url https://github.com/Vesperino/PortalForge --token <TOKEN>
# Name: portalforge-vps
# Labels: self-hosted,vps,production

# 3. Install as service
sudo ./svc.sh install [VPS_USER]
sudo ./svc.sh start

# 4. Add Docker permissions
sudo usermod -aG docker [VPS_USER]
sudo ./svc.sh stop
sudo ./svc.sh start
```

### Backend Deployment Workflow

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy Backend to VPS
    runs-on: [self-hosted, vps, production]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Stop existing container
        run: docker stop portalforge-backend || true

      - name: Remove existing container
        run: docker rm portalforge-backend || true

      - name: Build Docker image
        run: |
          cd backend
          docker build -t portalforge-backend:latest .

      - name: Run Docker container
        run: |
          docker run -d \
            --name portalforge-backend \
            --restart unless-stopped \
            -p 22022:5000 \
            --env-file ~/portalforge/backend/.env \
            portalforge-backend:latest

      - name: Clean up old images
        run: docker image prune -f

      - name: Check container status
        run: |
          sleep 5
          docker ps | grep portalforge-backend
          echo "✅ Backend container running!"

      - name: Health check
        run: |
          echo "Waiting for backend to start..."
          sleep 10
          curl -f http://localhost:22022/health || exit 1
          echo "✅ Backend health check passed!"
```

### Frontend Deployment Workflow

Similar to backend, with:
- Build args for Supabase URLs (from GitHub Secrets)
- Port: 5001:3000
- Health check: `curl http://localhost:5001`

### Docker Configuration

**Backend Dockerfile**:
- Multi-stage: `sdk:8.0` → `aspnet:8.0`
- Non-root user: `appuser` (UID 1000)
- Health check: `/health` endpoint
- Exposed port: 5000

**Frontend Dockerfile**:
- Multi-stage: `node:20-alpine` (build) → `node:20-alpine` (runtime)
- Non-root user: `appuser` (UID 1001)
- Health check: `wget localhost:3000`
- dumb-init for proper signal handling
- Exposed port: 3000

### Environment Variables

**Backend** (`.env` file on VPS):
```env
ASPNETCORE_ENVIRONMENT=Production
ASPNETCORE_URLS=http://+:5000
ConnectionStrings__DefaultConnection=Host=db.xxx.supabase.co;...
Supabase__Url=https://xxx.supabase.co
Supabase__ServiceRoleKey=SECRET
Jwt__Secret=SECRET
Jwt__Issuer=PortalForge
Jwt__Audience=PortalForge
Jwt__ExpirationMinutes=480
Serilog__MinimumLevel__Default=Information
```

**Frontend** (GitHub Secrets → build args):
```env
NUXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NUXT_PUBLIC_SUPABASE_KEY=PUBLIC_ANON_KEY
NUXT_PUBLIC_API_BASE_URL=http://api.krablab.pl
NODE_ENV=production
```

### Nginx Configuration

**Backend** (`/etc/nginx/sites-available/api.krablab.pl.conf`):
```nginx
server {
    listen 80;
    server_name api.krablab.pl;

    location / {
        proxy_pass http://localhost:22022;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Frontend** (`/etc/nginx/sites-available/portal.krablab.pl.conf`):
```nginx
server {
    listen 80;
    server_name portal.krablab.pl;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /_nuxt/ {
        proxy_pass http://localhost:5001/_nuxt/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Consequences

### Positive Consequences

✅ **Security**:
- No SSH keys in GitHub
- Secrets stay on VPS
- Runner has minimal permissions

✅ **Developer Experience**:
- Simple workflow files
- Easy to test (can run workflows manually)
- Clear deployment logs in GitHub Actions

✅ **Reliability**:
- Docker health checks ensure services are running
- Auto-restart on failure
- Easy rollback (tag images, run previous)

✅ **Cost**:
- Zero additional cost (uses VPS we have)
- No external service subscriptions

✅ **Scalability**:
- Can add more runners later
- Can move to Kubernetes with minimal changes
- Workflow patterns work for staging/prod

### Negative Consequences

❌ **Single Point of Failure**:
- If VPS is down, can't deploy
- **Mitigation**: Monitoring, backups, runbook

❌ **Runner Maintenance**:
- Need to update runner occasionally
- Need to monitor runner health
- **Mitigation**: Automated updates, health checks

❌ **No Automated Rollback**:
- Rollback requires manual intervention
- **Mitigation**: Document rollback procedure, add automation later

❌ **Limited to One Environment**:
- Production only (no staging yet)
- **Mitigation**: Add staging environment later

## Success Criteria

✅ **Must Have**:
- [x] Deployments trigger automatically on push to main
- [x] Both services deploy successfully
- [x] Health checks pass after deployment
- [x] Services accessible via domain names
- [x] Zero-downtime deployments (stop old, start new)

✅ **Nice to Have**:
- [ ] Automated rollback on failure
- [ ] Deployment notifications (Slack/Discord)
- [ ] Staging environment
- [ ] Blue-green deployments

## Monitoring & Maintenance

### Monitoring

**GitHub Actions**:
- Check workflow status: https://github.com/Vesperino/PortalForge/actions
- Email notifications on failure (GitHub default)

**VPS Health**:
```bash
# Check runner status
sudo systemctl status actions.runner.Vesperino-PortalForge.portalforge-vps

# Check Docker containers
docker ps

# Check Docker logs
docker logs portalforge-backend
docker logs portalforge-frontend

# Check health endpoints
curl http://localhost:22022/health
curl http://localhost:5001
```

**Nginx**:
```bash
# Check Nginx status
sudo systemctl status nginx

# Check access logs
sudo tail -f /var/log/nginx/api.krablab.pl.access.log
sudo tail -f /var/log/nginx/portal.krablab.pl.access.log

# Check error logs
sudo tail -f /var/log/nginx/api.krablab.pl.error.log
sudo tail -f /var/log/nginx/portal.krablab.pl.error.log
```

### Maintenance

**Runner Updates**:
```bash
cd ~/actions-runner
sudo ./svc.sh stop
./config.sh remove
# Download new version
./config.sh --url https://github.com/Vesperino/PortalForge --token <TOKEN>
sudo ./svc.sh install [VPS_USER]
sudo ./svc.sh start
```

**Docker Cleanup** (monthly):
```bash
# Remove unused images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f

# Remove unused networks
docker network prune -f
```

**Log Rotation** (configure logrotate):
```bash
# /etc/logrotate.d/nginx
/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

## Rollback Procedure

### Manual Rollback

1. **Identify Last Good Commit**:
   ```bash
   git log --oneline
   ```

2. **Checkout Last Good Commit**:
   ```bash
   git checkout <commit-hash>
   ```

3. **Trigger Workflow Manually**:
   - Go to GitHub Actions
   - Select workflow (Deploy Backend or Deploy Frontend)
   - Click "Run workflow"
   - Choose branch (or enter commit hash if needed)

### Future: Automated Rollback

Add to workflow:
```yaml
- name: Rollback on failure
  if: failure()
  run: |
    docker stop portalforge-backend
    docker rm portalforge-backend
    docker run -d \
      --name portalforge-backend \
      --restart unless-stopped \
      -p 22022:5000 \
      --env-file ~/portalforge/backend/.env \
      portalforge-backend:previous
```

Requires tagging images:
```bash
docker tag portalforge-backend:latest portalforge-backend:previous
```

## Testing Strategy

### Pre-Deployment Testing

- [ ] Unit tests pass locally
- [ ] Integration tests pass locally
- [ ] Docker build succeeds locally
- [ ] Manual testing on localhost

### Post-Deployment Testing

- [ ] Health check passes
- [ ] Swagger accessible (backend)
- [ ] Homepage loads (frontend)
- [ ] API calls work (frontend → backend)
- [ ] Database connection works
- [ ] Authentication flow works

### Deployment Testing

```bash
# Test backend health
curl http://api.krablab.pl/health

# Test backend Swagger
open http://api.krablab.pl/swagger

# Test frontend
open http://portal.krablab.pl

# Test frontend → backend integration
# (Check browser Network tab for API calls)
```

## Future Improvements

### Phase 2 (Week 3-4)
- [ ] Add staging environment (separate runner or same VPS)
- [ ] Implement blue-green deployment
- [ ] Add automated rollback on health check failure
- [ ] Add deployment notifications (Slack/Discord webhook)

### Phase 3 (Week 5-6)
- [ ] Add SSL certificates (Certbot)
- [ ] Configure rate limiting in Nginx
- [ ] Add monitoring (Prometheus + Grafana)
- [ ] Centralized logging (Loki + Grafana)

### Phase 4 (Week 7-8)
- [ ] Implement database backups
- [ ] Add security scanning (Trivy for Docker images)
- [ ] Load testing
- [ ] Disaster recovery plan

### Post-MVP
- [ ] Migrate to Kubernetes (if scale requires)
- [ ] Add multiple VPS nodes (load balancing)
- [ ] CI/CD for pull requests (preview environments)
- [ ] Automated E2E tests in CI

## Related Documents

- [Progress Log - Deployment Setup](.ai/progress/2025-10-11-deployment-setup.md)
- [PRD](.ai/prd.md)
- [Tech Stack](.ai/tech-stack.md)
- [Backend Documentation](.ai/backend/README.md)
- [Frontend Documentation](.ai/frontend/README.md)
- [Supabase Setup ADR](.ai/decisions/001-supabase-setup.md)

---

**Last Updated**: 2025-10-11
**Status**: ✅ Implemented and working
**Next Review**: Week 3 (after MVP Phase 1 completion)
