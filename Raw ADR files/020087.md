# ADR-003: Agent Architecture for Wayfinder

## Status

**Proposed** - Awaiting review and discussion

## Context

The Wayfinder 3-Pod architecture includes a dedicated **Agent Pod** for each department, but the current demo has no actual agents implemented. As government increasingly adopts AI and automation, we need a coherent strategy for:

1. What agents exist and what they do
2. How they're governed (policies, permissions, accountability)
3. How they're discovered (via Wayfinder itself)
4. How they interact with services and data
5. Government-specific considerations (accountability, transparency, oversight)

This ADR proposes a comprehensive agent framework for the Wayfinder demo and production systems.

---

## Decision

We will implement a first-class **Agent** entity type in Wayfinder with clear taxonomy, governance model, and lifecycle management.

---

## Agent Taxonomy

### 1. Discovery Agents
**Purpose:** Help humans find information across government

| Agent | Owner | Function | Services Consumed |
|-------|-------|----------|-------------------|
| `wayfinder-discovery` | DSO | Natural language search across Wayfinder knowledge base | OpenSearch, Neptune (production) |
| `slack-assistant` | DSO | Slack bot answering queries about services, teams, patterns | Wayfinder API |
| `teams-assistant` | DSO | MS Teams equivalent of Slack assistant | Wayfinder API |

### 2. Operations Agents
**Purpose:** Automate routine operational tasks

| Agent | Owner | Function | Services Consumed |
|-------|-------|----------|-------------------|
| `deploy-bot` | Per team | Automated deployments to approved environments | Gov Cloud Platform, GitHub Actions |
| `monitor-bot` | Per team | Watches service health, alerts on anomalies | Monitoring Platform, PagerDuty |
| `docs-sync-bot` | Per team | Keeps API docs in sync with code | GitHub, Confluence, Data Pod |
| `dependency-checker` | DSO | Scans for outdated/vulnerable dependencies | GitHub, NCSC advisories |

### 3. Compliance Agents
**Purpose:** Ensure adherence to policies and standards

| Agent | Owner | Function | Services Consumed |
|-------|-------|----------|-------------------|
| `accessibility-checker` | DSO | Automated WCAG 2.1 AA testing | Service endpoints, axe-core |
| `security-scanner` | DSO | Continuous security posture checking | NCSC feeds, vulnerability DBs |
| `policy-enforcer` | DSO | Validates services against active policies | Policy API, Service registry |
| `carbon-tracker` | DSO | Monitors digital carbon footprint per service | Cloud metrics, Carbon API |

### 4. Data Agents
**Purpose:** Manage data flows and synchronisation

| Agent | Owner | Function | Services Consumed |
|-------|-------|----------|-------------------|
| `pod-sync-agent` | Per dept | Syncs Pod data to central discovery layer | Solid Pods, Neptune, OpenSearch |
| `data-quality-agent` | Per dept | Validates data freshness and consistency | Data Pods, validation rules |
| `consent-tracker` | DCS | Monitors consent status for citizen data | Consent Management Platform |

### 5. Intelligence Agents
**Purpose:** AI-powered analysis and recommendations

| Agent | Owner | Function | Services Consumed |
|-------|-------|----------|-------------------|
| `pattern-suggester` | DSO | Recommends patterns based on service characteristics | Pattern library, Bedrock/Claude |
| `impact-analyser` | DSO | Analyses impact of proposed changes | Dependency graph, Neptune |
| `knowledge-extractor` | Per dept | Extracts entities from internal docs (sovereign AI) | Dept docs, local LLM |

### 6. Support Services Agents
**Purpose:** Support core departmental operations beyond digital teams

These agents serve business functions across government that depend on digital infrastructure but aren't purely technical. They help comms teams, private offices, caseworkers, and policy teams.

