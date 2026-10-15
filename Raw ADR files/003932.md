# ADR-001: Rely on External Virtual Audio Device for Mic Routing

## Status

Accepted

## Date

2026-01-04

## Context

Users want to play soundboard audio into voice calls (Discord, Teams, etc.) alongside their microphone. This requires other applications to "hear" the soundboard as if it were a microphone input.

We evaluated whether the app should provide a built-in "mic passthrough" mode that:
1. Captures the user's real microphone
2. Mixes soundboard audio with the mic signal
3. Outputs to a virtual microphone device that other apps can use

### Technical Findings

**The core problem**: Windows does not allow user-mode applications to create virtual audio devices. Virtual microphones (like VoiceMeeter's "VoiceMeeter Output") require kernel-mode audio drivers.

**Options evaluated**:

| Option | Complexity | Notes |
|--------|------------|-------|
| Continue requiring external virtual audio device | None | Current approach, works well |
| Write/license a kernel-mode audio driver | Very High | Requires WHQL signing, security implications, installer complexity |
| Bundle open-source virtual audio driver | High | Licensing restrictions, support burden, signing requirements |
| Add mic capture + mixing only (still need external device) | Medium | Reduces VoiceMeeter config complexity but still requires it |

**Additional considerations for mic passthrough**:
- Sample rate mismatches between mic and soundboard pipeline
- Buffer synchronization between capture and playback
- Latency accumulation (capture + process + output)
- Device hot-plug handling
- Exclusive mode conflicts with other apps

## Decision

**We will not implement mic passthrough functionality.** The app will continue to require users to install and configure an external virtual audio device (VoiceMeeter, VB-Cable, or similar).

## Rationale

1. **Complexity vs. value**: Implementing mic passthrough without a bundled virtual device still requires the user to install external software, providing minimal UX improvement for significant development effort.

2. **Driver development is out of scope**: Writing or licensing a kernel-mode audio driver is a major undertaking inappropriate for this project's scope.

3. **Existing solutions work well**: VoiceMeeter Banana is free, well-documented, and provides additional features (EQ, compression, multi-source mixing) that users may want anyway.

4. **Maintenance burden**: Supporting mic capture adds edge cases (device enumeration, hot-plug, latency tuning, troubleshooting) that distract from core soundboard functionality.

## Consequences

### Positive
- Simpler codebase with clear scope boundaries
- No audio driver maintenance or signing requirements
- Users get access to VoiceMeeter's full feature set
- No additional latency from mic passthrough chain

### Negative
- Users must install and configure third-party software
- Setup is more complex than a hypothetical "just works" solution
- Some users may be confused by the requirement

### Mitigations
- Added comprehensive "Audio Routing Setup" section to README
- Documented recommended VoiceMeeter configuration steps
- Listed alternative virtual audio device options
