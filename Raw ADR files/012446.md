# Design

## Context

nippo-cli currently uses XDG Base Directory specification for file locations on
Unix systems. However:

- File paths are hardcoded in the codebase
- Windows users cannot use the tool without XDG environment variables
- Users cannot customize paths for their specific needs (e.g., storing
  credentials in a secure location)

### Current File Locations

| File Type      | Current Location                        | Semantic |
| -------------- | --------------------------------------- | -------- |
| Config         | `$XDG_CONFIG_HOME/nippo/nippo.toml`     | Config   |
| Credentials    | `$XDG_DATA_HOME/nippo/credentials.json` | Data     |
| Token          | `$XDG_DATA_HOME/nippo/token.json`       | Data     |
| Templates      | `$XDG_DATA_HOME/nippo/templates/`       | Data     |
| Markdown cache | `$XDG_CACHE_HOME/nippo/md/`             | Cache    |
| Build output   | `$XDG_CACHE_HOME/nippo/output/`         | Cache    |

## Goals / Non-Goals

### Goals

1. Make file paths configurable via `nippo.toml`
2. Provide sensible cross-platform defaults (Unix XDG, Windows APPDATA)
3. Maintain backward compatibility with existing installations
4. Clear separation of config, data, and cache directories

### Non-Goals

1. Complex multi-profile configuration (out of scope)
2. Cloud storage integration for configuration (future consideration)
3. Encryption of sensitive files (handled by file system permissions)

## Decisions

### Decision 1: Path Configuration Structure

Add `[project]` enhancements and a new `[paths]` section to `nippo.toml`:

```toml
[project]
drive_folder_id = "1HNSRS2tJI2t7DKP_8XQJ2NTleSH-rs4y"
site_url = "https://nippo.c18t.me"
url = "https://github.com/c18t/nippo"
branch = "main"
template_path = "/templates"  # Source path in ZIP for templates
asset_path = "/dist"          # Source path in ZIP for static assets

[paths]
# Uncomment and modify to customize file locations.
# data_dir: templates/, assets/, credentials.json, token.json
# cache_dir: md/, output/, nippo-template.zip
# data_dir = "/Users/xxx/.local/share/nippo"
# cache_dir = "/Users/xxx/.cache/nippo"
```

**Note**: `cache_dir` is the base directory where `md/` (markdown cache) and
`output/` (build output) subdirectories are created.

**Rationale**: Grouping path settings under `[paths]` keeps configuration
organized and allows future expansion without polluting the root namespace.
The init command writes `[paths]` section with commented-out defaults, making
all valid configuration options visible to users. Users who want to customize
paths can simply uncomment and modify the values.

### Decision 2: Path Resolution Fallback Chain

The system uses a three-level fallback chain for resolving default paths:

1. **XDG environment variables** (highest priority)
   - `$XDG_CONFIG_HOME/nippo`
   - `$XDG_DATA_HOME/nippo`
   - `$XDG_CACHE_HOME/nippo`

2. **Windows environment variables** (Windows only, when XDG not set)
   - `%APPDATA%\nippo` (config)
   - `%LOCALAPPDATA%\nippo` (data)
   - `%LOCALAPPDATA%\nippo\cache` (cache)

3. **Default XDG paths** (lowest priority fallback)
   - `~/.config/nippo`
   - `~/.local/share/nippo`
   - `~/.cache/nippo`

**Rationale**: XDG environment variables take precedence on all platforms,
allowing users to explicitly control paths. Windows-specific paths provide
sensible defaults for Windows users who haven't set XDG variables. The default
XDG paths ensure the application works even when no environment variables are
set.

**Alternative considered**: Using `os.UserConfigDir()` and `os.UserCacheDir()`.
Rejected because Go's standard library functions don't provide data directory
on Windows, and we want consistent XDG-first behavior across platforms.

### Decision 3: Relative Path Resolution

- Relative paths in configuration are resolved relative to the config file
  directory
- Absolute paths are used as-is
- Environment variables in paths are expanded

**Rationale**: Relative paths allow portable configuration when the config
directory is moved.

