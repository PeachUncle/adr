---
docid: ADR-075
title: ADR 032 Cli Auto Update Brainstorm
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# CLI Auto-Update Functionality - Brainstorm

**Date:** January 5, 2026  
**Context:** ADR-031 CLI Architecture Split  
**Authors:** @Architect, @DevOps, @Security  
**Status:** Brainstorm - Initial Ideas

---

> ⚠️ **Pre-Release Notice (GL-014)**  
> B2X is currently in v0.x pre-release development. CLI commands and APIs may change without deprecation cycles. Backwards compatibility is NOT guaranteed until v1.0.0 release. See [GL-014] for details.

---

## Problem Statement

CLI tools need to stay current with:
- Security patches and vulnerability fixes
- New features and bug fixes
- API compatibility updates
- Performance improvements

Current challenges:
- Manual update process (`dotnet tool update`) requires user awareness
- Version drift across different users/teams
- Delayed security patch application
- Inconsistent tool versions in CI/CD pipelines

---

## Solution Concepts

### 1. Native .NET Tool Updates
**Leverage existing `dotnet tool` ecosystem**

#### Implementation
```bash
# Automatic update check on startup
dotnet tool update B2X.CLI.Administration --global

# Or via package management
dotnet tool update --all --global
```

#### Pros
- ✅ Uses established .NET tooling
- ✅ No custom implementation needed
- ✅ Handles dependencies automatically
- ✅ Works offline (when packages cached)

#### Cons
- ❌ Requires .NET SDK installed
- ❌ No selective update control
- ❌ No rollback capability
- ❌ No progress indication

### 2. Custom Update Service
**Build update checker into CLI itself**

#### Architecture
```
CLI Startup Flow:
1. Check for updates (configurable)
2. Download new version if available
3. Replace executable
4. Restart with new version
```

#### Implementation Options

**Option A: GitHub Releases Integration**
```csharp
public class UpdateService
{
    private readonly HttpClient _client;
    private readonly string _currentVersion;
    private readonly string _repoUrl;

    public async Task<UpdateInfo> CheckForUpdates()
    {
        var releases = await _client.GetFromJsonAsync<GitHubRelease[]>(
            $"{_repoUrl}/releases"
        );

        var latest = releases.FirstOrDefault(r => !r.Prerelease);
        return latest?.TagName != _currentVersion
            ? new UpdateInfo { Available = true, Version = latest.TagName }
            : new UpdateInfo { Available = false };
    }
}
```

**Option B: Internal Update API**
```csharp
// For Operations CLI (internal)
var updateUrl = "https://updates.B2X.internal/api/cli-updates";

// For Administration CLI (public)
var updateUrl = "https://api.B2X.com/cli-updates";
```

**Option C: Self-Contained Updater**
```bash
# CLI downloads updater executable
curl -o updater.exe https://updates.B2X.com/updater.exe
./updater.exe --update-cli --version latest
```

#### Pros
- ✅ Full control over update process
- ✅ Can implement rollback
- ✅ Progress indication possible
- ✅ Version-specific updates
- ✅ Can work without .NET SDK

#### Cons
- ❌ Complex implementation
- ❌ Security risks (malicious updates)
- ❌ Platform-specific binaries needed
- ❌ Network dependency

### 3. Hybrid Approach
**Combine native tooling with custom enhancements**

#### Implementation
```csharp
public class SmartUpdateService
{
    public async Task UpdateIfNeeded(UpdateMode mode)
    {
        switch (mode)
        {
            case UpdateMode.Automatic:
                await PerformSilentUpdate();
                break;
            case UpdateMode.Notify:
                var update = await CheckForUpdates();
                if (update.Available)
                    await PromptUser(update);
                break;
            case UpdateMode.Manual:
                // User-initiated only
                break;
        }
    }
}
```

---

## Security Considerations

### Update Verification
- **Code Signing:** All releases must be signed
- **Checksum Verification:** SHA256 hashes for integrity
- **Certificate Pinning:** Prevent MITM attacks
- **Trust Chain:** Validate update source authenticity

### Attack Vectors
- **Malicious Updates:** Compromised update server
- **Downgrade Attacks:** Force older vulnerable versions
- **Update Spam:** Frequent unnecessary updates
- **Network Interception:** Man-in-the-middle during download

### Mitigation Strategies
```csharp
public class SecureUpdateService
{
    private readonly ICertificateValidator _certValidator;
    private readonly IChecksumVerifier _checksumVerifier;

    public async Task<bool> VerifyUpdate(UpdatePackage package)
    {
        // Verify certificate chain
        if (!await _certValidator.Validate(package.Certificate))
            throw new SecurityException("Invalid certificate");

        // Verify checksum
        if (!await _checksumVerifier.Verify(package.Checksum))
            throw new SecurityException("Checksum mismatch");

        return true;
    }
}
```

