# ADR-005: Cilium CNI with Multus Multi-Network Strategy

## Status
Accepted

## Date
2024-12-01

## Context
The RH OVE ecosystem requires advanced networking capabilities to support both container and VM workloads with enterprise-grade security, performance, and observability. Traditional iptables-based CNI solutions lack the performance and security features needed for modern hybrid workloads.

## Decision
We will implement **Cilium as the primary CNI** with **Multus for multi-network support**, providing eBPF-powered networking with advanced security and observability capabilities.

## Rationale

### Advantages of Cilium
1. **eBPF Performance**: Superior performance compared to iptables-based solutions
2. **Identity-Aware Security**: Security policies based on workload identity, not IP addresses
3. **L7 Security**: Application-layer security without sidecar proxies
4. **Service Mesh Capabilities**: Built-in service mesh functionality
5. **Red Hat Certification**: Certified CNI plugin for OpenShift
6. **Hubble Observability**: Deep network visibility and monitoring
7. **Transparent Encryption**: Built-in WireGuard and IPsec support

### Advantages of Multus Integration
1. **Multi-Network Support**: Attach multiple network interfaces to VMs
2. **Legacy Network Integration**: Support for existing VLAN-based networks
3. **Performance Networks**: SR-IOV for high-performance workloads
4. **Network Segmentation**: Separate management, storage, and data networks

### Alternatives Considered

#### 1. OVN-Kubernetes (OpenShift Default)
- **Pros**: Native OpenShift integration, mature
- **Cons**: Limited eBPF features, performance overhead
- **Rejected**: Cilium provides superior performance and security

#### 2. Calico
- **Pros**: Strong network policies, eBPF support
- **Cons**: No built-in service mesh, complex multi-network setup
- **Rejected**: Cilium offers better integrated solution

#### 3. Flannel
- **Pros**: Simple, lightweight
- **Cons**: Limited security features, no eBPF support
- **Rejected**: Insufficient for enterprise requirements

## Implementation Details

### Cilium Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cilium-config
  namespace: kube-system
data:
  # Enable Cilium features
  enable-ipv4: "true"
  enable-ipv6: "false"
  
  # eBPF configuration
  enable-bpf-masquerade: "true"
  enable-host-reachable-services: "true"
  
  # Security features
  enable-l7-proxy: "true"
  enable-policy: "default"
  policy-enforcement-mode: "default"
  
  # Service mesh capabilities
  enable-envoy-config: "true"
  
  # Encryption
  enable-wireguard: "true"
  wireguard-userspace-fallback: "true"
  
  # Observability
  enable-hubble: "true"
  hubble-listen-address: ":4244"
  hubble-metrics-server: ":9091"
  hubble-metrics: |
    dns:query;ignoreAAAA
    drop
    tcp
    flow
    icmp
    http
  
  # Performance optimizations
  enable-bandwidth-manager: "true"
  enable-local-redirect-policy: "true"
  kube-proxy-replacement: "strict"
```

### Multus Installation
```yaml
apiVersion: operator.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  additionalNetworks:
  - name: management-network
    namespace: default
    type: Raw
    rawCNIConfig: |
      {
        "cniVersion": "0.3.1",
        "name": "management-network",
        "type": "macvlan",
        "master": "ens192",
        "mode": "bridge",
        "ipam": {
          "type": "static"
        }
      }
```

### Network Attachment Definitions
```yaml
# Management Network
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: management-net
  namespace: vm-infrastructure
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "management-net",
      "type": "macvlan",
      "master": "ens192",
      "mode": "bridge",
      "ipam": {
        "type": "static",
        "addresses": [
          {
            "address": "192.168.100.0/24",
            "gateway": "192.168.100.1"
          }
        ]
      }
    }
---
# High-Performance SR-IOV Network
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: sriov-net
  namespace: vm-production
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "sriov-net",
      "type": "sriov",
      "deviceID": "1017",
      "vf": 0,
      "ipam": {
        "type": "static"
      }
    }
```

### Identity-Aware Network Policies
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: web-to-database-policy
  namespace: app-web-prod
spec:
  endpointSelector:
    matchLabels:
      app: web-frontend
  egress:
  - toEndpoints:
    - matchLabels:
        app: database
        environment: production
    toPorts:
    - ports:
      - port: "5432"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/health"
```

### L7 Security Policies
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-security-policy
  namespace: app-api-prod
spec:
  endpointSelector:
    matchLabels:
      app: api-server
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: web-frontend
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/.*"
        - method: "POST"
          path: "/api/v1/users"
          headers:
          - "Content-Type: application/json"
