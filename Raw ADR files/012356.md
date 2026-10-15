# ADR-001: Security Hardening for Media Server Stack

## Status
Proposed

## Context
The current media server implementation uses basic security measures but lacks enterprise-grade security controls. Analysis reveals several security gaps including plain-text secrets, missing container hardening, and incomplete network policies.

## Decision
Implement comprehensive security hardening across all services following defense-in-depth principles.

## Consequences

### Positive
- Reduced attack surface through container hardening
- Protection against container escape vulnerabilities
- Encrypted secrets management
- Audit trail for compliance
- Protection against lateral movement

### Negative
- Increased complexity in deployment
- Potential performance impact from security controls
- Additional operational overhead
- Learning curve for team members

## Implementation Details

### 1. Container Hardening
```yaml
x-security-hardened: &security-hardened
  security_opt:
    - no-new-privileges:true
    - apparmor:docker-default
    - seccomp:default
  cap_drop:
    - ALL
  cap_add:
    - CHOWN
    - SETUID
    - SETGID
    - DAC_OVERRIDE
  read_only: true
  tmpfs:
    - /tmp:noexec,nosuid,size=1G
    - /var/tmp:noexec,nosuid,size=1G
  user: "${PUID}:${PGID}"
```

### 2. Secrets Management
```yaml
secrets:
  db_password:
    external: true
    external_name: mediaserver_db_password
  jwt_secret:
    external: true
    external_name: mediaserver_jwt_secret
  vpn_private_key:
    file: ./secrets/vpn_private_key
    
services:
  postgres:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
```

### 3. Network Policies
```yaml
services:
  jellyfin:
    networks:
      frontend:
        aliases:
          - media-server
      backend:
        internal: true
    sysctls:
      - net.ipv4.ip_unprivileged_port_start=0
    labels:
      - "traefik.docker.network=frontend"
```

### 4. Runtime Security Monitoring
```yaml
falco:
  image: falcosecurity/falco:latest
  privileged: true
  volumes:
    - /var/run/docker.sock:/host/var/run/docker.sock
    - /proc:/host/proc:ro
    - /boot:/host/boot:ro
    - /lib/modules:/host/lib/modules:ro
    - /usr:/host/usr:ro
  command: 
    - /usr/bin/falco
    - -K 
    - /host/boot/config-$(uname -r)
    - -k 
    - https://download.falco.org/driver
```

### 5. Vulnerability Scanning Pipeline
```yaml
# In CI/CD pipeline
stages:
  - scan
  
scan-images:
  stage: scan
  script:
    - trivy image --severity HIGH,CRITICAL jellyfin/jellyfin:latest
    - trivy image --severity HIGH,CRITICAL lscr.io/linuxserver/sonarr:latest
    - grype dir:. --fail-on high
```

### 6. RBAC Implementation
```yaml
authelia:
  access_control:
    default_policy: deny
    rules:
      - domain: "*.media.local"
        policy: two_factor
        subject:
          - "group:media_users"
      - domain: "admin.media.local"
        policy: two_factor
        subject:
          - "group:administrators"
        resources:
          - "^/api/admin.*$"
```

## Rollout Plan

### Phase 1: Foundation (Week 1)
1. Implement Docker secrets
2. Create security baseline configuration
3. Set up vulnerability scanning

### Phase 2: Container Hardening (Week 2)
1. Apply security options to all containers
2. Implement read-only root filesystems
3. Configure tmpfs mounts

### Phase 3: Network Security (Week 3)
1. Implement network policies
2. Configure service isolation
3. Set up internal networks

### Phase 4: Monitoring (Week 4)
1. Deploy Falco for runtime security
2. Configure security alerts
3. Implement audit logging

## Validation Criteria
- All containers pass CIS Docker Benchmark
- No HIGH/CRITICAL vulnerabilities in production images
- Successful penetration test results
- Zero security incidents in 30-day period

## References
- CIS Docker Benchmark v1.4.0
- NIST Container Security Guide SP 800-190
- OWASP Container Security Top 10