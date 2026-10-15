# Design: Front-Matter Support

## Context

nippo-cli currently derives all metadata from filenames (e.g., `2024-01-15.md`).
This limits metadata capabilities and requires filename-based date extraction.
Users want to store explicit `created` and `updated` timestamps within files.

The challenge is maintaining backward compatibility while enabling richer
metadata. Additionally, existing files on Google Drive lack front-matter, so the
system must handle migration gracefully.

## Goals / Non-Goals

**Goals:**

- Parse YAML front-matter from Markdown files
- Provide `format` command to manage front-matter (add to new files, update
  placeholders)
- Maintain backward compatibility with filename-based dates in `build`
- Keep `build` command read-only (no Drive modifications)

**Non-Goals:**

- Support for TOML or JSON front-matter formats
- Custom user-defined front-matter fields (future enhancement)
- Automatic front-matter injection during `build`

## Decisions

### Decision: Separate `format` command for front-matter management

**Rationale:** Separating write operations into a dedicated command follows the
principle of least surprise. Users expect `build` to be a read-only operation.
The `format` command makes the intent explicit and gives users control over
when Drive files are modified. The name `format` reflects its use as a routine
operation in daily workflows, not just a one-time migration.

**Alternatives considered:**

- Auto-inject during build - Violates user expectation of read-only build
- Config flag for auto-inject - Adds complexity, easy to forget

### Decision: Use `go.yaml.in/yaml/v3` for YAML parsing

**Rationale:** Standard, well-maintained Go YAML library. Already commonly used
in the Go ecosystem. Provides robust error handling for malformed YAML. The new
module path `go.yaml.in/yaml/v3` is preferred over the legacy `gopkg.in/yaml.v3`.

### Decision: Manual front-matter extraction

**Rationale:** Implement front-matter parsing manually rather than using a
library like `github.com/adrg/frontmatter`. This approach:

- Allows parsing into `map[string]interface{}` to preserve unknown fields
- Provides full control over edge case handling
- Avoids additional dependencies

**Implementation approach:**

```go
var frontMatterDelimiter = []byte("---")

func ParseFrontMatter(content []byte) (map[string]interface{}, []byte, error) {
    // 1. Check if content starts with "---"
    // 2. Find second "---" delimiter
    // 3. Extract YAML content between delimiters
    // 4. Parse YAML into map[string]interface{}
    // 5. Return parsed map and remaining body content
}
```

When updating front-matter, merge changes into the existing map to preserve
unknown fields, then serialize back to YAML.

### Decision: Use RFC 3339 datetime format with local timezone

**Rationale:** Standard, unambiguous datetime format. Uses local timezone
(e.g., `+09:00` for JST) to preserve the user's local context. Widely supported
across languages and tools.

**Format example:** `2024-01-15T09:30:00+09:00`

### Decision: Omit `updated` field by default

**Rationale:** Prevents the `modifiedTime` from being set to the format
timestamp rather than the actual content update time. The `updated` field is
omitted entirely (not set to empty/null) for cleaner YAML. Users can explicitly
add `updated: now` when they want to capture the current modification time.

### Decision: Preserve unknown fields in front-matter

**Rationale:** Users may add custom fields (e.g., `tags`, `author`) to their
front-matter. The system should not remove these fields when updating
`created` or replacing `now` placeholder. This allows for future extensibility
without data loss.

### Decision: Special `now` placeholder for updated field

**Rationale:** Allows users to mark files for timestamp update without needing
to know the exact time. The format command replaces `now` with Drive's
`modifiedTime`, capturing the actual last edit time. The `now` keyword is
unquoted for ease of use (YAML treats it as a string).

**User workflow:**

1. Edit file content
2. Set `updated: now` in front-matter
3. Save to Drive
4. Run `nippo format` to resolve `now` to actual timestamp

### Decision: Fallback chain for build command

**Priority order:**

1. Front-matter `created` field (explicit user intent)
2. Filename-derived date (`YYYY-MM-DD` pattern)

**Rationale:** Front-matter represents explicit user intent and takes priority.
Filename-based date is used for backward compatibility with existing files that
haven't been processed by `format` yet. This maintains the current behavior for
users who haven't adopted front-matter.

## Component Changes

### `internal/domain/model/nippo.go`

```go
type FrontMatter struct {
    Created time.Time `yaml:"created"`
    Updated time.Time `yaml:"updated,omitempty"`
}

type Nippo struct {
    Date        NippoDate
    FilePath    string
    Content     []byte
    FrontMatter *FrontMatter  // New field
    RemoteFile  *drive.File
}

func ParseFrontMatter(content []byte) (*FrontMatter, []byte, error)
func GenerateFrontMatter(created time.Time) string
func HasFrontMatter(content []byte) bool
func HasNowPlaceholder(content []byte) bool
```

### `internal/adapter/gateway/drive_file_provider.go`

Add `Update` method:

```go
type DriveFileProvider interface {
    // ... existing methods
    Update(fileId string, content []byte) error
}
```

### New files for format command

```text
cmd/format.go
cmd/format_invoker.go
internal/inject/format.go
internal/usecase/port/format.go
internal/usecase/interactor/format.go
internal/adapter/controller/format.go
internal/adapter/presenter/format.go
```

### `internal/core/config.go`

Add format tracking (stored in user's config file):

```go
type Config struct {
    // ... existing fields
    LastFormatTimestamp time.Time `yaml:"last_format_timestamp"`
}
```

The `LastFormatTimestamp` is persisted to the config file and used to determine
which files to process on subsequent `format` runs. On first run (when timestamp
is zero), all files are processed.

**Important:** The timestamp is only updated when format completes without any
failures. If any file fails to upload, the timestamp remains unchanged so that
failed files are reprocessed in the next run.

## Risks / Trade-offs

### Trade-off: Manual format step required

**Accepted:** Users must run `nippo format` to add front-matter to files. This
is intentional to give users control over Drive modifications. The alternative
(auto-inject during build) would surprise users with unexpected writes.

### Risk: User forgets to run format

**Mitigation:** Build command works without front-matter by falling back to
Drive API metadata. Users get correct timestamps even without format. A future
enhancement could add a reminder message during build.

### Risk: Concurrent edits during format

**Mitigation:** Acceptable for single-user workflow. Drive API handles atomic
updates. If user edits a file while format is running, the worst case is that
the front-matter reflects slightly outdated metadata. Documentation should note
that users should not edit files during format execution.

### Trade-off: Skip upload when no changes

**Rationale:** Comparing content before and after processing avoids unnecessary
API calls. This improves performance and prevents updating Drive's `modifiedTime`
when no actual changes were made.

## Open Questions

None - all questions resolved through user clarification.
