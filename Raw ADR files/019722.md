# ADR-003: Narrative Layer Architecture

**Status:** Accepted
**Date:** 2025-10-24
**Deciders:** Engineering Team, UX
**Context:** Patient transparency, real-time diagnostics

---

## Context and Problem Statement

**Problem:** Patients undergoing advanced diagnostics (OCT, DEXA, VIS) experience anxiety when they don't understand what's happening, why it matters, or where their data goes. This leads to:
- **Quality degradation:** Patients move/blink during capture → retakes → longer sessions
- **Trust erosion:** "Black box" systems feel invasive; patients don't understand data flow
- **Support burden:** Facilitators repeatedly explain the same steps

**Current state:** Temporal workflows track operational events (ActivityTaskScheduled, ActivityTaskCompleted) but these are engineering-focused, not patient-friendly.

**Need:** Transform low-level workflow/device events into plain-language updates that show:
- **What** is happening ("We're focusing on your left eye")
- **Why** it matters ("This helps measure retina layers clearly")
- **What to do now** ("Look at the green dot. Try not to blink.")
- **Where data goes** ("Processing locally" vs "Sending summary to cloud")

---

## Decision

We introduce a **Narrative Layer**: a small service that subscribes to Temporal workflow events, maps them through YAML templates, and pushes patient-safe updates to mobile/iPad in real time.

### Architecture

```
┌───────────────┐       Signals/Attrs        ┌───────────────────────┐
│ Temporal/Cloud│ ─────────────────────────▶ │ Narrative Service     │
│ (workflow SoR)│                            │ (Computer 2 primary)  │
└─────┬─────────┘                            │ - Maps events→story   │
      │ CDC / WS                            │ - i18n + safety copy  │
      ▼                                      │ - Privacy ring status │
┌───────────────┐   RTP/ROS2/MQTT events     └───────────┬───────────┘
│ Workstation   │ ◀───────────────────────────┐          │
│ (ingest+AI)   │                             │          │
└─────┬─────────┘                             │     WebSocket/tRPC
      │                                       │          │
      ▼                                       ▼          ▼
┌───────────────┐                      ┌──────────┐  ┌──────────┐
│ Jetson (edge) │                      │ iPad (UX)│  │ Mobile   │
│ (prep)        │                      │ in-room  │  │ (patient)│
└───────────────┘                      └──────────┘  └──────────┘
```

**Separation of concerns:**
- **Temporal:** Operational truth (workflow state, retry logic, timeouts)
- **Narrative Layer:** Patient story (plain-language, privacy badges, actions)

Same ground truth, different views.

### Data Model

Each **NarrativeEvent** contains:

| Field | Purpose | Example |
|:--|:--|:--|
| `step` | Stage identifier | `oct.focus_left_eye` |
| `plainText` | 6th-grade reading level | "We're focusing on your left eye." |
| `why` | Short rationale | "This helps measure retina layers clearly." |
| `doNow` | Patient action | "Look at the green dot. Try not to blink." |
| `progress` | 0–100 | 45 |
| `privacyBadge` | Data locality (Ring status) | `processing_local` / `sending_summary` / `cloud_processing` |
| `etaHint` | Soft estimate (optional) | "~a minute" |
| `alert` | Safety flag (optional) | "Laser is low-power; blink if uncomfortable." |

**Guardrails:**
- No clinical claims or diagnoses ("Your retina looks healthy" → forbidden)
- 6th-grade reading level (Flesch-Kincaid)
- Privacy badge always reflects actual data flow (Ring 1/2/3)

### YAML Templates

Non-engineers can safely edit narrative copy:

