# ADR 001: Google Meet Attendance Monitoring System Integration Approach
Status: Proposed :progress:
Date: 2025-07-26
Deciders: Abdelfettah Ghazi

## Context and Problem Statement
We need to develop an automated system to detect and track participant presence in Google Meet sessions within an organization. The system must provide near real-time monitoring (< 1 minute delay) of when participants join and leave meetings, while ensuring compliance with Google Workspace policies and maintaining minimal permissions.

**Key requirements** (see `Requirements.md` for full specification):
- Detect participant join/leave events with ≤ 60 seconds delay
- Support up to 1000 concurrent meetings and 50,000 participants
- Use only official Google APIs and documented integration methods
- Operate with minimal permissions and no additional licensing fees
- Maintain GDPR/privacy compliance and data security

## Considered Options
- [**Google Workspace Events API**](./propositions/1-google-workspace-events-api.md) – Subscribe to real-time events from Google Workspace using webhooks and event notifications for meeting activities
- [**Google Meet SDK**](./propositions/2-google-meet-sdk.md) – Use Google Meet SDK to build custom meet add-on with participant tracking capabilities
- [**Bot as Participant**](./propositions/bot-as-participant.md) – Deploy an automated bot that joins meetings as a participant to monitor attendance (high complexity, policy risks)
- [**WebRTC Integration**](./propositions/webrtc-integration.md) – Use WebRTC protocols with Google Meet Media API to monitor participant streams via CSRC tracking (requires Developer Preview enrollment)
- [**Browser Extension**](./propositions/browser-extension.md) – Create a browser extension that monitors Google Meet sessions from the client-side using DOM observation (lightweight, high feasibility)
- [**Multi-Modal System**](./propositions/multi-modal-system.md) – Hybrid approach combining automated bots, API integrations, and browser extensions for comprehensive monitoring (comprehensive but complex)

(Detailed evaluation with pros & cons available in propositions folder)

## Chosen Option
**No option selected yet** – evaluation and decision pending based on technical feasibility analysis and compliance requirements assessment.

## Consequences
**To be determined** – consequences will be documented once a solution approach is selected and evaluated.

## Validation (optional)
How this decision will be reviewed/enforced (e.g. in code/design review, monitoring, testing).

## More Information
**References:**
- `Requirements.md` – Complete system requirements specification
- Detailed solution analyses in `Solution ADR/propositions/` folder
- [Google Meet Integration Guide 2025](https://screenapp.io/blog/how-to-integrate-with-google-meet-2025?utm_source=chatgpt.com)
- [Google Workspace Meet API Overview](https://developers.google.com/workspace/meet/overview)

**Assumptions:**
- Google Workspace organization with appropriate admin permissions
- Compliance with Google Workspace Terms of Service required
- Official APIs preferred over unofficial/undocumented methods
