# Real-Time Alerts to Nurse Station SPA Client

## Status
ACCEPTED

## Context
The Hospital Software System requires a mechanism to deliver real-time alerts to nurse stations, ensuring timely awareness of critical events. Traditional polling mechanisms may introduce latency, impacting the responsiveness of alert delivery to nurse stations.

## Decision
After considering various options for delivering real-time alerts to the Nurse Station Single Page Application (SPA) clients, including WebSocket-based communication, Server-Sent Events (SSE), Push Notifications, and a Polling Mechanism, we acknowledge Server-Sent Events (SSE) but give it less weightage due to improper browser support. The chosen approach is a WebSocket-based mechanism that leverages the WebSocket protocol's bidirectional communication, enabling instant push notifications to nurse stations upon the detection of anomalies or critical events. Timely delivery of alerts remains an essential part of patient monitoring.

### Choices Considered:

1. **Push Notifications:**
   - *Explanation:* Implementing a push notification system where the server pushes updates to the client when new data is available.
   - *Consideration:* While push notifications can be efficient for real-time updates, they may introduce unpredictable latency and might not be as suitable for scenarios where instant responsiveness is crucial. Additionally, the Nurse Station Monitoring app being on-prem and a web client prefers WebSocket for better compatibility.

2. **Server-Sent Events (SSE):**
   - *Explanation:* SSE provides a unidirectional communication channel from the server to the client, allowing continuous updates. It's more lightweight than WebSocket and doesn't require constant connections.
   - *Consideration:* SSE is suitable for scenarios where real-time updates are critical, but its adoption may be limited due to improper browser support. Given this limitation and the preference for WebSocket in an on-prem and web client environment, we give less weightage to SSE in our decision-making.

3. **Polling Mechanism:**
   - *Explanation:* Polling involves periodic requests for updated data at predefined intervals, ensuring a timely display of metrics without overwhelming the server with continuous requests.
   - *Consideration:* Traditional polling mechanisms may introduce latency, impacting the responsiveness of alert delivery, but they are simpler to implement and may be suitable for scenarios with less stringent real-time requirements.

4. **WebSocket-Based Approach (Chosen):**
   - *Explanation:* WebSocket communication allows bidirectional communication, enabling instant push notifications and reducing latency for real-time alerts.
   - *Reasoning:* In the context of patient monitoring, where timely responsiveness is crucial for alerting medical staff to critical events, the WebSocket-based approach aligns well with the need for instant push notifications. The on-prem and web client nature of the Nurse Station Monitoring app further supports the preference for WebSocket.

## Consequences
The use of WebSocket-based real-time alerts reduces latency and ensures that nurse stations receive critical information promptly. This decision aligns with the need for timely responsiveness in the context of patient monitoring.

The chosen option of a WebSocket-based approach is preferred over other alternatives, considering the improper browser support for Server-Sent Events and the on-prem and web client preference for WebSocket.
