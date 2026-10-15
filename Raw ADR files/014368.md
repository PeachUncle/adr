# ADR-001: GitHub Integration Approach for Portfolio Project Scaffolding

**Status:** Proposed  
**Date:** 2025-10-29  
**Deciders:** Chris Clements  
**Tier:** Portfolio Meta  
**Project:** Portfolio Project Scaffolding System

---

## Context

Portfolio Project Scaffolding System needs to create GitHub repositories as part of project initialization. Two main approaches exist: GitHub CLI (`gh`) vs direct REST API integration.

**Use case:**
- Create new GitHub repo when scaffolding project
- Set repo metadata (description, visibility, topics)
- Configure labels, branch protection, settings
- Push initial commit

---

## Decision Drivers

* **Simplicity:** Easy to implement and maintain
* **Reliability:** Works consistently across environments
* **Features:** Supports needed GitHub operations
* **Dependencies:** Minimal external dependencies
* **CI/Headless:** Works in automated/CI contexts
* **Error Handling:** Clear failure modes and recovery
* **User Experience:** Intuitive for human users

---

## Considered Options

### Option 1: GitHub CLI (`gh`) Primary

**Description:**
Use `gh` CLI as primary integration method with REST API fallback

**Implementation:**
```powershell
# Check if gh available
if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh repo create $owner/$slug `
        --$visibility `
        --description $description `
        --source . `
        --remote origin `
        --push
} else {
    # Fallback to REST API
    Invoke-GitHubAPI -Method POST -Endpoint "/user/repos" -Body @{...}
}
```

**Pros:**
- ✅ Simple, declarative commands
- ✅ Handles authentication automatically (gh auth login)
- ✅ Supports complex operations (labels, branch protection, secrets)
- ✅ Good error messages and user feedback
- ✅ Actively maintained by GitHub
- ✅ Works with both personal and org repos
- ✅ Can pipe output for automation

**Cons:**
- ⚠️ External dependency (must be installed)
- ⚠️ Requires PATH configuration
- ⚠️ Another tool to maintain/version
- ⚠️ Might not be available in some CI environments

**Cost/Effort:** Low - `gh` is already familiar and installed

---

### Option 2: REST API Direct

**Description:**
Use GitHub REST API directly via PowerShell `Invoke-RestMethod`

**Implementation:**
```powershell
$headers = @{
    Authorization = "Bearer $env:GITHUB_TOKEN"
    Accept = "application/vnd.github.v3+json"
}

