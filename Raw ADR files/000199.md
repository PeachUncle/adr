# ADR-0003: Propose/Apply Workflow with Review-Before-Commit

**Date:** 2026-01-09  
**Status:** Accepted  
**Deciders:** blecx, GitHub Copilot  
**Related:** [MVP Spec](../spec/mvp-iso21500-agent.md), [ADR-0001](0001-docs-repo-mounted-git.md), [Chat Transcript](../chat/2026-01-09-blecx-copilot-transcript.md)

## Context

The AI-Agent-Framework generates and modifies project documentation using AI/LLM. When AI generates or modifies files, there's a risk of:

1. **Unintended changes** that don't match user expectations
2. **Overwrites** of important content without user awareness
3. **Compliance issues** if changes lack human review
4. **Quality problems** that could have been caught before committing
5. **Lack of transparency** in what the AI is doing
6. **Difficult rollback** after changes are committed

We need a workflow that ensures human oversight while maintaining efficiency.

### Problem Statement

How should we handle AI-generated changes to ensure quality, safety, and compliance while maintaining usability?

**Options Considered:**

**Option 1: Direct Apply (No Review)**
- AI generates content → Immediately write to files → Auto-commit
- ✅ Fastest workflow
- ✅ Minimal user interaction
- ❌ No user review before changes
- ❌ Can't preview what AI will do
- ❌ Risky for overwrites
- ❌ Compliance issues (no human oversight)
- ❌ Difficult to catch errors

**Option 2: Preview Only (No Git Integration)**
- AI generates content → Show in UI → User manually saves
- ✅ User sees content before saving
- ❌ No version control
- ❌ No audit trail
- ❌ User must manually manage files
- ❌ Doesn't leverage git benefits

**Option 3: Propose/Review/Apply (Two-Step)**
- AI generates content → Show preview with diff → User approves → Write & commit
- ✅ User reviews before changes committed
- ✅ Shows exactly what will change (diff)
- ✅ Can cancel or modify before applying
- ✅ Maintains audit trail via git
- ✅ Compliant with human-in-the-loop requirements
- ✅ Reduces errors through review
- ❌ Requires extra click to apply
- ❌ Slightly slower workflow

**Option 4: Sandbox/Branch Preview**
- AI generates in temporary branch → User reviews → Merge if approved
- ✅ Isolated changes for review
- ❌ Overly complex for small changes
- ❌ Git branch overhead for each operation
- ❌ More difficult for non-technical users

## Decision

We will **implement a two-step Propose/Apply workflow with review-before-commit**.

### Workflow Design

**Step 1: Propose**
```
User Request → Render Prompt → Call LLM → Generate Content → Create Proposal
                                                                   ↓
                                                    Return: proposal_id
                                                           + file changes
                                                           + unified diffs
                                                           + metadata
```

**Step 2: Review (User)**
```
Display Proposal → Show File Changes → Show Unified Diffs → User Decision
                                                                   ↓
                                                          Cancel OR Apply
```

**Step 3: Apply (If Approved)**
```
Apply Request → Validate proposal_id → Write Files → Git Commit → Return commit hash
```

### Implementation Details

**API Endpoints:**

**Propose Endpoint:**
```
POST /projects/{project_key}/commands/propose
{
  "command": "assess_gaps" | "generate_artifact" | "generate_plan",
  "parameters": {
    "artifact_name": "...",    // For generate_artifact
    "artifact_type": "..."      // For generate_artifact
  }
}

Response:
{
  "proposal_id": "uuid-v4",
  "message": "Ready to create gap assessment report",
  "changes": [
    {
      "path": "reports/gap_assessment.md",
      "operation": "create" | "update" | "delete",
      "diff": "unified diff string"
    }
  ]
}
```

**Apply Endpoint:**
```
POST /projects/{project_key}/commands/apply
{
  "proposal_id": "uuid-v4"
}

Response:
{
  "success": true,
  "commit_hash": "abc123...",
  "files_changed": ["reports/gap_assessment.md"],
  "message": "Applied proposal successfully"
}
```

**Proposal Storage:**

Proposals stored in memory (dict) during user session:
- Key: `proposal_id` (UUID)
- Value: Proposal object with file changes, content, metadata
- Lifetime: Until applied or 1 hour timeout
- No persistence needed (user completes workflow in single session)

**Unified Diff Generation:**

For each file change:
```python
import difflib

def generate_unified_diff(old_content: str, new_content: str, filename: str) -> str:
    old_lines = old_content.splitlines(keepends=True) if old_content else []
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm=""
    )
    
    return "".join(diff)
```

**Audit Logging:**

Each operation logs to `events.ndjson`:

**Propose Event:**
```json
{
  "timestamp": "2026-01-09T12:00:00Z",
  "event_type": "command_proposed",
  "command": "assess_gaps",
  "proposal_id": "uuid",
  "user": "system",
  "prompt_hash": "sha256:...",
  "files_to_change": ["reports/gap_assessment.md"]
}
```

