# ADR 003: Mobile App Technology Selection

## Status

Proposed

## Context

We are building a mobile-first application that enables developers to delegate coding tasks to AI agents from their phone. The core MVP workflow is:

1. View GitHub issues
2. Select an issue and instruct an AI agent
3. Agent creates a branch, commits code, and opens a PR
4. Review and iterate on the PR from mobile

### MVP Requirements

The MVP is intentionally simple:
- GitHub OAuth authentication
- List view of GitHub issues
- Issue detail view
- Trigger agent button with basic configuration
- Status tracking and result display
- Basic PR viewing

### Future Requirements

Later phases will require more sophisticated features:
- Advanced diff viewing optimised for mobile (critical for PR review)
- Inline code commenting
- PR thread management
- CI failure explorer with detailed logs
- Gesture-driven navigation (swipe between files, tap-to-expand hunks)
- Offline support with action queuing

### Team Constraints

- Small team (likely 1-2 developers initially)
- Need to move fast and iterate quickly
- Want to avoid maintaining two separate native codebases
- Limited time for app store submission processes during rapid iteration

### Technology Options

**1. React Native**
- Cross-platform with single codebase
- JavaScript/TypeScript (familiar to most web developers)
- Large ecosystem and community
- Mature libraries for GitHub OAuth, navigation, and networking
- Reasonable diff viewing libraries available

**2. Flutter**
- Cross-platform with single codebase
- Dart language (less common, learning curve for most teams)
- Strong performance and UI customisation
- Good widget library, but smaller ecosystem than React Native
- Fewer GitHub-specific libraries

**3. Progressive Web App (PWA)**
- Web-based, no app store required
- Works on any device with a browser
- Instant deployment and updates
- Limited access to native features (notifications, background tasks)
- Diff viewing can leverage web-based solutions (Monaco, CodeMirror)

**4. Native (Swift for iOS / Kotlin for Android)**
- Best possible UX and performance
- Full access to platform features
- Requires 2x development effort (separate codebases)
- Longer iteration cycles

## Decision

**Build the MVP as a Progressive Web App (PWA), with a clear migration path to React Native if native features become critical.**

### Rationale

**For MVP (PWA):**

1. **Speed of iteration**: Deploy instantly without app store review. Critical for a small team validating product-market fit.

2. **Simplicity matches requirements**: The MVP features (lists, buttons, OAuth, status display) work perfectly in a web context. No complex native integrations needed initially.

3. **Excellent diff viewing**: Web has mature, battle-tested diff viewers (react-diff-view, Monaco Editor, CodeMirror) that are actually superior to most mobile native alternatives. This is critical for future phases.

4. **OAuth is well-supported**: GitHub OAuth flow works smoothly with PWAs using standard web flows.

5. **Universal access**: Works on iOS, Android, tablets, and desktop without any changes. Useful for developers who might want to use both phone and laptop.

6. **Development velocity**: Standard web stack (React, TypeScript, modern bundler). Fast hot-reload, familiar debugging tools, easy testing.

**Migration path to React Native:**

If we later discover we need:
- Push notifications (high priority for agent completion alerts)
- Background task processing
- Better offline support
- App store presence for discoverability

We can migrate to React Native because:
- React Native uses React and JavaScript/TypeScript
- Most business logic and UI components can be reused
- Diff viewing libraries we choose (React-based) will largely port over
- GitHub API integration code is identical

**Why not the alternatives:**

- **Flutter**: Dart learning curve slows initial development. Smaller ecosystem for GitHub-specific needs. No clear advantage for our use case.

- **Native**: 2x the development effort for features that don't require native capabilities yet. Premature optimisation.

- **React Native immediately**: Adds complexity (native build tools, simulators, app store process) that slows iteration without providing value for MVP features. Better as a second step if needed.

## Consequences

### Positive

- **Fastest path to user feedback**: Deploy and iterate multiple times per day if needed.

- **Lower initial complexity**: No native build toolchains, simulators, or app store accounts required.

- **Best diff viewing UX**: Can leverage mature web-based code viewing libraries that are actually superior to mobile native options.

- **Future flexibility**: Not locked in. Can migrate to React Native if we validate that native features are essential.

- **Development experience**: Fast hot-reload, familiar debugging, easy CI/CD.

### Negative

- **No push notifications initially**: Must rely on browser notifications (less reliable) or polling. Mitigated by: users will mostly use app in foreground during active development sessions.

- **Perceived as "less native"**: Some users may expect app store presence. Mitigated by: PWA install experience is quite good on modern browsers, and our target users (developers) are comfortable with web apps.

- **Limited offline capabilities**: Service workers help but less robust than native. Mitigated by: MVP doesn't require offline operation; later migration to React Native addresses this.

- **Potential future migration cost**: If we move to React Native, there will be migration work. Mitigated by: keeping business logic separate from presentation, using React patterns that port cleanly, and only migrating if we validate the need.

### Technical Implementation Notes

- Use React + TypeScript + Vite for fast development
- Implement service worker for basic offline support and installability
- Use react-diff-view or similar for diff viewing (critical future feature)
- Design component architecture to facilitate potential React Native migration (avoid web-specific APIs in business logic)
- Use GitHub REST/GraphQL APIs directly (works identically in PWA and React Native)

### Success Criteria for Migration Decision

We should consider migrating to React Native if:

1. User research shows push notifications are critical (agents completing tasks while user isn't actively using app)
2. App store presence becomes important for discovery/credibility
3. Offline operation becomes a validated user need
4. We've validated product-market fit and are ready to invest in longer-term technical foundation

Until then, PWA provides the optimal speed/functionality trade-off for a small team building an MVP.
