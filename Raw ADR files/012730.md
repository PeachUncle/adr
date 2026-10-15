# ADR-001: Bible Study Plan Generator Architecture

**Status**: Proposed  
**Date**: 2024-12-02  
**Decision Makers**: Development Team  
**Technical Story**: Bible Study Plan Generator for Obsidian

---

## Context

We need to build a Python-based tool that generates daily Bible study plans as Markdown files optimized for the Obsidian note-taking application. Users should be able to configure their reading schedule, choose different Bible scopes (complete Bible, New Testament only, or Old Testament only), and have files generated with rich metadata for tracking progress and integrating with Obsidian's ecosystem.

### Problem Statement
- Manual creation of daily Bible reading plans is time-consuming
- Users want consistent, structured study materials in Obsidian
- Need flexibility in reading plans (scope, pace, order)
- Require progress tracking and statistical insights
- Must integrate seamlessly with Obsidian's linking, tagging, and query features

### Constraints
- Must generate valid Markdown compatible with Obsidian
- Should handle leap years correctly
- Must be extensible for different reading strategies
- Performance: generate full year plan in < 5 seconds
- Python 3.10+ only

---

## Decision

We will implement a modular, plugin-based Python CLI application with the following architectural decisions:

### 1. Architecture Pattern: Strategy Pattern with Dependency Injection

**Decision**: Use Strategy pattern for reading plan generation with dependency injection for component orchestration.

**Rationale**:
- Different reading strategies (canonical, chronological, custom) share common interface
- Easy to add new plan types without modifying core code
- Testable and maintainable
- Clear separation of concerns

### 2. Reading Scope Options

**Decision**: Support three Bible reading scopes with automatic day adjustment.

**Scopes**:
- `complete`: Full Bible (66 books, 1,189 chapters)
- `new-testament`: NT only (27 books, 260 chapters)
- `old-testament`: OT only (39 books, 929 chapters)

**Day Calculation**:
```
Complete Bible: 365 days (avg 3.3 chapters/day)
New Testament: 90-180 days (user configurable)
Old Testament: 180-270 days (user configurable)
```

**Rationale**:
- Many users focus on single testament studies
- Allows deeper, slower reading for shorter scopes
- More manageable for new readers (NT-only for 90 days)

### 3. Template System: Jinja2

**Decision**: Use Jinja2 for template rendering with custom filters.

**Rationale**:
- Widely adopted, well-documented
- Powerful template inheritance
- Custom filters for Bible-specific formatting
- Easy for users to customize templates

### 4. Data Storage: JSON for Bible Structure

**Decision**: Store Bible metadata in JSON files, not a database.

**Rationale**:
- Bible structure is static data
- No need for query optimization
- Easy to version control
- Simple for users to modify/extend
- No external database dependencies

### 5. Configuration: YAML with CLI Override

**Decision**: YAML configuration files with command-line argument precedence.

**Rationale**:
- Human-readable for non-programmers
- Supports complex nested structures
- CLI args override config for quick adjustments
- Industry standard (similar to Docker Compose, Kubernetes)

### 6. File Organization: Configurable Patterns

**Decision**: Support multiple folder/file naming patterns via configuration.

**Rationale**:
- Users have different organizational preferences
- Obsidian works well with various structures
- Examples: flat, by-month, by-quarter, by-testament

### 7. Progress Tracking: Dedicated Dashboard File

**Decision**: Generate a master dashboard file with progress tracking capabilities.

**Features**:
- Daily completion checkboxes
- Visual progress bars (via Dataview)
- Statistics summary
- Calendar view integration

**Rationale**:
- Centralized tracking improves motivation
- Leverages Obsidian's task management
- No external tools needed
- Auto-updates via Dataview queries

### 8. Obsidian Integration: Rich Metadata Strategy

**Decision**: Implement comprehensive frontmatter with Dataview-optimized fields.