| Agent | Owner | Function | Services Consumed |
|-------|-------|----------|-------------------|
| `ministerial-correspondence-triage` | Per dept (Private Office) | Triages incoming ministerial emails by urgency, topic, and routing | Email gateway, Document classification API, Bedrock |
| `pq-assistant` | Per dept (Parliamentary team) | Routes Parliamentary Questions, suggests draft responses from knowledge base | PQ management system, Wayfinder, Hansard API |
| `foi-classifier` | Per dept (FOI team) | Classifies FOI requests, estimates complexity, routes to appropriate team | FOI case system, Document store, Classification API |
| `casework-categoriser` | DCS, RTS, VLA | Categorises citizen casework, suggests priority and relevant guidance | Case management system, Policy KB, Bedrock |
| `briefing-assembler` | Per dept (Private Office) | Assembles ministerial briefings from multiple sources | Document store, Diary system, Wayfinder |
| `translation-agent` | DSO (shared service) | Translates content to Welsh/other languages, maintains consistency | Translation memory, Style guide API |
| `media-monitor` | Per dept (Comms) | Monitors media mentions, summarises relevant coverage | News APIs, Social media APIs, Bedrock |
| `consultation-analyser` | Per dept (Policy) | Analyses public consultation responses, identifies themes | Consultation platform, NLP services, Bedrock |

**Key characteristics of Support Services Agents:**
- Serve non-digital teams (comms, policy, private office, casework)
- Higher sensitivity due to ministerial/citizen content
- Often require human-in-the-loop before action
- Bridge between operational systems and AI capabilities
- May handle OFFICIAL-SENSITIVE content requiring additional controls

---

## Agent Data Model

### Core Schema

```typescript
/**
 * Agent identity stored in the Agent Pod
 */
export interface Agent {
  id: string;                      // e.g., "deploy-bot-granite"
  webId: string;                   // Solid WebID for the agent
  name: string;                    // Human-readable name
  type: AgentType;

  // Ownership
  departmentId: string;            // Owning department
  teamId: string;                  // Owning team

  // Identity & Trust
  description: string;             // What this agent does
  version: string;                 // Agent version
  sourceRepository?: string;       // Where agent code lives

  // Capabilities
  capabilities: AgentCapability[]; // What this agent can do
  consumesServices: string[];      // Service IDs this agent uses

  // Permissions (scoped)
  permissions: AgentPermission[];  // Fine-grained permissions

  // Status
  status: AgentStatus;
  createdAt: string;
  lastActiveAt: string;

  // Lifecycle
  approvedBy: string;              // Who approved this agent
  reviewDate: string;              // Next review date

  // Tags for search
  tags: string[];
}

export type AgentType =
  | 'discovery'      // Helps find information
  | 'operations'     // Automates operations
  | 'compliance'     // Enforces policies
  | 'data'           // Manages data flows
  | 'intelligence'   // AI-powered analysis
  | 'support';       // Departmental operations (comms, casework, private office)

export type AgentStatus =
  | 'active'         // Running in production
  | 'testing'        // In testing/staging
  | 'suspended'      // Temporarily disabled
  | 'retired';       // No longer active

export interface AgentCapability {
  name: string;                    // e.g., "deploy_to_staging"
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
  requiresApproval: boolean;       // Needs human approval each time?
}

export interface AgentPermission {
  resource: string;                // Path pattern, e.g., "/deployments/*"
  actions: ('read' | 'write' | 'delete' | 'execute')[];
  conditions?: PermissionCondition[];
}

export interface PermissionCondition {
  type: 'time_window' | 'approval_required' | 'rate_limit' | 'environment';
  value: string;
}
```

### Relationships

```typescript
export type AgentRelationshipType =
  | 'consumes'       // agent -> service
  | 'owned-by'       // agent -> team
  | 'governed-by'    // agent -> policy
  | 'delegates-to'   // agent -> agent (chain of delegation)
  | 'reports-to';    // agent -> team (accountability)
```

### Audit Log Schema

```typescript
/**
 * Every agent action is logged for accountability
 */
export interface AgentAuditEntry {
  id: string;
  agentId: string;
  agentWebId: string;

  // What happened
  action: string;                  // e.g., "deployed", "read", "modified"
  resource: string;                // What was affected
  timestamp: string;

  // Context
  triggeredBy: 'schedule' | 'event' | 'human_request';
  requestedBy?: string;            // If human-triggered, who asked

  // Outcome
  outcome: 'success' | 'failure' | 'blocked';
  reason?: string;                 // Especially for blocked actions

  // Evidence
  inputHash?: string;              // Hash of inputs for reproducibility
  outputHash?: string;             // Hash of outputs
}
```

---

## Agent Governance Policies

### Policy: Agent Registration and Approval

All agents must be:
1. **Registered** in the Agent Pod with full metadata
2. **Approved** by a designated team lead before activation
3. **Reviewed** at least annually or upon significant capability change
4. **Auditable** with complete action logs

