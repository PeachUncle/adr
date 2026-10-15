# ADR: Deterministic Audio Fixture Harness for Transcription Integration Tests

Date: 2025-12-31  
Status: Proposed  
Owners: Speech pipeline

## Context
We need repeatable integration tests for the speech transcription pipeline that validate:
- Transcript accumulation across pauses.
- Timing segment stability and ordering.
- Export correctness for long sessions.

Current tests are mostly unit-level (segment merging, parsing) and do not exercise the end-to-end pipeline with real audio. Simulator-only UI tests are insufficient for speech recognition behavior. We already have an external-audio source path (`SpeechRecognizer.appendAudioBuffer` -> `TranscriptionEngine.appendAudioBuffer`) that can accept audio buffers from a non-microphone source.

## Decision (Proposed)
Introduce an optional, test-only “audio fixture mode” that feeds deterministic PCM buffers into the transcription engine and exposes the resulting transcript/timing for assertions. This would enable repeatable integration tests on device (primary target) and best-effort runs on simulator.

This ADR does not commit to implementation priority. It documents options, limitations, and a viable design path.

## Options Considered

### Option A: Device-only manual testing (status quo)
Pros:
- Closest to real user behavior.
- No new code paths.
Cons:
- Not repeatable; slow and hard to automate.
- Hard to detect subtle regressions in segment merging and timing.

### Option B: Deterministic audio fixture harness (this ADR)
Pros:
- Repeatable and automatable integration tests.
- Exercises real engine code paths (buffer streaming, partial/final handling).
- Can validate timing exports against known fixtures.
Cons:
- Still subject to speech engine nondeterminism (punctuation, casing, segmentation).
- On-device recognition requirements may block simulator runs.
- Requires new test-only injection path and fixture data management.

### Option C: Mock transcription engine for UI tests
Pros:
- Fully deterministic; works on simulator/CI.
- Fast UI validation.
Cons:
- Does not validate speech framework integration or audio buffer handling.
- Risk of false confidence.

### Option D: File-based recognition (`SFSpeechURLRecognitionRequest`)
Pros:
- Easier to feed a file.
Cons:
- Not streaming; does not exercise the live buffer pipeline.
- Different behavior from the in-app flow.

### Option E: Third-party engine (e.g., Whisper)
Pros:
- Deterministic output if model + seed are fixed.
Cons:
- Large integration cost; model packaging and performance risks.
- Not aligned with current on-device Apple framework approach.

## Proposed Design (Option B)

### Test Mode Entry
- Add a test-only toggle (e.g., env var `SPEECHDICTATION_TEST_AUDIO_FIXTURE=1`) that:
  - Forces external audio source mode in `SpeechRecognizer.startTranscribing(isExternalAudioSource: true)`.
  - Disables microphone permission prompts for the test run (UI still exercises permissions if needed).

### Fixture Playback
- Store fixtures in the test bundle (`.wav` or `.caf`, PCM 16-bit or float).
- Use `AVAudioFile` + `AVAudioPCMBuffer` to read frames.
- Feed buffers through `SpeechRecognizer.appendAudioBuffer` at a controlled cadence:
  - Real-time pacing for UI realism.
  - Accelerated pacing for test speed, if the engine tolerates it.

### Assertions
- Use tolerant assertions on transcripts (key phrases, word presence, or token counts).
- Validate timing invariants: monotonic timestamps, no overlaps, and stable segment ordering.
- Validate export formats (SRT/VTT/TTML/JSON) against fixture expectations.

### Isolation
- Keep fixture harness in test targets only.
- Avoid storing any real user audio; use synthetic recordings.

## Limitations and Risks
- **Nondeterminism**: Speech recognition output varies with OS version, locale, and model updates.
- **Device requirements**: On-device recognition may be unavailable or restricted for some languages.
- **Simulator reliability**: Speech framework behavior in simulator is not guaranteed; plan for device as the primary target.
- **Timing sensitivity**: Streaming cadence affects partial/final segmentation.
- **Permissions**: Some flows still require speech/microphone authorization.

## References
- Apple Speech framework overview: https://developer.apple.com/documentation/speech  
- `SFSpeechAudioBufferRecognitionRequest` (streaming audio input): https://developer.apple.com/documentation/speech/sfspeechaudiobufferrecognitionrequest  
- `requiresOnDeviceRecognition`: https://developer.apple.com/documentation/speech/sfspeechrecognitionrequest/1648621-requiresondevicerecognition  
- `SpeechTranscriber` audio time range attribute: https://developer.apple.com/documentation/speech/speechtranscriber/resultattributeoption/audiotimerange  
- WWDC session on SpeechAnalyzer (iOS 26+): https://developer.apple.com/videos/play/wwdc2025/277/  
- Related repo doc: `Research/ADR-IntegrationEndToEndTesting.txt`
