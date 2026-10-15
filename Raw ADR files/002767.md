## Context
Staff Wars is a widely-used music education tool for teaching note reading on the staff. This implementation recreates the core "classic" tap-to-answer loop where notes scroll from right to left and the player must identify the note name before it reaches the clef.

**Background:**
- Primary users: Elementary to secondary music learners (ages 7-14)
- Secondary users: Music educators facilitating classroom practice sessions
- Reference: Original Staff Wars app uses clef selection, note spawning, progressive speed, three-life system

**Constraints:**
- Must work on mobile/tablet browsers (touch-friendly)
- Must maintain 60 FPS animation performance
- Must use only MIT-licensed libraries
- Must not include trademarked/branded assets
- MVP excludes microphone input (Staff Wars Live mode) - deferred to future enhancement
- MVP excludes instrument fingering modes - deferred to future enhancement

## Goals / Non-Goals

**Goals:**
- Deliver smooth, classroom-ready note reading practice
- Support configurable clef (treble, bass, alto) and note range
- Provide progressive difficulty through speed escalation
- Enable quick start (< 10 seconds from load to gameplay)
- Maintain performance on low-end tablets
- Support accessibility requirements (WCAG 2.1 AA)

**Non-Goals:**
- Platform-native mobile apps (web-only for MVP)
- Microphone pitch detection / Staff Wars Live mode
- Instrument fingering visualization
- Multi-player or leaderboard features (beyond local high scores)
- Server-side persistence (localStorage only for MVP)
- Solfège or non-letter note naming systems

## Decisions

### Architecture: Client-Only SPA with Game Loop

**Decision:** Implement as a pure client-side SPA using requestAnimationFrame for the game loop, with no server dependencies for gameplay.

**Rationale:**
- Aligns with existing project architecture (static SPA deployment)
- Minimizes latency for smooth 60 FPS animation
- Simplifies deployment and reduces infrastructure costs
- localStorage sufficient for high score persistence in MVP

**Alternatives considered:**
- Server-based game state: Rejected due to latency concerns and unnecessary complexity for single-player game
- Canvas-only rendering: Partially adopted via VexFlow's Canvas output mode

### Notation Library: VexFlow

**Decision:** Use VexFlow v5.x (TypeScript-native library) for staff and note rendering via Canvas.

**Rationale:**
- **TypeScript-native**: Written in TypeScript, compiled to ES6 - perfect alignment with project stack
- **MIT licensed**, actively maintained with 131 code snippets in documentation
- **SMuFL-compatible glyphs** for standard notation (Bravura, Petaluma fonts)
- **Dual rendering**: Supports both Canvas and SVG output
  - **Canvas preferred** for this use case: better performance for real-time animation
  - SVG available as fallback if needed
- **Two APIs available**:
  - **Factory/EasyScore** (high-level): Quick stave + note creation
  - **Low-level API**: Fine-grained control for custom rendering
- **Automatic ledger lines**: Handles notes above/below staff automatically
- **Clef support**: Treble, bass, alto, tenor - all required clefs built-in

**Implementation approach:**
- Use Factory API to initialize renderer and stave once
- Use low-level StaveNote API to create/render individual notes
- Render to Canvas for optimal performance
- Either re-render on each frame OR use Canvas transforms to move rendered note elements
- Estimated bundle size: ~200KB minified (acceptable for this feature)

**Alternatives considered:**
- abcjs: Rejected - designed for ABC notation parsing and static rendering, not real-time games
- Custom SVG/Canvas rendering: Rejected - would require extensive music engraving expertise and manual ledger line calculation
- OpenSheetMusicDisplay (OSMD): Rejected - built on VexFlow but designed for full MusicXML scores, too heavy for single-note rendering
- Verovio: Rejected - MEI/MusicXML focus, C++ compiled to WASM, larger bundle size

### Audio: Extend Existing audioService

**Decision:** Use the existing Web Audio API-based audioService (client/src/lib/audioService.ts) for all audio feedback.

**Rationale:**
- App already has a robust Web Audio API service with success/error tones
- audioService.playSuccessTone() and audioService.playErrorTone() already implemented
- No need for external audio files or file loading libraries
- All sounds synthesized programmatically (consistent with existing games)
- Volume control and master gain already implemented
- Zero additional dependencies

**Requirements:**
- All audio must be toggleable (muted mode for classrooms) - already supported
- No gameplay-critical audio (visual feedback sufficient) - existing pattern
- Synthesized tones only (no audio files)

**Alternatives considered:**
- howler.js: Rejected - designed for loading/playing audio files, unnecessary for synthesized tones
- Tone.js: Rejected - overkill for simple feedback tones; existing audioService is sufficient

### Game Loop: requestAnimationFrame with Delta Time

**Decision:** Implement deterministic game loop using requestAnimationFrame with delta time tracking for consistent physics across varying frame rates.

**Pattern:**
```typescript
let lastTime = 0;
function gameLoop(currentTime: number) {
  const deltaTime = currentTime - lastTime;
  lastTime = currentTime;

  updateNotePosition(deltaTime);
  checkCollisions();
  render();

  if (gameActive) {
    requestAnimationFrame(gameLoop);
  }
}
```

**Rationale:**
- Browser-native timing mechanism, optimized for 60 FPS
- Delta time ensures speed consistency on devices with variable frame rates
- Automatic pause when tab is not visible (battery-friendly)

### Difficulty Progression: Speed-Based Escalation