**Metadata Structure**:
```yaml
---
date: 2025-01-01
day: 1
tags: [bible-study, daily, genesis, old-testament, law]
testament: old
genre: law
book: Genesis
chapters: "1-3"
estimated_minutes: 12
verse_count: 78
word_count: 2350
status: pending  # pending, in-progress, completed
---
```

**Rationale**:
- Enables powerful Dataview queries
- Supports graph view filtering
- Allows statistical analysis
- Future-proof for additional features

---

## Component Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                            │
│  (Argument Parsing, User Interaction, Error Handling)      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                   Configuration Manager                      │
│         (Load YAML, Validate, Merge CLI Args)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Service                       │
│              (Coordinates Component Workflow)                │
└───┬─────────────────┬─────────────────┬─────────────────┬───┘
    │                 │                 │                 │
    ↓                 ↓                 ↓                 ↓
┌─────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────────┐
│ Bible   │   │  Reading     │   │ Template │   │ Progress     │
│ Data    │   │  Plan        │   │ Renderer │   │ Tracker      │
│ Manager │   │  Strategy    │   │          │   │              │
└─────────┘   └──────────────┘   └──────────┘   └──────────────┘
                      │
                      ↓
                ┌──────────────┐
                │   Canonical  │
                │Chronological │
                │   Custom     │
                └──────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                      File Writer                            │
│         (Create Directories, Write Files, Index)            │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
obsidian_daily_bible_study_generator/
├── bible_study_planner/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── cli.py                   # Command-line interface
│   ├── config.py                # Configuration management
│   ├── orchestrator.py          # Main workflow coordinator
│   │
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── reading_segment.py
│   │   └── study_day.py
│   │
│   ├── bible/                   # Bible data management
│   │   ├── __init__.py
│   │   ├── data_manager.py
│   │   ├── scope_filter.py     # OT/NT/Complete filtering
│   │   └── statistics.py       # Word count, time estimates
│   │
│   ├── plans/                   # Reading plan strategies
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── canonical.py
│   │   ├── chronological.py
│   │   └── custom.py
│   │
│   ├── rendering/               # Template rendering
│   │   ├── __init__.py
│   │   ├── renderer.py
│   │   ├── filters.py          # Custom Jinja2 filters
│   │   └── dashboard.py        # Progress dashboard generator
│   │
│   ├── output/                  # File writing
│   │   ├── __init__.py
│   │   ├── file_writer.py
│   │   ├── structure.py        # Folder organization
│   │   └── index_generator.py  # Table of contents
│   │
│   └── utils/
│       ├── __init__.py
│       ├── date_helpers.py
│       ├── validation.py
│       └── logger.py
│
├── data/
│   ├── bible_structure.json     # Complete Bible metadata
│   ├── bible_stats.json         # Word counts, verse counts
│   ├── reading_plans/
│   │   ├── canonical.json
│   │   ├── chronological.json
│   │   └── mclean.json          # Popular plan examples
│   └── translations/
│       └── metadata.json        # Translation info
│
├── templates/
│   ├── daily/
│   │   ├── default.md.jinja2
│   │   ├── detailed.md.jinja2
│   │   ├── minimal.md.jinja2
│   │   └── academic.md.jinja2
│   ├── dashboard/
│   │   ├── progress.md.jinja2
│   │   └── statistics.md.jinja2
│   └── index/
│       └── toc.md.jinja2
│
├── config/
│   ├── default_config.yaml
│   └── examples/
│       ├── complete_bible.yaml
│       ├── new_testament.yaml
│       └── old_testament.yaml
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/
│   ├── ADR/
│   │   └── 001-architecture.md
│   ├── user-guide.md
│   └── templates.md
│
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Core Components Specification

### 1. CLI Interface (`cli.py`)

**Responsibilities**:
- Parse command-line arguments
- Display help and usage information
- Handle dry-run mode
- Progress indicators

