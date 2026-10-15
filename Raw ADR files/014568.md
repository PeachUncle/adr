# ADR-006: Distribution Strategy - Multi-Channel Approach

**Status:** Accepted
**Date:** 2025-11-27
**Deciders:** Project Catalyst Team
**Technical Story:** Plugin Distribution & Discovery (Launch Phase 6)

---

## Context

### Background

Project Catalyst must be easily discoverable and installable by Claude Code users. The plugin ecosystem is evolving, with multiple distribution channels emerging. A well-designed distribution strategy maximizes reach, simplifies installation, and enables seamless updates.

### Requirements

1. **Easy Installation:** Users should install with one command
2. **Multiple Channels:** Reach users through various discovery paths
3. **Automatic Updates:** Users get latest templates and patterns
4. **Offline Capability:** Plugin works without internet after initial install
5. **Versioning:** Clear semantic versioning for compatibility
6. **Documentation:** Installation guides for all user types
7. **Validation:** Verify plugin integrity post-install

### User Personas

**Persona 1: Technical Developer**
- Comfortable with Git and CLI
- Prefers manual control over installations
- Wants to inspect code before installation
- **Channel Preference:** GitHub repository (clone + symlink)

**Persona 2: Productivity User**
- Wants fastest installation method
- Trusts official Claude Code tooling
- Doesn't want to configure manually
- **Channel Preference:** Claude CLI (`claude plugin add`)

**Persona 3: Non-Technical User**
- May be intimidated by command line
- Wants "one-click" installation
- Needs clear, step-by-step instructions
- **Channel Preference:** Setup script (automated)

---

## Decision

### Chosen Approach: Multi-Channel Distribution with Primary GitHub Repository

We adopt a **multi-channel strategy** with GitHub as the source of truth, complemented by Claude CLI integration, marketplace listing, and automated setup scripts.

### Channel 1: GitHub Repository (Primary)

**Repository:** https://github.com/jcmrs/project-catalyst

**Installation Method:**
```bash
# Manual installation (full control)
git clone https://github.com/jcmrs/project-catalyst.git
cd project-catalyst

# Symlink to Claude Code plugins directory
# Windows:
mklink /D "%USERPROFILE%\.claude\plugins\project-catalyst" "%CD%"

# macOS/Linux:
ln -s "$(pwd)" "$HOME/.claude/plugins/project-catalyst"

# Verify installation
claude plugin list
```

**Benefits:**
- Full transparency (users can inspect code)
- Version control (git tags for releases)
- Community contributions (pull requests)
- Issue tracking (GitHub Issues)
- Open source (MIT license)

**README.md Installation Section:**
```markdown
## 🚀 Quick Start

### Method 1: Claude CLI (Recommended)
\`\`\`bash
claude plugin add gh:jcmrs/project-catalyst
\`\`\`

### Method 2: Manual Installation
\`\`\`bash
git clone https://github.com/jcmrs/project-catalyst.git
cd project-catalyst
# Windows: mklink /D "%USERPROFILE%\.claude\plugins\project-catalyst" "%CD%"
# macOS/Linux: ln -s "$(pwd)" "$HOME/.claude/plugins/project-catalyst"
\`\`\`

### Method 3: Automated Setup (Easy)
\`\`\`bash
curl -fsSL https://raw.githubusercontent.com/jcmrs/project-catalyst/main/scripts/install.sh | bash
\`\`\`
```

### Channel 2: Claude CLI Integration

**Command:** `claude plugin add gh:jcmrs/project-catalyst`

**Implementation:**
```json
// plugin.json
{
  "name": "project-catalyst",
  "version": "1.0.0",
  "homepage": "https://github.com/jcmrs/project-catalyst",
  "repository": "https://github.com/jcmrs/project-catalyst"
}
```

**Benefits:**
- Official installation method
- Automatic dependency resolution
- Built-in update mechanism
- Validation and verification
- One-command installation

**User Experience:**
```bash
$ claude plugin add gh:jcmrs/project-catalyst
📦 Installing project-catalyst...
✓ Cloned repository
✓ Validated plugin.json
✓ Linked to ~/.claude/plugins/
✅ project-catalyst v1.0.0 installed successfully

Try: claude --help
```

### Channel 3: Claude Code Marketplace (Future)

**Status:** Planned (when marketplace launches)

