# ADR-003: End Date Option for Reading Plans

**Status**: Approved & Implemented  
**Date**: 2025-12-02
**Decision Makers**: deltajuliet  
**Supersedes**: N/A  
**Related to**: ADR-002 (Flexible Start Date)

---

## Context

With the implementation of ADR-002, users can now specify a flexible start date for their reading plans. However, they still must specify the duration using the `--days` option. This requires users to manually calculate the number of days between two dates when they want to:

- Create a plan that ends on a specific date (birthday, holiday, etc.)
- Align completion with an event or milestone
- Fill a specific time period without manual day counting
- Create plans for quarters, seasons, or other natural time periods

### Current Behavior

```bash
# User wants to read from March 1 to June 1 (92 days)
# Must manually calculate: 31 (Mar) + 30 (Apr) + 31 (May) + 1 (Jun) = 93 days
bible-study-planner generate --start-date 2025-03-01 --days 93 --scope nt
```

### User Feedback

Users have expressed the need to:
1. Specify end dates directly without calculating days
2. Create plans that align with calendar periods naturally
3. Avoid off-by-one errors in day calculations
4. Have more intuitive date range specification

---

## Decision

We will implement an `--end-date` option that allows users to specify the ending date for their reading plan. When `--end-date` is provided, the `--days` option becomes optional and will be ignored if both are specified.

### Proposed CLI Changes

**New Option**:
```bash
--end-date DATE      Ending date for the reading plan (YYYY-MM-DD format)
                     When specified, --days is calculated automatically
```

**Priority Logic**:
1. If `--end-date` is provided, calculate days from start-date to end-date
2. If only `--days` is provided, use it as before
3. If both are provided, use `--end-date` and show warning about ignoring `--days`
4. If neither is provided, use scope defaults (365 for complete, 270 for OT, 90 for NT)

### Examples

**Specify date range:**
```bash
bible-study-planner generate --start-date 2025-03-01 --end-date 2025-06-01 --scope nt
# Automatically calculates 92 days
```

**Quarter-based plan:**
```bash
bible-study-planner generate --start-date 2025-01-01 --end-date 2025-03-31 --scope nt
# Q1 plan: Jan 1 - Mar 31 (90 days)
```

**Default start (today) with end date:**
```bash
bible-study-planner generate --end-date 2025-12-31 --scope complete
# Starts today, ends Dec 31, 2025
```

**Until birthday:**
```bash
bible-study-planner generate --start-date 2025-01-01 --end-date 2025-08-15 --scope ot
# 227-day plan ending on birthday
```

---

## Design Considerations

### 1. Date Range Calculation

**Decision**: Calculate inclusive date range (both start and end dates included)

**Rationale**:
- User expectation: "March 1 to March 3" means 3 days (1st, 2nd, 3rd)
- Aligns with natural language interpretation
- Consistent with calendar-based thinking

**Calculation**:
```python
days = (end_date - start_date).days + 1  # +1 for inclusive range
```

**Example**:
- Start: 2025-03-01, End: 2025-03-03
- Calculation: 3 - 1 = 2 days, + 1 = 3 days ✓
- Days: March 1, March 2, March 3

### 2. End Date Validation

**Validations**:
- End date must be after start date (at least 1 day)
- End date must be a valid calendar date
- End date follows same range restrictions as start date (not more than 10 years in future)
- Resulting day count must be reasonable (1 to 3650 days / ~10 years)

**Error Messages**:
```bash
bible-study-planner generate --start-date 2025-03-01 --end-date 2025-02-28
# Error: End date (2025-02-28) must be after start date (2025-03-01)

bible-study-planner generate --start-date 2025-03-01 --end-date 2025-03-01
# Error: End date must be at least 1 day after start date

bible-study-planner generate --start-date 2025-01-01 --end-date 2045-01-01
# Error: Date range too long (7305 days). Maximum is 3650 days (~10 years)
```

### 3. Interaction with --days Option