---

## Command Stability & Backward Compatibility

### Critical Requirement: Released Commands Must Remain Functional

**Core Principle:** Once a CLI command is released to customers, its interface and behavior must remain stable. CLI commands are public APIs with stability guarantees.

#### Command Interface Contract
```csharp
// Example: Stable command interface
[Command("tenant", "create", Description = "Create a new tenant")]
public class CreateTenantCommand : BaseCommand
{
    [Option("--name", Required = true, Description = "Tenant name")]
    public string Name { get; set; }

    [Option("--domain", Description = "Tenant domain (optional)")]
    public string? Domain { get; set; }

    // Interface must remain stable once released
    public override async Task<int> ExecuteAsync()
    {
        // Implementation can change, but interface cannot
    }
}
```

#### Breaking Change Policy
1. **Major Version (X.0.0):** Breaking changes allowed
2. **Minor Version (x.Y.0):** New features, backward compatible
3. **Patch Version (x.y.Z):** Bug fixes only

#### Deprecation Strategy
**Deprecated commands must provide clear guidance and remain functional during transition period.**

```csharp
[Obsolete("Use 'tenant create' instead. Will be removed in v3.0.0")]
[Command("create-tenant", "Legacy command - use 'tenant create'")]
public class LegacyCreateTenantCommand : BaseCommand
{
    public override async Task<int> ExecuteAsync()
    {
        // Show deprecation warning with guidance
        await _console.Output.WriteLineAsync(
            new Markup($"[yellow]⚠️  Command 'create-tenant' is deprecated[/]\n" +
                      $"   Use: [green]B2X-admin tenant create --name <name>[/]\n" +
                      $"   This command will be removed in v3.0.0"));

        // Still execute the command for backward compatibility
        return await ExecuteTenantCreationLogic();
    }
}
```

### User-Friendly Deprecation Messages

**Console Output Examples:**

```bash
# Running deprecated command
$ B2X-admin create-tenant --name "My Company"

⚠️  Command 'create-tenant' is deprecated
   New command: B2X-admin tenant create --name "My Company"
   Migration: This command will be removed in v3.0.0 (January 2027)

   Proceeding with legacy command execution...
   ✅ Tenant "My Company" created successfully

# Suggestion for similar commands
$ B2X-admin user-add --email john@company.com

⚠️  Command 'user-add' is deprecated
   New command: B2X-admin auth create-user --email john@company.com
   Alternative: B2X-admin user invite --email john@company.com
   Migration: This command will be removed in v3.0.0

   Proceeding with legacy command execution...
   ✅ User john@company.com added successfully
```

### Deprecation Warning Levels

1. **Info (v2.x):** Show warning but allow execution
2. **Warning (v2.9+):** Show prominent warning with migration guide
3. **Error (v3.0):** Command removed, show migration instructions

### Migration Assistance

**Automatic Command Translation:**
```csharp
public class CommandMigrator
{
    public static string GetMigrationHint(string deprecatedCommand, string[] args)
    {
        return deprecatedCommand switch
        {
            "create-tenant" => $"B2X-admin tenant create {string.Join(" ", args)}",
            "user-add" => $"B2X-admin auth create-user {string.Join(" ", args)}",
            "catalog-import" => $"B2X-admin catalog import {string.Join(" ", args)}",
            _ => "Please check the documentation for the new command syntax"
        };
    }
}
```

**Interactive Migration:**
```bash
$ B2X-admin create-tenant --name "Test"

⚠️  Command 'create-tenant' is deprecated

Would you like to:
  [R] Run the new command automatically
  [S] Show me the new command syntax
  [C] Continue with deprecated command
  [?] Help

Choice: R

Executing: B2X-admin tenant create --name "Test"
✅ Tenant "Test" created successfully
```

### Version Pinning for Stability
**Allow users to pin to specific versions when stability is critical:**

```bash
# Pin to specific version
dotnet tool install B2X.CLI.Administration --version 2.1.0 --global

# Update only within major version
B2X-admin update --allow-major=false

# Enterprise: Lock to approved versions
export B2X_CLI_PIN_VERSION="2.1.*"
```

### Semantic Versioning for CLI
- **MAJOR:** Breaking command changes, removed commands
- **MINOR:** New commands, new options (backward compatible)
- **PATCH:** Bug fixes, security patches, performance improvements