**Listing Preparation:**
```yaml
# marketplace-listing.yaml
plugin:
  name: Project Catalyst
  author: jcmrs
  category: Development Tools
  tags:
    - utilities
    - templates
    - best-practices
    - project-setup
  description: |
    Language-agnostic project utilities with AI-powered analysis.
    Provides 40+ production-ready templates for git, CI/CD, docs, and quality tools.
  screenshots:
    - assets/screenshots/analyzer-demo.png
    - assets/screenshots/template-apply.png
  pricing: Free (Open Source)
  license: MIT
```

**Benefits:**
- Maximum discoverability
- Official verification badge
- User reviews and ratings
- Featured placement opportunities
- Integrated update notifications

### Channel 4: Automated Setup Script

**Script:** `scripts/install.sh`

```bash
#!/bin/bash
# install.sh - Automated Project Catalyst installation
# Usage: curl -fsSL https://raw.githubusercontent.com/jcmrs/project-catalyst/main/scripts/install.sh | bash

set -e

REPO="jcmrs/project-catalyst"
INSTALL_DIR="$HOME/.claude/plugins/project-catalyst"

echo "🚀 Installing Project Catalyst..."

# Check prerequisites
check_prerequisites() {
  if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install git first."
    exit 1
  fi

  if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code not found. Please install Claude Code first."
    exit 1
  fi
}

# Clone repository
install_plugin() {
  if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Project Catalyst already installed at $INSTALL_DIR"
    read -p "   Update to latest version? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      cd "$INSTALL_DIR"
      git pull origin main
      echo "✅ Updated to latest version"
    fi
  else
    git clone "https://github.com/${REPO}.git" "$INSTALL_DIR"
    echo "✅ Installed successfully"
  fi
}

# Verify installation
verify_installation() {
  if claude plugin list | grep -q "project-catalyst"; then
    echo "✅ Installation verified"
    echo ""
    echo "🎉 Project Catalyst is ready!"
    echo "   Try: claude --help"
    echo "   Docs: https://github.com/${REPO}"
  else
    echo "⚠️  Installation complete, but plugin not recognized by Claude Code"
    echo "   Try restarting your terminal or running: claude plugin refresh"
  fi
}

# Run installation
check_prerequisites
install_plugin
verify_installation
```

**Benefits:**
- One-line installation
- Automated validation
- User-friendly error messages
- Update mechanism included
- Cross-platform (bash)

### Version Management

**Semantic Versioning:**
```
1.0.0 - Major.Minor.Patch
```

- **Major:** Breaking changes (template format changes, API changes)
- **Minor:** New features (new templates, analyzer enhancements)
- **Patch:** Bug fixes, doc updates, minor improvements

**Tagging Strategy:**
```bash
# Create release
git tag -a v1.0.0 -m "Release 1.0.0 - Initial public release"
git push origin v1.0.0

# Update plugin.json
{
  "version": "1.0.0"
}
```

**Update Mechanism:**
```bash
# User updates plugin
cd ~/.claude/plugins/project-catalyst
git fetch --tags
git checkout v1.1.0

# Or via Claude CLI
claude plugin update project-catalyst
```

### Distribution Timeline

**Phase 1 (Week 12): GitHub Release**
- Public repository launch
- README with installation instructions
- MIT license file
- CONTRIBUTING.md
- Initial release tag (v1.0.0)

**Phase 2 (Month 2): Claude CLI Integration**
- Test `claude plugin add` command
- Ensure plugin.json validation passes
- Document official installation method

**Phase 3 (Month 3): Marketplace Listing**
- Prepare marketplace submission
- Create screenshots/demos
- Submit for review
- Await approval

**Phase 4 (Month 4): Community Growth**
- Promote via social media
- Write blog posts
- Create video tutorials
- Engage community contributors

---

## Considered Alternatives

### Alternative 1: GitHub-Only Distribution

**Pros:**
- Single source of truth
- Simple maintenance
- Full transparency

**Cons:**
- Lower discoverability (users must know GitHub URL)
- No official verification
- Manual installation required
- Less accessible for non-technical users

**Why Not Chosen:**
Limits reach. Multi-channel approach maximizes discoverability while maintaining GitHub as source of truth.

### Alternative 2: Marketplace-Only Distribution

**Pros:**
- Maximum discoverability
- Official verification
- Integrated updates
- User reviews

**Cons:**
- Depends on marketplace launch (not yet available)
- Less transparency (no Git history visible)
- Review process delays
- Potential rejection risk

**Why Not Chosen:**
Marketplace not yet available. GitHub-first ensures early availability while preparing for marketplace.

