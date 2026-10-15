# ADR-002: Round-Robin Scheduling

## Status
Accepted

## Context
The Agent League System requires a scheduling algorithm to determine which players compete against each other and in what order. The scheduling algorithm must:

1. **Fairness**: Every player must have equal opportunity to compete
2. **Determinism**: Given the same set of players, the schedule must be identical
3. **Completeness**: All required matchups must be scheduled exactly once
4. **Concurrency**: Support parallel match execution when multiple referees are available
5. **Simplicity**: Algorithm must be straightforward to implement and verify
6. **Game-agnostic**: Work for any game type without modification

The PRD explicitly requires (Section 4):
- Each player plays every other player exactly once
- Matches are grouped into rounds
- No player appears in more than one match per round
- Total matches: N * (N - 1) / 2 for N players

The system must support competitive leagues where all participants compete on equal terms, and the final standings reflect true relative skill across all matchups.

## Decision
We will use a deterministic Round-Robin scheduling algorithm to generate the league match schedule.

The algorithm will:
1. Generate all unique player pairs (combinations, not permutations)
2. Assign each pair to a match with a unique match_id
3. Group matches into rounds such that no player appears twice in the same round
4. Assign sequential round numbers and persist the schedule before league execution begins

## Rationale

### Fairness and Completeness
Round-robin scheduling ensures:
- **Equal matchups**: Every player plays every other player exactly once
- **No favoritism**: No player gets easier or harder opponents than others
- **Complete data**: Standings reflect performance across all possible matchups
- **Fair comparison**: Tie-breaking is meaningful because all players have equal opportunity

This is the fairest algorithm for small to medium-sized leagues where complete pairwise competition is feasible.

### Determinism
The algorithm is deterministic when:
- Players are sorted by player_id (lexicographic order) before pairing
- Match IDs are generated using a predictable pattern (e.g., hash of sorted player IDs)
- Round assignments follow a consistent grouping algorithm

Determinism enables:
- **Reproducibility**: Same players always produce same schedule
- **Testability**: Schedules can be verified against known-good outputs
- **Auditability**: Schedule generation can be explained and defended

### Concurrency Support
Grouping matches into rounds where no player appears twice allows:
- **Parallel execution**: All matches in a round can execute concurrently (limited by referee availability)
- **Progress visibility**: Rounds provide natural checkpoints for standings updates
- **Load balancing**: Referees can be assigned matches from the same round

For N players:
- Odd N: N rounds, each with (N-1)/2 matches
- Even N: N-1 rounds, each with N/2 matches

### Mathematical Properties
For N players:
- **Total matches**: N * (N - 1) / 2 (combinations formula C(N, 2))
- **Matches per player**: N - 1 (each player plays all others once)
- **Maximum concurrent matches per round**: floor(N / 2)

Examples:
- 3 players: 3 matches in 3 rounds (1 match per round)
- 4 players: 6 matches in 3 rounds (2 matches per round)
- 8 players: 28 matches in 7 rounds (4 matches per round)
- 10 players: 45 matches in 9 rounds (5 matches per round)

### Simplicity
Round-robin is well-studied and simple to implement:
- Standard algorithms exist (circle method, polygon method)
- No complex heuristics or optimization required
- Easy to explain to league administrators and participants
- Minimal configuration needed

### Game-Agnostic
The algorithm operates purely on player identities, with no knowledge of:
- Game type
- Game duration
- Player skill or strategy
- Historical outcomes

This makes it universally applicable across all game types supported by the league.

## Consequences

### Positive
1. **Guaranteed fairness**: Every player competes against every other player exactly once
2. **Simple implementation**: Well-known algorithms with reference implementations
3. **Predictable schedule size**: Easy to estimate league duration and resource needs
4. **Clear standings**: Results are comprehensive and tie-breaking is meaningful
5. **Concurrency friendly**: Rounds naturally group matches for parallel execution
6. **Testable**: Deterministic output can be verified programmatically
7. **Transparent**: Participants can verify they play all opponents

### Negative
1. **Quadratic growth**: Match count grows as N^2, limiting league size
   - 10 players: 45 matches
   - 50 players: 1,225 matches
   - 100 players: 4,950 matches (impractical)
2. **Fixed schedule**: No flexibility to adjust mid-league (e.g., add/remove players)
3. **No skill-based matching**: Strong players may have many one-sided victories
4. **Long duration**: Leagues with many players require many rounds
5. **No early termination**: All matches must complete even if standings are decided
6. **Requires complete participation**: Absent players create holes in the schedule

### Neutral
1. **Scheduling order**: The order in which specific matchups occur is arbitrary (deterministic but not strategic)
2. **Bye rounds**: Odd number of players results in one player idle per round
3. **Cold starts**: First matches have no historical context for strategy adaptation

## Implementation Notes

### Algorithm: Circle Method (Even Players)
For N players (even), use the circle method:
1. Arrange players in two columns
2. Fix player 1 in top-left position
3. Rotate remaining players clockwise each round
4. Pair across columns to generate matches

Example for 4 players (1, 2, 3, 4):
```
Round 1: 1-2, 3-4
Round 2: 1-3, 2-4
Round 3: 1-4, 2-3
```

### Algorithm: Circle Method (Odd Players)
For N players (odd):
1. Add a dummy "bye" player
2. Apply circle method for N+1 players
3. Remove matches involving "bye" player

Example for 3 players (1, 2, 3):
```
Round 1: 1-2 (3 has bye)
Round 2: 1-3 (2 has bye)
Round 3: 2-3 (1 has bye)
```

