## Context
Messaging currently supports media uploads for images and videos via a web-based file picker and a canonical NIP-98 authenticated upload endpoint at `https://nospeak.chat/api/upload`. The Android Capacitor shell integrates local notifications and remote media upload but does not yet surface a first-class camera capture flow in the chat media UI. Users want a fast way to snap a picture from the chat "add media" control, with uploads sized appropriately to avoid very large camera originals.

## Goals / Non-Goals
- Goals:
- Enable a "Take photo" action in the chat media upload UI that works on both Android native shell and mobile web.
- Ensure captured photos are resized client-side to a maximum dimension of 2048px and encoded as JPEG before upload.
- Reuse the existing NIP-98 authenticated media upload endpoint and messaging rendering semantics for captured images.
- Keep the implementation small and self-contained, avoiding new server-side APIs.
- Non-Goals:
- Changing how existing gallery-based image or video uploads work (beyond potential optional reuse of the resize helper).
- Introducing new server endpoints, storage backends, or media types.
- Implementing advanced image editing (cropping, filters, annotations) before upload.

## Decisions
- Decision: Model camera capture as an additional media source that feeds into the existing media upload pipeline instead of adding a new upload endpoint.
  - Rationale: Reuses NIP-98 auth, upload validation, and message rendering; keeps server behavior unchanged.
- Decision: Constrain captured photos to a maximum of 2048px on the longest edge and re-encode as JPEG with a moderate quality (around 0.8).
  - Rationale: Significantly reduces size of typical phone camera images while preserving adequate visual quality for chat.
- Decision: Use Capacitor Camera for the Android shell and a file input with `capture` hint on mobile web, falling back gracefully when capture is not available.
  - Rationale: Aligns with existing Native Dialogs patterns (Capacitor on Android, web primitives elsewhere) and avoids over-specializing for any one browser.
- Decision: Treat camera capture errors (permission denied, cancellation, plugin failure) as non-blocking errors surfaced via existing dialog patterns.
  - Rationale: Messaging should remain usable even when camera access is not available.

## Alternatives Considered
- Alternative: Perform resizing on the server only.
  - Rejected: Increases server work and bandwidth, does not help users on slow or metered networks, and is harder to tune per platform.
- Alternative: Introduce a separate "Camera message" content type.
  - Rejected: Adds protocol and rendering complexity without clear user benefit; standard media URLs are sufficient.

## Risks / Trade-offs
- Risk: Inconsistent support for the `capture` attribute on mobile browsers may cause the "Take photo" action to behave like a regular file chooser in some environments.
  - Mitigation: Document that behavior, keep the action label generic ("Take photo"), and rely on the Android native path for a consistent experience in the app shell.
- Risk: Client-side resizing relies on canvas APIs and may be limited by low-memory devices or very large originals.
  - Mitigation: Use conservative maximum dimensions (2048px), avoid upscaling, and fall back to uploading the original file if resizing fails.

## Migration Plan
- Implement camera capture and resizing behind the new spec requirements without changing existing upload semantics.
- Roll out to web and Android clients simultaneously, verifying behavior on representative devices.
- If necessary, follow up with additional tuning of max dimensions or quality based on observed performance and bandwidth.

## Open Questions
- Should gallery-based image uploads also be resized to a similar maximum dimension, or should resizing remain limited to camera-captured photos for now?
- Are there specific file size targets (e.g., under 1 MB) that should be enforced in addition to the 2048px limit?