**Command Structure**:
```bash
bible-study-planner generate [OPTIONS]

Options:
  --year YEAR                   Target year [required]
  --scope [complete|nt|ot]      Bible scope [default: complete]
  --plan TYPE                   Reading plan type [default: canonical]
  --days INTEGER                Number of days (overrides scope default)
  --output DIR                  Output directory [default: ./bible-study]
  --config FILE                 Config file path
  --template FILE               Custom template file
  --dry-run                     Preview without generating files
  --progress-dashboard          Generate progress tracking dashboard
  --force                       Overwrite existing files
  -v, --verbose                 Verbose output
  -q, --quiet                   Minimal output
  --help                        Show this message

Examples:
  # Complete Bible, 365 days
  bible-study-planner generate --year 2025

  # New Testament only, 90 days
  bible-study-planner generate --year 2025 --scope nt --days 90

  # Old Testament, chronological order
  bible-study-planner generate --year 2025 --scope ot --plan chronological
```

### 2. Configuration Schema (`config.py`)

**YAML Structure**:
```yaml
# Basic Settings
year: 2025
scope: complete  # complete, nt, ot
plan_type: canonical
days: null  # null = auto-calculate based on scope

# Output Configuration
output:
  directory: "./bible-study"
  folder_structure: "flat"  # flat, monthly, quarterly, testament
  file_pattern: "{year}-{month:02d}-{day:02d}"
  overwrite: false

# Reading Plan Settings
reading:
  chapters_per_day_range: [3, 5]  # Min and max
  allow_partial_books: false
  balance_load: true  # Distribute long books
  
# Scope-specific defaults
scope_defaults:
  complete:
    days: 365
    chapters_per_day: 3.3
  new_testament:
    days: 90
    chapters_per_day: 2.9
  old_testament:
    days: 270
    chapters_per_day: 3.4

# Template Configuration
template:
  name: "default"
  custom_path: null
  variables:
    translation: "ESV"
    include_cross_references: true
    include_reflection_questions: true

# Obsidian Integration
obsidian:
  frontmatter:
    enable: true
    fields: [date, day, tags, testament, genre, book, chapters, 
             estimated_minutes, verse_count, word_count, status]
  
  tags:
    base: ["bible-study", "daily"]
    include_testament: true
    include_genre: true
    include_book: false
  
  links:
    previous_next: true
    book_index: true
    dashboard: true
  
  dataview:
    enable: true
    inline_fields: true
    
# Progress Tracking
progress:
  enable_dashboard: true
  dashboard_filename: "00-Dashboard"
  statistics:
    daily: true
    weekly: true
    monthly: true
    by_testament: true
    by_genre: true
  completion_tracking: true
  
# Graph View Optimization
graph:
  tag_by_testament: true
  tag_by_genre: true
  tag_by_theme: false
  color_scheme:
    old_testament: "#2E7D32"
    new_testament: "#1565C0"
    law: "#F57C00"
    history: "#5E35B1"
    wisdom: "#FFB300"
    prophets: "#D84315"
    gospels: "#00ACC1"
    epistles: "#7B1FA2"
    apocalyptic: "#C62828"

# Statistics & Analytics
statistics:
  calculate_reading_time: true
  words_per_minute: 200
  include_verse_counts: true
  include_word_counts: true
  track_by_genre: true
  
# Advanced Options
advanced:
  encoding: "utf-8"
  line_endings: "unix"  # unix, windows
  validate_dates: true
  create_index: true
  backup_existing: false
```

### 3. Bible Data Manager (`bible/data_manager.py`)

**Responsibilities**:
- Load Bible structure from JSON
- Filter by scope (OT/NT/Complete)
- Provide metadata (testament, genre, chapters, verses, word counts)
- Calculate statistics

**Key Methods**:
```python
class BibleDataManager:
    def __init__(self, data_path: Path):
        """Load Bible structure and statistics"""
        
    def get_books(self, scope: BibleScope) -> List[Book]:
        """Return books for specified scope"""
        
    def get_chapter_count(self, scope: BibleScope) -> int:
        """Total chapters in scope"""
        
    def get_book_metadata(self, book_name: str) -> BookMetadata:
        """Get genre, testament, author, etc."""
        
    def calculate_reading_stats(
        self, 
        book: str, 
        chapters: List[int]
    ) -> ReadingStats:
        """Calculate verse count, word count, estimated time"""
        
    def get_books_by_genre(self, genre: str) -> List[Book]:
        """Filter books by genre"""
```

