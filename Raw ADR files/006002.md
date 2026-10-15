# ADR-003: Database Reset Strategy for Demo Environments

## Status
Accepted

## Context
We are establishing a Demo environment for "Best Shot" to allow potential customers to experience the application. 
The application relies on two distinct types of data:
1. **Infrastructure Data (Static/Slow-moving):** User accounts (`demo`, `admin`), Roles, and fundamental configuration.
2. **Domain Data (External/Scraped):** Tournaments, Matches, Teams, and Rounds sourced from SofaScore.
3. **User Activity Data (Dynamic/Ephemeral):** Guesses, Custom Leagues, and User Standings generated during user sessions.

**The Problem:**
We need different "reset" capabilities for different scenarios.
- **Scenario A (Development/Setup):** "I need to apply schema changes or fix a broken DB."
- **Scenario B (Sales/Demo):** "I have a call in 5 minutes. I need to clear the previous prospect's guesses so the dashboard looks fresh, but I MUST NOT lose the Tournament data."

## Decision

We will implement a **Dual-Tier Reset Strategy**: "Hard Reset" vs "Soft Reset".

| Feature | **Hard Reset** (Infrastructure) | **Soft Reset** (Activity) |
| :--- | :--- | :--- |
| **Analogy** | 💿 "Format Drive & Reinstall OS" | 🗑️ "Clear Browser History & Cache" |
| **What it does** | Wipes **EVERYTHING**. Re-creates tables. Seeds Admin users. | Wipes **User Content** (Guesses, Leagues). Keeps Users & Matches. |
| **When to use** | Initial setup, Schema updates, or recovering from corruption. | Before every demo call. Daily routine. |
| **Tool** | Local CLI (`yarn db:reset:demo`) | Admin API (`POST /admin/reset-user-activity`) |
| **Risk** | 🔴 **Destructive**: Deletes Scraped Data (Tournaments). | 🟡 **Safe**: Preserves Accounts & Scraped Data. |

### 1. Hard Reset Implementation
- **Commands:** `yarn db:migrate` + `yarn db:seed`
- **Connection:** Uses Supabase Transaction Pooler (IPv4 compatible) for reliability.
- **Configuration:** Managed via `package.json` scripts (e.g., `db:reset:demo`).

### 2. Soft Reset Implementation
- **Endpoint:** `POST /v2/admin/reset-user-activity`
- **Logic:** Transactionally deletes tables in dependency order:
    1. **Performances:** `T_LeaguePerformance`, `T_TournamentPerformance`
    2. **Guesses:** `T_Guess`
    3. **Leagues:** `T_League` (including `T_LeagueRole`, `T_LeagueTournament`)
- **Constraints:** 
  - Preserves `Member` table (Users).
  - Preserves `Tournament`, `Match`, `Team` tables (Scraped Data).
  - Only executable in `demo` or `development` environments (blocked in `production`).

## Consequences

### Positive
- **Stability:** Demo users always have a valid account to log in with.
- **Context:** The application always feels "alive" with real match data (Tournaments) immediately after a reset.
- **Efficiency:** Eliminates the need to re-scrape external APIs after every demo reset.
- **Safety:** Separating "Schema Management" from "Data Cleanup" reduces the risk of accidental production wipes.

### Negative
- **Maintenance:** We must maintain the "Activity Reset" logic as new features are added (e.g., if we add "Comments", we must remember to add them to the cleanup list).

## Compliance
- This strategy aligns with our `drizzle-orm` usage.
- Adheres to the "Fail Fast" safety checks for production environments.
