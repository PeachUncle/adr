# ADR-0001: Separate Project Documents Git Repository Mounted at /projectDocs

**Date:** 2026-01-09  
**Status:** Accepted  
**Deciders:** blecx, GitHub Copilot  
**Related:** [MVP Spec](../spec/mvp-iso21500-agent.md), [Chat Transcript](../chat/2026-01-09-blecx-copilot-transcript.md)

## Context

The AI-Agent-Framework generates project management documentation following ISO 21500 standards. We need a strategy for storing these generated documents that:

1. **Separates concerns** between application code and project data
2. **Provides version control** for all project documents
3. **Prevents contamination** of the code repository with customer/project data
4. **Enables portability** of project documents independent of the application
5. **Supports compliance** requirements for audit trails and data classification
6. **Simplifies backup** and recovery of project data

### Problem Statement

Where and how should we store generated project documents?

**Options Considered:**

**Option 1: Store documents in the code repository**
- ❌ Mixes code and data concerns
- ❌ Bloats code repository with customer data
- ❌ Difficult to separate for backup/export
- ❌ Compliance issues with data classification
- ✅ Simple deployment (everything in one place)

**Option 2: Store documents in external database**
- ✅ Clean separation of code and data
- ❌ No built-in version control
- ❌ Requires additional infrastructure (database server)
- ❌ More complex to backup and restore
- ❌ Less transparent (can't easily browse files)

**Option 3: Store documents in separate git repository mounted as volume**
- ✅ Clean separation of code and data
- ✅ Full version control via git
- ✅ Simple file-based storage
- ✅ Easy to backup, export, and share
- ✅ Transparent (can browse with any file manager or git client)
- ✅ No additional infrastructure required
- ✅ Supports compliance with audit trails
- ❌ Requires mount configuration in Docker

**Option 4: Store documents in cloud storage (S3, Azure Blob)**
- ✅ Scalable for large projects
- ✅ Built-in backup/replication
- ❌ Requires cloud account and credentials
- ❌ No built-in version control
- ❌ Higher complexity
- ❌ Vendor lock-in

## Decision

We will **store all project documents in a separate git repository mounted at `/projectDocs`**.

### Implementation Details

**Directory Structure:**
```
AI-Agent-Framework/              # Code repository
├── apps/                        # Application code
├── docker/                      # Docker config
├── configs/                     # Config files
└── projectDocs/                 # SEPARATE GIT REPO (mounted volume)
    ├── .git/                    # Git repository
    ├── PROJECT001/              # Project folder
    │   ├── project.json         # Metadata
    │   ├── artifacts/           # Generated docs
    │   ├── reports/             # Assessments
    │   └── events/              # Audit logs
    └── PROJECT002/              # Another project
        └── ...
```

**Auto-initialization:**
- Backend checks if `/projectDocs` exists on startup
- If not a git repository, initializes with `git init`
- Creates initial commit for tracking baseline
- All subsequent operations commit to this repository

**Volume Mounting:**
```yaml
# docker-compose.yml
services:
  api:
    volumes:
      - ./projectDocs:/projectDocs  # Mount host directory
```

**Git Operations:**
- Project creation: Commit with message "Create project {KEY}"
- Document generation: Commit with message "[{KEY}] {action description}"
- All commits attributed to "AI Agent System <system@localhost>"
- Full git history available for audit and rollback

**Exclusion from Code Repo:**
```gitignore
# .gitignore
projectDocs/
```

## Consequences

### Positive

1. **Clean Separation:**
   - Application code and project data are completely separate
   - Can update application without affecting project documents
   - Can backup/restore projects independently

2. **Full Version Control:**
   - Every document change tracked in git
   - Full commit history for audit trails
   - Easy rollback to any previous version
   - Branching/merging available for advanced workflows

3. **Transparency:**
   - Documents stored as plain files
   - Can browse with file manager, IDE, or git client
   - No proprietary formats or databases
   - Easy to export, share, or migrate

4. **Compliance Support:**
   - Immutable audit trail via git log
   - Point-in-time recovery for any document version
   - Clear data classification (project docs separate from code)
   - Supports retention policies (git history)

5. **Simple Backup:**
   - Single directory to backup (`projectDocs/`)
   - Standard git backup tools work (git clone, git bundle)
   - Can push to remote git servers for redundancy

6. **No Additional Infrastructure:**
   - No database server required
   - No cloud account required
   - Works offline
   - Minimal dependencies

7. **Developer-Friendly:**
   - Familiar git workflow
   - Easy to inspect and debug
   - Standard tooling (git, diff, log)

### Negative

1. **Git Learning Curve:**
   - Users need basic git knowledge for advanced operations
   - Mitigation: System abstracts git operations via API
   - Users can use system without knowing git

2. **Concurrent Access:**
   - Git not designed for high-concurrency writes
   - Mitigation: System uses file-locking for command execution
   - Acceptable for single-user or small team use

3. **Large Binary Files:**
   - Git not ideal for large binary files
   - Mitigation: System primarily generates text (Markdown)
   - Can use Git LFS if needed in future

4. **Mount Configuration:**
   - Requires volume mount in Docker
   - Mitigation: Well-documented in README and docker-compose.yml
   - One-time configuration during setup

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Accidental deletion of projectDocs/ | High | Low | Regular backups, git remote backup |
| Git repository corruption | High | Very Low | Git's integrity checks, regular backups |
| Disk space issues with history | Medium | Low | Git garbage collection, archive old projects |
| User overwrites files manually | Medium | Medium | Git tracking detects changes, can rollback |

## Compliance Notes

### EU AI Act
- **Transparency:** All document changes tracked with timestamps and attribution
- **Human Oversight:** Human review required before applying changes (propose/apply workflow)
- **Record Keeping:** Immutable git history provides audit trail

### ISO 27001
- **Access Control:** File system permissions control access to `/projectDocs`
- **Data Classification:** Project documents classified separately from code
- **Audit Logging:** Git log provides complete audit trail
- **Backup and Recovery:** Git enables point-in-time recovery

### GDPR (if processing personal data)
- **Right to Erasure:** Can delete project folders or use git-filter-repo to remove specific data
- **Data Portability:** Projects easily exported as git repositories or zip archives
- **Purpose Limitation:** Project data isolated from other systems

## Alternatives Considered

We considered but rejected:

1. **Single repository for code and data:**
   - Rejected due to mixing concerns and bloating code repo

2. **Database storage:**
   - Rejected due to complexity and lack of native version control

3. **Cloud storage:**
   - Rejected to avoid vendor lock-in and external dependencies

4. **File system without version control:**
   - Rejected due to lack of audit trail and rollback capability

## Implementation Notes

**Git Manager Service** (`apps/api/services/git_manager.py`):
```python
class GitManager:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self._ensure_git_initialized()
    
    def _ensure_git_initialized(self):
        """Auto-initialize git if not present"""
        if not (self.base_path / ".git").exists():
            repo = git.Repo.init(self.base_path)
            # Create initial commit
    
    def create_project(self, key: str, name: str):
        """Create project and commit"""
        # Create folder structure
        # Commit with message
    
    def commit_changes(self, message: str, files: List[str]):
        """Commit specified files"""
        repo = git.Repo(self.base_path)
        repo.index.add(files)
        repo.index.commit(message)
```

**Docker Compose Configuration:**
```yaml
services:
  api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile
    volumes:
      - ./projectDocs:/projectDocs:rw
    environment:
      - PROJECT_DOCS_PATH=/projectDocs
```

**Startup Checks:**
- Backend lifespan event checks for `/projectDocs` existence
- Initializes git if needed
- Logs status to console for visibility

## References

- [MVP Specification](../spec/mvp-iso21500-agent.md)
- [Git Documentation](https://git-scm.com/doc)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)
- [ISO 27001 Annex A.12 - Operations Security](https://www.iso.org/standard/54534.html)
- [Chat Transcript](../chat/2026-01-09-blecx-copilot-transcript.md) - Original discussion

## Review History

| Date | Reviewer | Decision |
|------|----------|----------|
| 2026-01-09 | blecx | Approved |
| 2026-01-09 | GitHub Copilot | Documented |

---

**Next ADR:** [ADR-0002: LLM HTTP Adapter with JSON Configuration](0002-llm-http-adapter-json-config.md)