### Policy: Principle of Least Privilege

- Agents receive minimum permissions needed for their function
- Permissions are scoped to specific resources and actions
- High-risk actions (write, delete, execute) require explicit grants
- Production access requires separate approval from dev/staging

### Policy: Human Oversight Requirements

| Risk Level | Oversight Requirement |
|------------|----------------------|
| Low | Audit log review weekly |
| Medium | Approval workflow for batched actions |
| High | Per-action human approval |
| Critical | Dual-approval with senior oversight |

### Policy: Cross-Boundary Operations

Agents operating across department boundaries must:
1. Have explicit grants from both source and target departments
2. Use the Data Sharing Framework for any citizen data
3. Log all cross-boundary actions with both departments
4. Respect the most restrictive policy of either department

### Policy: Transparency and Explainability

- All agents must describe their purpose in plain English
- AI-powered agents must explain their reasoning when requested
- Citizens can request disclosure of agents that processed their data
- Agent registrations are publicly discoverable in Wayfinder

### Policy: Incident Response

- Agents can be suspended instantly by any owner with appropriate permissions
- Suspended agents cannot be reactivated without review
- Incidents trigger automatic review of similar agents
- Post-incident reports are published to Wayfinder

---

## Agent Pod Implementation

### Pod Structure

```
/agents/{department}/
├── /agents/
│   ├── deploy-bot.ttl           # Agent identity
│   ├── monitor-bot.ttl
│   └── docs-sync-bot.ttl
├── /capabilities/
│   ├── deploy-bot-caps.ttl      # What it can do
│   └── monitor-bot-caps.ttl
├── /credentials/
│   ├── deploy-bot-tokens.ttl    # Scoped credentials (encrypted)
│   └── monitor-bot-tokens.ttl
├── /audit/
│   ├── 2026-01/                 # Monthly audit logs
│   │   ├── deploy-bot.jsonl
│   │   └── monitor-bot.jsonl
│   └── 2026-02/
└── /approvals/
    ├── deploy-bot-approval.ttl  # Approval record
    └── reviews/
        └── 2026-review.ttl
```

### RDF Vocabulary

```turtle
@prefix wfagent: <https://wayfinder.gov.example/vocab/agent#>.

wfagent:Agent a rdfs:Class ;
  rdfs:comment "An autonomous entity that acts on behalf of a team".

wfagent:hasCapability a rdf:Property ;
  rdfs:domain wfagent:Agent ;
  rdfs:range wfagent:Capability .

wfagent:consumesService a rdf:Property ;
  rdfs:domain wfagent:Agent ;
  rdfs:range wf:Service .

wfagent:ownedBy a rdf:Property ;
  rdfs:domain wfagent:Agent ;
  rdfs:range wf:Team .

wfagent:governedBy a rdf:Property ;
  rdfs:domain wfagent:Agent ;
  rdfs:range wf:Policy .
```

---

## Wayfinder's Own Agents

Wayfinder itself operates several agents that must follow the same governance model:

### 1. Discovery Agent (`wayfinder-discovery`)

**Purpose:** Powers the natural language query interface in both web UI and Slack

**Current Implementation:** The `AgentQueryInterface` component and Slack bot's `processSlackQuery()` function

**Governance:**
- Owned by DSO (Digital Standards Office)
- Read-only access to all Pods
- No citizen data access (aggregated metadata only)
- Public audit logs

### 2. Pod Sync Agent (`wayfinder-pod-sync`)

**Purpose:** Synchronises data from department Pods to the central discovery layer

**Implementation Notes:**
- Event-driven (listens for Pod changes via webhooks)
- Falls back to polling if webhooks unavailable
- Read-only from Pods, write to central Neptune/OpenSearch

**Governance:**
- Per-department instances (e.g., `wayfinder-pod-sync-dcs`)
- Each department approves their instance
- Central DSO coordinates overall sync

### 3. Knowledge Extractor (`wayfinder-knowledge-extractor`)

**Purpose:** (Production vision) Extracts entities from department documentation

**Key Design:**
- Runs WITHIN department boundary (sovereign AI)
- Outputs reviewed by humans before publishing
- Wayfinder provides the reference implementation
- Departments can fork and customise

---

## Discovery: Finding Agents in Wayfinder

### Agent as First-Class Entity

