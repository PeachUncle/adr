# ADR-20251015-manual-date-entry-format

## Status
Accepted

## Context
ExvoRed catalogs historical votive offerings (exvotos) dating from the 13th to 21st centuries. Historical documentation is often incomplete; many exvotos have unknown or partially known dates. Common scenarios include: knowing only the year (e.g., "1787"), knowing year and month but not day (e.g., "1787-05"), or knowing all components but with uncertainty about month or day.

HTML5's `<input type="date">` enforces strict YYYY-MM-DD validation and presents a date picker UI that only allows selecting complete, valid dates. This is incompatible with historical research needs where partial dates are common and must be explicitly recorded as incomplete. SQLite stores dates as text in ISO format, which allows arbitrary string values. The frontend and backend must coordinate on a consistent format for representing and validating partial dates.

Research conventions in art history and religious studies use placeholder notation to indicate unknown date components, commonly "X", "XX", or "?". The system must preserve the distinction between "unknown month" (represented explicitly) versus "month not yet researched" (field left empty).

## Decision
Replace all `<input type="date">` elements with `<input type="text">` fields that accept manual date entry in YYYY-MM-DD format. Support "X" as a placeholder for unknown month or day (e.g., "1787-X-01" means unknown month, "1787-05-X" means unknown day, "1787-X-X" means only year is known). Display format hints in placeholders: "YYYY-MM-DD (use X for unknown)". Implement custom validation in backend controllers to accept dates with X placeholders while rejecting invalid patterns. Store partial dates as text strings in SQLite without conversion to Date objects.

## Consequences

### Positive
- Historical accuracy: Researchers can explicitly document incomplete date information, preserving uncertainty in historical records
- Flexibility: Supports all date formats needed for 800+ years of exvoto history (1200-2025)
- Consistency with research conventions: "X" notation matches existing academic practices in art history catalogs
- No forced precision: Researchers are not required to guess or invent complete dates when information is incomplete
- SQLite compatibility: Text storage natively supports any date format without type conversion issues
- Backend validation control: Custom validation logic can evolve to support additional formats (e.g., circa dates "c. 1787")

### Negative
- User input validation complexity: Must validate multiple formats (YYYY-MM-DD, YYYY-MM-X, YYYY-X-DD, YYYY-X-X, YYYY) and reject invalid combinations
- No native date picker: Users must type dates manually; no calendar widget for selecting dates, slower for modern dates
- Format ambiguity risk: Users may use inconsistent placeholder notation ("X", "?", "0", "--") unless strictly enforced
- Sorting complexity: Text-based date sorting works for complete dates but may produce unexpected results with X placeholders (e.g., "1787-X-01" sorts as string, not chronologically)
- Potential user error: Typos and invalid dates (e.g., "1787-13-01", "1787-02-30") are easier to enter without browser validation
- Frontend validation required: Must implement JavaScript validation to provide immediate feedback before form submission

### Neutral
- Migration from existing data: Current database may contain dates from `<input type="date">` period; must verify all dates are valid partial dates or complete ISO dates
- Documentation needed: Users must understand X placeholder convention; add help text and examples in UI

## Alternatives Considered

### Alternative 1: HTML5 Date Input with Optional Fields
**Rejected because:** HTML5 `<input type="date">` does not support partial dates; browsers enforce complete YYYY-MM-DD validation. Separating date components into three separate dropdowns (year, month, day) with "Unknown" options clutters the UI and requires 3x the space. This approach also makes copying/pasting dates from external sources (papers, catalogs) more difficult. Users would need to manually parse "1787" into year=1787, month=unknown, day=unknown, slowing data entry.

### Alternative 2: Date Range Fields (Earliest-Latest)
**Rejected because:** Representing uncertainty as ranges (e.g., "1787-01-01 to 1787-12-31" for year-only dates) misrepresents the data. A date like "1787" does not mean "sometime in 1787"; it means "the year is 1787, and month/day are unknown." Ranges double the number of input fields, complicate sorting and filtering (queries must check if date falls within range), and confuse users who interpret ranges as indicating the miracle occurred over a period of time rather than on a specific unknown date.

### Alternative 3: Separate Year/Month/Day Fields with Checkboxes
**Rejected because:** Separate fields with "Unknown" checkboxes create excessive UI clutter (3 inputs + 2-3 checkboxes per date). This approach requires more clicks during data entry (type year, click "month unknown" checkbox, etc.). Copying dates from external sources becomes a multi-step operation instead of a single paste. Validating relationships between fields (e.g., February 30th is invalid) requires complex cross-field validation logic. Users familiar with ISO date format (YYYY-MM-DD) must mentally convert to the three-field model.

## References
- ISO 8601 date format standard: https://en.wikipedia.org/wiki/ISO_8601
- Historical date representation in digital humanities: https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-date.html
- Epoch utilities for date handling: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/src/utils/epochUtils.ts`
- Related plan item: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/.claude/docs/plan.md` (manual-date-entry-with-partial-dates)