**Data Model**:
```python
@dataclass
class Book:
    name: str
    abbreviation: str
    testament: Testament  # Enum: OLD, NEW
    genre: Genre  # Enum: LAW, HISTORY, WISDOM, PROPHETS, etc.
    chapters: int
    chapter_verses: List[int]
    total_verses: int
    total_words: int
    author: Optional[str]
    
@dataclass
class ReadingStats:
    verse_count: int
    word_count: int
    estimated_minutes: int
    chapters_covered: List[int]
```

### 4. Reading Plan Strategies (`plans/`)

**Base Interface**:
```python
from abc import ABC, abstractmethod

class ReadingPlanStrategy(ABC):
    @abstractmethod
    def generate_schedule(
        self, 
        year: int,
        days: int,
        bible_data: BibleDataManager,
        scope: BibleScope
    ) -> List[StudyDay]:
        """
        Generate complete reading schedule.
        
        Returns:
            List of StudyDay objects with reading assignments
        """
        pass
    
    @abstractmethod
    def validate_schedule(self, schedule: List[StudyDay]) -> bool:
        """Validate generated schedule meets requirements"""
        pass
```

**Canonical Plan Algorithm**:
```python
class CanonicalPlan(ReadingPlanStrategy):
    """
    Read Bible in book order: Genesis → Revelation
    
    Algorithm:
    1. Get books for scope (OT/NT/Complete)
    2. Calculate total chapters
    3. Distribute chapters across days:
       - Target: 3-4 chapters/day
       - Balance: Avoid 1-chapter days followed by 6-chapter days
       - Respect books: Try not to split short books
       - Smart grouping: Combine Philemon, 2-3 John, Jude
    4. Assign dates sequentially
    """
    
    def distribute_chapters(
        self, 
        books: List[Book], 
        days: int
    ) -> List[ReadingSegment]:
        """Implement smart chapter distribution"""
        # Implementation details...
```

### 5. Template System (`rendering/`)

**Default Template** (`templates/daily/default.md.jinja2`):
```jinja2
---
date: {{ date.strftime('%Y-%m-%d') }}
day: {{ day_number }}
tags: {{ tags | tojson }}
testament: {{ testament }}
genre: {{ genre }}
book: {{ reading.book }}
chapters: "{{ reading.start_chapter }}-{{ reading.end_chapter }}"
estimated_minutes: {{ reading.estimated_minutes }}
verse_count: {{ reading.verse_count }}
word_count: {{ reading.word_count }}
status: pending
---

# Day {{ day_number }}: {{ date.strftime('%A, %B %d, %Y') }}

## 📖 Today's Reading

**{{ reading.book }} {{ reading.start_chapter }}{% if reading.end_chapter != reading.start_chapter %}-{{ reading.end_chapter }}{% endif %}**

- 📊 {{ reading.verse_count }} verses
- 📝 ~{{ reading.word_count }} words
- ⏱️ {{ reading.estimated_minutes }} minutes

{% if config.include_context %}
### Context
{{ reading.context_note }}
{% endif %}

---

## 📝 Notes & Observations

*What did you notice in today's reading?*



---

## 💭 Reflection

### Key Themes


### Questions


### Personal Application


---

## 🙏 Prayer


---

## 📊 Metadata

**Testament**: {{ testament | title }}  
**Genre**: {{ genre | title }}  
**Progress**: Day {{ day_number }} of {{ total_days }} ({{ progress_percentage }}%)

{% if config.dataview_inline %}
Reading:: [[{{ reading.book }}]]
Status:: #status/pending
{% endif %}

---

{% if links.previous %}[[{{ links.previous }}|← Previous Day]]{% endif %} | {% if links.dashboard %}[[{{ links.dashboard }}|Dashboard]]{% endif %} | {% if links.next %}[[{{ links.next }}|Next Day →]]{% endif %}
```