Agents appear alongside services, teams, patterns, and policies in Wayfinder:

```typescript
// Extended query intents
export type QueryIntent =
  | ... // existing intents
  | 'find_agent'        // "what agents does RTS run"
  | 'list_agents'       // "show all compliance agents"
  | 'agent_for_service' // "what agents maintain the Identity API"
```

### Example Queries

| Query | Response |
|-------|----------|
| "What agents does DSO run?" | Lists all DSO agents with purposes |
| "Who deployed the Tax API recently?" | Shows `deploy-bot-rts` with audit link |
| "What agents consume the Identity API?" | Lists agents with `consumesServices` including that API |
| "Show me compliance agents" | Lists all agents where `type === 'compliance'` |

### Slack Integration

The Slack bot should answer agent queries:

```
User: "@wayfinder what agents run the deployments for Citizen Portal?"

Bot: *Citizen Portal Deployments*
Managed by `deploy-bot-puffin` (Puffin Team, DCS)

- Type: operations
- Last active: 2 hours ago
- Status: active
- Permissions: deploy to staging, deploy to prod (approval required)

View full details: [Agent Profile] | [Audit Log]
```

---

## Cloning and Instancing

### Template Agents

Common agent patterns can be templated for reuse:

```typescript
export interface AgentTemplate {
  id: string;                      // e.g., "deploy-bot-template"
  name: string;
  type: AgentType;
  description: string;

  // Template capabilities
  capabilities: AgentCapability[];
  defaultPermissions: AgentPermission[];

  // Customisation points
  configurableFields: string[];    // What teams can customise

  // Provenance
  maintainer: string;              // Who maintains this template
  version: string;
}
```

### Instantiation Flow

1. Team selects a template (e.g., "Standard Deploy Bot")
2. Team customises allowed fields (environment, service scope)
3. Team lead approves the instance
4. Instance is registered in team's Agent Pod
5. Instance inherits template updates (optional)

### Multi-Environment Instances

Same agent can have environment-specific instances:

```
deploy-bot-granite-dev      # Dev environment
deploy-bot-granite-staging  # Staging environment
deploy-bot-granite-prod     # Production (stricter permissions)
```

Each environment instance:
- Has its own WebID
- Has environment-specific permissions
- Logs to the same audit trail (tagged by environment)

---

## Government-Specific Considerations

### 1. Accountability Chain

Every agent action must have a clear accountability chain:

```
Minister → SRO → Delivery Manager → Team Lead → Agent
```

If an agent causes harm, the chain is traversed for accountability.

### 2. Freedom of Information

Agent registrations and audit summaries may be subject to FOI requests. Design assumes:
- Agent purposes are public
- Aggregated action counts are disclosable
- Specific citizen data access is protected

### 3. Procurement and Vendor Lock-in

Agents using third-party AI services must:
- Document the service provider
- Have exit strategy if provider changes
- Prefer open-source/local alternatives where security-appropriate

### 4. Security Accreditation

Agents inherit the security accreditation of their host environment:
- Agents running on OFFICIAL systems have OFFICIAL clearance
- Agents needing SECRET access require separate accreditation
- Cross-boundary agents need accreditation for both environments

### 5. Continuity of Service

Agents must not be single points of failure:
- Document agent dependencies clearly
- Have fallback procedures if agent fails
- Human override always available

### 6. Ministerial Visibility

Dashboard for ministerial oversight showing:
- Active agents by department
- High-risk actions requiring approval
- Incidents and suspensions
- Compliance posture

---

## Demo Implementation Plan

### Phase 1: Data Model & Schema (2 days)

1. Add `Agent` and `AgentAuditEntry` to `schema.ts`
2. Create `agents.ts` with demo agent data
3. Add agent relationships to graph

### Phase 2: Agent Pod Structure (1 day)

1. Define Agent Pod seed data for demo Solid server
2. Create sample agent profiles in Turtle format
3. Add agent audit log examples

### Phase 3: Discovery Integration (2 days)

1. Add agent query intents to query engine
2. Extend Slack bot to answer agent queries
3. Add agents to knowledge graph visualisation

### Phase 4: UI Pages (2 days)

1. Create `/agents` listing page
2. Create `/agents/[id]` detail page
3. Add agent information to service and team pages
4. Show "maintained by agents" alongside "maintained by people"

### Phase 5: Governance Display (1 day)

