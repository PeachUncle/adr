---
type: DRR
winner_id: per-service-yaml-files-with-shared-globals
created: 2025-12-23T18:43:47-08:00
content_hash: 69f236d73500ca68c2149e326fdcc019
---

# Per-Service YAML Configuration with Git-Based Deployment for SpeedData v0.3

## Context
SpeedData v0.3 requires configuration system for multi-machine deployment with:
- Channel-to-port mappings (relay input)
- Multicast endpoints (relay→stripchart/pivot communication)
- AVRO file rotation thresholds (time or size-based)
- Data retention policies (TTL or storage quota)
- Storage paths for AVRO files

**User Requirements:**
- Multi-machine deployment (relay, stripchart, pivot on separate hosts)
- No existing config management tooling (but open to lightweight solutions)
- Preference for per-service file approach (not monolithic)
- Format flexible (JSON, YAML, or TOML acceptable)
- Load-time configuration only (no hot-reload in v0.3)

**Critical Constraint:**
User has experience with git+rsync approach: "scales for the lab well and breaks hard for production at 10-100 field units." User explicitly accepts this trade-off for v0.3 lab/development deployment.

## Decision
**Selected Option:** per-service-yaml-files-with-shared-globals

**Adopt Per-Service YAML Files with Shared Globals + Git-Based Deployment**

**File Structure:**
```
config/
├── global.yaml          # Shared settings (multicast endpoints, storage paths)
├── relay.yaml           # Relay-specific (channels, ports, rotation, retention)
├── stripchart.yaml      # Stripchart-specific (websocket, decimation)
├── pivot.yaml           # Pivot-specific (API settings, limits)
└── deploy.sh            # Simple git+rsync deployment script
```

**Configuration Discovery:**
- CLI arg: `--config-dir /etc/speeddata/`
- ENV var: `SPEEDDATA_CONFIG_DIR`
- Default: `./config/`, `/etc/speeddata/`

**Deployment Mechanism:**
Simple bash script using git + rsync:
```bash
#!/bin/bash
# config/deploy.sh
git pull origin main
rsync -av config/ user@relay-host:/etc/speeddata/
rsync -av config/ user@stripchart-host:/etc/speeddata/
rsync -av config/ user@pivot-host:/etc/speeddata/
```

**Configuration Loading (Python):**
1. Load `global.yaml`
2. Load service-specific YAML (e.g., `relay.yaml`)
3. Merge: service-specific overrides global
4. Validate required fields on startup
5. Fail-fast if invalid configuration

## Rationale
**Why this approach won:**

1. **Matches User Preference:** Only hypothesis meeting "per-service file" requirement. Single YAML, JSON Schema, and TOML are all monolithic.

2. **Multi-Machine Friendly:** Each service only needs its config file + global, unlike monolithic approaches requiring full config on every machine.

3. **Separation of Concerns:** Service-specific settings isolated from shared infrastructure (multicast endpoints, storage paths).

4. **Proven Pattern:** Validated by Docker Compose multiple files + extends pattern. Industry-standard for distributed service configuration.

5. **Lightweight Config Management:** Git+rsync is minimal tooling (no Ansible/Chef/Puppet learning curve). User has direct experience with this approach.

6. **YAML Format:** Human-readable, supports comments (unlike JSON), widely familiar (matches user preference "feels like JSON or YAML").

7. **Config Drift Mitigation:** git provides version control and audit trail. Deployment script ensures atomic updates across machines.

**Trade-off Accepted:**

User explicitly stated: "scales for the lab well and breaks hard for production at 10-100 field units."

This is a **deliberate v0.3 choice** optimizing for lab/development deployment. The scaling limitation is known and accepted. For production field deployment (v0.4+), would need proper config management (Ansible, Kubernetes ConfigMaps, or centralized config server).

**Why alternatives rejected:**

- **Single YAML:** User said "assume multi-machine", requires shared filesystem (NFS) which adds deployment complexity
- **JSON Schema:** Monolithic file, doesn't match "per-service file" preference. No comments hurts readability.
- **TOML:** Monolithic file, user didn't request TOML format ("feels like JSON or YAML" - TOML not mentioned), requires custom interpolation logic

### Characteristic Space (C.16)
- Distributed configuration pattern (per-service files + shared global)
- YAML format (human-readable, comments supported)
- Git-based version control and deployment
- Rsync for file synchronization across machines
- Load-time configuration (no hot-reload)
- Merge logic (service-specific overrides global)
- Fail-fast validation on service startup
- CLI args and ENV var discovery
- Optimized for lab/development deployment (1-10 machines)
- Known scaling limit (breaks at 10-100+ production field units)

## Consequences
**Immediate Implementation Actions:**

1. **Create config directory structure:**
   ```
   mkdir -p config/agents
   touch config/{global,relay,stripchart,pivot}.yaml
   touch config/deploy.sh && chmod +x config/deploy.sh
   ```

2. **Implement global.yaml:**
   - Multicast endpoints (full_rate, decimated)
   - Shared storage path
   - Common defaults

3. **Implement service-specific YAML files:**
   - `relay.yaml`: channels array (name, port, schema), rotation/retention policies
   - `stripchart.yaml`: websocket port, decimation settings
   - `pivot.yaml`: API port, limits (max_channels, max_duration_minutes)

4. **Create Python config loader:**
   - `lib/python/speeddata_config.py` module
   - Load global + service-specific with merge logic
   - Validation on startup (fail-fast for missing required fields)
   - Support CLI args (`--config-dir`), ENV vars, defaults

5. **Update service startup:**
   - `relay/python/rowdog.py`: Read `relay.yaml` for channel-port mappings
   - `stripchart/server/server.js`: Read `stripchart.yaml` for multicast subscribe
   - `pivot/python/api_server.py`: Read `pivot.yaml` for API settings

6. **Create deployment script:**
   - `config/deploy.sh`: git pull + rsync to target hosts
   - Document SSH key setup, target host configuration
   - Add to README with deployment instructions

**Scaling Limitations (KNOWN):**

- **Lab/Development (1-10 machines):** ✅ Works well
- **Production Field Deployment (10-100+ units):** ❌ Breaks hard
  - Manual rsync doesn't scale
  - No centralized management
  - Config drift detection but not prevention
  - No rollback mechanism beyond git revert + re-deploy

**Future Evolution Path (v0.4+):**

When scaling to production field deployment:
1. **Option A:** Migrate to Ansible/SaltStack/Puppet for config management
2. **Option B:** Containerize with Kubernetes ConfigMaps
3. **Option C:** Centralized config server (Consul, etcd) with service discovery
4. **Option D:** Hybrid - keep YAML files but deploy via CI/CD pipeline

**Technical Debt Incurred:**

- Git+rsync deployment script is fragile (no error handling, atomic updates, rollback)
- No config validation before deployment (services fail at startup, not at deploy time)
- No diff visualization (what changed between config versions?)
- SSH key management not addressed (manual setup required)

**Constraints Accepted:**

- v0.3 scope: lab/development deployment only
- Load-time configuration only (changes require service restart)
- No live registration (channel-port mappings static)
- Global.yaml must be synchronized (deployment script responsibility)

**Success Criteria:**

- Services successfully load config from YAML files
- Multi-machine deployment works via deploy.sh script
- Config changes propagate to all services after deployment
- Multicast endpoints consistent across relay (publish) and stripchart/pivot (subscribe)
