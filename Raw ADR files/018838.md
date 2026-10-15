# 06. Multiplayer Tetris User Experience Flow

Date: 2025-05-25

## Status

Accepted

## Context

With the transition to a true multiplayer architecture supporting multiple devices, the user experience must be reimagined to accommodate remote players joining, playing, and leaving games in a seamless and intuitive way. The client application should guide users from landing on the site, through joining or creating a game session, to playing and eventually seeing results or starting a new game. This ADR outlines the recommended user flow and the corresponding client-side pages/screens, as well as the actions available to users at each stage.

## Decision

The multiplayer Tetris client will consist of the following main pages/screens:

### 1. Landing Page / Home

- **Purpose:** Welcome users and provide entry points to create or join a game.
- **Actions:**
  - Enter a player name and (optionally) select a color/avatar.
  - Choose to "Create Game" (host) or "Join Game" (enter a room code or select from a list).
  - View basic instructions or a "How to Play" link.

### 2. Lobby / Waiting Room

- **Purpose:** Allow players to gather before the game starts.
- **Actions:**
  - See a list of connected players (names, colors).
  - Copy/share the game link or room code with friends.
  - Host can start the game when ready (if applicable).
  - Option to leave the lobby and return to Home.
  - See status messages (e.g., "Waiting for players...").

### 3. Game Screen

- **Purpose:** Main gameplay interface.
- **Actions:**
  - Play Tetris using keyboard/touch controls.
  - See own and (optionally) other players' boards/scores.
  - View current points, next piece, and other game info.
  - Receive real-time updates from the server (state sync).
  - Option to pause (if supported) or forfeit/leave the game.

### 4. Game Over / Results

- **Purpose:** Show results after the game ends.
- **Actions:**
  - View final scores and rankings.
  - Option to play again (restart with same players), return to lobby, or go back to Home.
  - Share results (optional).
  - See summary of actions (e.g., lines cleared, time played).

### 5. Error / Disconnection Screen (as needed)

- **Purpose:** Handle network errors, lost connections, or invalid room codes.
- **Actions:**
  - Display error messages and guidance.
  - Option to retry, return to Home, or contact support.

#### Optional: Spectator Mode

- Allow users to join as spectators and watch ongoing games.

## Consequences

- **Improved Onboarding:** Clear separation of joining/creating games and gameplay reduces confusion for new users.
- **Social Play:** Lobby enables players to coordinate before starting, improving the multiplayer experience.
- **Resilience:** Dedicated error handling screens improve robustness in the face of network issues.
- **Replayability:** Game Over screen encourages replay and sharing, increasing engagement.
- **Extensibility:** This flow supports future features such as matchmaking, chat, or tournaments.

## Example Flow

1. **User visits site →** enters name → chooses "Create Game" or "Join Game".
2. **Lobby:** Waits for friends to join, sees player list.
3. **Game starts:** Plays Tetris, receives real-time updates.
4. **Game ends:** Sees results, can play again or return home.