### Alternative 3: npm Package Distribution

**Pros:**
- Familiar to JavaScript developers
- `npm install -g` is well-known
- Automatic dependency management
- Versioning built-in

**Cons:**
- Requires Node.js (not all users have it)
- Adds npm as dependency
- Package size considerations
- Not official Claude Code channel

**Why Not Chosen:**
Claude CLI (`claude plugin add`) is the official installation method. npm adds unnecessary dependency.

### Alternative 4: Docker Container Distribution

**Pros:**
- Isolated environment
- Reproducible installations
- Cross-platform consistency

**Cons:**
- Requires Docker (significant overhead)
- Complex for simple plugin
- Not standard for Claude Code plugins
- Adds latency (container startup)

**Why Not Chosen:**
Overkill for plugin distribution. Claude Code plugins are file-based, not container-based.

---

## Consequences

### Positive

1. **Maximum Reach:** Multiple channels increase discoverability
2. **User Choice:** Different installation methods for different personas
3. **Easy Updates:** Git-based updates via `git pull` or `claude plugin update`
4. **Open Source:** GitHub enables community contributions
5. **Official Support:** Claude CLI integration provides official endorsement
6. **Future-Proof:** Marketplace-ready when available
7. **Automated Setup:** Script lowers barrier for non-technical users

### Negative

1. **Maintenance Overhead:** Must maintain multiple distribution channels (mitigated: GitHub is source of truth)
2. **Documentation Burden:** Installation guides for each method (mitigated: clear README)
3. **Version Sync:** Must keep plugin.json version in sync with Git tags (mitigated: CI/CD automation)
4. **Support Complexity:** Different installation methods = different support scenarios (mitigated: troubleshooting guide)

### Risks

**Risk 1: GitHub Repository Unavailable**
- **Impact:** Users cannot install or update plugin
- **Probability:** Very Low (GitHub 99.9% uptime)
- **Mitigation:** Mirror repository on GitLab as backup

**Risk 2: Claude CLI Breaking Changes**
- **Impact:** `claude plugin add` command stops working
- **Probability:** Low (stable API)
- **Mitigation:** Maintain manual installation docs as fallback

**Risk 3: Marketplace Rejection**
- **Impact:** Cannot list in official marketplace
- **Probability:** Medium (review process strict)
- **Mitigation:** GitHub + Claude CLI sufficient for initial success

**Risk 4: Version Confusion**
- **Impact:** Users install wrong version
- **Probability:** Medium (multiple versions available)
- **Mitigation:** Clear version tags, documentation emphasizes latest stable

---

## Implementation Notes

### Phase 1 (Week 12): Public Launch

**Pre-Launch Checklist:**
- ✅ README.md complete with installation instructions
- ✅ LICENSE file (MIT)
- ✅ CONTRIBUTING.md with contribution guidelines
- ✅ plugin.json validated
- ✅ All ADRs published in docs/adr/
- ✅ Git tags for v1.0.0
- ✅ GitHub Issues enabled
- ✅ GitHub Discussions enabled (for Q&A)
- ✅ CI/CD pipeline passing

**Launch Actions:**
```bash
# Tag release
git tag -a v1.0.0 -m "Release 1.0.0 - Initial public release"
git push origin main --tags

# Create GitHub Release
gh release create v1.0.0 \
  --title "Project Catalyst v1.0.0" \
  --notes "Initial public release with 15 MVP templates and AI-powered analysis"

# Test installation
claude plugin add gh:jcmrs/project-catalyst
claude plugin list | grep project-catalyst
```

### Phase 2 (Month 2): Claude CLI Testing

**Validation:**
- Test `claude plugin add gh:jcmrs/project-catalyst`
- Verify plugin.json passes validation
- Test `claude plugin update project-catalyst`
- Test `claude plugin remove project-catalyst`
- Document any issues or limitations

### Phase 3 (Month 3): Marketplace Submission

**Submission Package:**
- plugin.json (validated)
- README.md (clear, professional)
- Screenshots (analyzer demo, template application)
- Video demo (2-minute overview)
- Security audit results
- Test coverage report (80%+)

### Phase 4 (Month 4): Promotion

**Marketing Channels:**
- Blog post: "Introducing Project Catalyst"
- Reddit: r/ClaudeCode (if exists)
- Twitter/X: @anthropicai mentions
- LinkedIn: Technical article
- YouTube: Tutorial video
- GitHub: Star campaign

### Automated Release Script