**Decision:** Increase note travel speed every N correct answers using a configurable curve mapping milestones to pixels-per-second.

**Example configuration:**
```json
{
  "speedCurve": [
    { "correctAnswers": 0, "pxPerSecond": 50 },
    { "correctAnswers": 5, "pxPerSecond": 75 },
    { "correctAnswers": 10, "pxPerSecond": 100 },
    { "correctAnswers": 20, "pxPerSecond": 150 }
  ]
}
```

**Rationale:**
- Simple to tune for different age groups
- Predictable progression for learners
- No complex adaptive difficulty for MVP

**Alternatives considered:**
- Time-based acceleration: Rejected - less pedagogically sound, punishes thoughtful players
- Adaptive difficulty based on accuracy: Deferred to post-MVP

### State Management: Local Component State

**Decision:** Use React useState/useReducer for game state, no global state library.

**Rationale:**
- Game state is isolated to the Staff Wars component
- No cross-game state sharing required
- Simplicity aligns with project conventions ("boring technology")

**State structure:**
```typescript
interface GameState {
  clef: 'treble' | 'bass' | 'alto' | 'grand';
  range: { min: string; max: string }; // e.g., { min: 'C4', max: 'C5' }
  score: number;
  lives: number; // 0-3
  level: number;
  currentNote: Note | null;
  gameStatus: 'setup' | 'playing' | 'paused' | 'gameOver';
  highScores: number[]; // localStorage-persisted
}
```

### Note Generation: Weighted Random with Anti-Repeat

**Decision:** Generate notes randomly within selected range, avoiding immediate repeats (last 2 notes).

**Rationale:**
- Maintains unpredictability while preventing boring repetition
- Simple to implement and test
- Sufficient for MVP; smarter spacing deferred to post-MVP

### UI Framework: Radix UI + Tailwind

**Decision:** Use existing project UI stack (Radix primitives + Tailwind) for setup screen and overlays; Canvas for staff rendering.

**Rationale:**
- Consistency with existing games
- Radix ensures accessibility (dialogs, focus management)
- Tailwind speeds development with utility classes

## Risks / Trade-offs

**Risk: Performance degradation at high speeds on low-end devices**
- Mitigation: Limit Canvas redraw regions, optimize VexFlow render calls, test on target devices (iPad 6th gen, Android tablet)
- Fallback: Configurable speed caps per device capability

**Risk: VexFlow learning curve and rendering quirks**
- Mitigation: Start with minimal rendering (single note + staff), expand incrementally
- Fallback: If VexFlow proves problematic, consider simpler SVG note sprites (would lose SMuFL compliance)

**Risk: Confusion between classic tap-to-answer and Live microphone modes**
- Mitigation: Clearly label MVP as "classic" mode, reserve feature flag for future Live mode
- No microphone permissions requested in MVP

**Risk: Overly broad note ranges frustrate beginners**
- Mitigation: Provide age-appropriate presets (e.g., "Beginner: C4-G4", "Intermediate: C4-C5")
- Default to conservative range (treble C4-C5, bass E2-E3)

**Trade-off: localStorage-only persistence vs. server-side**
- Pro: Simpler, faster, privacy-friendly
- Con: Scores lost if browser data cleared; no cross-device sync
- Decision: Acceptable for MVP, revisit if user demand emerges

## Migration Plan

**Phase 1: Scaffold and Dependencies**
1. Add VexFlow and howler.js to package.json
2. Create `/games/staff-wars/` directory structure
3. Register game in `config/games.ts` with placeholder route

**Phase 2: Core Game Loop (Minimal Viable)**
1. Implement basic Canvas rendering (staff + clef + single note)
2. Implement note spawning and right-to-left movement
3. Add note-name button input and answer checking
4. Implement lives system (3 lives, decrement on wrong answer)
5. Add game over screen

**Phase 3: Configuration and Progression**
1. Add setup screen (clef selector, range picker)
2. Implement difficulty progression (speed curve)
3. Add score tracking and HUD

**Phase 4: Polish and Accessibility**
1. Add pause/resume functionality
2. Implement high score persistence (localStorage)
3. Add accessibility features (touch targets, high contrast, SFX toggle)
4. Add visual feedback (correct/incorrect animations)
5. Optional howler.js SFX integration

**Phase 5: Testing and Documentation**
1. Unit tests for note generation, scoring, lives, speed progression
2. Manual QA on target devices (mobile/tablet)
3. Performance profiling (ensure 60 FPS at max speed)
4. User-facing documentation (how to play, classroom tips)

**Rollback:** If VexFlow integration proves too complex, fall back to simplified SVG note sprites and defer staff rendering quality to post-MVP.

## Open Questions

**Q1: Should grand staff mode be included in MVP or deferred?**
- Leaning toward: Feature flag in config, disabled by default (requires additional complexity for two-staff rendering)

**Q2: What is the optimal speed curve for different age groups?**
- Leaning toward: Conservative default (slow progression) with JSON config for teacher customization

**Q3: Should we include note names in multiple languages (solfège, German notation)?**
- Leaning toward: MVP uses letter names (C, D, E, etc.); localization deferred to post-MVP

**Q4: Should incorrect answers pause note movement or continue scrolling?**
- Leaning toward: Continue scrolling (maintains tension); deducted life is feedback enough

**Q5: Visual theme - space-like or music-themed?**
- Leaning toward: Neutral space-like (no trademarked imagery) with musical staff as focal point
