# ADR-007: Reset Philosophy — Clearing Form State

## Status
Accepted

## Context
CharacterCraft Lite allows users to create structured chatbot personas through a multi-step form. As the app evolved to include both random generation and detailed editing, we needed a clear, consistent approach to *resetting* the form:
- Should it reset visual chips, input values, and internal state?
- Should it refresh the UI, or preserve it visually?
- Should it also clear the generated output or just the inputs?

Confusion arose during modular refactoring, especially as `resetForm()` began to be used by both the *Reset* and *Surprise Me!* buttons.

## Decision
We treat form resets as **intentional state transitions**, and implemented a `resetForm(withUIUpdate = true)` function that supports both soft and hard resets.

### Reset Types
- `resetForm(false)` — used by **Surprise Me!**
  - Clears values without triggering full UI update
  - Avoids flicker when quickly re-filling fields
- `resetForm(true)` (or default) — used by **Start Over** button
  - Resets all form inputs and visual selections
  - Restores visibility of the input card and hides output card

### Reset Includes:
- Input fields: cleared
- Hidden inputs: cleared
- Chips: unselected
- Custom input visibility: reset
- DOM visibility: updated only on `withUIUpdate = true`

## Consequences
✅ Clearly separates logic and UI concerns
✅ Prevents jarring visual changes when Surprise Me! is used
✅ Supports future reuse of `resetForm()` in other features (e.g. form validation, role-switching)
⚠️ Requires developers to be explicit about reset intent

## Alternatives Considered
- Full reload of the page (disruptive)
- Separate `resetUI()` and `resetData()` functions (more granular, but more complex)

## Future Considerations
- Add optional parameters for partial resets (e.g. clear only one section)
- Consider tracking form dirty state to warn before navigating away

---

*This strategy supports modularity, user experience, and reuse.*

