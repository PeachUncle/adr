# ADR-0001: Consistent Trigger Strategy

<!--  ctrl + shift + v-->
<!-- Metadata Section -->

| Metadata   | Value      |
| ---------- | ---------- |
| **Status** | Accepted   |
| **Date**   | 21-05-2025 |

---

## Context and Problem Statement {################# REQUIRED #################}

We need to ensure that form data is reliably submitted to Dynamics when a user navigates away from the page at any step of the process. The current implementation relies on the unload event, which has proven unreliable and will be deprecated in near future — particularly in Edge during refresh actions and in Chrome when closing the tab or browser. This results in a low submission success rate (~60%), which is insufficient. A more robust and consistent trigger mechanism is required to improve data reliability and user experience.

---

## Decision Drivers

Key factors influencing this decision:

- Reliability – Ensure form submission is consistently triggered regardless of how the user leaves the page.
- Browser Compatibility – Support consistent behavior across mobile/desktop browsers.
- Success Rate – Improve submission success rate significantly beyond the current ~60%.

---

## Considered Options {################# REQUIRED #################}

1. **Change event**  
   _One option is to use the visibilitychange or pagehide events to trigger form submission. This approach can improve reliability on mobile devices and covers scenarios like app switching or minimizing the browser. While pagehide offers a slight improvement over the deprecated unload event, visibilitychange may lead to excessive and unnecessary API calls, as it fires whenever the page is hidden—even during harmless actions like tab switching or minimizing the window._
2. **Move submission to a specific step in the flow**  
   _A second option is to remove event-based submission entirely and instead trigger the submission at a defined step in the flow (e.g., step 4), immediately after the page loads. This avoids the issues associated with unreliable unload-like events and gives more control over when the submission happens. However, it risks missing data if the user exits the process before reaching that step or navigates away immediately after loading._
3. **Use sendBeacon instead of fetch**  
   _The third option is to switch from using fetch to the sendBeacon API, which is designed for sending data in the background during page unload. This method offers improved reliability over fetch for such use cases. Unfortunately, sendBeacon only supports sending data as text/plain or Blob, which makes it incompatible with the Dynamics API that expects application/json content._

---

## Decision Outcome {################# REQUIRED #################}

**Chosen Option:** Option 2

**Justification:** Option 2 was chosen because it allows best journey entry success rate

---

### Consequences {################# REQUIRED #################}

| Aspect       | Impact                                 |
| ------------ | -------------------------------------- |
| **Positive** | Success rate                           |
| **Negative** | Email link will always come from step3 |

---

## Validation

- [x] Performance testing

---
