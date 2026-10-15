# ADR-013: Archon Plugin System (Scope, Types, Permissions, Jira Integration)

Status: Accepted
Date: 2025-08-24
Owners: Archon Core

## Context

Archon’s core value is a Git-versioned, hierarchical configuration model. To unlock broad use cases (labs, museums, test benches, IT asset configs), we need a plugin system that goes well beyond “imports.” Mature ecosystems show that successful plugins offer:

- **UI contribution points** (commands, menus, custom views) so features feel native.  [oai_citation:0‡Visual Studio Code](https://code.visualstudio.com/api/references/contribution-points?utm_source=chatgpt.com)
- **Typed plugin categories** (e.g., panels, data sources, apps) so developers know where to hook in.  [oai_citation:1‡Grafana Labs](https://grafana.com/developers/plugin-tools/key-concepts/plugin-types-usage?utm_source=chatgpt.com)
- **Least-privilege sandboxes/permissions** for safe extensibility. (Reference models like Figma’s plugins.)  [oai_citation:2‡Figma](https://www.figma.com/plugin-docs/working-in-dev-mode/?utm_source=chatgpt.com) [oai_citation:3‡Figma Help Center](https://help.figma.com/hc/en-us/articles/16354660649495-Security-disclosure-principles?utm_source=chatgpt.com)

## Decision

Introduce a **first-class plugin platform** with the following **types**, **permissions**, and **events**. Plugins are JS/TS modules executed in a sandboxed worker by default. (Native/Go plugins may be considered later.)

### A) Plugin Types (v1)

We define explicit “where/how” plugins extend Archon:

1. **Importer** – create nodes from external bytes/strings.  
2. **Exporter** – serialize nodes/subtrees/snapshots into external formats.  
3. **Transformer** – mutate a working set (bulk edits, key normalization).  
4. **Validator** – read-only checks; can block commit/snapshot with errors/warnings.  
5. **Panel** – visual UI panel (e.g., diagrams, BOM viewers) mounted in Archon’s side panel or main area.  
6. **Provider** – connector to external systems (read/write), e.g., CMDB/ERP/Jira; exposes pull/push operations.  
7. **AttachmentProcessor** – analyze/transform attachments (OCR, metadata extraction).  
8. **ConflictResolver** – supply semantic merge strategies for specific fields or node kinds.  
9. **SearchIndexer** – add tokenizers/normalizers for domain text to the local SQLite index.  
10. **UIContrib** – contribute commands, menus, keybindings, and small contextual views.

These categories map to proven patterns (VS Code: commands/views; Grafana: panels/data sources/apps), giving structure without locking us in.  [oai_citation:4‡Visual Studio Code](https://code.visualstudio.com/api/references/contribution-points?utm_source=chatgpt.com) [oai_citation:5‡Grafana Labs](https://grafana.com/developers/plugin-tools/key-concepts/plugin-types-usage?utm_source=chatgpt.com)

### B) Core TypeScript Interfaces (v1)
>
> **File:** `frontend/src/plugins/api.ts`

```ts
export type NodeId = string;
export type ArchonScalar = string | number | boolean | null;

export interface ArchonNode {
  id: NodeId;
  name: string;
  description?: string;
  properties: Record<string, ArchonScalar>;
  children: NodeId[]; // order is meaningful
}

// ---- Shared host services (capabilities gated by permissions) ----
export interface Host {
  // Model access
  getNode(id: NodeId): Promise<ArchonNode | null>;
  listChildren(id: NodeId): Promise<NodeId[]>;
  query(selector: string): Promise<NodeId[]>; // future: simple selectors
  apply(edits: Mutation[]): Promise<void>;    // gated by "writeRepo"
  // Git & snapshots
  commit(message: string): Promise<string>;   // returns commit sha
  snapshot(tag: string, notes?: Record<string, any>): Promise<string>;
  // Attachments
  readAttachment(hash: string): Promise<ArrayBuffer>;
  writeAttachment(bytes: ArrayBuffer, filename?: string): Promise<{ hash: string, path: string }>;
  // Network (only if permission granted)
  fetch(input: RequestInfo, init?: RequestInit): Promise<Response>;
  // Index (if granted)
  indexPut(docs: IndexDoc[]): Promise<void>;
  // UI
  ui: UI;
  // Secrets (scoped; e.g., Jira token)
  secrets: Secrets;
}

export interface UI {
  registerCommand(cmd: Command): void;
  showPanel(panel: PanelDescriptor): void;
  showModal(modal: ModalDescriptor): Promise<void>;
  notify(opts: { level: "info"|"warn"|"error", message: string }): void;
}

export interface Secrets {
  get(name: string): Promise<string | null>;
  set(name: string, value: string, opts?: { description?: string }): Promise<void>;
  delete(name: string): Promise<void>;
}

// ---- Plugin kinds ----
export interface Importer {
  kind: "importer";
  meta: { id: string; name: string; version: string; formats: string[] };
  run(input: Uint8Array | string, options?: Record<string, any>): Promise<{ root: ArchonNode }>;
}

export interface Exporter {
  kind: "exporter";
  meta: { id: string; name: string; version: string; formats: string[] };
  run(root: NodeId, options?: Record<string, any>): Promise<Uint8Array | string>;
}

export interface Transformer {
  kind: "transformer";
  meta: { id: string; name: string; version: string };
  run(scope: NodeId | NodeId[], options?: Record<string, any>): Promise<Mutation[]>;
}

export interface Validator {
  kind: "validator";
  meta: { id: string; name: string; version: string };
  run(scope: NodeId | NodeId[], options?: Record<string, any>): Promise<ValidationReport>;
}

export interface Panel {
  kind: "panel";
  meta: { id: string; name: string; version: string };
  mount(host: Host, props: { root: NodeId }): PanelHandle;
}

export interface Provider {
  kind: "provider";
  meta: { id: string; name: string; version: string; services: string[] }; // e.g., ["jira"]
  configure(config: Record<string, any>): Promise<void>;
  pull(options?: Record<string, any>): Promise<ProviderPullResult>;
  push(options?: Record<string, any>): Promise<ProviderPushResult>;
}

export interface AttachmentProcessor {
  kind: "attachment-processor";
  meta: { id: string; name: string; version: string; types: string[] }; // MIME
  run(file: ArrayBuffer, filename?: string): Promise<AttachmentAnalysis>;
}

export interface ConflictResolver {
  kind: "conflict-resolver";
  meta: { id: string; name: string; version: string; fields?: string[] };
  resolve(base: ArchonNode, ours: ArchonNode, theirs: ArchonNode): Promise<ArchonNode | "conflict">;
}

export interface SearchIndexer {
  kind: "search-indexer";
  meta: { id: string; name: string; version: string };
  index(scope: NodeId | NodeId[], emit: (doc: IndexDoc) => void): Promise<void>;
}

// ---- Events (optional subscriptions a plugin can export) ----
export interface Events {
  onBeforeCommit?(ctx: CommitContext): Promise<void | "block">;
  onAfterCommit?(ctx: CommitContext): Promise<void>;
  onBeforeSnapshot?(tag: string): Promise<void | "block">;
  onAfterSnapshot?(tag: string): Promise<void>;
  onPull?(result: PullResult): Promise<void>;
  onMergeStart?(ctx: MergeContext): Promise<void>;
  onMergeEnd?(ctx: MergeResult): Promise<void>;
}
```

### C) Permissions (least privilege)

Declared in plugin manifest; every host API is gated. UX shows a one-time consent dialog and per-run prompts for sensitive scopes.

| Permission | Grants |
|---|---|
| `readRepo` | `getNode, listChildren, query` |
| `writeRepo` | `apply, commit, snapshot` |
| `attachments` | `readAttachment, writeAttachment` |
| `net` | `host.fetch (scoped, rate-limited)` |
| `indexWrite` | `indexPut` |
| `ui` | `ui.* (commands, panels, modals, toasts)` |
| `secrets:jira*` | `read/write a scoped secret (e.g., Jira API token/OAuth)` |


Figma-style constraints (sandbox, explicit permissions, and small surface) inform this design.  ￼ ￼

### D) Lifecycle & Events

Plugins can subscribe to lifecycle events: onBeforeCommit, onAfterCommit, onBeforeSnapshot, onAfterSnapshot, onPull, onMergeStart/End. This enables validators, reporters, and workflow automations without polling.

### E) Jira Integration (what fits where)

Goal: Treat Jira as (1) a Provider (data source/sink), (2) a Workflow Automation target via events, and (3) a Validator for policy gates.

- Provider (read/write):
  - pull: Query Jira with JQL to import issues into a subtree (e.g., “Open tasks for Bench A”), mapping fields → node properties.  ￼
  - push: Create or update Jira issues from Archon nodes (e.g., create “Replace filter” tickets).
  - Auth: Prefer OAuth 2.0 (3LO) for Jira Cloud or API tokens (Basic auth) stored in secrets:jira.  ￼
  - Change intake: Register webhooks (site admin) so Jira events (issue updated, transition, comment) can trigger Archon notifications or background pulls.  ￼ ￼
- Workflow Automation (events → actions):
  - onAfterSnapshot: Post a change summary comment to a linked Jira issue.
  - onBeforeCommit: Block commit if referenced Jira ticket isn’t in an allowed status or doesn’t exist (policy gate).
- Validator (policy gates):
  - Require Jira-Key property to match an existing issue; use JQL to check status/assignee. If failing, return actionable errors.  ￼

Why these categories? They mirror the “data source/app/panel” taxonomy used successfully in other ecosystems while aligning to Jira’s capabilities (JQL, webhooks, OAuth).  ￼

### F) Example Mini-Contracts for Jira

```ts
// Provider-specific options (example)
type JiraProviderConfig = {
  siteUrl: string;                   // e.g., https://yourorg.atlassian.net
  auth: { type: "oauth" | "token"; secretName: "jira-token" | "jira-oauth" };
  projectKey?: string;
  fieldMap?: Record<string,string>;  // JiraField -> Node property key
};

type JiraPullOptions = {
  jql: string;           // e.g., project = ABC AND status = "To Do"
  attachComments?: boolean;
  linkToNodesBy?: "key" | "customField";
};

type JiraPushOptions = {
  createIfMissing?: boolean;
  updateStrategy?: "upsert" | "create-only";
  statusTransition?: string;        // e.g., "In Progress"
};
```

### G) Packaging & Discovery

- Manifest declares: id, name, version, kind[], permissions[], entry points, minimum Archon version, and (optionally) integrity hash.
- Install sources: local directory (~/.archon/plugins) and “Install from file/URL.” A curated gallery/registry can follow (post-MVP). (Comparable to Grafana’s plugin catalog and types.)  ￼

Rationale

- Clear types reduce ambiguity, improve UX consistency, and guide third-party developers. (VS Code/Grafana evidence.)  ￼ ￼
- Least-privilege permissions and sandboxing protect users and organizations. (Figma pattern.)  ￼
- Formal Provider role captures integrations like Jira using JQL queries, OAuth/API tokens, and webhooks for real-time signals.  ￼ ￼

Alternatives Considered

- Single “script” plugin type: simple, but leads to ad-hoc UX and security sprawl.
- Native plugins (Go/Rust): powerful but heavy to distribute and audit for v1.
- Always-on network: convenient, but conflicts with privacy/enterprise policies.

Consequences

- Positive: Extensible across I/O, UI, rules, search, and workflow; safe by default; Jira and similar systems are first-class.
- Negative: More host surface area to maintain; requires permission UX and stable APIs.
- Mitigations: Versioned APIs, compatibility layer, and strong CI/examples.

Implementation Notes

- Runtime: Web Worker sandbox for plugin code; no FS or network unless granted. (Figma-like.)  ￼
- Event bus: Internal pub/sub emits lifecycle events to subscribed plugins.
- Jira auth:
  - Cloud: OAuth 2.0 (3LO) preferable for orgs; API token supported for quick start.  ￼
  - Data Center/Server: OAuth 2.0 provider or PAT per deployment policy.  ￼
- Webhooks: Document admin steps to register Jira webhooks that notify Archon (issue updated, transition, comment).  ￼
- Indexing: SearchIndexer writes normalized tokens (part numbers, serials) into Archon’s local SQLite FTS cache.

Review / Revisit

- Revisit when:
  - We introduce DAG/cross-links (affects Transformer/Validator scope),
  - A server-backed realtime mode is added (new events/capabilities),
  - We formalize a public plugin registry with signing and review.

---

### Where Jira “fits” (quick map you can share with the team)

- **Provider:** Pull with **JQL**, push issues/updates; auth via **OAuth 2.0 (3LO)** or API tokens; keep in sync with **webhooks**.  [oai_citation:24‡Atlassian Support](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/?utm_source=chatgpt.com) [oai_citation:25‡Atlassian Developer](https://developer.atlassian.com/cloud/confluence/oauth-2-3lo-apps/?utm_source=chatgpt.com)  
- **Validator:** Gate commits/snapshots on Jira status/labels (policy).  [oai_citation:26‡Atlassian Support](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/?utm_source=chatgpt.com)  
- **Workflow:** Post snapshot change logs as Jira comments; transition issues after successful merges; notify watchers on `onAfterSnapshot`.  [oai_citation:27‡Atlassian Support](https://support.atlassian.com/jira-cloud-administration/docs/manage-webhooks/?utm_source=chatgpt.com)
