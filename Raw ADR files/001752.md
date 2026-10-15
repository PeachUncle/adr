# ADR: Choose Hybrid Storage Strategy (Local + Remote)
## 📚 Table of Contents

- [Summary](#summary)
- [Issue](#issue)
- [Decision](#decision)
- [Status](#status)
- [Assumptions](#assumptions)
- [Constraints](#constraints)
- [Positions: Comparative Analysis](#positions-comparative-analysis)
- [Argument](#argument)
- [Implications](#implications)
- [Related Decisions](#related-decisions)
- [Related Requirements](#related-requirements)
- [Related Artifacts](#related-artifacts)
- [Related Principles](#related-principles)
- [Notes](#notes)
- [References](#references)

---

## Summary
Define a storage strategy that allows the FitMind AI mobile app to work offline, support cross-device sync, and secure personal data, while meeting tight MVP deadlines.

## Issue
We need to support offline workouts and cross-device sync in an environment with intermittent connectivity, while also enabling long-term scalability and secure data handling.

## Decision
Hybrid storage combining local storage (AsyncStorage) and remote backend (MongoDB Atlas) with periodic sync.

## Status
Accepted

## Details
 # Assumptions
•	Users expect offline access to workout content.
•	Data must be synchronized securely across devices.
•	The backend uses MongoDB Atlas for persistent storage.
•	We must handle sensitive health-related user data.
•	Real-time sync is not required in MVP, but offline support is.
 # Constraints
•	Project Timeline 
•	App must work reliably in low-connectivity environments.
•	No real-time sync architecture due to time constraints.
 # Positions: Comparative Analysis
Option	Pros	Cons
Remote Storage Only	- Centralized data
- Simplified analytics
- Scalable	- No offline access
- High latency
- Poor UX in poor signal
Local Storage Only	- Very fast
- Works offline
- Easy to implement	- No sync
- No backups
- Risk of data loss
Hybrid (Chosen)	- Offline-first UX
- Sync + backup support
- Balanced model	- Requires sync/conflict logic
- Dual-layer security complexity
None (Memory only)	- Extremely fast
- Zero infra	- Data lost on app exit
- Useless for persistent features

## Argument
Hybrid storage offers the best compromise for our use case. Local AsyncStorage provides fast, offline-first access, while remote MongoDB storage ensures persistence and cross-device functionality. Sync logic can be optimized over time, but even a simple push/pull strategy supports MVP goals.

## Implications
 # Positive
•	Smooth offline experience
•	Reliable cloud backup and sync
•	Responsive UI from local caching
•	Scalability for future growth
 # Negative
•	Increased complexity due to sync conflicts
•	Security and validation needed in both layers
•	Extra testing for sync scenarios

## Related Decisions
•	ADR: Choose Backend Database

## Related Requirements
•	Support for offline workouts and progress logging
•	Cross-device data sync
•	Secure handling of health data

## Related Artifacts
•	Sync logic spec document
•	AsyncStorage wrapper module
•	MongoDB data sync APIs

## Related Principles
•	Offline-first design
•	User data safety and ownership
•	Scalable-by-default

## Notes
Syncing will initially be periodic (e.g., on app open/close or manual trigger), with conflict resolution based on timestamps or client priority.

## References
[1] MongoDB, "MongoDB Manual," MongoDB Documentation, 2024. [Online]. Available: https://www.mongodb.com/docs/manual/
[2] F. Gomez et al., “Hybrid cloud-mobile architectures for fitness apps,” IEEE Access, vol. 8, pp. 11100–11112, 2020.
[3] R. Kumar and S. Sharma, “Data persistence challenges in mobile app design,” IEEE Software, vol. 36, no. 5, pp. 38–45, 2019.


