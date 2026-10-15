# ADR-004: Audio Format Standardization

## Status

Accepted

## Date

2026-01-04

## Context

The app needs to:
1. Accept various audio file formats (WAV, MP3, FLAC, etc.)
2. Mix multiple sounds together in real-time
3. Output to potentially different audio devices simultaneously
4. Achieve <50ms latency from hotkey press to audio output

We needed to decide on an internal audio format and decode strategy.

## Decision

We standardize all audio to a fixed internal format:
- **Sample rate**: 48,000 Hz
- **Sample format**: IEEE float32 (32-bit floating-point)
- **Channels**: Stereo (2 channels)

All audio is **decoded on first access** (eager loading) and cached in memory as raw PCM data.

### Conversion Pipeline

```
Source file (any format)
    ↓ NAudio decoder
Mono → Stereo (MonoToStereoSampleProvider)
    ↓
Non-48kHz → 48kHz (WdlResamplingSampleProvider)
    ↓
float[] buffer (cached in SoundLibrary)
```

## Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **48kHz float32 stereo, decode on load (chosen)** | Zero playback latency, simple mixing, consistent format | Memory overhead (~1.9MB per 5-second clip), slow first access |
| **44.1kHz int16 stereo** | 54% smaller files, CD-standard | Requires resampling for Discord/games (48kHz ecosystem) |
| **Device-native sample rate** | Zero resampling | Can't share buffers between devices; complex buffer management |
| **Streaming decode (on-demand)** | Minimal RAM, handles huge files | 50-200ms first-play latency (unacceptable for hotkey response) |
| **Keep original format** | No conversion overhead | Complex mixing logic; format mismatches between sounds |

## Rationale

### Why 48kHz?

48kHz is the standard for:
- Modern gaming audio engines (Unity, Unreal)
- Discord, Teams, and other voice chat apps
- Video production and streaming

Most source audio is 44.1kHz (CD standard) or 48kHz. Resampling cost during decode is negligible (~4ms for 5-second clip).

### Why float32?

NAudio's `MixingSampleProvider` operates on float32 samples. While int16 would save 50% memory, it would require:
- Converting to float32 for mixing
- Converting back to int16 for storage
- Additional quantization noise

Float32 also provides headroom for mixing multiple voices without clipping concerns.

### Why decode on load?

**Hotkey latency is critical.** A soundboard must respond in <50ms to feel responsive during gaming. Streaming decode adds 50-200ms latency on first play, which is unacceptable.

Memory cost is acceptable: 16 clips × 5 seconds × 1.9MB = ~30MB, well within modern system capabilities.

### Why force stereo?

Simplifies the mixing pipeline. The `MixingSampleProvider` handles stereo natively. Mono sounds are losslessly upsampled (each sample duplicated to both channels).

## Consequences

### Positive
- Zero latency after first play (all audio pre-decoded in RAM)
- Simple mixing logic (all voices same format)
- High quality resampling (WDL Lanczos filter)
- Works with any NAudio-supported source format

### Negative
- **Memory overhead**: ~1.9MB per 5-second stereo clip at 48kHz float32
- **Slow first access**: Decoding happens on first `GetOrLoad()` call
- **Large files problematic**: A 2-hour file would consume 2.76GB RAM
- **Mono files waste memory**: Forced stereo doubles storage for mono sources

### Technical Debt
- Consider storing mono files as mono internally, expanding to stereo on playback
- Add memory usage display in settings ("Audio Cache: 96 MB")
- Document that the app is designed for short clips (3-30 seconds), not long-form audio

## Implementation Notes

Key files:
- `Services/SoundLibrary.cs` - Format definition (line 15), decode pipeline, caching
- `Audio/OutputBus.cs` - Output format (line 17)
- `Models/AudioBuffer.cs` - Raw PCM storage

The format is hardcoded in two places (`SoundLibrary` and `OutputBus`) and must match. If changed, both must be updated together.