$body = @{
    name = $slug
    description = $description
    private = ($visibility -eq "private")
    auto_init = $false
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "https://api.github.com/user/repos" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

**Pros:**
- ✅ No external dependencies
- ✅ Full control over API calls
- ✅ Works in any PowerShell environment
- ✅ Easy to customize and extend
- ✅ Direct error handling

**Cons:**
- ⚠️ More code to write and maintain
- ⚠️ Need to handle auth manually (GITHUB_TOKEN)
- ⚠️ More complex operations require multiple API calls
- ⚠️ Need to handle rate limiting, pagination, errors
- ⚠️ Less intuitive for human users (token management)

**Cost/Effort:** Medium - More code, more edge cases

---

### Option 3: Hybrid (gh Primary, REST Fallback)

**Description:**
Use `gh` when available, fall back to REST API when not

**Implementation:**
```powershell
function New-GitHubRepo {
    param($Owner, $Slug, $Description, $Visibility)
    
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        # Use gh CLI
        gh repo create "$Owner/$Slug" `
            --$Visibility `
            --description $Description `
            --source . `
            --push
    }
    elseif ($env:GITHUB_TOKEN) {
        # Fallback to REST API
        $result = Invoke-RestMethod `
            -Uri "https://api.github.com/user/repos" `
            -Method POST `
            -Headers @{ Authorization = "Bearer $env:GITHUB_TOKEN" } `
            -Body (@{ name=$Slug; private=($Visibility -eq "private") } | ConvertTo-Json)
        
        # Manual git remote add + push
        git remote add origin $result.clone_url
        git push -u origin main
    }
    else {
        throw "GitHub integration unavailable: Install 'gh' CLI or set GITHUB_TOKEN"
    }
}
```

**Pros:**
- ✅ Best of both worlds
- ✅ Works in more environments
- ✅ `gh` simplicity when available
- ✅ REST fallback for CI/automation
- ✅ Graceful degradation

**Cons:**
- ⚠️ More complex implementation
- ⚠️ Two code paths to maintain and test
- ⚠️ Potential for inconsistent behavior between paths

**Cost/Effort:** Medium - Both approaches needed

---

## Decision Outcome

**Chosen option:** **Option 3 - Hybrid (gh Primary, REST Fallback)**

**Rationale:**
- `gh` CLI provides best user experience and is already installed/familiar
- REST API fallback ensures automation works in CI environments
- Hybrid approach maximizes reliability across contexts
- Can start with `gh` only and add REST fallback later if needed
- Most flexible for future needs (human interactive AND automated)

**Decision:**
- Implement `gh` CLI integration first (Phase 1)
- Add REST API fallback second (Phase 2)
- Graceful error if neither available

---

## Consequences

### Positive Consequences

- ✅ Works for human users (gh auth login flow)
- ✅ Works in CI/automation (GITHUB_TOKEN fallback)
- ✅ Simple mental model (try gh, fall back to API)
- ✅ Can leverage gh's advanced features (secrets, variables, etc.)
- ✅ Future-proof (both methods maintained)

### Negative Consequences

- ⚠️ Two code paths require testing
- ⚠️ More complex than single-approach
- ⚠️ Need to keep both paths feature-equivalent (migration: Medium)

### Neutral Consequences

- ℹ️ Users need either `gh` OR `GITHUB_TOKEN` (acceptable trade-off)
- ℹ️ Documentation must cover both approaches

---

## Implementation

### Phase 1: gh CLI Integration (Week 1)

```powershell
function New-GitHubRepoViaGH {
    # Requires: gh CLI installed and authenticated
    # Handles: Repo creation, remote setup, initial push
}
```

**Features:**
- Repo creation with visibility/description
- Labels configuration (via `gh label create`)
- Topic/tag setting (via `gh repo edit`)

**Validation:**
- Check `gh` available: `Get-Command gh`
- Check `gh` authenticated: `gh auth status`
- Provide helpful error if not setup

---

### Phase 2: REST API Fallback (Week 2-3)

```powershell
function New-GitHubRepoViaAPI {
    # Requires: $env:GITHUB_TOKEN
    # Handles: Same operations via REST API
}
```

**Features:**
- Repo creation (POST /user/repos or /orgs/{org}/repos)
- Labels (POST /repos/{owner}/{repo}/labels)
- Topics (PUT /repos/{owner}/{repo}/topics)
- Manual git remote + push

**Token scopes needed:** `repo` (full control of private repos)

---

### Testing Strategy

**Test both paths:**
- ✅ Human interactive (gh auth login)
- ✅ CI automated (GITHUB_TOKEN env var)
- ✅ Graceful degradation
- ✅ Error messages helpful

**Edge cases:**
- Repo already exists (both methods)
- Auth failures (both methods)
- Network failures
- Rate limiting (REST API)

---

## Validation

### Success Criteria

**Within 2 weeks:**
- ✅ `gh` CLI path works for repo creation
- ✅ REST API fallback functional
- ✅ Both paths tested and documented
- ✅ Error handling graceful

**Metrics:**
- Success rate: >95% for repo creation
- User satisfaction: "Just works"
- CI compatibility: 100%

**Review date:** 2025-11-15

---

## Related Decisions

**Depends on:**
- Project template structure (needs repo to push to)
- .portfolio-meta.yaml schema (defines GitHub settings)

**Enables:**
- Automated project scaffolding (MVP feature)
- Concept graduation workflow
- Ideas-inbox integration

---

## AI Context

**AI-CONTEXT:**
- Always try `gh` CLI first (better UX, more reliable)
- Only use REST API if `gh` unavailable
- Never commit GITHUB_TOKEN to code
- Handle errors gracefully with helpful messages
- Log all GitHub operations for audit

---

## Links & References

**Documentation:**
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub REST API - Repos](https://docs.github.com/en/rest/repos/repos)

**Code:**
- Implementation: `00-meta/30-automation/scaffolding/github-integration.ps1`
- Tests: (to be created)

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-29  
**Review Date:** 2025-11-15
