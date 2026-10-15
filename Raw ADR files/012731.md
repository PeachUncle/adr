# ADR-002: Flexible Start Date for Reading Plans

**Status**: Approved & Implemented  
**Date**: 2024-12-02
**Decision Makers**: deltajuliet
**Supersedes**: N/A  
**Related to**: ADR-001 (Bible Study Planner Architecture)

---

## Context

Currently, the Bible study planner generates reading plans that always begin on January 1st of the specified year. This constraint limits flexibility for users who want to:

- Start their reading plan mid-year (e.g., beginning a New Year's resolution in March)
- Align their reading plan with personal milestones (birthday, anniversary, etc.)
- Begin immediately rather than waiting for January 1st
- Create plans that span across calendar years
- Restart after missing days without regenerating the entire plan

### Current Behavior

```bash
bible-study-planner generate --year 2025 --scope complete
# Always starts on 2025-01-01
```

### User Feedback

Users have expressed the need to:
1. Start reading plans on any arbitrary date
2. Generate plans that aren't tied to calendar years
3. Have more control over when their reading journey begins

---

## Decision

We will implement a `--start-date` option that allows users to specify any starting date for their reading plan, replacing the current `--year` parameter as the primary date specification method.

### Proposed CLI Changes

**New Option**:
```bash
--start-date DATE    Starting date for the reading plan (format: YYYY-MM-DD)
                     [default: today's date]
```

**Deprecation Strategy**:
- Keep `--year` option for backward compatibility
- If both `--start-date` and `--year` are provided, `--start-date` takes precedence
- If neither is provided, default to today's date
- Eventually deprecate `--year` in favor of `--start-date`

### Examples

**Start today:**
```bash
bible-study-planner generate --scope nt --days 90
# Defaults to today's date
```

**Start on a specific date:**
```bash
bible-study-planner generate --start-date 2025-03-15 --scope complete
```

**Start on a birthday:**
```bash
bible-study-planner generate --start-date 2025-06-01 --scope ot --days 180
```

**Span across years:**
```bash
bible-study-planner generate --start-date 2024-10-01 --days 365
# Plan runs from Oct 1, 2024 to Sep 30, 2025
```

---

## Design Considerations

### 1. Date Input Format

**Decision**: Use ISO 8601 format (YYYY-MM-DD)

**Rationale**:
- International standard
- Unambiguous (no month/day confusion)
- Easily parsable by Python's `datetime` module
- Sorts correctly alphabetically

**Alternative Formats Considered**:
- `MM/DD/YYYY` - US format, but ambiguous internationally
- `DD-MM-YYYY` - European format, still ambiguous
- Natural language ("next Monday") - Too complex, error-prone

### 2. Default Behavior

**Decision**: Default to today's date if no date specified

**Rationale**:
- Most users want to start immediately
- Eliminates the need to calculate dates manually
- More intuitive for "start now" use case
- Backward compatible with `--year` for those who want Jan 1st

### 3. File Naming Strategy

**Current**: `YYYY-MM-DD-day-NNN.md` (e.g., `2025-01-01-day-001.md`)

**Keep unchanged** - Files already use full date format, so they naturally support any start date.

### 4. Progress Tracking

**Current**: "Day X of Y"

**Keep unchanged** - Day numbers are sequential regardless of calendar dates.

**Example**:
- Start date: 2025-03-15
- File: `2025-03-15-day-001.md` → "Day 1 of 365"
- Next: `2025-03-16-day-002.md` → "Day 2 of 365"

### 5. Date Validation

**Validations**:
- Start date must be a valid calendar date
- Cannot be before 1900-01-01 (reasonable minimum)
- Cannot be more than 10 years in the future (safety check)
- Must be parseable in YYYY-MM-DD format

**Error Messages**:
```bash
bible-study-planner generate --start-date 2025-02-30
# Error: Invalid date: 2025-02-30 (February has 28 days in 2025)

bible-study-planner generate --start-date 2040-01-01
# Error: Start date cannot be more than 10 years in the future
```

### 6. Leap Year Handling

**No change needed** - Python's `datetime` module handles leap years automatically when generating sequential dates.

---

## Implementation Plan

### Phase 1: Add --start-date Option (v1.1)

**Changes**:
1. Add `--start-date` parameter to CLI
2. Update `_generate_dates()` in base plan strategy to accept start date
3. Modify date generation logic to use start date instead of `date(year, 1, 1)`
4. Add date validation function
5. Update help text and documentation

**Backward Compatibility**:
- Keep `--year` option functional
- If `--year` is used alone, convert to `date(year, 1, 1)`
- If both are specified, `--start-date` wins with a warning message

**Code Changes**:

```python
# cli.py
@click.option(
    "--start-date",
    type=str,
    default=None,
    help="Starting date for the reading plan (YYYY-MM-DD format)",
)
@click.option(
    "--year",
    type=int,
    default=None,
    help="[DEPRECATED] Use --start-date instead. Target year (defaults to Jan 1)",
)
def generate(start_date: str | None, year: int | None, ...):
    # Resolve start date
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    elif year:
        start = date(year, 1, 1)
        click.echo("⚠️  --year is deprecated. Use --start-date for more flexibility.")
    else:
        start = date.today()
```

```python
# plans/base.py
def _generate_dates(self, start_date: date, days: int) -> List[date]:
    """Generate sequential dates starting from start_date."""
    return [start_date + timedelta(days=i) for i in range(days)]
```

### Phase 2: Enhanced Date Features (v1.2) [Future]

**Potential Enhancements**:
1. **End date option**: `--end-date` to specify duration by end date instead of days
2. **Exclude days**: `--exclude-weekends` or `--exclude-days mon,wed` for flexible scheduling
3. **Natural language parsing**: `--start-date "next Monday"` using `dateutil.parser`
4. **Calendar integration**: Generate `.ics` calendar file for reminders

---

## API Changes

### Before (v1.0)

```python
plan.generate_schedule(year=2025, days=365, scope=BibleScope.COMPLETE)
```

### After (v1.1)

```python
plan.generate_schedule(
    start_date=date(2025, 3, 15), 
    days=365, 
    scope=BibleScope.COMPLETE
)
```

**Backward Compatibility**: Accept `year` as keyword argument, convert internally.

---

## Consequences

### Positive

1. **Increased Flexibility**: Users can start any time, not just January 1st
2. **Better User Experience**: "Start today" is more intuitive than specifying year
3. **Real-World Alignment**: Plans can align with personal schedules, not just calendar years
4. **Mid-Year Starts**: Users don't need to wait until next January to begin
5. **Restart Capability**: Easy to restart after missing days without complex calculations
6. **Cross-Year Plans**: Naturally handles plans that span multiple calendar years

### Negative

1. **Breaking Change**: Existing scripts using `--year` may need updates (mitigated by backward compatibility)
2. **Date Confusion**: Users might be confused about which date format to use (mitigated by clear error messages)
3. **Documentation Overhead**: Need to update all examples and documentation
4. **Testing Complexity**: More date edge cases to test (leap years, year boundaries, etc.)

### Neutral

1. **File Organization**: Files are still organized by date, but may not align with calendar year folders
2. **Progress Tracking**: Day numbering remains sequential, independent of calendar

---

## Migration Guide

### For Users

**Old way (v1.0)**:
```bash
bible-study-planner generate --year 2025 --scope complete
```

**New way (v1.1+)**:
```bash
# Start on January 1st, 2025 (equivalent to old behavior)
bible-study-planner generate --start-date 2025-01-01 --scope complete

# Or use the deprecated --year option (still works)
bible-study-planner generate --year 2025 --scope complete

# Or start today (new default)
bible-study-planner generate --scope complete
```

### For Developers

**Update imports**:
```python
# Old
plan.generate_schedule(year=2025, days=365, scope=scope)

# New
from datetime import date
plan.generate_schedule(start_date=date(2025, 1, 1), days=365, scope=scope)
```

---

## Testing Strategy

### Unit Tests

1. **Date Parsing**:
   - Valid ISO 8601 dates
   - Invalid dates (Feb 30, month 13, etc.)
   - Leap year dates (Feb 29)
   - Boundary dates (year 1900, 10 years future)

2. **Date Generation**:
   - Sequential dates from arbitrary start
   - Leap year transitions
   - Year boundary transitions
   - Month boundary transitions

3. **Backward Compatibility**:
   - `--year` still works
   - `--start-date` overrides `--year`
   - Default to today when neither specified

### Integration Tests

1. **Full Plans**:
   - 365-day plan starting mid-year
   - 90-day plan crossing year boundary
   - Plan starting on leap day (Feb 29)

2. **File Output**:
   - Verify date-based filenames
   - Confirm sequential day numbering
   - Check frontmatter dates

### Edge Cases

1. **Leap Years**:
   - Start on Feb 29, 2024 (leap year)
   - 365-day plan from Feb 1, 2024 (ends Feb 1, 2025)

2. **Year Boundaries**:
   - Start Dec 1, 2024, run 90 days (ends Mar 1, 2025)

3. **Very Long Plans**:
   - 1000-day plan (2+ years)

---

## Documentation Updates

### README.md

Add examples:
```markdown
### Start on a Specific Date

bible-study-planner generate --start-date 2025-06-15 --scope nt --days 90

### Start Today

bible-study-planner generate --scope complete
# Automatically starts today and runs for 365 days
```

### CLI Help Text

```
Options:
  --start-date DATE         Starting date (YYYY-MM-DD) [default: today]
  --year INTEGER           [DEPRECATED] Use --start-date instead
```

---

## Future Enhancements

### 1. End Date Option (v1.2)

Allow specifying end date instead of days:
```bash
bible-study-planner generate --start-date 2025-01-01 --end-date 2025-12-31
# Automatically calculates 365 days
```

### 2. Skip Days (v1.3)

Allow excluding specific days:
```bash
bible-study-planner generate --start-date 2025-01-01 --exclude-weekends
# Reading plan skips Saturdays and Sundays
```

### 3. Natural Language Dates (v2.0)

Use `dateutil.parser` for flexible input:
```bash
bible-study-planner generate --start-date "next Monday"
bible-study-planner generate --start-date "tomorrow"
bible-study-planner generate --start-date "first day of next month"
```

### 4. Progress Resume (v2.0)

Allow resuming after gaps:
```bash
bible-study-planner resume --from-day 45
# Regenerates plan starting from day 45 with today's date
```

---

## Success Metrics

1. **Adoption**: >50% of users use `--start-date` over `--year` within 3 months
2. **Flexibility**: Users successfully create mid-year plans
3. **Satisfaction**: Positive feedback on ability to start immediately
4. **Errors**: <5% of date parsing errors after validation implementation

---

## References

- [ISO 8601 Date Format](https://en.wikipedia.org/wiki/ISO_8601)
- [Python datetime module](https://docs.python.org/3/library/datetime.html)
- [Click date parameter types](https://click.palletsprojects.com/en/8.1.x/parameters/)

---

## Approval

- [x] Architecture Approved
- [x] Implementation Plan Approved
- [x] Breaking Changes Reviewed
- [x] Migration Strategy Approved
- [x] Ready for Development

**Approved By**: Development Team  
**Date**: 2025-12-02

---

## Changelog

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-12-02 | 1.0 | Initial ADR for flexible start date | Development Team |
| 2025-12-02 | 1.1 | Implemented in code (v1.1) | Development Team |