```bash
#!/bin/bash
# scripts/release.sh - Automated release process
# Usage: ./scripts/release.sh 1.0.0

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/release.sh <version>"
  exit 1
fi

echo "🚀 Releasing Project Catalyst v${VERSION}"

# Update plugin.json version
jq ".version = \"${VERSION}\"" plugin.json > plugin.json.tmp
mv plugin.json.tmp plugin.json

# Commit version bump
git add plugin.json
git commit -m "chore: bump version to ${VERSION}"

# Create tag
git tag -a "v${VERSION}" -m "Release ${VERSION}"

# Push
git push origin main --tags

# Create GitHub release
gh release create "v${VERSION}" \
  --title "Project Catalyst v${VERSION}" \
  --generate-notes

echo "✅ Release v${VERSION} published"
echo "   View: https://github.com/jcmrs/project-catalyst/releases/tag/v${VERSION}"
```

### Installation Verification Script

```bash
#!/bin/bash
# scripts/verify-installation.sh

set -e

echo "🔍 Verifying Project Catalyst installation..."

# Check plugin directory exists
if [ ! -d "$HOME/.claude/plugins/project-catalyst" ]; then
  echo "❌ Plugin directory not found"
  exit 1
fi

# Check plugin.json exists
if [ ! -f "$HOME/.claude/plugins/project-catalyst/plugin.json" ]; then
  echo "❌ plugin.json not found"
  exit 1
fi

# Check Claude recognizes plugin
if ! claude plugin list | grep -q "project-catalyst"; then
  echo "❌ Plugin not recognized by Claude Code"
  exit 1
fi

# Check Skills exist
if [ ! -d "$HOME/.claude/plugins/project-catalyst/skills" ]; then
  echo "❌ Skills directory not found"
  exit 1
fi

echo "✅ Installation verified"
echo "   Plugin: project-catalyst"
echo "   Location: $HOME/.claude/plugins/project-catalyst"
echo "   Status: Active"
```

---

## References

### Distribution Best Practices

1. [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
2. [Semantic Versioning](https://semver.org/)
3. [Open Source Licensing](https://choosealicense.com/)

### Claude Code Documentation

4. [Claude Code Plugin Installation](https://code.claude.com/docs/en/plugins#installing-plugins)
5. [Plugin Development Toolkit](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/README.md)

### Related ADRs

6. [ADR-001: Plugin Architecture](./001-plugin-architecture.md)
7. [ADR-004: Isolation Enforcement](./004-isolation-enforcement.md)

### Marketing References

8. [Product Hunt Launch Guide](https://www.producthunt.com/)
9. [Open Source Marketing](https://opensource.guide/finding-users/)

---

## Validation

### Success Criteria

**Installation Success:**
- ✅ GitHub installation works (manual + script)
- ✅ Claude CLI installation works (`claude plugin add`)
- ✅ Installation takes < 2 minutes
- ✅ Zero configuration required post-install

**Discoverability:**
- ✅ GitHub repository has clear README
- ✅ Repository shows up in GitHub search for "claude code plugin"
- ✅ Marketplace listing (when available)
- ✅ Installation guides indexed by search engines

**Updates:**
- ✅ Users can update with `git pull` or `claude plugin update`
- ✅ Version tags follow semantic versioning
- ✅ Release notes document changes
- ✅ Breaking changes clearly communicated

**Community:**
- ✅ GitHub Issues enabled and monitored
- ✅ Contribution guidelines published
- ✅ Code of conduct established
- ✅ Community engagement active

### Metrics

**Installation Metrics (Month 1):**
- GitHub clones: 100+ (target)
- Stars: 50+ (target)
- Forks: 10+ (target)
- Installation success rate: 95%+

**Distribution Channel Usage (Month 3):**
- GitHub direct: 40%
- Claude CLI: 50%
- Automated script: 10%

**User Satisfaction (Post-Launch Survey):**
- Installation ease: 4.5/5 stars
- Documentation clarity: 4.5/5 stars
- Update process: 4.5/5 stars

**Community Growth (Month 6):**
- Active users: 500+
- Contributors: 10+
- Pull requests: 20+
- Issues resolved: 95%+

---

**Last Updated:** 2025-11-27
**Related ADRs:** [ADR-001](./001-plugin-architecture.md), [ADR-002](./002-analyzer-design.md), [ADR-003](./003-template-system.md), [ADR-004](./004-isolation-enforcement.md), [ADR-005](./005-token-optimization.md)