```yaml
# packages/narrative/templates/oct.v1.yaml
modality: OCT
version: 1.2.0
steps:
  focus_left:
    text: "We're focusing on your left eye."
    why: "Focus helps capture sharp images of the retina."
    doNow: "Look at the green dot. Try not to blink."
    icon: "eye-focus"
    privacy: "processing_local"

  capture_left:
    text: "Taking an image of your left eye."
    why: "This image helps check retinal layers."
    doNow: "Hold still for a second."
    icon: "camera"
    privacy: "processing_local"

  ai_qc:
    text: "Checking image quality."
    why: "We verify clarity before moving on."
    doNow: "Relax—no action needed."
    icon: "ai-check"
    privacy: "processing_local"

  sending_summary:
    text: "Summarizing results."
    why: "We compute measurements for your report."
    doNow: "You're doing great."
    icon: "upload"
    privacy: "sending_summary" # Ring 2 transition
```

### Implementation

**1. Workflows emit `patientStep` signals:**

```typescript
// packages/workflows/src/oct.workflow.ts
import { upsertSearchAttributes, defineSignal } from '@temporalio/workflow'

export const patientStep = defineSignal<[{ step: string; progress?: number; privacy?: string }]>('patientStep')

export async function octWorkflow({ sessionId }) {
  upsertSearchAttributes({ SessionId: sessionId, Modality: 'OCT', Progress: 0 })

  await activities.dimLights()
  workflow.signal(patientStep, { step: 'prep_light', progress: 5, privacy: 'processing_local' })

  await activities.focusEye('left')
  workflow.signal(patientStep, { step: 'focus_left', progress: 20 })

  await activities.captureEye('left')
  workflow.signal(patientStep, { step: 'capture_left', progress: 40 })

  await activities.qualityCheck()
  workflow.signal(patientStep, { step: 'ai_qc', progress: 60 })

  await activities.computeSummary()
  workflow.signal(patientStep, { step: 'sending_summary', progress: 80, privacy: 'sending_summary' })

  upsertSearchAttributes({ Progress: 100, SessionStatus: 'COMPLETED' })
}
```

**2. Narrative Service maps events to copy:**

```typescript
// apps/narrative-service/src/event-mapper.ts
import templates from '../templates'

export function toNarrative(event: Event, modality: string): NarrativeEvent {
  const template = templates[modality][event.step]
  return {
    step: event.step,
    plainText: template.text,
    why: template.why,
    doNow: template.doNow,
    icon: template.icon,
    progress: event.progress ?? 0,
    privacyBadge: event.privacy ?? template.privacy
  }
}
```

**3. Push to mobile/iPad via WebSocket:**

```typescript
// apps/narrative-service/src/ws-server.ts
wss.on('connection', (socket, req) => {
  const { sessionId, modality } = parseQuery(req.url)

  subscribeTemporal(sessionId, (event) => {
    const narrative = toNarrative(event, modality)
    socket.send(JSON.stringify(narrative))
  })
})
```

**4. Mobile component:**

```tsx
// apps/mobile/components/LiveNarrative.tsx
export function LiveNarrative({ sessionId, modality }) {
  const [events, setEvents] = useState<NarrativeEvent[]>([])

  useEffect(() => {
    const ws = new WebSocket(`${API_WS}/narrative/${sessionId}?m=${modality}`)
    ws.onmessage = (msg) => setEvents((prev) => [...prev, JSON.parse(msg.data)])
    return () => ws.close()
  }, [sessionId, modality])

  return (
    <ScrollView className="p-4">
      {events.map((e, i) => (
        <View key={i} className="bg-white rounded-xl p-4 mb-3 shadow">
          <Text className="text-lg font-semibold">{humanize(e.step)}</Text>
          <Text className="text-gray-800 mt-1">{e.plainText}</Text>
          <Text className="text-gray-600 mt-1">Why: {e.why}</Text>
          <Text className="mt-1">{e.doNow}</Text>
          <ProgressBar value={e.progress} />
          <PrivacyBadge kind={e.privacyBadge} />
        </View>
      ))}
    </ScrollView>
  )
}
```

### Privacy Transparency

Privacy badges reflect **PHI Rings** (ADR-002):

| Badge | Meaning | Ring |
|:--|:--|:--|
| `processing_local` | "Your images are being processed on this device." | Ring 1 (workstation) |
| `sending_summary` | "We're sending a summary (not the full image) for analysis." | Ring 2 (features → cloud) |
| `cloud_processing` | "Encrypted processing in our secure data center." | Ring 2 (cloud) |