**Custom Filters** (`rendering/filters.py`):
```python
def format_chapter_range(start: int, end: int) -> str:
    """Format chapter range nicely"""
    if start == end:
        return str(start)
    return f"{start}-{end}"

def testament_emoji(testament: str) -> str:
    """Return emoji for testament"""
    return "📜" if testament == "old" else "✨"

def genre_color(genre: str) -> str:
    """Return color tag for genre"""
    colors = {
        "law": "🟧",
        "history": "🟪",
        "wisdom": "🟨",
        # ...
    }
    return colors.get(genre.lower(), "⬜")
```

### 6. Progress Dashboard (`rendering/dashboard.py`)

**Dashboard Template** (`templates/dashboard/progress.md.jinja2`):
```jinja2
---
title: {{ year }} Bible Study Progress
tags: [dashboard, bible-study, progress]
cssclass: dashboard
---

# 📖 {{ year }} Bible Study Dashboard

## 📊 Overall Progress

```dataview
TASK
FROM "{{ study_folder }}"
WHERE file.name != "{{ dashboard_name }}"
SORT date ASC
```

### Statistics

**Total Reading Days**: {{ total_days }}  
**Days Completed**: `= length(filter(file.tasks, (t) => t.completed))` / {{ total_days }}  
**Completion Rate**: `= round((length(filter(file.tasks, (t) => t.completed)) / {{ total_days }}) * 100, 1)`%

**Total Chapters**: {{ total_chapters }}  
**Total Verses**: {{ total_verses }}  
**Total Words**: ~{{ total_words | format_number }}

---

## 📅 Monthly Progress

```dataview
TABLE WITHOUT ID
  file.link as "Month",
  length(filter(rows.file.tasks, (t) => t.completed)) as "Completed",
  length(rows.file.tasks) as "Total",
  round((length(filter(rows.file.tasks, (t) => t.completed)) / length(rows.file.tasks)) * 100, 1) + "%" as "Progress"
FROM "{{ study_folder }}"
WHERE file.name != "{{ dashboard_name }}"
GROUP BY dateformat(date, "yyyy-MM") as month
SORT month ASC
```

---

## 📚 Progress by Testament

{% for testament in testaments %}
### {{ testament.name }}

**Books**: {{ testament.book_count }}  
**Chapters**: {{ testament.chapter_count }}  
**Estimated Time**: {{ testament.estimated_hours }}h

```dataview
LIST
FROM "{{ study_folder }}"
WHERE testament = "{{ testament.key }}" AND status = "completed"
SORT date ASC
```
{% endfor %}

---

## 🎯 Current Week

```dataview
TABLE WITHOUT ID
  file.link as "Day",
  book + " " + chapters as "Reading",
  estimated_minutes + " min" as "Time",
  status as "Status"
FROM "{{ study_folder }}"
WHERE date >= date(today) - dur(7 days) AND date <= date(today) + dur(7 days)
SORT date ASC
```

---

## 📈 Reading Streak

**Current Streak**: `= this.current_streak` days  
**Longest Streak**: `= this.longest_streak` days

---

## 🏆 Milestones

- [ ] Completed Old Testament
- [ ] Completed New Testament  
- [ ] Completed all Psalms (150 chapters)
- [ ] Completed all Proverbs (31 chapters)
- [ ] Read for 30 consecutive days
- [ ] Read for 90 consecutive days
- [ ] Completed full year

---

## 📖 Quick Links

{% for book in books %}
- [[{{ book.index_link }}|{{ book.name }}]]
{% endfor %}

---

*Last updated: {{ now.strftime('%Y-%m-%d %H:%M') }}*
```

### 7. Statistics Engine (`bible/statistics.py`)

**Responsibilities**:
- Calculate reading time estimates
- Track verse/word counts
- Generate progress metrics
- Group statistics by testament, genre, book