### Backward Compatibility Testing
```csharp
[TestFixture]
public class BackwardCompatibilityTests
{
    [Test]
    public async Task ReleasedCommands_RemainFunctional_AfterUpdate()
    {
        // Test all released command interfaces
        var result = await RunCommand("tenant create --name test");
        Assert.That(result.ExitCode, Is.EqualTo(0));
    }

    [Test]
    public async Task DeprecatedCommands_ShowMigrationGuidance()
    {
        // Test deprecated commands show helpful migration hints
        var result = await RunCommand("create-tenant --name test");

        // Should show deprecation warning
        Assert.That(result.StdOut, Contains("⚠️"));
        Assert.That(result.StdOut, Contains("deprecated"));
        Assert.That(result.StdOut, Contains("tenant create --name test"));

        // Should still execute successfully
        Assert.That(result.ExitCode, Is.EqualTo(0));
        Assert.That(result.StdOut, Contains("created successfully"));
    }

    [Test]
    public async Task DeprecationMessages_AreUserFriendly()
    {
        var result = await RunCommand("user-add --email test@example.com");

        // Check for clear migration guidance
        Assert.That(result.StdOut, Contains("New command:"));
        Assert.That(result.StdOut, Contains("auth create-user"));
        Assert.That(result.StdOut, Contains("Will be removed in v"));
    }

    [Test]
    public async Task CommandTranslation_WorksCorrectly()
    {
        var translator = new CommandMigrator();

        // Test various deprecated command translations
        Assert.That(translator.GetMigrationHint("create-tenant", ["--name", "Test"]),
                   Is.EqualTo("B2X-admin tenant create --name Test"));

        Assert.That(translator.GetMigrationHint("user-add", ["--email", "user@test.com"]),
                   Is.EqualTo("B2X-admin auth create-user --email user@test.com"));
    }
}
```

### Migration Path for Breaking Changes
1. **Phase 1:** Add new command alongside old
2. **Phase 2:** Mark old command as deprecated with warnings
3. **Phase 3:** Remove old command in next major version
4. **Phase 4:** Provide migration scripts for automation

### Enterprise Considerations
- **Air-gapped environments:** Allow offline version pinning
- **Change management:** Integration with enterprise approval workflows
- **Audit trails:** Track which versions are deployed where
- **Rollback windows:** Extended support for previous versions

---

## User Experience Design

### Update Modes
1. **Silent (Automatic)**
   - Updates happen in background
   - No user interaction required
   - Best for CI/CD and automated environments

2. **Notify (User Choice)**
   - CLI notifies of available update
   - User decides when to update
   - Good balance of automation and control

3. **Manual (User Initiated)**
   - User explicitly runs update command
   - Full control over timing
   - Minimal automation

### Configuration
```json
{
  "updates": {
    "mode": "notify",
    "checkInterval": "24h",
    "autoRestart": true,
    "rollbackEnabled": true,
    "maxDownloadSize": "50MB"
  }
}
```

### User Interface
```
🔄 Update available: v2.1.0 (current: v2.0.0)
   New features: Enhanced catalog import, security fixes
   Release notes: https://github.com/B2X/cli/releases/v2.1.0

   [U] Update now  [L] Later  [N] Never ask again  [?] More info
```

### Deprecation User Interface

**Clear, Helpful Deprecation Messages:**

```
⚠️  Command 'create-tenant' is deprecated
   New command: B2X-admin tenant create --name <name>
   Migration: This command will be removed in v3.0.0 (January 2027)

   Proceeding with legacy command execution...
   ✅ Tenant "My Company" created successfully
```

**Interactive Migration Options:**

```
⚠️  Command 'user-add' is deprecated

Would you like to:
  [R] Run the new command automatically (recommended)
  [S] Show me the new command syntax
  [C] Continue with deprecated command
  [?] Help

Choice (R/s/c/?):
```

**Progressive Warning Levels:**

```
# v2.x - Info Level
⚠️  'create-tenant' is deprecated. Consider using 'tenant create' instead.

# v2.9+ - Warning Level  
🚨 DEPRECATED: 'create-tenant' will be removed in v3.0.0
   Use: B2X-admin tenant create --name <name>
   Docs: https://docs.B2X.com/cli/migration

# v3.0+ - Error Level
❌ Command 'create-tenant' has been removed
   Migration: Use 'B2X-admin tenant create --name <name>'
   Help: Run 'B2X-admin tenant create --help'
```

---

## Platform-Specific Considerations

### Windows
- Use Windows Update APIs for integration
- Support for enterprise update policies
- Handle UAC prompts for system-level updates

### macOS
- Integration with Sparkle framework
- App Store sandbox considerations
- Gatekeeper compatibility

