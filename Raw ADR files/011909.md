# Polling Mechanism for Monitoring Dashboard

## Status
ACCEPTED

## Context
The Hospital Software System requires a mechanism to update and display vital metrics on monitoring dashboards. The system must strike a balance between real-time updates and server load to provide an efficient and responsive user experience.Also another key point of consideration is vital metrics are refreshed at defined polling frequency which is not less than 500ms.

## Decision
After considering various options for delivering vital metrics to the monitoring dashboard of the Single Page Application (SPA), including WebSocket communication, Server-Sent Events (SSE), Push Notifications, and Polling, we choose a polling mechanism for the following reasons:

### Choices Considered:

1. **WebSocket Communication:**
   - *Explanation:* WebSocket communication allows for bidirectional communication between the client (monitoring dashboard) and the server. It enables real-time updates without the need for periodic polling.
   - *Consideration:* While WebSocket communication is effective for real-time updates, it might introduce higher server load compared to polling, especially in scenarios where a large number of clients are connected.

2. **Server-Sent Events (SSE):**
   - *Explanation:* SSE is a unidirectional communication channel from the server to the client that allows continuous updates. It's more lightweight than WebSocket and doesn't require constant connections.
   - *Consideration:* SSE is suitable for scenarios where real-time updates are critical. However, its support may vary across different browsers, and it may not be as versatile as polling for controlling the update frequency.

3. **Push Notifications:**
   - *Explanation:* Implementing a push notification system where the server pushes updates to the client when new data is available.
   - *Consideration:* While push notifications can be efficient for real-time updates, they may require additional infrastructure, and introduce unpredictable latency which is undesirable in this context .

4. **Polling Mechanism:**
   - *Explanation:* Polling involves periodic requests for updated data at predefined intervals, ensuring a timely display of metrics without overwhelming the server with continuous requests.
   - *Reasoning:* Considering the requirement for monitoring patient vitals, where the polling frequency is not less than 500 ms for every vital, the polling mechanism aligns well with this need. It provides a balance between real-time updates and server load while ensuring predictability and compatibility.

## Consequences
By employing a polling mechanism, we achieve a balance between real-time updates and reduced server load. The monitoring dashboard receives updated information at regular intervals, optimizing resource utilization and responsiveness. This decision is driven by the critical nature of monitoring patient vitals, where reliability and predictability are paramount.

The chosen option of a polling mechanism is preferred over other alternatives to ensure a dependable and efficient monitoring experience for patient vitals.
