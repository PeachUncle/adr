# ADR-005: Speech Pipeline

## Status
**Approved** — 2024-12-21

## Context

The Reachy Home Assistant needs to communicate with family members through natural speech. This requires:

1. **Wake Word Detection**: Always-on listening for "Hey Reachy"
2. **Speech-to-Text (STT)**: Convert spoken commands to text
3. **Text-to-Speech (TTS)**: Convert responses to natural speech
4. **Speaker Identification**: Know who is speaking

### Key Requirements
- Low-latency wake word detection (<200ms)
- Accurate STT for all family members (including kids)
- Natural-sounding TTS (not robotic)
- Speaker identification for personalization
- Must run on Jetson Orin NX (16GB GPU)
- Privacy-first (prefer local processing)

## Decision

**Fully local speech pipeline using open-source models optimized for Jetson GPU.**

### Pipeline Architecture

```
                        ┌─────────────────────────────────────────┐
                        │           Audio Input (Microphone)       │
                        └─────────────────┬───────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Wake Word Detection                              │
│                         (OpenWakeWord - always on)                       │
│                         "Hey Reachy" → trigger                           │
└─────────────────────────────────────────┬───────────────────────────────┘
                                          │ Triggered
                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Audio Capture                                    │
│                         (Record until silence detected)                  │
└─────────────────────────────────────────┬───────────────────────────────┘
                                          │
                          ┌───────────────┴───────────────┐
                          ▼                               ▼
┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│     Speech-to-Text               │   │     Speaker Identification       │
│     (faster-whisper small)       │   │     (pyannote embeddings)        │
│     GPU: ~100ms for 5s audio     │   │     GPU: ~50ms                   │
└──────────────────────────────────┘   └──────────────────────────────────┘
                          │                               │
                          └───────────────┬───────────────┘
                                          ▼
                        ┌─────────────────────────────────────────┐
                        │           Conversation Manager           │
                        │           (Text + User ID → Response)    │
                        └─────────────────────────────────────────┘
                                          │
                                          ▼
                        ┌─────────────────────────────────────────┐
                        │           Text-to-Speech                 │
                        │           (Kokoro TTS - local)           │
                        │           GPU: ~200ms for typical response│
                        └─────────────────────────────────────────┘
                                          │
                                          ▼
                        ┌─────────────────────────────────────────┐
                        │           Audio Output (Speaker)         │
                        └─────────────────────────────────────────┘
```

### Component Selection

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Wake Word | OpenWakeWord | Open-source, customizable, low resource |
| STT | faster-whisper (small) | Excellent accuracy, GPU-optimized, ~100ms |
| Speaker ID | pyannote.audio | Strong embeddings, works with short audio |
| TTS | Kokoro | Natural voices, fast, local, MIT license |
| Audio I/O | sounddevice | Low-latency, cross-platform |

### Model Specifications

| Model | Size | GPU Memory | Inference Time |
|-------|------|------------|----------------|
| OpenWakeWord | ~5MB | Minimal | ~10ms |
| faster-whisper small | ~500MB | ~1GB | ~100ms/5s audio |
| pyannote embedding | ~100MB | ~500MB | ~50ms |
| Kokoro TTS | ~500MB | ~1GB | ~200ms/sentence |

**Total GPU memory**: ~3-4GB (fits well within Jetson's 16GB)

## Consequences

### Positive
- **Privacy**: All processing local, no audio leaves device
- **Low latency**: Sub-second end-to-end response time
- **No API costs**: All models run locally
- **Offline capable**: Works without internet
- **Customizable**: Can train custom wake word

### Negative
- **Accuracy trade-off**: Whisper small < large (but good enough)
- **Resource usage**: Continuous GPU utilization for wake word
- **Voice variety**: Limited to Kokoro's voice options
- **Setup complexity**: Multiple models to configure

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Wake word false positives | Tune threshold, add confirmation |
| Kids' speech recognition | Test with kids, consider fine-tuning |
| Background noise | Use noise suppression, directional mic |
| Model updates break things | Pin model versions, test before updating |

## Implementation Notes

### Wake Word Configuration
```python
from openwakeword import Model

wake_model = Model(
    wakeword_models=["hey_reachy"],  # Custom trained
    inference_framework="onnx"
)

def detect_wake_word(audio_chunk):
    prediction = wake_model.predict(audio_chunk)
    return prediction["hey_reachy"] > 0.5
```

### STT Configuration
```python
from faster_whisper import WhisperModel

whisper = WhisperModel(
    "small",
    device="cuda",
    compute_type="float16"  # Optimized for Jetson
)

def transcribe(audio):
    segments, info = whisper.transcribe(audio, language="en")
    return " ".join([s.text for s in segments])
```

### TTS Configuration
```python
from kokoro import KokoroTTS

tts = KokoroTTS(
    voice="af_bella",  # Natural American female voice
    speed=1.0
)

def speak(text):
    audio = tts.generate(text)
    play_audio(audio)
```

### Speaker Identification
```python
from pyannote.audio import Model, Inference

speaker_model = Model.from_pretrained("pyannote/embedding")
inference = Inference(speaker_model)

def identify_speaker(audio):
    embedding = inference(audio)
    user_id, confidence = match_embedding(embedding, enrolled_voices)
    return user_id if confidence > 0.7 else None
```

### Audio Flow Manager
```python
class AudioPipeline:
    def __init__(self):
        self.wake_word = WakeWordDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.speaker_id = SpeakerIdentifier()

    async def run(self):
        while True:
            # Always listening for wake word
            if await self.wake_word.detected():
                # Record until silence
                audio = await self.record_utterance()

                # Parallel processing
                text, speaker = await asyncio.gather(
                    self.stt.transcribe(audio),
                    self.speaker_id.identify(audio)
                )

                # Process and respond
                response = await self.conversation.process(text, speaker)
                await self.tts.speak(response)
```

## Latency Budget

| Stage | Target | Notes |
|-------|--------|-------|
| Wake word detection | <200ms | From wake word end to recording start |
| Recording | Variable | Until 1s silence detected |
| STT | <500ms | For typical 3-5s utterance |
| Speaker ID | <100ms | Runs parallel to STT |
| LLM (Claude) | <2000ms | API call |
| TTS | <300ms | For typical response |
| **Total** | **<3s** | From end of speech to start of response |

## Future Considerations

1. **Custom wake word training**: Train on family's voices
2. **Whisper fine-tuning**: For kids' speech patterns
3. **Emotion detection**: Adjust responses based on tone
4. **Multi-language**: Support for other languages if needed

## Related Decisions
- ADR-004: LLM strategy (text processing between STT and TTS)
- ADR-006: Deployment architecture (hardware requirements)
