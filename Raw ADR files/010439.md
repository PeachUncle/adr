# ADR-0001: Use Resource-Level Sharing for Service Account Access

## Status
Accepted

## Context

The Libre Google Workspace Agents project requires secure authentication to access Google Workspace APIs (Sheets, Drive, Docs, etc.) through MCP servers. We need to determine the appropriate Service Account authentication pattern.

### Background

Google Cloud Platform provides two primary approaches for Service Account access to Google Workspace resources:

1. **Resource-Level Sharing** ("External" Service Account)
   - Service Account is explicitly added to specific resources (folders, files)
   - Permissions granted at the resource level (Owner, Editor, Viewer)
   - Each MCP server instance configured with folder/drive scope via `DRIVE_FOLDER_ID`

2. **Domain-Wide Delegation** ("Internal" Service Account)
   - Service Account can impersonate any user in the Workspace domain
   - Requires Google Workspace Admin to grant domain-wide authority
   - Actions appear to originate from impersonated user
   - Intended for organization-wide automation tools

### Investigation Findings

**Current Setup Verification:**
- Service Account: `sa-wellard-mcp-shared@connect-wellard-workspace-app.iam.gserviceaccount.com`
- Two MCP server instances: `google-sheets-cw` and `google-sheets-local`
- Authentication: Resource-level sharing (folders explicitly shared with SA)
- Testing: Successful CRUD operations on two test spreadsheets via Claude Desktop

**Security Research:**

Domain-Wide Delegation presents significant security risks:
- **DeleFriend Vulnerability**: Privilege escalation vulnerability allowing Service Accounts with domain-wide delegation to impersonate super-admins
- **Excessive Privilege**: Violates Principle of Least Privilege by granting organization-wide access
- **Audit Trail Issues**: Actions appear as impersonated user, making attribution difficult
- **Revocation Complexity**: Removing access requires Admin Console, not just resource permissions

Resource-Level Sharing advantages:
- **Explicit Permissions**: Clear, auditable folder/file access
- **Easy Revocation**: Remove SA from resource or delete SA key
- **Principle of Least Privilege**: SA only accesses specifically shared resources
- **Google Recommended**: Official documentation discourages domain-wide delegation for new applications

**Source Analysis:**

Reviewed `mcp-google-sheets` server implementation (`/Users/smalcolm/src/github.com/xing5/mcp-google-sheets/src/mcp_google_sheets/server.py`):
- Does NOT implement domain-wide delegation
- Uses standard Service Account authentication
- Supports Shared Drives via `supportsAllDrives=True`
- Authentication priority: CREDENTIALS_CONFIG → SERVICE_ACCOUNT_PATH → OAuth → ADC

## Decision

**We will use Resource-Level Sharing (current approach) for Service Account authentication.**

The current setup with Service Accounts explicitly added to shared folders/drives is the correct, recommended, and secure pattern. No changes needed to authentication architecture.

### Implementation Details

Each MCP server instance will:
1. Use Service Account credentials from `SERVICE_ACCOUNT_PATH`
2. Specify folder scope via `DRIVE_FOLDER_ID` environment variable
3. Service Account must be explicitly granted permissions to that folder
4. Scopes limited to: `spreadsheets` and `drive`

Example configuration:
```json
{
  "mcpServers": {
    "google-sheets-instance": {
      "command": "mcp-google-sheets",
      "env": {
        "SERVICE_ACCOUNT_PATH": "/path/to/service-account.json",
        "DRIVE_FOLDER_ID": "folder_id_with_explicit_SA_permissions"
      }
    }
  }
}
```

## Consequences

### Positive

- **Security Compliance**: Follows Google Cloud security best practices
- **Clear Audit Trail**: All actions attributed to Service Account, not impersonated users
- **Easy Permission Management**: Standard Drive sharing UI for granting/revoking access
- **Production Ready**: Current implementation validated through testing
- **No Admin Dependency**: Does not require Google Workspace Admin for permission changes
- **Revocation Simplicity**: Remove SA from folder or delete key to revoke access

### Negative

- **Per-Resource Setup**: Service Account must be explicitly added to each folder/drive
- **Collaboration Overhead**: Team members must remember to share resources with SA
- **No User Impersonation**: Cannot act on behalf of specific users (this is actually a positive security-wise)

### Neutral

- **Multiple MCP Instances**: Each AI client can have own SA and folder scope
- **Folder Organization**: Encourages structured Drive organization (folders per use case)
- **Service Account Lifecycle**: Standard GCP SA key rotation and management practices apply

## Verification

Verified through comprehensive CRUD testing:

**Test Spreadsheet A** (`1Qo7ysEI706kpsTYwRX6wQIyy6xfckAVHKzc--gFxlbE`):
- ✅ List sheets
- ✅ Read data (Sheet1!A1:C5)
- ✅ Update cells (added row 6)
- ✅ Create sheet (MCP_Test_20251229_140000)

**Test Spreadsheet B** (`17OEVlMMpZkeCUqIf0Gg7c5YmQUhxpmEeF0o1TsokG1E`):
- ✅ Access empty spreadsheet
- ✅ Write test data
- ✅ Create sheet (2025-12-29_claude-mcp-test)

All operations completed successfully via:
- Claude Desktop MCP integration (`google-sheets-cw`, `google-sheets-local`)
- Service Account with resource-level permissions only
- No domain-wide delegation configured

## Alternatives Considered

### Domain-Wide Delegation

**Rejected** for the following reasons:

1. **Security Risks**
   - DeleFriend vulnerability (CVE-level)
   - Can impersonate super-admins
   - Organization-wide access scope

2. **Operational Complexity**
   - Requires Google Workspace Admin approval
   - Complex OAuth consent screen configuration
   - Difficult to audit and revoke

3. **Use Case Mismatch**
   - Domain-wide delegation intended for organization-wide tools (e.g., backup systems)
   - Our use case: AI agents accessing specific projects/folders
   - Resource-level sharing better fits our access patterns

4. **Google Guidance**
   - Google explicitly discourages domain-wide delegation for new applications
   - Recommends resource-level sharing as default approach

### OAuth 2.0 User Credentials

**Rejected** because:
- Requires interactive browser authentication
- Tokens expire requiring periodic re-authentication
- User-specific (not shared across team/agents)
- Not suitable for automated MCP server scenarios

## References

- [Previous Conversation Context](/Users/smalcolm/.claude/plans/zippy-wondering-parnas.md) - Original investigation and verification plan
- [Google Cloud Service Account Documentation](https://cloud.google.com/iam/docs/service-account-overview)
- [Google Workspace Domain-Wide Delegation](https://developers.google.com/workspace/guides/create-credentials#optional_set_up_domain-wide_delegation_for_a_service_account)
- [DeleFriend Security Research](https://rhinosecuritylabs.com/gcp/delefriend-vulnerability-google-cloud-service-accounts/)
- [mcp-google-sheets Implementation](https://github.com/xing5/mcp-google-sheets)

## Related Issues

Closes: GH-1

## Metadata

- **Author**: Sebastian Malcolm (@sebastianmalcolm)
- **Co-Author**: Claude Sonnet 4.5
- **Date**: 2025-12-29
- **Status**: Accepted
- **Supersedes**: N/A (first ADR)
- **Superseded by**: N/A
