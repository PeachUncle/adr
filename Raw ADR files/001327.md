# ADR-004: Docker Containerization for Air-Side

**Status:** Accepted
**Date:** 2024-10 (Initial Air-Side deployment)
**Updated:** 2025-11-11
**Deciders:** DevOps, Development Team
**Related Issues:** #33 (NVMe migration), #46, #50, #51 (Deployment issues)
**Related Views:** `view-deployment.md`, `view-security-reliability.md`

---

## Context

Air-Side service runs on Raspberry Pi 5 and must:

1. **Control Sony camera** via USB and proprietary SDK
2. **Run continuously** during flight operations (high availability)
3. **Update frequently** during development (rapid iteration)
4. **Isolate dependencies** (Sony SDK, system libraries)
5. **Recover from crashes** automatically (fault tolerance)
6. **Monitor resources** (CPU, memory, temperature)

**Deployment Challenges:**
- Sony SDK requires specific library versions (libusb, system libs)
- Development vs. production builds need different configurations
- Manual deployment error-prone (cp, chmod, systemd service management)
- System-level changes risk breaking other services
- Rollback difficult if update breaks

**Platform:**
- Raspberry Pi 5 (8GB RAM, NVMe SSD)
- Ubuntu 24.04 LTS ARM64
- No physical access during flight (remote-only management)

---

## Decision

**We will deploy Air-Side service as a Docker container:**

1. **Containerization:** Package application + dependencies in Docker image
2. **Base Image:** Ubuntu 24.04 ARM64 (matches host OS)
3. **Multi-Stage Build:** Separate build stage from runtime stage
4. **Host Networking:** Use `--network=host` for UDP broadcast
5. **USB Passthrough:** Mount `/dev/bus/usb` for camera access
6. **Auto-Restart:** Docker restart policy `always`
7. **Logging:** Docker logs + file logging to mounted volume
8. **Build Script:** `build_container.sh` for reproducible builds
9. **Run Script:** `run_container.sh` with environment configs

**Deployment Unit:** Docker image `payload-manager:latest`

---

## Docker Configuration

### Dockerfile.prod (Production)

```dockerfile
# ====================
# Stage 1: Build Stage
# ====================
FROM ubuntu:24.04 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libusb-1.0-0-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
WORKDIR /app
COPY sbc/ /app/sbc/
COPY sdk/ /app/sdk/

# Build application
RUN cd /app/sbc && \
    mkdir -p build && \
    cd build && \
    cmake .. && \
    make -j4

# Copy Sony SDK adapters (CRITICAL for camera enumeration)
RUN mkdir -p /app/sbc/build/CrAdapter && \
    cp -r /app/sdk/external/crsdk/CrAdapter/* /app/sbc/build/CrAdapter/

# ====================
# Stage 2: Runtime Stage
# ====================
FROM ubuntu:24.04

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy built binary and libraries
COPY --from=builder /app/sbc/build/payload_manager /app/payload_manager
COPY --from=builder /app/sbc/build/CrAdapter /app/sbc/build/CrAdapter
COPY --from=builder /app/sdk/external/crsdk/lib /app/lib

# Copy protocol specifications
COPY docs/protocol/*.json /app/specs/

# Set library path
ENV LD_LIBRARY_PATH=/app/lib:$LD_LIBRARY_PATH

# Set working directory
WORKDIR /app

# Expose ports (documentation only, using host networking)
EXPOSE 5000 5001 5002

# Run application
CMD ["/app/payload_manager"]
```

### run_container.sh (Production)

```bash
#!/bin/bash
docker run -d \
  --name payload-manager \
  --restart=always \
  --network=host \
  --device /dev/bus/usb:/dev/bus/usb \
  -v /var/log/payload-manager:/var/log/payload-manager \
  -e LOG_LEVEL=INFO \
  -e AIR_SIDE_IP=192.168.144.53 \
  payload-manager:latest
```

---

## Alternatives Considered

### Alternative 1: Systemd Service (Native Binary)

**Approach:** Install binary directly on host, manage via systemd

**Deployment:**
```bash
# Build
cd ~/DPM-V2/sbc/build
cmake .. && make

# Install
sudo cp payload_manager /usr/local/bin/
sudo cp payload-manager.service /etc/systemd/system/
sudo systemctl enable payload-manager
sudo systemctl start payload-manager
```

**Pros:**
- No Docker overhead (direct system access)
- Simpler for users familiar with systemd
- No container layer

**Cons:**
- ❌ **Dependency Hell:** Must install libusb, Sony SDK libs on host
  - Version conflicts with system packages
  - Difficult to roll back if upgrade breaks