Badge always matches actual data flow; engineers cannot fake it.

### Narrative Editor

Non-engineers edit templates safely:

```tsx
// apps/facilitator-portal/pages/narrative-editor.tsx
export default function NarrativeEditor() {
  const [templates, setTemplates] = useState<Template[]>(loadTemplates())

  const handleSave = async (template: Template) => {
    // Validate: no clinical claims, reading level check
    await validateTemplate(template)

    // Save with Git commit
    await fetch('/api/narrative/save', {
      method: 'POST',
      body: JSON.stringify(template)
    })

    // Audit log
    logger.info('Narrative template updated', { templateId: template.id, userId })
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Narrative Editor</h1>
      {templates.map(t => (
        <TemplateEditor key={t.id} template={t} onSave={handleSave} />
      ))}
    </div>
  )
}
```

---

## Consequences

### Positive

- **Reduced patient anxiety:** Clear "what/why/do now" guidance improves capture quality (fewer retakes)
- **Trust through transparency:** Privacy badges show where data goes; patients see local processing
- **Scalable to all modalities:** YAML templates mean adding new diagnostic = writing new narrative, not code
- **Non-engineer friendly:** Facilitators/UX can iterate copy without touching workflows
- **i18n-ready:** YAML files per language (oct.v1.en.yaml, oct.v1.es.yaml)
- **Compliance benefit:** Narrative + privacy badges = consent transparency

### Negative

- **Template drift:** YAML may fall out of sync with workflow steps
  - *Mitigation:* CI test validates all steps in workflow have template entries
- **Narrative Service is a SPOF:** If it crashes, patients see no updates
  - *Mitigation:* Deploy redundant instance; fallback to basic "Step X of Y" progress bar
- **Subjective copy quality:** "6th-grade reading level" hard to enforce
  - *Mitigation:* Flesch-Kincaid scoring in CI; manual UX review before prod
- **WebSocket scalability:** 100 concurrent sessions = 100 WS connections
  - *Mitigation:* Use tRPC subscriptions or Server-Sent Events (SSE) instead

---

## Alternatives Considered

### Alternative 1: Embed Patient Copy in Temporal Workflows

**Pros:** No separate service; simpler deployment
**Cons:** Workflows become bloated; copy changes require workflow versioning; hard to iterate UX

**Decision:** Rejected. Separation of concerns is critical; workflows should stay engineering-focused.

### Alternative 2: Static Progress Bar ("Step 3 of 7")

**Pros:** Simple; no templates needed
**Cons:** No "why" or "do now"; no privacy transparency; patients still confused

**Decision:** Rejected. Not sufficient for trust-building.

### Alternative 3: Video Explainers (Pre-recorded)

**Pros:** Rich media; professional production
**Cons:** Cannot adapt to workflow state (e.g., "retake needed"); no real-time updates

**Decision:** Rejected. Use as supplemental onboarding, not live narrative.

---

## Validation Metrics

| Metric | Goal | Measurement |
|:--|:--|:--|
| **Comprehension tap** ("Got it") | > 85% per step | 1-tap feedback on cards |
| **Aborted captures (motion/blink)** | −30% | Correlate QC failures with narrative timing |
| **Session anxiety score** | −20% | Post-session 3-question survey |
| **Support interrupts** | −50% | Fewer facilitator interventions |

---

## Related Decisions

- **ADR-002:** PHI Rings (privacy badges reflect ring transitions)
- **ADR-001:** Local Compute Policy (badges show where compute runs)
- **Development Plan:** Week 3 (Narrative Layer Foundation)

---

## References

- [Flesch-Kincaid Grade Level](https://readable.com/readability/flesch-reading-ease-flesch-kincaid-grade-level/)
- [Plain Language Medical Communication](https://www.nih.gov/institutes-nih/nih-office-director/office-communications-public-liaison/clear-communication/plain-language)
- Temporal Signals: [docs/architecture/temporal-integration.md](../temporal-integration.md)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-24
**Maintained By:** Vantage Engineering + UX