**Decision**: When both `--end-date` and `--days` are provided, use `--end-date` and ignore `--days`

**Rationale**:
- End date provides explicit, unambiguous intent
- Avoids conflicting specifications
- Follows precedent from `--start-date` / `--year` interaction

**Warning Message**:
```bash
bible-study-planner generate --start-date 2025-03-01 --end-date 2025-06-01 --days 100
# ⚠️ Warning: Both --end-date and --days provided. Using --end-date (ignoring --days).
# Plan will run for 92 days (2025-03-01 to 2025-06-01)
```

### 4. Default Start Date Behavior

**When only --end-date is provided:**
- Start date defaults to today
- Plan runs from today until specified end date

**Example**:
```bash
# Today is 2025-12-02
bible-study-planner generate --end-date 2025-12-31 --scope complete
# Starts: 2025-12-02, Ends: 2025-12-31 (30 days)
```

### 5. Minimum and Maximum Duration

**Constraints**:
- Minimum: 1 day (start and end must be different, or same day?)
- Maximum: 3650 days (~10 years)

**Alternative for minimum**: Allow same-day (start = end = 1 day)?
- **Decision**: Require at least 1 day difference
- **Rationale**: A single-day plan is unusual and likely an error

### 6. Scope Interaction

**Consideration**: What if the date range is too short for the scope?

**Decision**: Allow any duration, let the planner distribute content accordingly
- Short durations = more chapters per day
- Long durations = fewer chapters per day
- No minimum or maximum based on scope

**Rationale**:
- Users might want intensive short-term plans
- Or leisurely long-term plans with repetition
- Flexibility is key

**Warning for extreme cases**:
```bash
bible-study-planner generate --start-date 2025-03-01 --end-date 2025-03-05 --scope complete
# ⚠️ Warning: Very short duration (5 days) for complete Bible (1189 chapters)
# This will result in ~238 chapters per day (~26 hours of reading)
# Consider using a longer duration or smaller scope
```

---

## Implementation Plan

### Phase 1: Add --end-date Option (v1.2)

**Changes**:
1. Add `--end-date` parameter to CLI
2. Add date range calculation function
3. Update date resolution logic to handle end-date
4. Add validation for end-date
5. Update help text and error messages
6. Add warnings for conflicting options

**Files to Modify**:
- `bible_study_planner/cli.py` - Add option and resolution logic
- No changes needed to planner classes (they already accept days parameter)

**Code Changes**:

```python
# cli.py
@click.option(
    "--end-date",
    type=str,
    default=None,
    help="Ending date for the reading plan (YYYY-MM-DD format)",
)
def generate(
    start_date: str | None,
    end_date: str | None,
    year: int | None,
    days: int | None,
    scope: str,
    output: Path,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Generate a Bible reading plan."""
    
    # Resolve start date
    resolved_start_date = _resolve_start_date(start_date, year)
    
    # Resolve days (considering end_date)
    resolved_days = _resolve_days(resolved_start_date, end_date, days, bible_scope)
    
    # ... rest of generation logic
```

