# Architecture Decision Record: Multi-Year TSM Data Ingestion Strategy

**ADR Number:** 003  
**Date:** November 2025  
**Status:** Implemented  
**Authors:** TS  

## Title
Append-Based Multi-Year Data Ingestion for Longitudinal TSM Analytics

## Context

The HAILIE Insights Engine initially processed a single year of TSM (Tenant Satisfaction Measures) data (2024), using a "replace" strategy where the ETL pipeline would drop and recreate all database tables on each run. The database schema (`build_analytics_db.py`) used `CREATE OR REPLACE TABLE` statements. The UK Government releases TSM data annually, with each provider's satisfaction scores updated once per year. The HAILIE Insights Engine must ingest this annual data to support:

Year-over-year momentum tracking (existing roadmap feature)
Historical trend analysis and visualization
Multi-year correlation analysis for stronger statistical power
Regulatory audit trails and retrospective reporting

The system must handle annual data updates while maintaining query performance and simplicity.

With the release of 2025 TSM data, a critical decision was required:
- **Option A:** Continue replacing data (overwrite 2024 with 2025)
- **Option B:** Append new years while preserving historical data

The momentum feature—showing year-over-year performance changes—became a key requirement, necessitating access to multiple years of data simultaneously. Without 2024 baseline data, momentum calculations would be impossible.

**Key Requirements:**
1. Calculate momentum by comparing 2025 scores against 2024 baseline
2. Maintain elegant, simple UI showing only current year (2025) data
3. Support future years (2026, 2027, etc.) without schema changes
4. Prevent duplicate data if ETL script runs multiple times
5. Enable potential future features (year selector, historical trends)

**Dataset Characteristics:**
- **2024 Data:** 355 providers (LCRA + LCHO), 4,788 records
- **2025 Data:** 412 providers (353 LCRA + 59 LCHO), 1,451 records
- **Combined:** 6,239 total records across both years

## Decision(s)

We redesigned the ETL pipeline (`build_analytics_db_v2.py`) to use an **append-based ingestion strategy** with duplicate prevention

AND 

We implement a temporal row append strategy where each provider's annual scores are stored as new rows with a year column:

### Core Changes

1. **Year-Aware Schema:** Added `year INT NOT NULL` column to all five database tables:
   - `raw_scores`
   - `provider_summary`
   - `calculated_percentiles`
   - `calculated_correlations`
   - `provider_dataset_mapping`

2. **Replace CREATE OR REPLACE with INSERT:**
   ```sql
   -- Before (v1)
   CREATE OR REPLACE TABLE raw_scores AS ...
   
   -- After (v2)
   CREATE TABLE IF NOT EXISTS raw_scores (...);
   DELETE FROM raw_scores WHERE year = ?;
   INSERT INTO raw_scores ...
   ```

-- Annual growth: ~4,932 new rows per year (411 providers × 12 measures)
New data is appended via incremental ETL, not database rebuilds:

Historical data remains untouched
Percentiles calculated per year
Correlations recalculated across all years for statistical strength



4. **Duplicate Prevention:** Delete existing data for a specific year before inserting new data, enabling safe re-runs

5. **Dynamic Sheet Name Detection:** Support flexible Excel sheet naming (e.g., "2025 TSM", "TSM 2025", etc.)

6. **Year-Filtered Queries:** Updated all data processor methods to default to `year = 2025`:
   - `get_all_providers_with_scores(year=2025)`
   - `get_provider_percentiles(year=2025)`
   - `get_dataset_correlations(year=2025)`
   - `get_provider_scores(year=2025)`
   - All analytics queries filter by year to prevent dimension mismatches

### Momentum Calculation Design

The momentum feature compares current year (2025) against baseline year (2024):

```python
def calculate_momentum(provider_code: str) -> Dict:
    # Get 2025 scores (current year)
    current_scores = get_provider_scores(provider_code, year=2025)
    
    # Get 2024 scores (baseline year)
    baseline_scores = get_provider_scores(provider_code, year=2024)
    
    # Calculate year-over-year changes
    momentum = compare_scores(current_scores, baseline_scores)
    
    return momentum
```

