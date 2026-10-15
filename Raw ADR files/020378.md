# ADR-0005: Projects as Foundation Architecture

**Status:** Accepted  
**Date:** 2025-12-01  
**Supersedes:** None  
**Superseded By:** N/A

---

## Context

During Week 1 exploration, we conducted an automated inventory of the user's project landscape, discovering **59 unique projects** across GitHub and local directories. This empirical data revealed critical insights that challenged our original feature prioritization:

**Inventory Findings:**

- **59 projects total:** 20 Work, 16 Personal, 17 Learning, 6 Inactive
- **24 programming languages/technologies** in active use
- **Multi-organizational context:** DRW (host), Apprenti (employer), Personal projects
- **Learning projects constitute 29%** of total portfolio
- **Complex classification needs:** Work-related vs personal development learning

**Original Requirements (Pre-Inventory):**

1. Daily Focus (tasks)
2. Skills Matrix
3. Learning Journal
4. Goals
5. Engagement/Meetings
6. Feedback
7. Energy Tracking

**Problem Identified:**

- Projects were initially considered an "8th potential feature expansion"
- User's core challenge is **project organization**, not adding more planning systems
- Without project context, other features lack grounding in reality
- Skills Matrix cannot leverage discovered tech stack data
- Daily Focus simplified to "Which project am I working on today?"

**User Feedback:**

> "Maybe right now, the project needs to start with organization of my projects in general?"

**Strategic Question:** Should we add more productivity systems before organizing what the user already has?

## Decision

We will **promote Projects to Priority #1** and make it the **foundational feature** of the MVP architecture. The application will follow a **Projects-First** approach where:

1. **Projects is the Core Feature** (Priority #1)

   - Full CRUD for project management
   - Organization-aware (DRW / Apprenti / Personal)
   - Classification system (Work / Personal / Learning / Inactive)
   - Learning project sub-classification (Work-related vs Personal development)
   - Tech stack tracking and visualization
   - Project search and filtering

2. **Daily Focus Simplified** (Priority #2)

   - Reframed as "Which project am I working on today?"
   - Project-centric task tracking
   - Links to project context

3. **Skills Matrix Seeded** (Priority #3)

   - Bootstrap from 24 discovered languages/technologies
   - Skills-to-Projects many-to-many relationship
   - Track skill usage across project portfolio

4. **Other Features Build Upon Projects:**
   - Learning Journal → Associated with Learning projects
   - Goals → Tied to project milestones
   - Meetings → Project context for engagement

### Hybrid Complexity Model

**Phase 1 (Week 2-3): Projects Core**

- Projects CRUD with full classification
- Organization support (DRW, Apprenti, Personal)
- Learning sub-classification (work_related, personal_dev, hybrid)
- Tech stack tracking
- Project search/filtering (SQLite FTS5)

**Phase 2 (Week 4-5): Simple Planning**

- Simplified Daily Focus (project-centric)
- Basic task tracking tied to projects
- Skills Matrix seeded from inventory

**Phase 3 (Week 6-7): Connections**

- Projects-to-Skills relationships
- Learning context for projects
- Project insights and analytics

**Phase 4 (Week 8+): Advanced Planning**

- Goals tied to projects
- Engagement/meetings with project context
- Advanced filtering and reporting

## Consequences

### Positive

- **Data-Driven Decision:** Based on real inventory findings (59 projects), not assumptions
- **Immediate Value:** User can organize existing projects on Day 1
- **Reduces Cognitive Load:** Focus on "what am I working on" instead of complex planning
- **Leverages Real Data:** Skills Matrix bootstrapped from 24 discovered technologies
- **Natural Foundation:** Other features have clear context when tied to projects
- **Validates Tech Stack:** SQLite search (FTS5), React filtering components, Zustand state
- **Clear MVP Scope:** Phase 1 delivers tangible value quickly
- **Scalable Architecture:** Hybrid complexity allows incremental feature addition

### Negative

- **Delays Original Features:** Daily Focus, Learning Journal deferred to Phases 2-3
- **Schema Complexity:** Projects table requires careful design upfront
- **Search Infrastructure:** Requires SQLite FTS5 implementation early
- **Learning Classification Complexity:** Sub-classification adds schema and UI complexity
- **User Onboarding:** Need to import 59 projects from inventory data

**Mitigation:**

- Original features not abandoned, just reframed with project context
- Projects table schema thoroughly researched (Week 2 topic)
- SQLite FTS5 is built-in, well-documented, suitable for <1000 records
- Learning taxonomy clearly documented in `learning-project-taxonomy.md`
- Import scripts already created during POC (deduplicate-projects.py)

## Alternatives Considered

### Alternative 1: Original Priority Order (Daily Focus First)

**Description:** Implement Daily Focus (task tracking) as Priority #1, add Projects as 8th feature later

**Pros:**

- Matches original requirements document
- Familiar productivity pattern (task lists)
- Simpler initial UI

**Cons:**

- Tasks lack project context ("What project is this task for?")
- Ignores user's actual pain point (59 projects to organize)
- Skills Matrix can't leverage discovered tech stack data
- Adds complexity before solving root problem
- Inventory data becomes unused

**Why Not Chosen:** Contradicts empirical evidence. User doesn't need more planning systems before organizing existing work. Would create task-centric app when user needs project organization.

### Alternative 2: Parallel Implementation (Projects + Daily Focus)

**Description:** Build Projects and Daily Focus simultaneously in Phase 1

**Pros:**

- Delivers both features quickly
- Satisfies original requirements
- Shows connection between projects and tasks

**Cons:**

- Splits focus between two major features
- Increases Phase 1 complexity
- Risks shipping neither feature well
- Doubles MVP scope and timeline

**Why Not Chosen:** Violates "do one thing well" principle. Better to deliver excellent project management than mediocre project + task tracking.

### Alternative 3: Minimal Projects (No Learning Sub-Classification)

**Description:** Implement Projects as Priority #1 but defer Learning sub-classification

**Pros:**

- Simpler initial schema
- Faster Phase 1 delivery
- Fewer UI components

**Cons:**

- 17 Learning projects (29%) lack proper classification
- Can't distinguish work-required learning from personal hobbies
- Metrics and time allocation inaccurate
- Difficult to retrofit classification later

**Why Not Chosen:** Learning sub-classification is critical for MVP. Without it, 29% of projects lack proper context. User explicitly requested work vs personal learning separation.

## Implementation Notes

### Phase 1 Priorities (Week 2-3)

1. **Projects Data Model Research** (HIGH - Week 2)

   - Schema design with Learning classification fields
   - Projects-to-Skills many-to-many relationship
   - Organization context (DRW, Apprenti, Personal)
   - Status lifecycle (active, learning, archived, inactive)

2. **Project Search Architecture** (HIGH - Week 2)

   - SQLite FTS5 implementation
   - Multi-faceted filtering (org + classification + learning_type)
   - React search components (react-select, react-search-autocomplete)

3. **Learning Taxonomy** (✅ Complete - 2025-12-01)
   - Documented in `learning-project-taxonomy.md`
   - Categories: Work-related, Personal development, Hybrid
   - Schema: learning_type, learning_context, learning_status

### Database Schema Changes (ADR-0003 Impact)

**New Tables:**

- **Projects** (Priority #1 table)

  - Core fields: name, path, remote_url, organization, classification, status
  - Learning fields: learning_type, learning_context, learning_status
  - Tech stack: tech_stack (JSON array or separate table)
  - Metadata: created_at, updated_at, last_worked_on

- **projects_skills** (Junction table)
  - Many-to-many relationship between Projects and Skills

**Modified Priority:**

- Projects table implemented **before** Tasks, Skills, or Learnings
- Skills table seeded from inventory (24 languages/technologies)

### Import Strategy

1. Use existing `classifications-merged.json` (59 projects, deduplicated)
2. Create import script to populate Projects table
3. Prompt user for Learning sub-classification during import
4. Auto-detect tech stack from GitHub languages API and local file analysis

### Success Criteria

- **Phase 1 Complete:** User can manage 59 projects in organized interface
- **Search Functional:** Can find projects by name, tech, classification, learning type
- **Learning Classified:** All 17 Learning projects properly sub-categorized
- **Tech Stack Visible:** Skills Matrix shows 24 languages with project associations
- **Organization Context:** Clear separation of DRW, Apprenti, Personal projects

## References

- [Projects-First Strategy Document](../planning/notes/projects-first-strategy.md) - Strategic rationale (450+ lines)
- [Learning Project Taxonomy](../research/data-models/learning-project-taxonomy.md) - Classification design
- [Current State Inventory](../exploration/current-state-inventory.md) - 59 projects documented
- [Discovered Skills](../exploration/discovered-skills.md) - 24 technologies identified
- [SQLite Database Design Research](../research/tech-stack/sqlite-database-design.md) - Schema foundation
- [ADR-0003: SQLite Database Design](ADR-0003-sqlite-database-design.md) - Database architecture

## Related ADRs

**Foundational Decisions (Week 1):**

This feature architecture builds upon the Week 1 technology stack decisions:

- **ADR-0001:** Flask Backend Architecture - Provides `/api/projects` blueprint pattern and service layer for Projects feature
- **ADR-0002:** React Frontend Architecture - Provides `projects/` feature module structure and Zustand state management
- **ADR-0003:** SQLite Database Design - Extended with Projects table and projects_skills junction (see ADR-0003 Addendum)
- **ADR-0004:** Flask-React Integration Strategy - Integration approach used for Projects API communication

**Decision Flow:**

1. ADRs 0001-0004 established tech stack (Flask, React, SQLite, integration)
2. Week 1 inventory POC discovered 59 projects needing organization
3. ADR-0005 promotes Projects to Priority #1 within that tech stack
4. ADRs 0001-0002 updated to include Projects in blueprint/feature lists

---

**Last Updated:** 2025-12-01  
**Status:** ✅ Accepted and Active
