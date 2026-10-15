# ADR-0002: Greenfield Binary Gems Architecture

**Date:** 2026-01-01
**Status:** Proposed
**Decision Maker(s):** Repository Owner
**Supersedes:** N/A (this repo to be retired after migration)

---

## Context

**Problem Statement:**
The current `lich5-gtk3-gems` repository successfully demonstrates building precompiled binary gems for Windows UCRT (Ruby 3.3+), but has accumulated technical debt and architectural limitations that prevent it from scaling to multiple gem suites and supporting an automated installer build process.

**Background:**
Through iterative development, we identified 13 concerns that need to be addressed:

| # | Concern | Summary |
|---|---------|---------|
| 1 | Pristine gem sources vs. modifications | Track modifications vs CI transforms |
| 2 | DRY: 1500+ line workflow | Refactor to reusable workflows |
| 3 | Hardcoded gem versions | Dynamic from rubygems.org |
| 4 | Generic dependency capture | Auto-discover build deps |
| 5 | Generic repo population/update | Pull upstream, apply mods |
| 6 | Repo architecture | Multi-suite support (GTK3, Nokogiri, SQLite3) |
| 7 | Dev vs User gem loads | Different gem configs for installs |
| 8 | InnoSetup automation | Build & release installer |
| 9 | CI Ruby version matrix | Test across Ruby versions |
| 10 | CI workflow configuration abstraction | Heavy abstraction layer |
| 11 | Artifact naming inconsistency | mingw32 vs mingw-ucrt |
| 12 | No install/require validation | Build succeeds != gem works |
| 13 | Workarounds not self-documenting | rcairo, CFLAGS hacks |

**Constraints:**
- Must support Ruby 3.3, 3.4, and 4.0 on Windows x64 UCRT
- Must keep gem source as close to upstream as possible
- Must support multiple gem suites beyond GTK3
- Must integrate with InnoSetup installer build process
- Must follow SOLID principles with emphasis on DRY
- **Build stability over freshness:** Rebuilds are annual (Ruby version cycle) or manual (security/critical fixes), NOT triggered by every upstream version bump

---

## Decision

Adopt **Option B: No Vendoring - Fetch & Patch at Build Time** for the new `lich5-binary-gems` repository.

**Implementation:**

```
lich5-binary-gems/
├── .github/workflows/
│   ├── _build-gem.yml          # Reusable: build single gem
│   ├── _consolidate-gem.yml    # Reusable: consolidate Ruby versions
│   ├── _validate-gem.yml       # Reusable: install + require test
│   ├── suite-gtk3.yml          # Orchestrator for GTK3 suite
│   ├── suite-nokogiri.yml      # Orchestrator for Nokogiri suite
│   └── release-installer.yml   # InnoSetup build & release
├── config/
│   ├── suites/
│   │   ├── gtk3.yml            # GTK3 suite definition
│   │   ├── nokogiri.yml        # Nokogiri suite definition
│   │   └── sqlite3.yml         # SQLite3 suite definition
│   └── ruby-versions.yml       # Supported Ruby versions
├── patches/
│   └── gtk3/
│       ├── platform-ucrt.patch # gemspec platform fix
│       └── README.md           # Documents each patch
├── scripts/
│   ├── fetch-gem-source.rb     # Fetch from rubygems.org
│   ├── apply-patches.rb        # Apply suite patches
│   ├── discover-dependencies.rb # Auto-discover deps
│   └── validate-install.rb     # Install + require test
└── docs/
    ├── adr/                    # Architecture decisions
    └── patches/                # Patch documentation
```

---

## Options Considered

### Option A: Monorepo with Vendored Source (Current Pattern, Improved)

Keep gem source in repo, add abstraction layers.

**Pros:**
- Reproducible builds (offline-capable)
- Clear audit trail of source
- Works today (proven)

**Cons:**
- Large repository size
- Manual update burden
- Merge conflicts with upstream
- Difficult to scale to multiple suites

### Option B: No Vendoring - Fetch & Patch at Build Time

Don't store gem source. Fetch from rubygems.org, apply patches dynamically.

**Pros:**
- Always current with upstream versions
- Small repository footprint
- Clean separation of concerns
- Scales naturally to multiple suites
- rubygems.org API provides version AND dependency info

**Cons:**
- Requires network at build time
- Patch maintenance as upstream changes
- Build reproducibility requires version pinning

### Option C: Hybrid - Cached Source with Refresh Workflow