1. Show policies governing each agent
2. Display permissions in human-readable form
3. Link to (mock) audit logs

---

## Demo Agent Seed Data

### Wayfinder Discovery Agent

```typescript
{
  id: 'wayfinder-discovery',
  name: 'Wayfinder Discovery Agent',
  type: 'discovery',
  departmentId: 'dso',
  teamId: 'granite-team',
  description: 'Powers natural language search across the Wayfinder knowledge base. Helps government teams find services, patterns, teams, and policies.',
  version: '1.0.0',
  sourceRepository: 'https://github.com/cabinet-office/wayfinder',
  capabilities: [
    { name: 'query_services', description: 'Search service catalogue', riskLevel: 'low', requiresApproval: false },
    { name: 'query_people', description: 'Find team contacts', riskLevel: 'low', requiresApproval: false },
    { name: 'query_patterns', description: 'Search pattern library', riskLevel: 'low', requiresApproval: false },
  ],
  consumesServices: ['neptune-graph', 'opensearch-index'],
  permissions: [
    { resource: '/services/*', actions: ['read'] },
    { resource: '/teams/*', actions: ['read'] },
    { resource: '/patterns/*', actions: ['read'] },
    { resource: '/policies/*', actions: ['read'] },
  ],
  status: 'active',
  createdAt: '2026-01-01',
  lastActiveAt: '2026-01-12',
  approvedBy: 'dso-sro',
  reviewDate: '2027-01-01',
  tags: ['discovery', 'search', 'nlp', 'wayfinder'],
}
```

### Deploy Bot (RTS Example)

```typescript
{
  id: 'deploy-bot-revenue',
  name: 'Revenue Platform Deploy Bot',
  type: 'operations',
  departmentId: 'rts',
  teamId: 'revenue-platform',
  description: 'Automated deployment agent for Revenue Platform services. Deploys to staging automatically, production requires approval.',
  version: '2.1.0',
  sourceRepository: 'https://github.com/rts-digital/deploy-bot',
  capabilities: [
    { name: 'deploy_staging', description: 'Deploy to staging environment', riskLevel: 'medium', requiresApproval: false },
    { name: 'deploy_production', description: 'Deploy to production', riskLevel: 'high', requiresApproval: true },
    { name: 'rollback', description: 'Rollback to previous version', riskLevel: 'high', requiresApproval: true },
  ],
  consumesServices: ['gov-cloud-platform', 'github-actions', 'slack-notifications'],
  permissions: [
    { resource: '/deployments/staging/*', actions: ['read', 'write', 'execute'] },
    { resource: '/deployments/production/*', actions: ['read', 'write', 'execute'], conditions: [{ type: 'approval_required', value: 'team-lead' }] },
  ],
  status: 'active',
  createdAt: '2025-06-15',
  lastActiveAt: '2026-01-11',
  approvedBy: 'rts-delivery-manager',
  reviewDate: '2026-06-15',
  tags: ['deployment', 'ci-cd', 'automation', 'revenue'],
}
```

### Policy Enforcer (DSO)

```typescript
{
  id: 'policy-enforcer',
  name: 'Cross-Government Policy Enforcer',
  type: 'compliance',
  departmentId: 'dso',
  teamId: 'governance-team',
  description: 'Validates that services comply with active cross-government policies. Flags non-compliance for human review.',
  version: '1.2.0',
  capabilities: [
    { name: 'scan_services', description: 'Scan services for policy compliance', riskLevel: 'low', requiresApproval: false },
    { name: 'flag_violation', description: 'Flag potential policy violations', riskLevel: 'medium', requiresApproval: false },
    { name: 'block_deployment', description: 'Block non-compliant deployments', riskLevel: 'high', requiresApproval: true },
  ],
  consumesServices: ['wayfinder-api', 'policy-registry', 'notification-service'],
  permissions: [
    { resource: '/services/*', actions: ['read'] },
    { resource: '/policies/*', actions: ['read'] },
    { resource: '/compliance-flags/*', actions: ['read', 'write'] },
  ],
  status: 'active',
  createdAt: '2025-09-01',
  lastActiveAt: '2026-01-12',
  approvedBy: 'dso-sro',
  reviewDate: '2026-09-01',
  tags: ['compliance', 'policy', 'governance', 'enforcement'],
}
```