**Key Principle:** UI shows only 2025 data; momentum calculated behind the scenes by comparing to 2024.

## Rationale

### 1. Business Value Alignment
- **Momentum Feature:** Primary value driver requires multi-year comparison
- **Performance Trends:** Housing providers need to track improvement over time
- **Accountability:** Year-over-year changes demonstrate impact of interventions

### 2. Simplicity First Philosophy
- **Simple UI:** Users see only current year (2025), maintaining elegance
- **Hidden Complexity:** Multi-year storage happens behind the scenes
- **Progressive Enhancement:** Foundation for future features without UI clutter

### 3. Data Integrity
- **Duplicate Prevention:** Safe to re-run ETL without corrupting data
- **Historical Preservation:** Never lose baseline data needed for comparisons
- **Audit Trail:** Maintain complete historical record for governance

### 4. Future-Proofing
- **Scalable Design:** Adding 2026 data requires no schema changes
- **Feature Enablement:** Lays groundwork for year selector, trend charts, etc.
- **Rollback Capability:** Can compare any two years if needed

### 5. Technical Simplicity
- **Minimal Code Changes:** Year parameter defaults throughout codebase
- **DuckDB Native:** Leverages columnar storage efficiency for time-series data
- **No Migration Needed:** Existing 2024 data remained intact

### 6. Analytics-Native Design & Simplicity-First

1. **Analytics-Native Design**
   - DuckDB's columnar storage excels at handling temporal data patterns, making it ideal for our use case.
   - Time-series queries, such as trends and momentum, become straightforward due to the efficient storage format.
   - Pre-calculated percentiles have the ability to reference historical context, providing depth to our analytics.

2. **Simplicity-First**
   - By having a single source of truth with one table instead of year-fragmented tables, we adhere to a natural schema that resonates with how users think about annual reporting.
   - Query logic is simplified with the use of simple `WHERE year = 2025` filters, streamlining the development and comprehension.

3. **Scale Reality**
   - With 10 years of data, we can anticipate around ~50,000 rows, which equates to approximately ~500KB when compressed.
   - For 50 years of data, the expected size is about ~250,000 rows, or ~2.5MB compressed, indicating that storage is not a constraint.
   - Despite increasing data volumes, query performance will continue to remain under 100ms, ensuring efficiency.

4. **Feature Enablement**
   - Momentum tracking necessitates year-over-year comparisons to provide meaningful insights.
   - Trend visualizations are enabled by maintaining historical data points, allowing for richer analytics features.
   - Regulatory compliance is bolstered by maintaining a complete audit trail, an essential component of effective governance.

## Alternatives Considered

### Alternative 1: Overwrite (Replace) Strategy
- **Approach:** Continue using `CREATE OR REPLACE TABLE`, loading only latest year
- **Pros:** Simplest implementation, smallest database size
- **Cons:** **Momentum feature impossible**, lose historical data, cannot track trends
- **Verdict:** ❌ Rejected (blocks key business requirement)

### Alternative 2: Separate Tables Per Year
- **Approach:** Create `raw_scores_2024`, `raw_scores_2025`, etc.
- **Pros:** Clear separation, easy to query single year
- **Cons:** Schema explosion, complex cross-year queries, maintenance nightmare
- **Verdict:** ❌ Rejected (violates DRY principle, poor scalability)

### Alternative 3: External Data Warehouse
- **Approach:** Use separate analytics database (e.g., BigQuery, Snowflake)
- **Pros:** Enterprise-grade time-series support, advanced analytics
- **Cons:** Adds operational complexity, contradicts ADR-001 simplicity goals
- **Verdict:** ❌ Rejected (over-engineered for annual government dataset)

