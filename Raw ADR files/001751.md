# ADR: Choose Backend Database
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
Select a backend database solution to support the FitMind AI app's need to store and manage user profiles, workout media, AI-generated plans, and progress logs.

## Issue
We need a backend database that integrates well with our JavaScript-based stack (Node.js, TypeScript, React Native) and can handle both structured and semi-structured data types while supporting scalability and fast development.

## Decision
MongoDB was selected as the backend database.

## Status
Accepted

## Details
 # Assumptions
•	The backend will be built with Node.js and TypeScript.
•	Developers have moderate JavaScript experience but limited SQL exposure.
•	Data structures (e.g., workouts, AI-generated plans) are expected to evolve rapidly.
•	We require a cloud-scalable and mobile-friendly backend.
 # Constraints
•	Project Timeline
•	Limited team expertise in SQL.
•	AI and analytics features depend on flexible data models.
 # Positions: Comparative Analysis
Option	Pros	Cons
MongoDB (NoSQL)	- Schema flexibility
- Native Node.js support
- Scalable via MongoDB Atlas	- No foreign keys
- Complex joins are inefficient
- Requires app-level validation
PostgreSQL (SQL)	- Strong relational integrity
- Great for analytics
- Robust constraints	- Slower dev cycles
- Steeper learning curve
- Less ideal for dynamic/nested data
Firebase Firestore	- Real-time sync
- Serverless
- Mobile-first integration	- Limited query flexibility
- Vendor lock-in
- Expensive at scale
None (In-memory)	- Extremely fast dev
- No storage/compliance needs	- Data lost on restart
- No syncing
- No persistence or personalization

## Argument
MongoDB offers the flexibility needed for rapid MVP development and supports semi-structured and evolving data. It integrates easily with Node.js via Mongoose and allows for horizontal scaling via MongoDB Atlas. Though it lacks relational constraints, this tradeoff is manageable for the MVP scope.

## Implications
 # Positive
•	Fast iteration using JavaScript-native tools
•	Flexible schema fits AI and dynamic workout data
•	Horizontal scalability and JSON-friendly structure
•	Pairs well with mobile local storage strategies
# Negative
•	Requires app-managed validation and consistency
•	Less effective for complex analytical reporting
•	Risk of data inconsistency without strict schemas

## Related Decisions
•	ADR: Choose Hybrid Storage Strategy (Local + Remote)

## Related Requirements
•	Scalable, cloud-hosted database
•	Support for both structured and unstructured data
•	Easy backend integration with JavaScript stack

## Related Artifacts
•	MongoDB schema design drafts
•	Mongoose ODM configuration
•	MVP development plan

## Related Principles
•	Build for MVP speed and flexibility
•	Cloud-native and mobile-first architecture

## Notes
Validation logic will be implemented in the application using Mongoose schemas. Future analytics use cases may require ETL pipelines or data modeling extensions.

## References
[1] MongoDB, "MongoDB Manual," MongoDB Documentation, 2024. [Online]. Available: https://www.mongodb.com/docs/manual/
[2] C. S. A. Fernandes, “NoSQL databases for flexible fitness app data,” Journal of Software Engineering, vol. 15, no. 3, pp. 120–130, 2022.
[3] J. Patel and M. Thompson, “Choosing databases for scalable mobile applications,” IEEE Software, vol. 37, no. 2, pp. 45–53, 2020.