### Match ID Generation
Generate deterministic match IDs:
```python
import hashlib

def generate_match_id(player_1, player_2):
    # Sort players for determinism
    players = sorted([player_1, player_2])
    # Hash sorted pair
    pair_str = f"{players[0]}:{players[1]}"
    hash_digest = hashlib.sha256(pair_str.encode()).hexdigest()[:12]
    return f"match-{hash_digest}"
```

### Round ID Generation
```python
def generate_round_id(league_id, round_number):
    return f"{league_id}-round-{round_number:03d}"
```

### Persistence
Schedule must be persisted before league execution:
1. Generate complete schedule
2. Insert all rounds into `rounds` table
3. Insert all matches into `matches` table with status='PENDING'
4. Commit transaction atomically

### Validation
After schedule generation, validate:
- Total matches = N * (N - 1) / 2
- Each player appears exactly N - 1 times across all matches
- No player appears twice in the same round
- All player pairs appear exactly once across all matches

### Configuration
Expose configuration options:
```yaml
scheduling:
  algorithm: "round_robin"  # Only option in v1
  shuffle_rounds: false     # If true, randomize round order (but keep pairings deterministic)
  shuffle_within_rounds: false  # If true, randomize match order within rounds
```

### Extension Points
Future scheduling algorithms (out of scope for v1) could be swapped via configuration:
- Swiss-system (for large leagues)
- Knockout/elimination (for tournaments)
- League + playoff hybrid

## Alternatives Considered

### Alternative 1: Swiss-System Tournament
- **Description**: Pair players with similar records each round (no complete round-robin)
- **Pros**:
  - Scales to large player counts (logarithmic rounds: ~log2(N))
  - Competitive matchups (similar skill levels paired each round)
  - Early leaders emerge quickly
  - Fewer total matches (N * log2(N) instead of N^2)
- **Cons**:
  - Not all players compete against each other (incomplete data)
  - Requires dynamic scheduling (cannot precompute entire schedule)
  - Pairing algorithm is complex (tiebreaking, color balancing in chess-like games)
  - Less suitable for deterministic, reproducible schedules
  - Standings are less definitive (some pairs never meet)
- **Reason for rejection**: PRD explicitly requires "each player plays every other player exactly once" (Section 4.2). Swiss-system is incomplete.

### Alternative 2: Single-Elimination (Knockout)
- **Description**: Bracket-style tournament where losers are eliminated
- **Pros**:
  - Fast: log2(N) rounds
  - Exciting: every match is high-stakes
  - Clear winner determination
  - Familiar format (March Madness, World Cup)
- **Cons**:
  - Most players eliminated quickly (play only 1-3 matches)
  - Final standings are incomplete (cannot rank all players fairly)
  - Requires power-of-2 players (or byes for odd counts)
  - Seeding affects outcomes significantly (unfair if no prior data)
  - Does not satisfy "each player plays every other player" requirement
- **Reason for rejection**: Violates completeness requirement. Does not produce comprehensive standings.

### Alternative 3: Random Matchmaking
- **Description**: Randomly pair players each round
- **Pros**:
  - Simple implementation
  - Flexible (can add/remove players mid-league)
  - Fast schedule generation
- **Cons**:
  - Non-deterministic (same players produce different schedules)
  - Unfair (some pairs may never meet, others may meet multiple times)
  - Standings are not comparable (players face different opponents)
  - No guarantee of completeness
  - Difficult to audit or verify
- **Reason for rejection**: Violates fairness, determinism, and completeness requirements.

### Alternative 4: Ladder/Ranking-Based Matchmaking
- **Description**: Players challenge others near them in the ladder (Elo-based pairing)
- **Pros**:
  - Continuous league (no fixed schedule)
  - Skill-based matchups (competitive games)
  - Players can join/leave dynamically
- **Cons**:
  - Not round-robin (incomplete pairwise data)
  - Requires external ranking system (Elo, TrueSkill)
  - Difficult to determine "final" standings
  - Non-deterministic (ladder changes based on timing of challenges)
  - Complex rules for challenge eligibility
- **Reason for rejection**: Does not satisfy fixed schedule or completeness requirements. Too complex for initial implementation.

### Alternative 5: Double Round-Robin
- **Description**: Each player plays every other player twice (home and away concept)
- **Pros**:
  - More robust results (variance reduction)
  - Accounts for asymmetric games (first-player advantage)
  - Richer data for standings
- **Cons**:
  - Doubles match count: N * (N - 1) instead of N * (N - 1) / 2
  - Doubles league duration
  - Unnecessary for symmetric games (even/odd, rock-paper-scissors)
  - Exacerbates scalability problems
- **Reason for rejection**: Single round-robin is sufficient for symmetric games. Double round-robin is future enhancement if asymmetric games are introduced.

## References
- [PRD Section 4: Scheduling and Round Management](../prd/section-4-scheduling-and-rounds.md)
- [Wikipedia: Round-robin tournament](https://en.wikipedia.org/wiki/Round-robin_tournament)
- [Circle method algorithm](https://en.wikipedia.org/wiki/Round-robin_tournament#Scheduling_algorithm)
- [Architecture Documentation - Scheduling Flow](../Architecture.md#32-scheduling-and-match-assignment-flow)
- [Diagram: scheduling-flow.md](../diagrams/scheduling-flow.md)

## Metadata
- **Author**: architecture-author agent
- **Date**: 2025-01-21
- **Status**: Accepted
- **Related ADRs**:
  - [ADR-001: JSON-RPC Transport](001-json-rpc-transport.md) (schedule delivered via JSON-RPC messages)
- **Related PRD Sections**:
  - Section 4: Scheduling and Round Management
  - Section 6: Result Reporting and Standings (depends on complete pairwise data)