### Ministerial Correspondence Triage (DCS Example)

```typescript
{
  id: 'ministerial-triage-dcs',
  name: 'DCS Ministerial Correspondence Triage',
  type: 'support',
  departmentId: 'dcs',
  teamId: 'private-office',
  description: 'Triages incoming ministerial correspondence for the Department of Citizen Support. Classifies by urgency (routine, priority, urgent, immediate), topic area, and suggests routing to appropriate policy team. All classifications reviewed by Private Office staff before action.',
  version: '1.0.0',
  capabilities: [
    { name: 'classify_correspondence', description: 'Classify incoming emails by urgency and topic', riskLevel: 'medium', requiresApproval: false },
    { name: 'suggest_routing', description: 'Suggest which team should handle', riskLevel: 'low', requiresApproval: false },
    { name: 'draft_acknowledgement', description: 'Draft acknowledgement response', riskLevel: 'medium', requiresApproval: true },
    { name: 'flag_vip', description: 'Flag correspondence from MPs, peers, senior officials', riskLevel: 'low', requiresApproval: false },
  ],
  consumesServices: ['email-gateway', 'document-classification-api', 'bedrock-claude', 'staff-directory'],
  permissions: [
    { resource: '/correspondence/inbox/*', actions: ['read'] },
    { resource: '/correspondence/classification/*', actions: ['read', 'write'] },
    { resource: '/correspondence/drafts/*', actions: ['write'], conditions: [{ type: 'approval_required', value: 'private-office-staff' }] },
  ],
  status: 'active',
  createdAt: '2026-02-01',
  lastActiveAt: '2026-01-12',
  approvedBy: 'dcs-perm-sec-office',
  reviewDate: '2026-08-01',
  tags: ['ministerial', 'correspondence', 'triage', 'private-office', 'comms'],
}
```

**Note on Support Services Agents:** These agents handle sensitive content (ministerial correspondence, citizen casework, FOI requests) and require:
- Higher oversight thresholds
- More frequent reviews (6-monthly rather than annual)
- Approval from Permanent Secretary's office or equivalent
- Clear data handling controls for OFFICIAL-SENSITIVE content

---

## Consequences

### Positive

1. **First-class agent identity** - Agents are discoverable and accountable
2. **Clear governance** - Policies apply to agents as they do to services
3. **Transparency** - Citizens and oversight bodies can see what agents exist
4. **Scalability** - Template/instance model supports government-wide adoption
5. **Future-proofing** - As AI adoption grows, the framework is ready

### Negative

1. **Complexity** - Additional entity type to manage
2. **Overhead** - Agent registration and review processes add friction
3. **Cultural shift** - Teams must think about agent identity, not just service accounts

### Neutral

1. **Standards evolution** - May need to adapt as AI governance standards mature
2. **Cross-government alignment** - Other initiatives (CDDO, GDS) may have overlapping work

---

## References

- [3-Pod Architecture](/architecture)
- [NCSC Guidance on AI Security](https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development)
- [CDDO AI Assurance Framework](https://www.gov.uk/government/publications/ai-assurance-techniques)
- [W3C Solid Specification](https://solidproject.org/TR/)

---

## Appendix: Agent Governance Policy (Draft)

### AG-001: Agent Registration

All autonomous agents operating within government digital infrastructure must be registered in the appropriate Agent Pod before activation.

**Required information:**
- Unique identifier and human-readable name
- Owning department and team
- Clear description of purpose
- List of capabilities with risk ratings
- Services consumed
- Approval chain

### AG-002: Agent Permissions

Agents must operate under the principle of least privilege.

**Rules:**
1. Permissions must be scoped to specific resources
2. Write permissions require explicit justification
3. Cross-department access requires bilateral approval
4. Production access requires separate approval from dev/staging

### AG-003: Agent Audit

All agent actions must be logged to the Agent Pod audit trail.

**Retention:**
- Routine actions: 1 year
- High-risk actions: 7 years
- Incidents: Permanent

### AG-004: Agent Review

Agents must be reviewed periodically.

**Schedule:**
- Low-risk agents: Annually
- Medium-risk agents: 6 months
- High-risk agents: Quarterly
- Following any incident: Immediate

### AG-005: Agent Suspension

Agents may be suspended immediately by:
- The owning team lead
- Department security officer
- Central DSO in emergencies

Suspension disables all agent permissions until review.
