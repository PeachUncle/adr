# ADR3 – Server-Side Data Store  

**Title:** Use PostgreSQL for the server-side data store  

**Status:** Revised -- Cycle 2

**Context:**  
- Allowed options: SQLite or PostgreSQL.  
- The system must support concurrent bookings without double-booking.  
- PostgreSQL offers robust concurrency control and transactional guarantees suitable for handling simultaneous bookings.  
- SQLite is lightweight and simpler to configure but not ideal for multi-user concurrent environments.  
- The database must also integrate cleanly with Docker to support the team’s containerized setup.

**Alternatives Considered:**  
- **SQLite:** Lightweight and easy to set up, but poor support for concurrent writes makes it unsuitable for handling booking conflicts in real time.  
- **In-memory storage:** Very fast, but would lose data persistence and make the application unreliable after container restarts.  
- **PostgreSQL:** Strong concurrency, transactional guarantees, and wide support with Node.js.

**Quantitative Implications:**  
- PostgreSQL can safely handle multiple concurrent write operations without data corruption, unlike SQLite which uses database-level locking.  
- Migration setup and initial configuration required more effort (~2–3x that of SQLite), but provides more stability long term.  
- Structured schema design simplifies handling of booking conflicts and reduces data integrity errors.  
- Integration with TypeORM allows for more maintainable schema migrations and version control of the database.

**Decision:**
We will use PostgreSQL as the server-side data store.  

**Consequences:**  
- ✅ Strong concurrency control, which is critical for bookings.  
- ✅ Works well with Docker packaging, which this project requires.  
- ✅ Easy to import the CSV classroom data into the schema.  
- ✅ Scales better if the project grows beyond the demo or if more classrooms are added.  
- ✅ Supports more robust data integrity checks and indexing than SQLite.

- ❌ Heavier setup than SQLite.  
- ❌ Requires schema migrations when requirements change.  
- ❌ More complex to administer compared to SQLite.

**Reflection:**  
- While PostgreSQL provides strong support for relational data modeling and concurrency, our current implementation did not progress far enough to fully leverage those capabilities.  
- The initial schema design became more complex than necessary at this stage, especially when we tried to account for future features like role-based access before the frontend–backend integration was stable.  
- PostgreSQL enables advanced data structures, but those features should be introduced gradually to ensure smooth implementation.  
- The project requires further development to fully realize the benefits of this architectural decision.

**Related User Stories**
- [User Story 4: Staff can view booking history](https://gitlab.csc.uvic.ca/courses/2025091/SENG350_COSI/teams/group_10_proj/-/issues/4)
- [User Story 10: Registrar can manage schedule integrity](https://gitlab.csc.uvic.ca/courses/2025091/SENG350_COSI/teams/group_10_proj/-/issues/24)