**Key Calculations**:
```python
class StatisticsEngine:
    def __init__(self, words_per_minute: int = 200):
        self.wpm = words_per_minute
    
    def calculate_reading_time(self, word_count: int) -> int:
        """Return estimated minutes to read"""
        return math.ceil(word_count / self.wpm)
    
    def get_progress_percentage(
        self, 
        completed_days: int, 
        total_days: int
    ) -> float:
        """Calculate completion percentage"""
        return round((completed_days / total_days) * 100, 1)
    
    def get_testament_breakdown(
        self, 
        schedule: List[StudyDay]
    ) -> Dict[str, TestamentStats]:
        """Statistics by testament"""
        
    def get_genre_breakdown(
        self, 
        schedule: List[StudyDay]
    ) -> Dict[str, GenreStats]:
        """Statistics by genre"""
```

---

## Data Schemas

### Bible Structure Data (`data/bible_structure.json`)

```json
{
  "metadata": {
    "version": "1.0",
    "translation": "ESV",
    "total_books": 66,
    "total_chapters": 1189,
    "total_verses": 31102
  },
  "old_testament": [
    {
      "name": "Genesis",
      "abbreviation": "Gen",
      "testament": "old",
      "genre": "law",
      "chapters": 50,
      "chapter_verses": [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, ...],
      "total_verses": 1533,
      "total_words": 38267,
      "author": "Moses",
      "themes": ["creation", "covenant", "promise"]
    }
  ],
  "new_testament": [
    {
      "name": "Matthew",
      "abbreviation": "Matt",
      "testament": "new",
      "genre": "gospel",
      "chapters": 28,
      "chapter_verses": [25, 23, 17, 25, 48, 34, 29, 34, ...],
      "total_verses": 1071,
      "total_words": 23684,
      "author": "Matthew",
      "themes": ["messiah", "kingdom", "fulfillment"]
    }
  ]
}
```

### Bible Statistics (`data/bible_stats.json`)

```json
{
  "complete": {
    "total_chapters": 1189,
    "total_verses": 31102,
    "total_words": 783137,
    "estimated_hours": 65.3,
    "average_chapters_per_day": 3.26
  },
  "old_testament": {
    "total_chapters": 929,
    "total_verses": 23145,
    "total_words": 622700,
    "estimated_hours": 51.9,
    "books": 39
  },
  "new_testament": {
    "total_chapters": 260,
    "total_verses": 7957,
    "total_words": 184437,
    "estimated_hours": 15.4,
    "books": 27
  },
  "genres": {
    "law": {"books": 5, "chapters": 187},
    "history": {"books": 12, "chapters": 249},
    "wisdom": {"books": 5, "chapters": 243},
    "major_prophets": {"books": 5, "chapters": 183},
    "minor_prophets": {"books": 12, "chapters": 67},
    "gospels": {"books": 4, "chapters": 89},
    "acts": {"books": 1, "chapters": 28},
    "epistles": {"books": 21, "chapters": 138},
    "apocalyptic": {"books": 1, "chapters": 22}
  }
}
```

---

## Consequences

### Positive

1. **Flexibility**: Support for complete Bible, NT-only, OT-only accommodates various study goals
2. **Progress Tracking**: Built-in dashboard provides motivation and accountability
3. **Obsidian Optimization**: Rich metadata enables powerful queries and graph visualization
4. **Extensibility**: Plugin architecture allows custom reading plans
5. **User Control**: Extensive configuration options without code changes
6. **Statistics**: Reading time and progress metrics help planning
7. **No External Dependencies**: Self-contained, runs offline
8. **Maintainability**: Clear separation of concerns, testable components

### Negative

1. **Complexity**: Many features increase initial development time
2. **Configuration Overhead**: Users may find YAML config intimidating
3. **Template Learning Curve**: Custom templates require Jinja2 knowledge
4. **Dataview Dependency**: Dashboard features require Obsidian Dataview plugin
5. **Data Accuracy**: Word counts and time estimates are approximate
6. **Maintenance**: Bible data requires updates for different translations

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Incorrect chapter distribution | High | Extensive testing, validate against known plans |
| Leap year bugs | Medium | Comprehensive date handling tests |
| File conflicts | Medium | Implement backup/overwrite options |
| Template errors | Medium | Validate templates before generation |
| Performance with large outputs | Low | Batch file writes, progress indicators |
| Unicode encoding issues | Low | Force UTF-8, test with various OS |

