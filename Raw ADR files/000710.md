## Context
Audixa is a language-learning-first video/audio player. MVP focuses on Windows (Desktop) + Android, with iOS planned, and Browser explicitly excluded. MVP must support video playback, Local + SMB sources, external SRT/VTT subtitles, and local persistence. Cloud sync is out of scope for MVP, but the data model must not block adding sync later.

## Goals / Non-Goals
- Goals
  - Implement a maintainable MVVM + DI architecture in Avalonia with a single source of truth for playback state.
  - Ship MVP features: Local + SMB sources, video playback, external bilingual subtitles (SRT/VTT), masking, sentence navigation, and SQLite persistence.
  - Keep the storage model sync-ready (stable IDs + change tracking).
- Non-Goals (MVP)
  - WebDAV/DLNA, cloud-drive APIs
  - Online subtitle search/download, embedded subtitle extraction, Whisper/ASR
  - ASS advanced rendering and interaction
  - Pitch-preserving time-stretch

## Decisions
### Decision: Layered architecture in the shared project
- Presentation: Avalonia Views + ViewModels (MVVM Toolkit)
- Application: service interfaces + orchestrators (e.g., `PlaybackService`)
- Infrastructure: SQLite, SMB client, filesystem access
- Platform: per-platform playback adapter + optional platform services

Rationale: keeps UI declarative and testable; avoids duplicating logic across pages; enables future sync by isolating persistence and domain events.

### Decision: Platform-native playback via adapter pattern (Option B)
Define an abstraction:
- `IMediaPlayerAdapter`: play/pause/seek/speed, emits position/time events, exposes video size/aspect, and accepts a platform-specific rendering target.
- `IPlaybackService`: app-level orchestration (queue, current item, errors, state stream) using the adapter.

Rationale: avoids LGPL/GPL risk; isolates platform differences; supports incremental improvement per platform.

### Decision: Normalize playback input and allow a future transcoding proxy
The application SHALL NOT assume that the player always receives a file path. Instead, `IPlaybackService` opens a normalized `PlaybackInput`:
- `DirectUriPlaybackInput`: local file path / content URI / platform URL
- `SeekableStreamPlaybackInput`: a seekable stream abstraction for SMB or local
- `HttpProxyPlaybackInput`: a local HTTP URL served by the app (supports Range)

Future extension: add an optional `ITranscodingProxy` that can transform an arbitrary source (e.g., MKV) into a supported stream (e.g., MP4/HLS) and expose it as `HttpProxyPlaybackInput`.

Rationale: Desktop playback (especially WebView2/HTML5) may support only a subset of codecs; a transcoding proxy allows unsupported formats to be played without changing UI or player orchestration.

Licensing note: FFmpeg-based transcoding will require a separate license review and SHOULD be implemented as an external process boundary behind `ITranscodingProxy` to minimize coupling.

### Decision: External subtitle tracks only in MVP
Implement:
- `ISubtitleService` parses SRT/VTT and maps playback time -> active subtitle index.
- UI binds to derived state (active line, masking mode) and routes click-to-seek back to `IPlaybackService`.

Rationale: reduces complexity; keeps the subtitle-as-UI interaction core intact.

### Decision: Local-first SQLite with sync-ready metadata
All persisted entities MUST include:
- `Id` (stable, string/UUID)
- `UpdatedAtUtc`
- `Deleted` (tombstone)
And a minimal `Outbox` table for future sync (append-only change log).

Rationale: enables v2.0 cloud sync without rewriting local storage.

## Alternatives considered
- LibVLC / libmpv core: rejected due to licensing/commercial risk.
- Monolithic UI-driven state: rejected (hard to test, duplicates logic).

## Risks / Trade-offs
- Desktop video rendering approach is uncertain in Avalonia without third-party cores.
  - Mitigation: implement a spike and select one approach early:
    - WebView2 + local HTTP range streaming + JS bridge
    - MediaFoundation/DirectShow hosted via `NativeControlHost`
- SMB streaming and seeking may vary by server and credentials.
  - Mitigation: enforce a seekable stream contract and add robust error reporting.
 - Non-Windows platforms can also have codec availability differences (device/OS dependent).
   - Mitigation: keep the same `PlaybackInput` abstraction and allow using the transcoding proxy on any platform when needed.

## Migration Plan
- MVP ships with local-only SQLite.
- v2.0 adds a `SyncService` reading from Outbox and applying remote changes; no schema rewrite required.

## Open Questions
- Desktop playback adapter selection (spike required).
- SMB library choice (MIT/Apache) and performance characteristics with large MKV files.
- Bilingual subtitle strategy: two files (Primary+Secondary) vs merged bilingual cues in one file.
 - Transcoding output format choice (MP4 progressive vs HLS) and latency trade-offs.