### Decision 4: Migration Strategy

1. Existing installations continue to work (defaults unchanged)
2. No automatic migration of files
3. New `paths` section is optional
4. Clear documentation for manual migration if desired

**Rationale**: Avoid data loss or confusion from automatic file moves.

### Decision 5: TOML File Update Behavior

When `init` command updates an existing configuration file:

1. User-entered values are merged with existing configuration
2. Comments in the original file may be lost during rewrite
3. The `[paths]` section is preserved if already present

**Rationale**: Preserving comments perfectly requires complex TOML manipulation.
The trade-off of potentially losing comments is acceptable because:

- Users rarely edit the config file directly after initial setup
- The `[paths]` section with commented defaults is regenerated if missing
- Critical configuration values are always preserved

### Decision 8: Zip Slip Vulnerability Prevention

When extracting files from the template ZIP, the system SHALL validate that
each extracted file path is contained within the intended destination directory:

```go
func isPathSafe(basePath, targetPath string) bool {
    absBase, _ := filepath.Abs(basePath)
    absTarget, _ := filepath.Abs(targetPath)
    return strings.HasPrefix(absTarget, absBase + string(filepath.Separator))
}
```

**Rationale**: The `project.template_path` and `project.asset_path` settings
are user-configurable. Malicious or misconfigured values containing `../` could
cause files to be written outside the intended directory. Validating that the
resolved absolute path starts with the destination directory prevents this
"Zip Slip" vulnerability.

### Decision 7: Git Repository Detection

The `doctor` command checks if `data_dir` is under a git repository by
traversing parent directories looking for `.git`:

```go
func isUnderGitRepo(path string) bool {
    absPath, _ := filepath.Abs(path)
    for {
        gitPath := filepath.Join(absPath, ".git")
        if _, err := os.Stat(gitPath); err == nil {
            return true
        }
        parent := filepath.Dir(absPath)
        if parent == absPath { // reached root
            return false
        }
        absPath = parent
    }
}
```

**Rationale**: This approach doesn't require git to be installed. While it may
miss edge cases like worktrees or submodules, it covers the common case of
accidentally placing credentials in a git repository. The doctor command is for
diagnostics, so reliable operation is more important than perfect accuracy.

**Known Limitations**:

- Git worktrees (`.git` is a file, not a directory) are not detected
- Git submodules with external `.git` references are not detected
- Symbolic links may cause false positives or negatives

These edge cases are acceptable trade-offs for simplicity and portability.

### Decision 6: Separate Auth Command

OAuth authentication is separated from `init` into a dedicated `auth` command:

- `nippo init` - Configuration and template setup only
- `nippo auth` - Google Drive OAuth authentication only

**Rationale**:

1. Simplifies init (no waiting for OAuth flow)
2. Re-authentication is easier (`nippo auth` instead of re-running init)
3. Clear separation of concerns (config vs authentication)
4. init can complete without network access to Google (only needs GitHub for
   templates)

## Risks / Trade-offs

### Risk 1: Configuration Complexity

Adding path configuration increases cognitive load for users.

**Mitigation**: Paths are optional with sensible defaults. Most users never
need to configure them.

### Risk 2: Path Resolution Edge Cases

Complex interactions between relative paths, environment variables, and
platform-specific defaults.

**Mitigation**: Clear precedence rules documented in spec. Comprehensive test
coverage for path resolution.

### Risk 3: Security of Credential Paths

Users might place credentials in insecure locations.

**Mitigation**: Documentation warns about security implications. Application
does not validate path security (user responsibility).

## Open Questions

1. ~~Should we add a `nippo paths` command to show resolved paths?~~
   - **Resolved**: Yes, but as `nippo doctor` command with comprehensive health
     checks instead of just path display
   - Checks configuration validity, directory existence, required files
   - Reports issues with suggested fixes

2. Should environment variables in paths be expanded?
   - Allows `credentials_file = "$HOME/.secrets/nippo-credentials.json"`
   - Cross-platform considerations (Windows uses `%VAR%`)
   - **Resolved**: Yes, use `os.ExpandEnv()` which handles both formats