---

## Implementation Plan

### Phase 1: Core Functionality (Week 1-2)
- [ ] Project structure setup
- [ ] CLI interface with argparse
- [ ] Configuration management (YAML)
- [ ] Bible data loading and scope filtering
- [ ] Basic canonical reading plan
- [ ] Simple template rendering
- [ ] File writing with folder structure

### Phase 2: Enhanced Features (Week 3)
- [ ] Statistics engine (reading time, word counts)
- [ ] Dataview metadata generation
- [ ] Graph view tagging system
- [ ] Template system with multiple options
- [ ] Chronological reading plan
- [ ] Date handling and validation

### Phase 3: Progress Tracking (Week 4)
- [ ] Dashboard template development
- [ ] Dataview query integration
- [ ] Progress calculation logic
- [ ] Milestone tracking
- [ ] Statistics by testament/genre
- [ ] Index file generation

### Phase 4: Polish & Testing (Week 5)
- [ ] Comprehensive unit tests
- [ ] Integration tests
- [ ] Documentation (user guide, template guide)
- [ ] Example configurations
- [ ] Error handling refinement
- [ ] Performance optimization

### Phase 5: Release (Week 6)
- [ ] Package for PyPI
- [ ] CI/CD setup
- [ ] Community templates
- [ ] Tutorial videos/docs
- [ ] Example Obsidian vault

---

## Testing Strategy

### Unit Tests
- Bible data loading and filtering
- Date calculations (including leap years)
- Chapter distribution algorithms
- Template rendering
- Statistics calculations
- File naming patterns

### Integration Tests
- Full year generation (complete, NT, OT)
- Template + data pipeline
- Config loading + CLI override
- Dashboard generation

### Test Fixtures
- Sample Bible data (Genesis + Matthew only)
- Mock configurations
- Expected output files

### Validation Tests
- Verify all chapters assigned exactly once
- Confirm day count matches year
- Check file naming consistency
- Validate YAML frontmatter
- Dataview query syntax

---

## Success Metrics

1. **Functionality**: Generate valid plans for all scopes and plan types
2. **Performance**: Complete year generation in < 5 seconds
3. **Accuracy**: Zero missed chapters, correct chapter distribution
4. **Usability**: Clear error messages, helpful CLI help text
5. **Integration**: Dashboard queries work in Obsidian with Dataview
6. **Maintainability**: >80% test coverage
7. **Adoption**: Positive user feedback, feature requests

---

## Future Enhancements (Not in Initial Release)

1. **Multi-Translation Support**: Parallel passages from multiple versions
2. **Commentary Integration**: Link to study notes/commentaries
3. **Audio Links**: Include Bible audio URLs
4. **Memory Verse System**: Highlight verses for memorization
5. **Study Guide Integration**: Connect to reading guides
6. **Mobile Optimization**: Special templates for mobile Obsidian
7. **Collaborative Plans**: Shared group study schedules
8. **Reading History Import**: Track past progress
9. **Custom Genre Definitions**: User-defined book groupings
10. **API for External Tools**: Webhook/API for progress tracking apps

---

## References

- [Obsidian Documentation](https://help.obsidian.md/)
- [Dataview Plugin](https://blacksmithgu.github.io/obsidian-dataview/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Bible Gateway Statistics](https://www.biblegateway.com/blog/2013/02/interesting-facts-about-the-bible/)
- [Chronological Bible Reading Plans](https://www.biblestudytools.com/bible-reading-plan/)

---

## Approval

- [ ] Architecture Approved
- [ ] Technical Approach Approved  
- [ ] Implementation Plan Approved
- [ ] Ready for Development

**Approved By**: _________________  
**Date**: _________________

---

## Changelog

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-12-02 | 1.0 | Initial ADR | Development Team |