### Linux
- Package manager integration (apt, yum, etc.)
- Systemd service updates
- Container environment handling

### CI/CD Environments
- Respect CI/CD environment variables
- No interactive prompts
- Prefer silent updates
- Integration with deployment pipelines

---

## Implementation Complexity

### Effort Estimate
- **Basic Version Check:** 2-3 days
- **Full Auto-Update:** 1-2 weeks
- **Cross-Platform:** Additional 1 week
- **Security Hardening:** 3-5 days
- **Testing:** 1 week

### Dependencies
- **NuGet Packages:**
  - `System.Net.Http.Json` (for API calls)
  - `Microsoft.Extensions.Http` (for HTTP client)
  - `Octokit` (GitHub API integration)

- **External Services:**
  - Update metadata API
  - CDN for binary distribution
  - Certificate authority for signing

### Testing Requirements
- Unit tests for update logic
- Integration tests for update process
- Network failure simulation
- Rollback testing
- Cross-platform compatibility
- Security testing (penetration testing)

---

## Business Impact

### Benefits
- **Security:** Faster patch deployment
- **User Experience:** Always current features
- **Support:** Reduced "please update" tickets
- **Compliance:** Easier to enforce version standards

### Risks
- **Downtime:** Failed updates could break CLI
- **Support:** More complex troubleshooting
- **Cost:** Development and maintenance overhead
- **Compatibility:** Update conflicts with custom environments

### Success Metrics
- **Adoption Rate:** % of users with auto-update enabled
- **Update Success Rate:** % of updates that complete successfully
- **Time to Update:** Average time between release and user update
- **Support Ticket Reduction:** % decrease in version-related issues

---

## Recommended Approach

### Phase 1: Basic Update Notification + Stability Foundation (Low Risk)
```bash
# Add to CLI startup
B2X-admin check-updates
B2X-admin update
```

**Implementation:**
- Simple version check against GitHub releases
- Manual update command
- No automatic downloads
- Easy rollback via `dotnet tool`
- **Stability:** Establish semantic versioning policy
- **Testing:** Basic backward compatibility tests

### Phase 2: Smart Update Service + Command Stability (Medium Risk)
- Background update checking
- User notification system
- Safe update process with rollback
- Configuration management
- **Stability:** Command interface contracts
- **Testing:** Comprehensive backward compatibility test suite
- **Migration:** Deprecation warnings for changed commands

### Phase 3: Full Automation + Enterprise Stability (High Risk)
- Silent updates for CI/CD
- Advanced rollback capabilities
- Enterprise integration
- Advanced security features
- **Stability:** Version pinning, enterprise change management
- **Testing:** Cross-version compatibility matrix
- **Migration:** Automated migration scripts for breaking changes

---

## Integration with ADR-031

### Operations CLI (Internal)
- **Update Mode:** Automatic (silent updates)
- **Update Source:** Internal artifact repository
- **Security:** Enterprise certificate validation
- **Monitoring:** Update success/failure telemetry

### Administration CLI (Customer-Facing)
- **Update Mode:** Notify (user choice)
- **Update Source:** Public NuGet or GitHub releases
- **Security:** Standard code signing
- **Monitoring:** Anonymous usage telemetry

### Shared Library Integration
```csharp
// Add to B2X.CLI.Shared
public interface IUpdateService
{
    Task<UpdateInfo> CheckForUpdates();
    Task UpdateToVersion(string version);
    Task RollbackVersion();
}
```

---

## Next Steps

1. **Stability Assessment:** Audit current commands for interface stability
2. **Versioning Policy:** Define semantic versioning for CLI releases
3. **Prototype:** Build basic update checker with stability guarantees
4. **Security Review:** Validate approach with @Security (including stability risks)
5. **User Research:** Survey potential users on update preferences and stability needs
6. **Technical Spike:** Implement proof-of-concept with backward compatibility tests
7. **Decision:** Create ADR for auto-update feature with stability requirements

---

## Open Questions

- Should updates be enabled by default?
- How to handle enterprise proxy environments?
- What's the update check frequency?
- How to handle beta/pre-release versions?
- Should we support offline updates?
- Integration with existing deployment pipelines?
- **Stability:** How long to support deprecated commands?
- **Stability:** What constitutes a "breaking change" for CLI commands?
- **Stability:** How to communicate breaking changes to customers?
- **Stability:** Should we offer LTS (Long Term Support) versions?

---

**Status:** Brainstorm Complete - Ready for prototyping  
**Next Action:** Create technical spike for basic update notification</content>
<parameter name="filePath">/Users/holger/Documents/Projekte/B2X/.ai/decisions/ADR-032-cli-auto-update-brainstorm.md