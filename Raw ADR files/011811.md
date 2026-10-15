# ADR 002: Agent Trigger Mechanism

## Status

Proposed

## Context

We are building a mobile-first application that enables developers to delegate coding tasks to AI agents directly from their phones. The core MVP workflow is:

1. Developer creates or identifies a GitHub issue
2. Developer instructs the agent to work on it via the mobile app
3. Agent runs as a GitHub Actions workflow
4. Agent creates a branch, makes commits, and opens a pull request

We need to decide how the mobile application triggers the GitHub Actions workflow that runs the agent. This decision impacts the user experience, visibility of agent activities, and the complexity of the implementation.

### Options Evaluated

#### Option 1: Label-based Triggering

The mobile app adds a label (e.g., `ai:implement`) to the issue. The GitHub Actions workflow triggers on the `issues.labeled` event.

**Pros:**
- Simple to implement on both mobile and workflow side
- Highly visible in issue history and issue list
- Native GitHub audit trail
- No additional API permissions needed beyond issue write access
- Works naturally with GitHub's event model
- Visual indicator on issue that agent is/was involved
- Can filter issues by agent-related labels

**Cons:**
- Clutters the label namespace (mitigated by `ai:` prefix convention)
- Difficult to pass complex parameters (can be addressed with issue body parsing or follow-up comments)
- Label remains after execution unless explicitly removed (can be workflow responsibility)
- Re-triggering requires removing and re-adding label (acceptable for MVP)

#### Option 2: Workflow Dispatch API

The mobile app directly triggers the workflow using GitHub's `workflow_dispatch` API, passing the issue number and instructions as inputs.

**Pros:**
- Clean programmatic API
- Can pass structured parameters easily
- No label clutter
- Easy to re-trigger

**Cons:**
- Requires manual interaction via GitHub UI "Run workflow" button
- Poor mobile experience - requires navigating to Actions tab
- Less visible in issue history
- Not suitable for mobile-first workflow
- Requires additional API permissions

#### Option 3: Comment-based Triggering

The mobile app posts a comment (e.g., `/agent implement`) to the issue. The workflow triggers on the `issue_comment.created` event.

**Pros:**
- Highly visible in issue timeline
- Natural audit trail
- Can pass parameters in comment text
- Familiar slash command pattern

**Cons:**
- Requires comment parsing and validation
- Noisy if many commands are tried
- Anyone with comment access can trigger
- Comment remains even if malformed

## Decision

We will use **label-based triggering** as the primary mechanism for the MVP.

The mobile app will add specific labels to issues to trigger agent workflows:
- `ai:implement` - Agent should implement the feature/fix described in the issue
- Additional instruction labels can be added in future (e.g., `ai:review`, `ai:test`, `ai:refactor`)

The GitHub Actions workflow will:
1. Trigger on `issues.labeled` event
2. Filter for labels matching `ai:*` pattern
3. Remove the trigger label once processing starts
4. Add status labels during execution (e.g., `ai:in-progress`, `ai:completed`, `ai:failed`)
5. Post comments with links to PRs or error messages

## Consequences

### Positive

- **Mobile-first**: Labels are easy to add via GitHub API from mobile, no complex UI needed
- **Visibility**: Everyone can see at a glance which issues have agent involvement
- **Simplicity**: Leverages GitHub's native event system, no custom infrastructure
- **Permissions**: Only requires issue write access, which the mobile app already needs
- **Audit trail**: Label events appear in issue timeline automatically
- **Filtering**: Can easily query/filter issues by agent status labels
- **Reliability**: GitHub's event delivery is robust and well-tested
- **No manual steps**: Unlike workflow dispatch, this is fully automated

### Negative

- **Label namespace**: Adds several labels to the repository (mitigated by `ai:` prefix)
- **Parameter passing**: Complex instructions need to be in issue body or comments (acceptable for MVP where instructions are simple)
- **Re-triggering**: Requires removing and re-adding label (acceptable for MVP, can improve later)
- **Cleanup**: Need to manage label lifecycle in workflow to avoid clutter

### Mitigations

- Use consistent `ai:` prefix for all agent-related labels to keep them organised
- Workflow automatically removes trigger labels and replaces with status labels
- Document label semantics clearly in repository
- Consider label colours to make agent-related labels visually distinct
- Issue body can contain structured YAML/JSON frontmatter for complex parameters if needed

### Future Considerations

- May add comment-based parameters in addition to labels (e.g., label triggers, comment provides details)
- Could implement more granular labels for different instruction types
- May need label-based queueing if multiple labels are added simultaneously
- Consider adding a status label cleanup mechanism for closed issues
- Could use label descriptions (new GitHub feature) to provide inline documentation

### Implementation Notes

Workflow trigger configuration:
```yaml
on:
  issues:
    types: [labeled]
```

Workflow should check:
1. Label name matches `ai:*` pattern
2. Issue is open (not closed)
3. Agent has necessary permissions
4. Issue body contains required information