**Apply Event:**
```json
{
  "timestamp": "2026-01-09T12:00:30Z",
  "event_type": "command_applied",
  "proposal_id": "uuid",
  "commit_hash": "abc123...",
  "files_changed": ["reports/gap_assessment.md"],
  "user": "system"
}
```

**Frontend UI:**

**Command Panel:**
- User selects command
- Enters parameters (if needed)
- Clicks "Propose Changes"

**Proposal Modal:**
- Shows proposal message
- Lists file changes (create/update/delete)
- Displays unified diff for each file
- Two buttons: "Cancel" and "Apply & Commit"

**After Apply:**
- Success message with commit hash
- Refresh artifacts list
- Modal closes

## Consequences

### Positive

1. **Human Oversight (Compliance):**
   - Every AI-generated change reviewed by human before commit
   - Meets EU AI Act requirements for human-in-the-loop
   - Meets ISO 21500 requirements for quality review
   - Satisfies risk management policies

2. **Transparency:**
   - User sees exactly what will change before it happens
   - Unified diff shows additions, deletions, modifications
   - No surprises or unexpected changes
   - Builds user trust in AI system

3. **Safety:**
   - Can't accidentally overwrite important content
   - User can cancel if AI generates wrong content
   - Easy to catch errors before they become commits
   - Reduces risk of data loss

4. **Quality Control:**
   - User can verify AI output quality
   - Can reject low-quality generations
   - Opportunity to refine prompt if needed
   - Continuous improvement through feedback

5. **Audit Trail:**
   - Proposal logged before apply
   - Apply logged with commit hash
   - Full traceability from request → proposal → commit
   - Compliance with audit requirements

6. **Git Integration:**
   - Changes committed only after approval
   - Clean git history (no trial-and-error commits)
   - Rollback via git if needed
   - Proper commit messages describing changes

7. **User Control:**
   - User decides when to apply changes
   - Can review at their own pace
   - Can compare with existing content
   - Empowering rather than autonomous

### Negative

1. **Extra Click Required:**
   - User must click "Apply & Commit" after reviewing
   - Mitigation: UI makes it clear and easy
   - Acceptable trade-off for safety and compliance

2. **Slightly Slower Workflow:**
   - Two API calls instead of one (propose, then apply)
   - Mitigation: Propose is async, user can review while waiting
   - Time difference is negligible (<1 second)

3. **Proposal State Management:**
   - Must track proposals between API calls
   - Mitigation: Simple in-memory storage with UUID
   - Timeout cleanup prevents memory leaks

4. **Can't "Undo" After Apply:**
   - Once applied, requires git revert to undo
   - Mitigation: Review step prevents mistakes
   - Git history provides rollback capability

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| User applies without reviewing | Medium | Medium | Clear UI prompts, diff prominently displayed |
| Proposal expires before apply | Low | Low | 1-hour timeout sufficient for review |
| Concurrent proposals conflict | Medium | Low | File-level locking, sequential command execution |
| User confusion about workflow | Low | Medium | Clear UI labels, tooltips, documentation |

## Compliance Notes

### EU AI Act

**Article 14 - Human Oversight:**
✅ Humans can:
- Understand AI system capabilities and limitations
- Monitor AI system operation
- Interpret AI system output
- **Decide when and how to use AI output**
- Intervene or interrupt AI operation

This workflow explicitly implements "decide when to use AI output" through the review-and-approve step.

**Article 12 - Record Keeping:**
✅ System logs:
- When proposals were generated
- When proposals were applied
- What content was changed
- Who approved the changes

### ISO 21500 - Project Management

**Quality Management:**
✅ Quality control gates for AI-generated documents
✅ Review process before finalizing documents
✅ Traceability of document versions

**Risk Management:**
✅ Reduces risk of unintended document changes
✅ Provides rollback mechanism via version control

### ISO 27001 - Information Security

**A.12.1 - Operational Procedures:**
✅ Change management process for documents
✅ Approval required before implementing changes
✅ Audit log of all changes

**A.18.1 - Compliance:**
✅ Supports regulatory compliance requirements
✅ Provides evidence of human oversight
✅ Maintains accountability for changes

## Implementation Notes