```python
def _resolve_days(
    start_date: date,
    end_date_str: str | None,
    days: int | None,
    scope: BibleScope,
) -> int:
    """Resolve the number of days for the plan.
    
    Args:
        start_date: Resolved start date
        end_date_str: Optional end date string
        days: Optional explicit days count
        scope: Bible scope for default days
        
    Returns:
        Number of days for the plan
        
    Raises:
        ValueError: If dates are invalid or conflicting
    """
    # Case 1: --end-date provided
    if end_date_str:
        if days:
            click.echo(
                "⚠️  Warning: Both --end-date and --days provided. "
                "Using --end-date (ignoring --days)."
            )
        
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"Invalid end date format: '{end_date_str}'. "
                "Expected YYYY-MM-DD format."
            )
        
        # Validate end date
        _validate_date_range(end_date)
        
        # Calculate days (inclusive)
        calculated_days = (end_date - start_date).days + 1
        
        if calculated_days < 1:
            raise ValueError(
                f"End date ({end_date}) must be after start date ({start_date})"
            )
        
        if calculated_days > 3650:  # ~10 years
            raise ValueError(
                f"Date range too long ({calculated_days} days). "
                f"Maximum is 3650 days (~10 years)"
            )
        
        # Warn for extreme durations
        if calculated_days < 7:
            click.echo(
                f"⚠️  Note: Short duration ({calculated_days} days) may result in "
                "heavy daily reading load."
            )
        
        return calculated_days
    
    # Case 2: --days provided
    if days:
        return days
    
    # Case 3: Use scope defaults
    default_days = {
        BibleScope.COMPLETE: 365,
        BibleScope.OLD_TESTAMENT: 270,
        BibleScope.NEW_TESTAMENT: 90,
    }
    return default_days[scope]
```

---

## API Changes

### CLI Interface

**Before (v1.1)**:
```bash
bible-study-planner generate --start-date 2025-03-01 --days 92 --scope nt
```

**After (v1.2)**:
```bash
# Using end-date instead of days
bible-study-planner generate --start-date 2025-03-01 --end-date 2025-06-01 --scope nt

# Or mixing (end-date takes priority)
bible-study-planner generate --start-date 2025-03-01 --end-date 2025-06-01 --days 100 --scope nt
```

**Backward Compatibility**: All existing commands continue to work unchanged.

---

## Consequences

### Positive

1. **Intuitive Date Ranges**: Users can specify "from X to Y" naturally
2. **No Manual Calculation**: System calculates days automatically
3. **Calendar Alignment**: Easy to align with quarters, semesters, seasons
4. **Reduced Errors**: Eliminates off-by-one errors in day counting
5. **Event-Driven Planning**: Can end on specific meaningful dates
6. **Flexible Combinations**: Works with all start-date options (today, specific date, year)

### Negative

1. **Option Complexity**: More CLI options to understand
2. **Potential Confusion**: Users might not know whether to use --days or --end-date
3. **Leap Year Complexity**: Date calculations must account for leap years (handled by Python)
4. **Edge Case Testing**: More combinations to test and validate

### Neutral

1. **No Breaking Changes**: Existing functionality unchanged
2. **Optional Feature**: Users can continue using --days if preferred

---

## Migration Guide

### For Users

**Old approach (still works)**:
```bash
# Manually calculate 92 days from Mar 1 to Jun 1
bible-study-planner generate --start-date 2025-03-01 --days 92 --scope nt
```

**New approach**:
```bash
# Let the system calculate days
bible-study-planner generate --start-date 2025-03-01 --end-date 2025-06-01 --scope nt
```

**Combined with defaults**:
```bash
# Start today, end on specific date
bible-study-planner generate --end-date 2025-12-31 --scope complete
```

---

## Testing Strategy

### Unit Tests

1. **Date Range Calculation**:
   - Single day difference (start + 1 day)
   - Same month range
   - Month boundary crossing
   - Year boundary crossing  
   - Leap year February
   - Long ranges (365+ days)

2. **End Date Validation**:
   - End date before start date (error)
   - End date equals start date (error)
   - Valid end date after start date
   - Invalid date format
   - Date outside 10-year window

3. **Option Priority**:
   - Only --days provided
   - Only --end-date provided
   - Both --days and --end-date (end-date wins)
   - Neither provided (scope defaults)

4. **Edge Cases**:
   - Maximum duration (3650 days)
   - Very short duration (2-3 days)
   - Leap day handling (Feb 29)

### Integration Tests

1. **Full Plans**:
   - 90-day plan with end-date
   - Cross-year plan (Dec to Mar)
   - Leap year plan
   - Very short plan (5 days)

2. **File Output**:
   - Verify correct number of files generated
   - Check date sequence in filenames
   - Validate last file matches end-date

