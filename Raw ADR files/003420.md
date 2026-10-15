# ADR 001: Use Heartbeat Mechanism


We previously selected Availability as a key quality attribute for the Flight Tracker system. A [fault injection experiment - Experiment 2](https://docs.google.com/document/d/16N1N-vS0hyGsK_7ds6XFNXFj4Xg0ZByGWQRLtgze0B8/edit?tab=t.0#heading=h.bk02gqp2jods) revealed that when the SDR is physically disconnected from the Raspberry Pi, the Flight Tracker successfully logs the error condition, but the RUI remains unaware of the fault.

Moreover, no interface exists to communicate fault states between the Flight Tracker and the RUI. Recovery is not automatically initiated or visible to the user. This lack of fault awareness at the RUI level can lead to incorrect assumptions about system operation (e.g., displaying aircraft on the map and CPA calculation).

## Decision

We will implement a Heartbeat mechanism and define a fault status reporting interface between the Flight Tracker and the Remote User Interface (RUI). The heartbeat will periodically convey operational status (e.g., `"OK"`, `"SDR_DISCONNECTED"`, `"RECONNECTING"`) from the Flight Tracker to the RUI.

The RUI will interpret the heartbeat signal and respond accordingly by alerting the user or adjusting the UI state.

The heartbeat protocol will include:

- Regular transmission intervals (e.g., every 500ms)
- Lightweight JSON or binary-encoded status payloads
- Fault code enumeration to indicate specific issues (e.g., SDR disconnected, TCP failure)
- (Optional) Recovery flag to indicate progress or success

## Rationale

This decision addresses a critical gap in system observability and recoverability, directly impacting availability.

Without fault information, the RUI may present stale or misleading aircraft tracks to users. By applying the Heartbeat architectural tactic, the system becomes capable of:

- Fault detection  
- Fault propagation  
- User notification  

—all necessary for resilient behavior.

We considered an alternative where the RUI independently probes the Flight Tracker’s TCP status or relies on data freshness (e.g., no aircraft update in X seconds), but:

- These methods lack clarity
- Increase implementation complexity
- Do not account for internal errors like SDR detachment

The heartbeat interface provides a more structured, extensible, and low-overhead solution.

## Status

**Accepted**

## Consequences

✅ Improved system availability by ensuring the RUI is aware of hardware faults and can alert users accordingly  
✅ Enables future automated recovery triggers or UI-level failover options  
✅ Facilitates more accurate system monitoring and debugging  

⚠ Requires modification of both the Flight Tracker and RUI to implement the heartbeat sender and listener modules  
⚠ Introduces a continuous background communication channel (though lightweight)  
⚠ Requires design of a fault code scheme and agreement on payload format