Store source as build cache, automated refresh workflow syncs from rubygems.org.

**Pros:**
- Reproducible builds
- Automated updates via workflow
- Best of both approaches

**Cons:**
- Complexity of cache management
- Storage requirements for cached source
- More moving parts to maintain

---

## Rationale

Option B was chosen because:

1. **Addresses most concerns directly:**
   - #1 (pristine sources): No vendoring = no modification debate
   - #3, #4 (versions, deps): rubygems.org API as single source of truth
   - #5 (updates): Fetch IS the update mechanism
   - #6 (multi-suite): Suite config drives everything

2. **Aligns with DRY principle:**
   - Suite configuration files eliminate repetition
   - Reusable workflows replace 1500+ lines of copy-paste
   - Patches document workarounds explicitly

3. **Simplifies maintenance:**
   - No merge conflicts with upstream
   - Version updates are config changes, not code changes
   - Patches are isolated and documented

4. **Enables future growth:**
   - Adding a suite = adding a config file
   - Common infrastructure serves all suites

---

## Consequences

**Positive:**
- Dramatic reduction in workflow complexity
- Self-documenting workarounds via patches
- Scalable to any number of gem suites
- Single source of truth (rubygems.org)
- Smaller, cleaner repository

**Negative:**
- Network dependency for builds
- Initial migration effort from current repo
- Learning curve for new architecture

**Risks:**
- rubygems.org API changes: Mitigate with abstraction layer in fetch script
- Patch breakage on upstream updates: Mitigate with CI validation
- Build reproducibility: Mitigate with version pinning in suite configs

**Follow-up Actions:**
- [ ] Create new `lich5-binary-gems` repository
- [ ] Implement core scripts (fetch, patch, discover, validate)
- [ ] Create reusable workflows
- [ ] Migrate GTK3 suite configuration
- [ ] Create patches from current modifications
- [ ] Validate complete GTK3 build
- [ ] Retire `lich5-gtk3-gems` repository
- [ ] Add Nokogiri and SQLite3 suites
- [ ] Implement InnoSetup automation

---

## References

- Current POC: `lich5-gtk3-gems` repository
- ADR-0001: Binary Gem Upstream Modifications (documents current approach)
- rubygems.org API: https://guides.rubygems.org/rubygems-org-api/

---

## Notes

### Suite Configuration Schema (Draft)

```yaml
# config/suites/gtk3.yml
suite:
  name: gtk3
  description: Ruby-GNOME GTK3 bindings for Windows

source:
  authority: rubygems.org

# Build triggers (conservative approach for installer stability):
# - Annual: Sunset oldest Ruby, incorporate newest Ruby
# - Manual: Security advisory or major bug fix in upstream
# NOT triggered by: minor version bumps, refactors, or non-critical changes
build_policy:
  trigger: manual
  annual_review: true
  security_watch: true

gems:
  - name: glib2
    type: native          # native | gi-only
    msys2_packages:
      - mingw-w64-x86_64-glib2
      - mingw-w64-x86_64-gobject-introspection
    patches:
      - platform-ucrt.patch

  - name: pango
    type: native
    depends_on: [glib2, gobject-introspection, cairo, cairo-gobject]
    msys2_packages:
      - mingw-w64-x86_64-pango
      - mingw-w64-x86_64-gobject-introspection
    build_config:
      cflags_append: "$(pkg-config --cflags gobject-introspection-1.0)"
    workarounds:
      - rcairo-copy  # Windows linker needs real files, not symlinks
    patches:
      - platform-ucrt.patch

profiles:
  user:
    gems: [glib2, gio2, cairo, pango, gdk_pixbuf2, atk, gdk3, gtk3]
  dev:
    gems: [glib2, gobject-introspection, gio2, cairo, cairo-gobject,
           pango, gdk_pixbuf2, atk, gdk3, gtk3]

ruby_versions: ["3.3", "3.4", "4.0"]
platforms: [x64-mingw-ucrt]
```

### Epic Summary

| Epic | Description | Addresses Concerns |
|------|-------------|-------------------|
| 1. Foundation | New repo, scripts, schema | #3, #4, #5, #6 |
| 2. Reusable Workflows | DRY CI infrastructure | #2, #9, #10, #11, #12 |
| 3. GTK3 Migration | Port current POC | #1, #13 |
| 4. Installer Automation | Dev/user profiles, InnoSetup | #7, #8 |
| 5. Additional Suites | Nokogiri, SQLite3, etc. | #6 |
