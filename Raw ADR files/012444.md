# Design: Fix directory creation and improve error messages

## Overview

This change ensures required directories are created before file operations and
provides helpful error messages when credentials are missing, preventing
initialization failures on fresh systems.

## Current Behavior

### Config Loading

`internal/core/config.go` loads configuration as follows:

```go
func (c *Config) LoadConfig(filePath string) error {
    // ... setup viper config path ...

    err := viper.ReadInConfig()
    if err != nil {
        switch err.(type) {
        case viper.ConfigFileNotFoundError:
            _ = viper.SafeWriteConfig()  // FAILS if directory doesn't exist
        default:
            return err
        }
    }
    return viper.Unmarshal(c)
}
```

### OAuth Credentials Loading

`internal/usecase/interactor/init_save_drive_token.go` reads credentials:

```go
dataDir := core.Cfg.GetDataDir()
b, err := os.ReadFile(filepath.Join(dataDir, "credentials.json"))
if err != nil {
    // Unhelpful error: "unable to read client secret file: %v"
    u.presenter.Suspend(fmt.Errorf("unable to read client secret file: %v", err))
    return
}
```

Similar code in `internal/adapter/gateway/drive_file_provider.go:104-106`.

## Proposed Implementation

### Config Directory Creation

Add directory creation before `SafeWriteConfig()` in `internal/core/config.go`:

```go
case viper.ConfigFileNotFoundError:
    // Ensure config directory exists
    configDir := c.GetConfigDir()
    if err := os.MkdirAll(configDir, 0755); err != nil {
        return fmt.Errorf("failed to create config directory: %w", err)
    }
    // Now safe to write config
    if err := viper.SafeWriteConfig(); err != nil {
        return fmt.Errorf("failed to write config: %w", err)
    }
```

### Data Directory Creation and Error Message

Update `internal/usecase/interactor/init_save_drive_token.go`:

```go
dataDir := core.Cfg.GetDataDir()

// Ensure data directory exists
if err := os.MkdirAll(dataDir, 0755); err != nil {
    u.presenter.Suspend(fmt.Errorf("failed to create data directory: %w", err))
    return
}

credPath := filepath.Join(dataDir, "credentials.json")
b, err := os.ReadFile(credPath)
if err != nil {
    if os.IsNotExist(err) {
        u.presenter.Suspend(fmt.Errorf(`credentials.json not found

Please download the OAuth 2.0 Client ID credentials from Google Cloud Console:

1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Application type: Desktop app)
3. Download the credentials JSON file
4. Save it to: %s`, credPath))
    } else {
        u.presenter.Suspend(fmt.Errorf("unable to read credentials file: %w", err))
    }
    return
}
```

### Drive Provider Error Message Only

Update `internal/adapter/gateway/drive_file_provider.go` with the same helpful
error message pattern, but **without** directory creation. Directory creation
is the responsibility of the `init` command, not the file provider.

```go
credPath := filepath.Join(dataDir, "credentials.json")
b, err := os.ReadFile(credPath)
if err != nil {
    if os.IsNotExist(err) {
        return nil, fmt.Errorf(`credentials.json not found

Please download the OAuth 2.0 Client ID credentials from Google Cloud Console:

1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Application type: Desktop app)
3. Download the credentials JSON file
4. Save it to: %s

Note: Run 'nippo init' to set up your environment.`, credPath)
    }
    return nil, fmt.Errorf("unable to read credentials file: %w", err)
}
```

## Design Decisions

### Directory Creation Pattern

**Decision**: Use `os.MkdirAll(dir, 0755)` pattern

**Rationale**:

- Consistent with existing codebase patterns (see
  `local_file_provider.go:71`, `template_service.go:24`,
  `nippo.go:163`)
- `MkdirAll` is idempotent (succeeds if directory already exists)
- Permission `0755` is standard for config directories (user: rwx, group/other:
  rx)

### Error Handling for File Operations

**Decision**: Return wrapped errors instead of ignoring them

**Rationale**:

- Current code silently ignores `SafeWriteConfig()` errors (`_ = ...`)
- Proper error handling helps users diagnose issues
- Follows Go error handling best practices with `fmt.Errorf` and `%w`

**Alternative Considered**: Keep ignoring errors

- **Rejected**: Silent failures make troubleshooting difficult

### User-Friendly credentials.json Error

**Decision**: Provide step-by-step instructions when credentials.json is missing

**Rationale**:

- New users don't know what "client secret file" means
- Google Cloud Console workflow is not obvious
- Showing the exact file path helps users place the file correctly
- Distinguishing "not found" from other read errors provides better UX

**Error Message Structure**:

1. What's missing ("credentials.json not found")
2. What it's for (implied by mentioning OAuth 2.0)
3. How to get it (numbered steps)
4. Where to put it (exact path)

**Alternative Considered**: Just show generic "file not found" error

- **Rejected**: Doesn't help users understand what to do next

### Location of Directory Creation

**Decision**: Create directories where they are first needed (config in
`LoadConfig()`, data in `init` command)

**Rationale**:

- Config directory: Created in `LoadConfig()` where the error occurs
- Data directory: Created in `init_save_drive_token` interactor, not in file
  providers
- File providers should not have side effects like directory creation
- Keeps directory creation as part of initialization, not data access

**Alternative Considered**: Create directory in `GetDataDir()` or file providers

- **Rejected**: Getters and providers should not have side effects

## Testing Strategy

1. **Fresh System Test**: Run `init` command with no existing directories
2. **Existing Directory Test**: Run `init` when directories already exist
3. **Missing credentials.json Test**: Verify helpful error message when file
   doesn't exist
4. **Permission Error Test**: Verify error message when directory creation
   fails (e.g., read-only filesystem)
5. **Other File Errors Test**: Verify error handling for non-existence errors
   (e.g., permission denied on existing file)

## Impact Analysis

- **Files Modified**:
  - `internal/core/config.go` - Config directory creation
  - `internal/usecase/interactor/init_save_drive_token.go` - Data directory
    creation and helpful error
  - `internal/adapter/gateway/drive_file_provider.go` - Helpful error message
- **Breaking Changes**: None
- **Behavioral Changes**:
  - Config and data directories now created automatically (positive change)
  - Error messages for missing credentials are more helpful (positive change)
- **Performance Impact**: Negligible (one-time directory creation)

## Rollback Plan

If issues arise, revert the commit(s) that modified the following files:

- `internal/core/config.go`
- `internal/usecase/interactor/init_save_drive_token.go`
- `internal/adapter/gateway/drive_file_provider.go`
