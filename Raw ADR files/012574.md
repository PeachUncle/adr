## Context
nospeak already supports encrypted Kind 15 file messages (including audio) and renders audio attachments via an in-bubble audio player. This change adds an in-app voice recording UX that produces an audio `File` and reuses the existing encryption + Blossom upload + Kind 15 send pipeline.

The current messaging spec emphasizes `.bin` URLs for encrypted blobs (served as `application/octet-stream`) while preserving the original media MIME type in the Kind 15 `file-type` tag.

## Goals
- Add a voice recording affordance optimized for mobile UX.
- Reuse the existing encrypted attachment pipeline without introducing new backend services.
- Keep the output interoperable with other NIP-17 clients by preserving MIME metadata.
- Support Android native recording to bypass WebView audio capture limitations on Android 16+.

## Non-Goals
- iOS voice recording support (the UI will hide the microphone button there).
- Transcoding/codec conversion.
- Background recording, lock-screen capture, or uploads without user interaction.

## Recording Format Decision

### Web/Desktop: Opus via `MediaRecorder`
- Prefer `audio/webm;codecs=opus` when supported.
- Fall back to `audio/ogg;codecs=opus` for Firefox where applicable.
- Final fallback `audio/webm`.

#### Rationale
- Good voice quality at low bitrates.
- Widely supported on Chromium desktop browsers.
- Avoids heavy client-side encoders (MP3) or wasm transcoding.

### Android native: M4A (AAC-LC) via `AudioRecord` + `MediaCodec`
Android 16 introduced a WebView bug where `getUserMedia` fails with "Unable to select communication device" even after microphone permission is granted. To bypass this, Android uses native recording instead of WebView `MediaRecorder`.

- Uses `AudioRecord` with `AudioSource.MIC` for raw PCM capture.
- Uses `MediaCodec` for real-time AAC-LC encoding.
- Uses `MediaMuxer` to write M4A container.
- Output: 44.1kHz, mono, 64kbps AAC-LC in M4A container (`audio/mp4`).
- Live waveform peaks computed from raw PCM samples (~125ms intervals) and emitted to JS via Capacitor plugin events.

#### Rationale
- Bypasses WebView audio capture bug on Android 16+.
- AAC encoding is hardware-accelerated and universally supported.
- M4A/AAC playback is universally supported on all platforms.

### iOS behavior
- The UI will hide the microphone button when recording prerequisites are not met.

## File naming vs MIME type
- The recorded `File` name SHOULD end with `.bin` (e.g. `voice-<timestamp>.bin`) to match existing encrypted media conventions.
- **Web/Desktop**: The recorded file's MIME type reflects the Opus container (e.g. `audio/webm;codecs=opus`).
- **Android native**: The recorded file's MIME type is `audio/mp4`.
- The encrypted upload continues to be sent as `application/octet-stream` so Blossom returns a `.bin` URL; the original MIME is preserved in the Kind 15 `file-type` tag.

## UI and State Machine

### Microphone button
- Render to the right of the message input.
- Hidden when the input contains non-whitespace text.
- Hidden when voice recording is unsupported.

### Bottom sheet behavior
- Opens on mic tap and starts recording immediately.
- Shows live waveform:
  - **Web/Desktop**: From `AudioContext` + `AnalyserNode` reading from the active mic stream.
  - **Android native**: From peak events emitted by the native recording plugin.
- Shows timer with a hard cap of 3:00.

### Controls

#### Web/Desktop recording
- Cancel: discards recording, stops tracks, closes sheet.
- Pause/Resume recording: uses `MediaRecorder.pause()` / `MediaRecorder.resume()`.
- Play/Pause preview: after pausing or stopping, allow preview via an `<audio>` element.
- Send: stops recording if needed, constructs `File`, and sends via existing `sendFileMessage` flow.

#### Android native recording
- Cancel: discards recording, deletes temp file, closes sheet.
- Done: finalizes recording, enables preview playback.
- Play/Pause preview: after pressing Done, allow preview via an `<audio>` element.
- Send: constructs `File` from recorded M4A, sends via existing `sendFileMessage` flow, then deletes temp file.

Note: Android native recording does not support pause/resume. The "Done" button finalizes the recording; the user can then preview and choose to Send or Cancel.

### Errors
- Permission denied, device unavailable, or recorder errors should keep the app functional.
- In Android shell, surface errors via native dialogs where possible; otherwise use existing in-app error patterns.

## Security / Privacy
- Microphone access is requested only on explicit user interaction.
- On Cancel/Send/error, always stop media tracks (web) or stop native recorder and delete temp files (Android).