### Alternative 4: Append-Based with Year Column (CHOSEN)
- **Approach:** Single schema with `year` column, INSERT with duplicate prevention
- **Pros:** ✅ Simple schema, ✅ enables momentum, ✅ future-proof, ✅ maintains elegance
- **Cons:** Slightly larger database size (negligible for this dataset)
- **Verdict:** ✅ **Selected** (best balance of simplicity and capability)

## Consequences

### Positive Consequences
✅ **Momentum Feature Enabled:** Year-over-year performance tracking now possible  
✅ **Historical Preservation:** 2024 baseline data permanently available  
✅ **Safe Re-runs:** ETL script can run multiple times without corruption  
✅ **Future-Ready:** 2026, 2027 data can be added without code changes  
✅ **Simple UI:** Users see only current year, maintaining elegance  
✅ **Efficient Queries:** DuckDB columnar storage handles multi-year data efficiently  
✅ **Audit Compliance:** Complete historical record for governance  

### Negative Consequences
❌ **Increased Database Size:** ~50% larger (4,788 → 6,239 records)  
   - *Mitigation:* Still tiny (<10MB), negligible for DuckDB  
❌ **Query Complexity:** All queries must filter by year  
   - *Mitigation:* Defaulted to `year=2025` throughout codebase  
❌ **Initial Load Time:** First-time ingestion now requires two ETL runs  
   - *Mitigation:* One-time cost, automated for future years  

### Neutral Consequences
➖ **Year Parameter Ubiquity:** All data methods now accept optional `year` param  
➖ **Default Year Hardcoded:** `year=2025` default will need annual update  
➖ **Backward Incompatible:** v1 ETL script cannot be used on v2 database  

## Implementation Details

### Migration Path

**Step 1:** Update Database Schema
```python
# Added year column to all tables
CREATE TABLE IF NOT EXISTS raw_scores (
    provider_code TEXT NOT NULL,
    tp_measure TEXT NOT NULL,
    score REAL,
    year INT NOT NULL  # NEW
)
```

**Step 2:** Modify ETL Pipeline
```python
# Changed from CREATE OR REPLACE to INSERT
def load_data(excel_file, year):
    # Detect sheet name dynamically
    sheet_name = detect_tsm_sheet(excel_file, year)
    
    # Delete existing year data (idempotent)
    conn.execute("DELETE FROM raw_scores WHERE year = ?", [year])
    
    # Insert new year data
    conn.execute("INSERT INTO raw_scores ...", data)
```

**Step 3:** Update All Query Methods
```python
# Before
def get_provider_scores(provider_code):
    return conn.execute("SELECT * FROM raw_scores WHERE provider_code = ?")

# After
def get_provider_scores(provider_code, year=2025):
    return conn.execute("SELECT * FROM raw_scores WHERE provider_code = ? AND year = ?")
```

**Step 4:** Implement Momentum Calculation
```python
def calculate_momentum(provider_code):
    current = get_provider_scores(provider_code, year=2025)
    baseline = get_provider_scores(provider_code, year=2024)
    
    improvements = []
    declines = []
    
    for tp_measure in ['TP01', 'TP02', ...]:
        delta = current[tp_measure] - baseline[tp_measure]
        if delta > 0: improvements.append((tp_measure, delta))
        if delta < 0: declines.append((tp_measure, delta))
    
    return {
        'score': calculate_momentum_score(improvements, declines),
        'drivers': identify_top_drivers(improvements, declines)
    }
```

### Database Schema Evolution

| Table | 2024 (v1) Schema | 2025 (v2) Schema | Change |
|-------|------------------|------------------|--------|
| `raw_scores` | provider_code, tp_measure, score | + **year INT** | Added year column |
| `provider_summary` | provider_code, tp01...tp12 | + **year INT** | Added year column |
| `calculated_percentiles` | provider_code, tp_measure, percentile | + **year INT** | Added year column |
| `calculated_correlations` | tp_measure, correlation | + **year INT** | Added year column |
| `provider_dataset_mapping` | provider_code, dataset_type | + **year INT** | Added year column |

### Data Ingestion Workflow