**Command Service** (`apps/api/services/command_service.py`):
```python
import uuid
from typing import Dict
from datetime import datetime, timedelta

class CommandService:
    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.proposal_timeout = timedelta(hours=1)
    
    async def propose_command(
        self,
        project_key: str,
        command: str,
        parameters: dict
    ) -> dict:
        """Generate proposal for changes"""
        # 1. Render prompt template
        prompt = self._render_prompt(command, parameters)
        
        # 2. Call LLM (or fallback to template)
        content = await self.llm_service.generate(prompt)
        
        # 3. Determine file changes
        changes = self._determine_changes(command, parameters, content)
        
        # 4. Generate diffs
        for change in changes:
            old_content = self._read_file_if_exists(change["path"])
            change["diff"] = self._generate_diff(old_content, change["content"])
        
        # 5. Store proposal
        proposal_id = str(uuid.uuid4())
        self.proposals[proposal_id] = Proposal(
            id=proposal_id,
            project_key=project_key,
            command=command,
            changes=changes,
            created_at=datetime.now()
        )
        
        # 6. Log proposal event
        self._log_event("command_proposed", proposal_id, command)
        
        # 7. Return proposal
        return {
            "proposal_id": proposal_id,
            "message": f"Ready to {self._describe_action(command)}",
            "changes": changes
        }
    
    async def apply_command(
        self,
        project_key: str,
        proposal_id: str
    ) -> dict:
        """Apply approved proposal"""
        # 1. Validate proposal exists
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found or expired")
        
        # 2. Check timeout
        if datetime.now() - proposal.created_at > self.proposal_timeout:
            del self.proposals[proposal_id]
            raise ValueError("Proposal expired")
        
        # 3. Write files
        files_changed = []
        for change in proposal.changes:
            self._write_file(change["path"], change["content"])
            files_changed.append(change["path"])
        
        # 4. Git commit
        commit_message = f"[{project_key}] {self._describe_action(proposal.command)}"
        commit_hash = self.git_manager.commit_changes(commit_message, files_changed)
        
        # 5. Log apply event
        self._log_event("command_applied", proposal_id, proposal.command, commit_hash)
        
        # 6. Cleanup proposal
        del self.proposals[proposal_id]
        
        # 7. Return result
        return {
            "success": True,
            "commit_hash": commit_hash,
            "files_changed": files_changed
        }
```

**Proposal Model:**
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class FileChange:
    path: str
    operation: str  # "create" | "update" | "delete"
    content: str
    diff: str

@dataclass
class Proposal:
    id: str
    project_key: str
    command: str
    changes: List[FileChange]
    created_at: datetime
```

**Frontend Proposal Modal** (`components/ProposalModal.jsx`):
```jsx
function ProposalModal({ proposal, onApply, onCancel }) {
  return (
    <div className="modal">
      <h2>Review Proposed Changes</h2>
      <p>{proposal.message}</p>
      
      <h3>File Changes:</h3>
      {proposal.changes.map(change => (
        <div key={change.path} className="change">
          <h4>{change.operation}: {change.path}</h4>
          <pre className="diff">{change.diff}</pre>
        </div>
      ))}
      
      <div className="actions">
        <button onClick={onCancel}>Cancel</button>
        <button onClick={() => onApply(proposal.proposal_id)}>
          Apply & Commit
        </button>
      </div>
    </div>
  );
}
```

## Alternatives Considered

We considered but rejected:

1. **Direct apply without review:**
   - Rejected due to safety and compliance concerns

2. **Preview without git integration:**
   - Rejected as doesn't meet version control requirements

3. **Git branch per proposal:**
   - Rejected as too complex for simple workflow

4. **Persistent proposal storage (database):**
   - Rejected as over-engineered; in-memory sufficient

## User Experience Flow

```
┌─────────────────┐
│ Select Command  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Enter Params    │
│ (if needed)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Click "Propose" │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend:        │
│ - Render prompt │
│ - Call LLM      │
│ - Generate diff │
│ - Store proposal│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Show Modal:     │
│ - File changes  │
│ - Unified diffs │
│ - Two buttons   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ Cancel │ │  Apply   │
└────────┘ └────┬─────┘
              │
              ▼
        ┌──────────────┐
        │ Backend:     │
        │ - Write files│
        │ - Git commit │
        │ - Log event  │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ Show Success │
        │ - Commit hash│
        │ - Close modal│
        └──────────────┘
```

## References

- [EU AI Act - Article 14 (Human Oversight)](https://artificialintelligenceact.eu/article/14/)
- [ISO 21500 - Quality Management](https://www.iso.org/standard/50003.html)
- [ISO 27001 - Annex A.12 Operations Security](https://www.iso.org/standard/54534.html)
- [MVP Specification](../spec/mvp-iso21500-agent.md)
- [ADR-0001: Separate Docs Repository](0001-docs-repo-mounted-git.md)
- [Chat Transcript](../chat/2026-01-09-blecx-copilot-transcript.md) - Original discussion

## Review History

| Date | Reviewer | Decision |
|------|----------|----------|
| 2026-01-09 | blecx | Approved |
| 2026-01-09 | GitHub Copilot | Documented |

---

**Previous:** [ADR-0002: LLM HTTP Adapter](0002-llm-http-adapter-json-config.md)  
**See Also:** [Chat Context Best Practices](../howto/chat-context-in-repo.md)
