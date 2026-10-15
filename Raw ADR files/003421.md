# ADR 002: Improve Performance of Close Control Display Time (Introduce Concurrency)


Before the application of the CPA feature, the Flight Close Control display for aircraft on the RUI met the QA-01 requirement (response time < 1s), with an average update time of 315.2ms over 30 attempts for 8,000 aircraft.

However, after applying CPA, the system could only display up to around 4,000 aircrafts, and performance issues arose due to latency affecting the update time of the Close Control display.
[Reference: Experiment 4](https://docs.google.com/document/d/14iqMM11d6TfCtYCdGdRo0fHWyrxUSejTZ_Kb75wdEPE/edit?tab=t.0)


## Decision

To isolate the impact of CPA computation on the RUI, a separate thread was created to perform only the CPA operations.  
(Tactic: Introduce Concurrency)


## Rationale

We will apply "Introduce Concurrency" tactic to improve the performance because of following reasons:
- It avoided unintended downgrades or side effects of CPA functionality.
- It separated CPA computation from RUI update processes.
- It improved both Close Control update and aircraft display performance.
- Although more complex, it effectively addressed the issue and reduced future risk.

Rejected alternatives and rationale:
"Reduced Computational Overhead" tactic was considered as alternative but not selected because of following reason :
To improve throughput during CPA computations, we reviewed the logic and excluded the following two cases from processing:
1) Aircraft without location information were excluded.
2) Aircraft projected to travel more than 100 nautical miles were excluded, based on a maximum CPA evaluation range of 90 nautical miles in the same direction.
Despite filtering out these unnecessary computation conditions and re-running the experiment, we found that this alone did not yield noticeable performance improvements. Although a complete revision of the CPA logic could potentially address the issue, this alternative was not feasible due to our current schedule constraints.


## Status

**Accepted**


## Consequences

### ✅ Positive Outcomes

- Achieved QA-01 response goal.
- Aircraft display performed well even at 100ms RUI refresh rate (Reference: *Experiment 6*).
- Supports QA-06 (Extensibility) by isolating CPA thread and minimizing impact on UI.
- Easier to extend RUI functionality without disrupting CPA logic.

### ⚠️ Negative Impacts

- Slight increase in design complexity due to threading and structural separation.
- Minor impact on Modifiability, though mitigated since CPA logic is parameterized and stable.