- ❌ **No Isolation:** Service can affect system (resource limits, crashes)
- ❌ **Manual Deployment:** Multi-step process error-prone
  - cp, chmod, systemctl commands must be run correctly
  - Easy to forget CrAdapter directory (Issue #33)
- ❌ **Environment Pollution:** Library paths, env vars clutter system
- ❌ **Rollback Difficulty:** Must track old binary versions manually
- ❌ **No Build Reproducibility:** "Works on my machine" syndrome

**Real-World Failure (Issue #33):**
Manual rebuild inside container forgot CrAdapter directory → camera enumeration failed (0x34563 error) → many hours debugging

**Rejection Reason:** Experienced pain in Issue #33, #46, #50, #51. Container isolation prevents entire class of deployment bugs.

---

### Alternative 2: Snap Package

**Approach:** Package as Ubuntu Snap for easy installation

**Pros:**
- Auto-updates
- Sandboxing
- Dependency bundling

**Cons:**
- ❌ **USB Access Restrictions:** Snap confinement blocks USB devices (requires manual interface connections)
- ❌ **Network Restrictions:** Snap may block raw socket access
- ❌ **Learning Curve:** Snap packaging complex (snapcraft.yaml)
- ❌ **Debugging Difficulty:** Snap internals opaque
- ❌ **ARM64 Support:** Snap store ARM64 support limited

**Rejection Reason:** Snap confinement model incompatible with USB camera access requirements

---

### Alternative 3: Virtual Environment (Python-style)

**Approach:** Not applicable (C++ application, not Python)

**Why Considered:** Team familiar with Python venv pattern

**Rejection:** N/A for compiled C++ binaries

---

### Alternative 4: Kubernetes / K3s

**Approach:** Deploy Air-Side as Kubernetes pod

**Pros:**
- Orchestration features (health checks, auto-restart, scaling)
- Industry-standard deployment pattern

**Cons:**
- ❌ **Overkill:** Single-node, single-service deployment doesn't need orchestration
- ❌ **Complexity:** Kubernetes YAML, kubectl, pod networking
- ❌ **Resource Overhead:** K3s requires ~500MB RAM (significant on 8GB Pi)
- ❌ **USB Passthrough:** More complex in Kubernetes (privileged pods, device plugins)

**Rejection Reason:** Kubernetes designed for multi-node clusters. Docker Compose or standalone Docker sufficient for single-service deployment.

---

## Consequences

### Positive

✅ **Dependency Isolation:** All libraries packaged in container
- Sony SDK, libusb, system libs versioned independently of host
- No conflicts with system packages
- Reproducible builds across development machines

✅ **Easy Rollback:** Tag images, roll back with single command
```bash
docker tag payload-manager:latest payload-manager:v1.2.3
# Later, if v1.2.4 breaks:
docker run payload-manager:v1.2.3
```

✅ **Automatic Recovery:** `--restart=always` restarts on crash
- Air-Side crash → Docker restarts container in <10 seconds
- System reboot → Docker starts container automatically
- No manual intervention required

✅ **Environment Consistency:** Development and production use same image
- "Works on my machine" eliminated
- CI/CD can test exact production image
- Staging environment identical to production

✅ **Multi-Stage Builds:** Separate build tools from runtime
- Build stage: gcc, cmake, git (~500MB)
- Runtime stage: Only libusb (~50MB)
- Result: Production image 1/10th size of build image

✅ **Resource Limits:** Docker can enforce CPU/memory constraints
```bash
docker run --memory=1g --cpus=2 payload-manager:latest
```

✅ **Logging Integration:** Docker logs API
```bash
docker logs payload-manager --tail=100 --follow
```

✅ **USB Passthrough:** `/dev/bus/usb` mount works reliably
- Container sees camera as if native
- Permissions via host udev rules

---

### Negative

⚠️ **Docker Learning Curve:** Team must learn Docker concepts
- **Mitigation:** Comprehensive scripts (`build_container.sh`, `run_container.sh`)
- **Mitigation:** Documentation in `sbc/docs/DOCKER_SETUP.md`
- **Reality:** One-time learning investment, now team comfortable

⚠️ **Host Networking Required:** UDP broadcast requires `--network=host`
- **Reason:** UDP broadcast doesn't work with Docker bridge networking
- **Impact:** Container shares host network namespace (less isolation)
- **Mitigation:** Firewall rules on host protect network
- **Alternative Rejected:** Multicast UDP more complex, not needed

⚠️ **USB Permissions:** Host udev rules still required
- **Reason:** Docker inherits host USB device permissions
- **Solution:** `99-sony-camera.rules` on host (documented)
- **One-time setup:** Added to deployment scripts

⚠️ **Container Restarts Lose Ephemeral State:** Runtime changes lost
- **Problem (Issue #33):** Rebuilt binary inside container → lost on restart
- **Solution:** Always rebuild Docker image, never modify running container
- **Best Practice:** "Pets vs. Cattle" - containers are disposable

⚠️ **Build Time:** Multi-stage build ~2-3 minutes on Pi 5
- **Mitigation:** Build on development machine (faster), transfer image via `docker save/load`
- **Mitigation:** Layer caching speeds incremental builds (~30 seconds)

⚠️ **Disk Space:** Docker images accumulate over time
- **Mitigation:** Periodic cleanup: `docker image prune`
- **Monitoring:** NVMe SSD has 256GB (sufficient for ~50 images)

---

## Implementation Notes

### Build Process

```bash
# Build image
cd ~/DPM-V2
docker build -f sbc/Dockerfile.prod -t payload-manager:latest .

# Tag with version
docker tag payload-manager:latest payload-manager:v1.2.3

# Save image for transfer
docker save payload-manager:latest | gzip > payload-manager.tar.gz

# Load image on Pi 5
gunzip -c payload-manager.tar.gz | docker load
```

### Deployment Process

```bash
# Stop old container
docker stop payload-manager
docker rm payload-manager

# Run new container
cd ~/DPM-V2/sbc
./run_container.sh prod
```

### Verification

```bash
# Check container running
docker ps | grep payload-manager

# Check logs
docker logs payload-manager --tail=50

# Check camera connection
docker exec payload-manager ls /app/sbc/build/CrAdapter/

# Monitor resources
docker stats payload-manager
```

### Troubleshooting

```bash
# Container won't start
docker logs payload-manager

# Camera not detected
docker exec payload-manager lsusb

# Shell into container (debugging)
docker exec -it payload-manager bash

# Restart container
docker restart payload-manager
```

---

## Critical Lessons (from LESSONS_LEARNED.md)

### Issue #33: Sony SDK Camera Enumeration Failure (0x34563)

**Problem:** Camera enumeration fails after fresh build

**Root Cause:** Missing `CrAdapter/` directory in build output

**Solution (in Dockerfile):**
```dockerfile
RUN mkdir -p /app/sbc/build/CrAdapter && \
    cp -r /app/sdk/external/crsdk/CrAdapter/* /app/sbc/build/CrAdapter/
```

**Verification:**
```bash
docker exec payload-manager ls /app/sbc/build/CrAdapter/
```

**Prevention:** Always use `Dockerfile.prod`, never manual container modifications

---

### Container Restart Persistence

**Lesson:** Docker container restarts lose runtime changes

**Impact:**
- Binary rebuilt inside container: ❌ Lost on restart
- CrAdapter manually copied: ❌ Lost on restart
- Files in image: ✅ Persistent

**Best Practice:**
- Always rebuild Docker image for code changes
- Never rely on `docker exec` modifications for permanent changes
- Use volumes for logs and data, not binaries

---

## Docker Compose (Alternative)

For teams preferring `docker-compose.yml`:

```yaml
version: '3.8'
services:
  payload-manager:
    image: payload-manager:latest
    container_name: payload-manager
    restart: always
    network_mode: host
    devices:
      - /dev/bus/usb:/dev/bus/usb
    volumes:
      - /var/log/payload-manager:/var/log/payload-manager
    environment:
      - LOG_LEVEL=INFO
      - AIR_SIDE_IP=192.168.144.53
```

Run: `docker-compose up -d`

---

## Future Enhancements

**Considered for Phase 2:**
- **Health Checks:** Docker `HEALTHCHECK` directive (ping camera endpoint)
- **Multi-Architecture Images:** Build for ARM64 and x86_64 (development on x86)
- **Registry:** Push images to private Docker registry (centralized distribution)
- **CI/CD Integration:** GitHub Actions builds image on commit
- **Resource Monitoring:** Prometheus exporter for container metrics

---

## Related Decisions

- **ADR-001:** Three-Domain Architecture (explains Air-Side as independent service)
- **ADR-007:** Stateless Air-Side Service (enables fast container restarts)
- **ADR-014:** Auto-Reconnect Strategy (complements Docker auto-restart)

---

## References

- Deployment View: `docs/architecture/view-deployment.md` (Software deployment section)
- Docker Setup: `sbc/docs/DOCKER_SETUP.md`
- Fresh Install: `sbc/docs/FRESH_INSTALL_GUIDE.md`
- NVMe Migration: `docs/RaspberryPi5_SD_to_NVMe_Migration_Guide-V2.md`
- LESSONS_LEARNED.md: Build & Deployment section (Issue #33 details)