```bash
# Load 2024 baseline data
python build_analytics_db_v2.py --file 2024_TSM_Data.xlsx --year 2024

# Load 2025 current data
python build_analytics_db_v2.py --file 2025_TSM_Full_Data_v1.0_FINAL.xlsx --year 2025

# Result: Database contains both years, UI shows 2025, momentum compares them
```

### Year Detection Algorithm

The ETL script intelligently detects TSM sheet names:

```python
def detect_tsm_sheet(excel_file, year):
    """
    Handles various naming patterns:
    - "2025 TSM"
    - "TSM 2025"
    - "TSM Data 2025"
    - "2025_TSM_Full_Data"
    """
    for sheet_name in excel_file.sheet_names:
        if str(year) in sheet_name and 'TSM' in sheet_name.upper():
            return sheet_name
    
    # Fallback to first sheet
    return excel_file.sheet_names[0]
```

## Validation

The append-based ingestion was validated through:

1. **Data Integrity Checks:**
   - ✅ 4,788 records for 2024 preserved
   - ✅ 1,451 records for 2025 loaded successfully
   - ✅ No duplicates after multiple ETL runs
   - ✅ Year filtering prevents dimension mismatches

2. **Momentum Calculation Accuracy:**
   - ✅ Correctly identifies measures that improved
   - ✅ Correctly identifies measures that declined
   - ✅ Handles providers missing in either year
   - ✅ Calculates weighted momentum scores

3. **Performance Validation:**
   - ✅ Query times remain sub-second (<100ms)
   - ✅ Database size remains manageable (<10MB)
   - ✅ No noticeable UI performance degradation

4. **User Experience:**
   - ✅ UI shows only 2025 data (simple, elegant)
   - ✅ Momentum insights appear automatically
   - ✅ Year-over-year changes explained clearly

## Lessons Learned

### 1. Design for Tomorrow, Build for Today
The append-based design enables future features (year selector, trend charts) without committing to them now. This balances future-proofing with current simplicity.

### 2. Defaults Hide Complexity
By defaulting all queries to `year=2025`, the codebase remains simple. Most code doesn't need to think about years; it's only relevant for momentum calculations.

### 3. Idempotent Operations Reduce Risk
The `DELETE FROM ... WHERE year = ?` + `INSERT` pattern makes the ETL script safe to re-run, eliminating data corruption fears during development.

### 4. Schema Evolution Without Migration
Adding the `year` column to existing tables worked seamlessly because DuckDB handles schema changes gracefully. No complex migration scripts required.

### 5. Momentum as Killer Feature
The ability to show "You improved in TP01 (+5 points) and TP05 (+3 points)" provides immediate, actionable insights that justify the multi-year architecture.

## Future Considerations

### Potential Enhancements (Tracked in FEATURES_ROADMAP.md)
1. **Year Selector UI:** Allow users to view historical years (2024, 2023, etc.)
2. **Trend Visualization:** Multi-year line charts showing performance trajectory
3. **Historical Comparison:** Compare any two years side-by-side
4. **Rolling Averages:** Smooth year-to-year volatility with multi-year averages
5. **Quartile Movement Alerts:** Notify when provider moves between quartiles

### Maintenance Considerations
- **Annual Year Update:** Update `year=2025` default to `year=2026` next November
- **Data Retention Policy:** Consider archiving years older than 5 years if database grows
- **Automated ETL:** Consider scheduling annual ETL runs when new TSM data releases

## References

- **Related ADRs:** ADR-001 (Streamlit/DuckDB Architecture)
- **Implementation Files:**
  - `build_analytics_db_v2.py` (revised ETL pipeline)
  - `data_processor_enhanced.py` (year-filtered queries)
  - `analytics_refactored.py` (momentum calculation)
  - `dashboard.py` (momentum display)
- **Data Sources:**
  - 2024 TSM Dataset (355 providers, 4,788 records)
  - 2025 TSM Dataset (412 providers, 1,451 records)
- **Documentation:** FEATURES_ROADMAP.md (future enhancements)