3. **CLI Output**:
   - Verify calculated days shown in output
   - Check warnings display correctly
   - Validate error messages

### Manual Tests

```bash
# Test 1: Basic end-date
py -m bible_study_planner generate --start-date 2025-03-01 --end-date 2025-03-31 --scope nt --dry-run

# Test 2: Cross-year
py -m bible_study_planner generate --start-date 2025-12-01 --end-date 2026-02-28 --scope nt --dry-run

# Test 3: Default start (today) with end
py -m bible_study_planner generate --end-date 2025-12-31 --scope nt --dry-run

# Test 4: Conflict (both days and end-date)
py -m bible_study_planner generate --start-date 2025-03-01 --end-date 2025-03-31 --days 100 --scope nt --dry-run

# Test 5: Invalid end before start
py -m bible_study_planner generate --start-date 2025-03-01 --end-date 2025-02-28 --scope nt --dry-run

# Test 6: Very short plan
py -m bible_study_planner generate --start-date 2025-03-01 --end-date 2025-03-03 --scope nt --dry-run
```

---

## Documentation Updates

### README.md

Add examples:
```markdown
### Specify Date Range

bible-study-planner generate --start-date 2025-03-01 --end-date 2025-06-01 --scope nt

The system automatically calculates the number of days (92) between the dates.

### Plan Until End of Year

bible-study-planner generate --end-date 2025-12-31 --scope complete

Starts today and runs until December 31st.

### Quarterly Plans

# Q1 Plan
bible-study-planner generate --start-date 2025-01-01 --end-date 2025-03-31 --scope nt

# Q2 Plan  
bible-study-planner generate --start-date 2025-04-01 --end-date 2025-06-30 --scope nt
```

### CLI Help Text

```
Options:
  --start-date DATE         Starting date (YYYY-MM-DD) [default: today]
  --end-date DATE          Ending date (YYYY-MM-DD). Auto-calculates days.
  --days INTEGER           Number of days. Ignored if --end-date provided.
  --year INTEGER           [DEPRECATED] Use --start-date instead
```

---

## Future Enhancements

### 1. Relative End Dates (v1.3)

Natural language end dates:
```bash
bible-study-planner generate --end-date "end of month"
bible-study-planner generate --end-date "end of quarter"
bible-study-planner generate --end-date "+90 days"
```

### 2. Duration Suggestions (v1.3)

Intelligent recommendations:
```bash
bible-study-planner generate --start-date 2025-03-01 --end-date 2025-03-05 --scope complete
# ⚠️ Warning: 5 days for complete Bible = 238 chapters/day
# Suggestion: Try --scope nt (52 chapters/day) or extend to 2025-12-31 (3 chapters/day)
```

### 3. Calendar Period Shortcuts (v1.4)

Predefined periods:
```bash
bible-study-planner generate --period "Q1-2025" --scope nt
bible-study-planner generate --period "2025-summer" --scope ot
bible-study-planner generate --period "this-month" --scope complete
```

---

## Success Metrics

1. **Adoption**: >30% of users use `--end-date` within 2 months
2. **Reduced Errors**: <3% date-related error reports
3. **User Satisfaction**: Positive feedback on date range specification
4. **Calendar Alignment**: Users successfully create quarter/month-aligned plans

---

## References

- [ADR-002: Flexible Start Date](./ADR-002-flexible-start-date.md)
- [Python datetime module](https://docs.python.org/3/library/datetime.html)
- [ISO 8601 Date Format](https://en.wikipedia.org/wiki/ISO_8601)

---

## Approval

- [x] Architecture Approved
- [x] Implementation Plan Approved
- [x] User Experience Reviewed
- [x] Testing Strategy Approved
- [x] Ready for Development

**Approved By**: Development Team  
**Date**: 2025-12-02

---

## Changelog

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-12-02 | 1.0 | Initial ADR for end-date option | Development Team |
| 2025-12-02 | 1.1 | Implemented in code (v1.2) | Development Team |