```

### VM Multi-Network Configuration
```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: multi-network-vm
  namespace: vm-infrastructure
  annotations:
    k8s.v1.cni.cncf.io/networks: |
      [
        {
          "name": "management-net",
          "ips": ["192.168.100.10/24"]
        },
        {
          "name": "storage-net",
          "ips": ["10.0.1.10/24"]
        }
      ]
spec:
  running: true
  template:
    spec:
      domain:
        devices:
          interfaces:
          - name: default
            masquerade: {}
          - name: management
            bridge: {}
          - name: storage
            bridge: {}
      networks:
      - name: default
        pod: {}
      - name: management
        multus:
          networkName: management-net
      - name: storage
        multus:
          networkName: storage-net
```

## Security Implementation

### Transparent Encryption
```yaml
# WireGuard encryption configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: cilium-config
  namespace: kube-system
data:
  enable-wireguard: "true"
  wireguard-userspace-fallback: "true"
  encryption-node: "true"
```

### Zero Trust Network Policies
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny-all
  namespace: app-web-prod
spec:
  endpointSelector: {}
  ingress: []
  egress:
  # Allow DNS
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: kube-system
        k8s:k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
```

## Observability with Hubble

### Hubble Relay Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hubble-config
  namespace: kube-system
data:
  config.yaml: |
    server:
      address: 0.0.0.0:4245
    relay:
      address: hubble-relay.kube-system.svc.cluster.local:80
    tls:
      enabled: false
```

### Network Flow Monitoring
```bash
# Monitor network flows
hubble observe --namespace app-web-prod

# Check policy violations
hubble observe --verdict DENIED

# Monitor specific VM traffic
hubble observe --pod vm-database-xxx
```

## Performance Optimization

### eBPF Host Routing
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cilium-config
  namespace: kube-system
data:
  enable-host-routing: "true"
  enable-external-ips: "true"
  enable-node-port: "true"
  enable-host-port: "true"
```

### Bandwidth Management
```yaml
apiVersion: cilium.io/v2
kind: CiliumBandwidthPolicy
metadata:
  name: bandwidth-limit
  namespace: app-web-prod
spec:
  endpointSelector:
    matchLabels:
      app: web-frontend
  egress:
  - bandwidth: "100M"
  - bandwidth: "1G"
    dscp: 46  # High priority traffic
```

## Consequences

### Positive
- **Superior Performance**: eBPF provides 10-100x better performance than iptables
- **Enhanced Security**: Identity-aware policies and L7 security without sidecars
- **Deep Observability**: Hubble provides comprehensive network visibility
- **Future-Proof**: eBPF is the future of Linux networking
- **Multi-Network Support**: Seamless integration with legacy and high-performance networks

### Negative
- **Learning Curve**: Teams need to learn eBPF concepts and Cilium specifics
- **Debugging Complexity**: eBPF programs can be harder to debug than traditional networking
- **Resource Requirements**: Higher memory usage compared to simpler CNI solutions
- **Compatibility Concerns**: Some legacy applications may need network policy adjustments

## Migration Strategy

### Phase 1: Preparation
1. Audit existing network policies and requirements
2. Set up test clusters with Cilium/Multus
3. Train operations team on eBPF and Cilium concepts

### Phase 2: Non-Production Deployment
1. Deploy Cilium in development and staging clusters
2. Migrate network policies to Cilium format
3. Implement Hubble monitoring and alerting

### Phase 3: Production Migration
1. Schedule maintenance window for CNI migration
2. Deploy Cilium with careful monitoring
3. Gradually enable advanced features (encryption, L7 policies)

### Phase 4: Advanced Features
1. Enable service mesh capabilities
2. Implement advanced security policies
3. Optimize performance settings based on workload patterns

## Monitoring and Alerting

### Key Metrics
- Network throughput per namespace/pod
- Policy enforcement latency
- eBPF program load and execution time
- Hubble flow processing rate
- Encryption overhead metrics

### Alerting Rules
```yaml
groups:
- name: cilium-alerts
  rules:
  - alert: CiliumAgentDown
    expr: up{job="cilium-agent"} == 0
    for: 5m
    labels:
      severity: critical
  - alert: NetworkPolicyViolation
    expr: increase(cilium_policy_verdicts_total{verdict="DENIED"}[5m]) > 10
    labels:
      severity: warning
```

This network architecture provides enterprise-grade performance, security, and observability for the RH OVE ecosystem while supporting both modern cloud-native applications and traditional VM workloads.
