## ADR-0005: Jellyfin Desktop and Web UI-dependent clients are not compatible with Melodee

- Date: 2026-01-02T15:36:00.000Z
- Status: Accepted

### Context

During Jellyfin API compatibility testing, we evaluated multiple Jellyfin client applications for use with Melodee's Jellyfin API implementation. Testing revealed a fundamental architectural distinction between client types.

**Jellyfin Desktop** (and similar clients like Jellyfin Media Player, official Jellyfin mobile apps) are Qt/Electron wrappers around the **Jellyfin Web UI**. These clients:
1. Connect to a server and verify connectivity via `/System/Info/Public`
2. Load the full Jellyfin Web UI from the server URL
3. Inject native player plugins (e.g., mpv) for enhanced playback
4. All user interaction happens through the web interface

**Pure API clients** like Gelly, Finamp, Feishin, and Symfonium:
1. Implement their own native UI
2. Communicate exclusively via the Jellyfin REST API
3. Do not require the server to host any web assets

### Decision

Melodee will **not attempt to serve the Jellyfin Web UI** or support web UI-dependent clients.

Melodee's Jellyfin API implementation targets **pure API clients only**.

### Rationale

- Melodee is a music server, not a Jellyfin server fork. Hosting the full Jellyfin Web UI would require:
  - Bundling/serving significant static web assets (~50MB+)
  - Maintaining compatibility with Jellyfin Web UI updates
  - Supporting video/TV/movie UI elements irrelevant to a music-only server
- Pure API clients (Gelly, Finamp, etc.) provide excellent user experiences for music playback without this overhead
- The Jellyfin API is well-documented and sufficient for music streaming use cases

### Compatible Clients (Tested/Recommended)

| Client | Platform | Status | Notes |
|--------|----------|--------|-------|
| Gelly | Linux (GTK) | ✅ Tested | Full functionality confirmed |
| Finamp | iOS/Android | 🎯 Target | Pure API client for music |
| Feishin | Desktop | 🎯 Target | Cross-platform music player |
| Symfonium | Android | 🎯 Target | Popular music streaming app |

### Incompatible Clients

| Client | Reason |
|--------|--------|
| Jellyfin Desktop | Requires Jellyfin Web UI |
| Jellyfin Media Player | Requires Jellyfin Web UI |
| Official Jellyfin Apps | Require Jellyfin Web UI |

### Consequences

- Users expecting to use Jellyfin Desktop with Melodee will see a blank screen after connection
- Documentation should clearly list compatible vs incompatible clients
- API development focuses on endpoints used by pure API clients

### Revisit / Future Work

If significant user demand exists, a minimal "music-only" web UI could be considered as a separate project/plugin, but this is not planned.

