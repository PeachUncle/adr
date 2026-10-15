# ADR-005: Vault Bible Linking for BibleGateway-to-Obsidian

**Status**: Proposed  
**Date**: 2025-12-02  
**Decision Makers**: Development Team  
**Supersedes**: N/A  
**Related to**: ADR-001 (Bible Study Planner Architecture)

---

## Context

Many Obsidian users maintain Bible content within their vault using [BibleGateway-to-Obsidian](https://github.com/selfire1/BibleGateway-to-Obsidian), a script that downloads Bible text from BibleGateway and formats it for use in Obsidian. This creates a structured Scripture folder with individual chapter files organized by book.

Currently, the Bible study planner generates daily reading notes with plain text references (e.g., "Genesis 1-3"). Users want these references to automatically link to their existing Bible chapter files, enabling seamless navigation between daily reading plans and the actual Scripture text.

### BibleGateway-to-Obsidian Structure

The BibleGateway-to-Obsidian script creates a standardized structure with one folder per chapter file:

```
Scripture/
  ├── 01 - Genesis/
  │   ├── Genesis 1.md
  │   ├── Genesis 2.md
  │   ├── Genesis 3.md
  │   └── ...
  ├── 02 - Exodus/
  │   ├── Exodus 1.md
  │   ├── Exodus 2.md
  │   └── ...
  └── 66 - Revelation/
      ├── Revelation 1.md
      └── ...
```

**Multiple Translation Support**:

Many users maintain multiple Bible translations in their vault, organizing them as:

```
Bible/
  ├── ESV/
  │   ├── 01 - Genesis/
  │   │   ├── Genesis 1.md
  │   │   └── ...
  │   └── 02 - Exodus/
  │       └── ...
  ├── NIV/
  │   ├── 01 - Genesis/
  │   │   └── ...
  │   └── ...
  └── WEB/
      ├── 01 - Genesis/
      │   └── ...
      └── ...
```

**Key Characteristics**:
- Top-level Bible folder with translation subfolders (e.g., `Bible/ESV/`)
- Numbered book folders: `{number} - {BookName}/`
- Chapter files: `{BookName} {chapter}.md`
- One file per chapter
- Consistent naming across all translations

### Current Behavior

Generated daily notes contain plain text:
```markdown
## 📖 Today's Reading

**Genesis 1-3**
```

### Desired Behavior

With `--vault-bible "Bible/ESV"` option:
```markdown
## 📖 Today's Reading

**[[Bible/ESV/01 - Genesis/Genesis 1|Genesis 1]]**
**[[Bible/ESV/01 - Genesis/Genesis 2|Genesis 2]]**
**[[Bible/ESV/01 - Genesis/Genesis 3|Genesis 3]]**
```

Or collapsed range format:
```markdown
## 📖 Today's Reading

**Genesis 1-3** ([[Bible/ESV/01 - Genesis/Genesis 1|1]], [[Bible/ESV/01 - Genesis/Genesis 2|2]], [[Bible/ESV/01 - Genesis/Genesis 3|3]])
```

### User Benefits

1. **One-Click Navigation**: Click directly from reading plan to Scripture text
2. **Backlinks**: See which reading days reference specific passages in Obsidian's backlink panel
3. **Graph View**: Visualize connections between daily studies and Scripture
4. **Unified Vault**: Keep Bible content and reading plans in one Obsidian vault
5. **Hover Previews**: Preview Scripture text without leaving the daily note

---

## Decision

We will implement a `--vault-bible` option that generates Obsidian wikilinks to chapter files created by the BibleGateway-to-Obsidian script. The implementation will be specifically tailored to this known structure, making it simple and reliable.

### Proposed CLI Option

```bash
--vault-bible PATH      Path to BibleGateway-to-Obsidian Scripture folder.
                        Supports single or multi-translation structure.
                        Examples: 
                          --vault-bible "Scripture"
                          --vault-bible "Bible/ESV"
                          --vault-bible "Resources/Bibles/NIV"
```

### Implementation Approach

**Assumptions**:
1. User has generated Bible content using BibleGateway-to-Obsidian
2. Scripture folder follows the standard structure: `{path}/{number} - {BookName}/{BookName} {chapter}.md`
3. Path provided includes the translation folder (e.g., `Bible/ESV`, `Bible/NIV`, `Scripture`)
4. Folder path is provided relative to the vault root or relative to the output directory

**Strategy**:
1. Accept a folder path that may include translation subfolder (e.g., "Scripture" or "Bible/ESV")
2. Generate individual chapter links for each chapter in a reading assignment
3. Use book number prefixes for folder paths (lookup table)
4. Support both expanded links and collapsed range formats
5. User specifies which translation to link to via the path

### Link Generation Examples

**Example 1: Single Chapter (ESV Translation)**
- Path: `Bible/ESV`
- Reading: Genesis 1
- Generated: `[[Bible/ESV/01 - Genesis/Genesis 1|Genesis 1]]`

**Example 2: Chapter Range (Expanded Format, NIV Translation)**
- Path: `Bible/NIV`
- Reading: Genesis 1-3
- Generated:
  ```markdown
  [[Bible/NIV/01 - Genesis/Genesis 1|Genesis 1]]
  [[Bible/NIV/01 - Genesis/Genesis 2|Genesis 2]]
  [[Bible/NIV/01 - Genesis/Genesis 3|Genesis 3]]
  ```

**Example 3: Chapter Range (Collapsed Format)**
- Path: `Bible/ESV`
- Reading: Genesis 1-3
- Generated: `Genesis 1-3 ([[Bible/ESV/01 - Genesis/Genesis 1|1]], [[Bible/ESV/01 - Genesis/Genesis 2|2]], [[Bible/ESV/01 - Genesis/Genesis 3|3]])`

**Example 4: Multiple Books**
- Path: `Bible/ESV`
- Reading: Genesis 50, Exodus 1-2
- Generated:
  ```markdown
  [[Bible/ESV/01 - Genesis/Genesis 50|Genesis 50]]
  [[Bible/ESV/02 - Exodus/Exodus 1|Exodus 1]]
  [[Bible/ESV/02 - Exodus/Exodus 2|Exodus 2]]
  ```

**Example 5: Simple Structure (No Translation Subfolder)**
- Path: `Scripture`
- Reading: Genesis 1
- Generated: `[[Scripture/01 - Genesis/Genesis 1|Genesis 1]]`

---

## Design Considerations

### 1. Book Number Mapping

**Decision**: Maintain a lookup table mapping book names to their standard Bible order numbers

**Implementation**:
```python
BIBLE_BOOK_NUMBERS = {
    # Old Testament
    "Genesis": 1,
    "Exodus": 2,
    "Leviticus": 3,
    "Numbers": 4,
    "Deuteronomy": 5,
    "Joshua": 6,
    "Judges": 7,
    "Ruth": 8,
    "1 Samuel": 9,
    "2 Samuel": 10,
    # ... all 66 books
    "Revelation": 66,
}

def get_book_number(book_name: str) -> int:
    """Get standard Bible book number (1-66)."""
    return BIBLE_BOOK_NUMBERS.get(book_name, 0)
```

**Rationale**:
- BibleGateway-to-Obsidian uses numbered folders consistently
- Fixed mapping works for all Bible translations
- Simple and reliable

### 2. Link Format Option

**Decision**: Provide a `--vault-bible-format` option to control link display

**Formats**:

**A. Expanded (Default)** - One link per line
```markdown
**[[Scripture/01 - Genesis/Genesis 1|Genesis 1]]**
**[[Scripture/01 - Genesis/Genesis 2|Genesis 2]]**
**[[Scripture/01 - Genesis/Genesis 3|Genesis 3]]**
```

**B. Inline** - Compact with chapter numbers
```markdown
**Genesis 1-3** ([[Scripture/01 - Genesis/Genesis 1|1]], [[Scripture/01 - Genesis/Genesis 2|2]], [[Scripture/01 - Genesis/Genesis 3|3]])
```

**C. Hybrid** - Full reference first, then links
```markdown
**Genesis 1-3**
- [[Scripture/01 - Genesis/Genesis 1|Chapter 1]]
- [[Scripture/01 - Genesis/Genesis 2|Chapter 2]]
- [[Scripture/01 - Genesis/Genesis 3|Chapter 3]]
```

**CLI Option**:
```bash
--vault-bible-format [expanded|inline|hybrid]
```

### 3. Path Handling

**Decision**: Support both absolute and relative paths, normalize to forward slashes

**Examples**:
- `Scripture` → `Scripture/`
- `Bible/ESV` → `Bible/ESV/`
- `Bible/NIV` → `Bible/NIV/`
- `../Bible/ESV` → `../Bible/ESV/`
- `Bible\ESV` (Windows) → `Bible/ESV/`

**Implementation**:
```python
def normalize_vault_path(path: str) -> str:
    """Normalize path for Obsidian wikilinks."""
    normalized = path.replace("\\", "/").strip("/")
    return normalized if normalized else ""
```

### 4. File Validation

**Decision**: Warn if Scripture folder doesn't exist, but continue generation

**Approach**:
- At generation start: Check if vault-bible folder exists
  - ✅ Found: Display confirmation message
  - ⚠️ Not found: Display warning, but continue (user may add Bible later)
- During generation: Always generate links regardless of file existence
- Links will work when user adds Scripture files

**User Experience**:
```bash
$ bible-study-planner generate --vault-bible "Bible/ESV"
⚠️  Warning: Bible folder not found at: Bible/ESV
   Links will be generated but may not resolve until you add Bible files.
   Generate Bible content using: https://github.com/selfire1/BibleGateway-to-Obsidian
```

### 5. Single vs. Multiple Chapters

**Decision**: Automatically expand chapter ranges into individual links

**Rationale**:
- Each chapter is a separate file in BibleGateway-to-Obsidian
- Individual links enable direct navigation
- Supports hover previews for each chapter
- Better backlink granularity

**Example**:
- Input: Genesis 1-5
- Output: 5 separate wikilinks (Genesis 1, Genesis 2, Genesis 3, Genesis 4, Genesis 5)

### 6. Frontmatter Links

**Decision**: Add a structured `scripture_links` field to frontmatter for Dataview queries

**Frontmatter Addition**:
```yaml
---
date: 2025-01-01
day: 1
plan_id: complete-2025-canonical
scripture_links:
  - "Bible/ESV/01 - Genesis/Genesis 1"
  - "Bible/ESV/01 - Genesis/Genesis 2"
  - "Bible/ESV/01 - Genesis/Genesis 3"
---
```

**Benefit**: Enables Dataview queries like:
```dataview
LIST
WHERE contains(scripture_links, "Genesis 1")
```

---

## Implementation Plan

### Phase 1: Core Functionality (v1.4)

**Tasks**:
1. Add `--vault-bible` CLI option
2. Add `--vault-bible-format` CLI option (default: "expanded")
3. Create `VaultBibleLinker` class
4. Implement book number lookup table (all 66 books)
5. Implement chapter link generation with expanded format
6. Update `_generate_simple_markdown()` to use linker
7. Add frontmatter `scripture_links` field
8. Add path validation with warning messages
9. Unit tests for link generation
10. Documentation and examples

**Code Structure**:

```python
# bible/vault_linker.py

from pathlib import Path
from typing import List

class VaultBibleLinker:
    """Generate wikilinks to BibleGateway-to-Obsidian chapter files."""
    
    BOOK_NUMBERS = {
        "Genesis": 1, "Exodus": 2, "Leviticus": 3, # ... all 66 books
    }
    
    def __init__(self, vault_folder: str, format_style: str = "expanded"):
        """Initialize with Scripture folder path and format style.
        
        Args:
            vault_folder: Path to Scripture folder including translation
                         (e.g., "Scripture", "Bible/ESV", "Bible/NIV")
            format_style: Link format (expanded, inline, hybrid)
        """
        self.vault_folder = vault_folder.replace("\\", "/").strip("/")
        self.format_style = format_style
    
    def validate_path(self, output_dir: Path) -> bool:
        """Check if Scripture folder exists relative to output."""
        # Try both relative to output and absolute
        paths_to_check = [
            output_dir.parent / self.vault_folder,
            Path(self.vault_folder)
        ]
        return any(p.exists() for p in paths_to_check)
    
    def generate_chapter_links(
        self, 
        book_name: str, 
        start_chapter: int, 
        end_chapter: int
    ) -> List[str]:
        """Generate list of wikilinks for chapter range.
        
        Args:
            book_name: Book name (e.g., "Genesis")
            start_chapter: Starting chapter number
            end_chapter: Ending chapter number
            
        Returns:
            List of wikilinks for each chapter
        """
        book_num = self.BOOK_NUMBERS.get(book_name)
        if not book_num:
            return []  # Unknown book
        
        book_num_str = f"{book_num:02d}"
        folder_name = f"{book_num_str} - {book_name}"
        
        links = []
        for chapter in range(start_chapter, end_chapter + 1):
            file_path = f"{self.vault_folder}/{folder_name}/{book_name} {chapter}"
            link = f"[[{file_path}|{book_name} {chapter}]]"
            links.append(link)
        
        return links
    
    def format_links(
        self, 
        links: List[str], 
        book_name: str, 
        start_chapter: int, 
        end_chapter: int
    ) -> str:
        """Format links according to style.
        
        Args:
            links: List of generated wikilinks
            book_name: Book name for display
            start_chapter: Starting chapter
            end_chapter: Ending chapter
            
        Returns:
            Formatted markdown string
        """
        if not links:
            # Fallback to plain text
            if end_chapter > start_chapter:
                return f"**{book_name} {start_chapter}-{end_chapter}**"
            return f"**{book_name} {start_chapter}**"
        
        if self.format_style == "expanded":
            # One link per line
            return "\n".join(f"**{link}**" for link in links)
        
        elif self.format_style == "inline":
            # Compact format
            if end_chapter > start_chapter:
                chapter_nums = [f"[[{link.split('|')[0][2:]}|{i}]]" 
                               for i, link in enumerate(links, start_chapter)]
                return f"**{book_name} {start_chapter}-{end_chapter}** ({', '.join(chapter_nums)})"
            return f"**{links[0]}**"
        
        elif self.format_style == "hybrid":
            # Bullet list format
            if end_chapter > start_chapter:
                range_str = f"**{book_name} {start_chapter}-{end_chapter}**\n"
            else:
                range_str = f"**{book_name} {start_chapter}**\n"
            bullet_links = "\n".join(f"- {link}" for link in links)
            return range_str + bullet_links
        
        return "\n".join(f"**{link}**" for link in links)  # Default to expanded
    
    def get_frontmatter_links(self, links: List[str]) -> List[str]:
        """Extract link paths for frontmatter.
        
        Args:
            links: Generated wikilinks
            
        Returns:
            List of link paths without brackets
        """
        paths = []
        for link in links:
            # Extract path from [[path|display]]
            if "[[" in link and "]]" in link:
                path = link.split("[[")[1].split("|")[0]
                paths.append(path)
        return paths
```

**CLI Changes**:

```python
# cli.py

@click.option(
    "--vault-bible",
    type=str,
    default=None,
    help="Link to BibleGateway-to-Obsidian Scripture folder. "
         "Include translation subfolder if using multiple translations "
         "(e.g., 'Scripture', 'Bible/ESV', 'Bible/NIV')",
)
@click.option(
    "--vault-bible-format",
    type=click.Choice(["expanded", "inline", "hybrid"], case_sensitive=False),
    default="expanded",
    help="Format for Bible links (default: expanded)",
)
def generate(
    # ... existing params ...
    vault_bible: str | None,
    vault_bible_format: str,
) -> None:
    """Generate a Bible reading plan."""
    
    # ... existing code ...
    
    # Initialize vault Bible linker
    bible_linker = None
    if vault_bible:
        bible_linker = VaultBibleLinker(vault_bible, vault_bible_format)
        
        # Validate path
        if not bible_linker.validate_path(output):
            click.echo(f"⚠️  Warning: Bible folder not found: {vault_bible}")
            click.echo("   Links will be generated but may not resolve.")
            click.echo("   Generate Bible: https://github.com/selfire1/BibleGateway-to-Obsidian")
        else:
            click.echo(f"✅ Found Bible folder: {vault_bible}")
    
    # ... generate schedule ...
    
    # Pass linker to markdown generation
    content = _generate_simple_markdown(day, resolved_plan_id, bible_linker)
```

**Markdown Generation Update**:

```python
def _generate_simple_markdown(
    day: StudyDay, 
    plan_id: str,
    bible_linker: VaultBibleLinker | None = None
) -> str:
    """Generate markdown with optional Bible links."""
    
    segments = day.reading_segments
    all_scripture_links = []
    
    # Frontmatter
    content = "---\n"
    content += f"date: {day.date.strftime('%Y-%m-%d')}\n"
    content += f"day: {day.day_number}\n"
    content += f"plan_id: {plan_id}\n"
    
    # Add scripture_links if linker enabled
    if bible_linker:
        for segment in segments:
            links = bible_linker.generate_chapter_links(
                segment.book.name,
                segment.start_chapter,
                segment.end_chapter
            )
            all_scripture_links.extend(bible_linker.get_frontmatter_links(links))
        
        if all_scripture_links:
            content += "scripture_links:\n"
            for link in all_scripture_links:
                content += f'  - "{link}"\n'
    
    # ... rest of frontmatter ...
    content += "---\n\n"
    
    # Body
    content += f"# Day {day.day_number}: {day.date.strftime('%A, %B %d, %Y')}\n\n"
    content += "## 📖 Today's Reading\n\n"
    
    for segment in segments:
        if bible_linker:
            links = bible_linker.generate_chapter_links(
                segment.book.name,
                segment.start_chapter,
                segment.end_chapter
            )
            formatted = bible_linker.format_links(
                links,
                segment.book.name,
                segment.start_chapter,
                segment.end_chapter
            )
            content += f"{formatted}\n\n"
        else:
            # Plain text (default)
            content += f"**{segment.book.name} {segment.chapter_range_str}**\n\n"
    
    # ... rest of content ...
    
    return content
```

### Phase 2: Enhancements (v1.5) [Future]

**Potential Features**:
1. Auto-detect Scripture folder in vault
2. Support custom book folder naming patterns
3. Generate "Read Bible" button links in daily notes
4. Integration with Obsidian Breadcrumbs plugin
5. Support for abbreviated book names in file paths

---

## Usage Examples

### Example 1: Basic Usage with Default Format

```bash
bible-study-planner generate \
  --start-date 2025-01-01 \
  --scope complete \
  --output "ReadingPlan" \
  --vault-bible "Bible/ESV"
```

**Generated File** (`2025-01-01-day-001.md`):
```markdown
---
date: 2025-01-01
day: 1
plan_id: complete-2025-canonical
scripture_links:
  - "Bible/ESV/01 - Genesis/Genesis 1"
  - "Bible/ESV/01 - Genesis/Genesis 2"
  - "Bible/ESV/01 - Genesis/Genesis 3"
tags: [bible-study, daily, genesis, old-testament, law]
---

# Day 1: Monday, January 01, 2025

## 📖 Today's Reading

**[[Bible/ESV/01 - Genesis/Genesis 1|Genesis 1]]**
**[[Bible/ESV/01 - Genesis/Genesis 2|Genesis 2]]**
**[[Bible/ESV/01 - Genesis/Genesis 3|Genesis 3]]**

- 📊 78 verses
- 📝 ~2,350 words
- ⏱️ 12 minutes
```

### Example 2: Inline Format with NIV Translation

```bash
bible-study-planner generate \
  --start-date 2025-01-01 \
  --scope nt \
  --vault-bible "Bible/NIV" \
  --vault-bible-format inline
```

**Generated Content**:
```markdown
## 📖 Today's Reading

**Matthew 1-2** ([[Bible/NIV/40 - Matthew/Matthew 1|1]], [[Bible/NIV/40 - Matthew/Matthew 2|2]])
```

### Example 3: Hybrid Format with WEB Translation

```bash
bible-study-planner generate \
  --start-date 2025-06-01 \
  --scope ot \
  --days 180 \
  --vault-bible "Bible/WEB" \
  --vault-bible-format hybrid
```

**Generated Content**:
```markdown
## 📖 Today's Reading

**Genesis 1-3**
- [[Bible/WEB/01 - Genesis/Genesis 1|Genesis 1]]
- [[Bible/WEB/01 - Genesis/Genesis 2|Genesis 2]]
- [[Bible/WEB/01 - Genesis/Genesis 3|Genesis 3]]
```

### Example 4: Multiple Books in One Day with ESV

```bash
bible-study-planner generate \
  --start-date 2025-01-01 \
  --scope complete \
  --days 180 \
  --vault-bible "Bible/ESV"
```

**Generated Content** (on a day with multiple books):
```markdown
## 📖 Today's Reading

**[[Bible/ESV/39 - Malachi/Malachi 3|Malachi 3]]**
**[[Bible/ESV/39 - Malachi/Malachi 4|Malachi 4]]**
**[[Bible/ESV/40 - Matthew/Matthew 1|Matthew 1]]**
```

### Example 5: Simple Structure (No Translation Subfolder)

```bash
bible-study-planner generate \
  --start-date 2025-01-01 \
  --scope complete \
  --vault-bible "Scripture"
```

**Generated Content**:
```markdown
## 📖 Today's Reading

**[[Scripture/01 - Genesis/Genesis 1|Genesis 1]]**
**[[Scripture/01 - Genesis/Genesis 2|Genesis 2]]**
**[[Scripture/01 - Genesis/Genesis 3|Genesis 3]]**
```

*Note: This works for users who maintain a single translation without subfolders.*

---

## Dataview Integration

With the `scripture_links` frontmatter field, users can create powerful queries:

### Find All Days Reading Genesis

```dataview
TABLE day, date, verse_count
WHERE contains(scripture_links, "Genesis")
SORT day ASC
```

### Track Progress Through a Book

```dataview
TABLE 
  length(filter(scripture_links, (x) => contains(x, "01 - Genesis"))) as "Genesis Chapters"
WHERE plan_id = "complete-2025-canonical" AND status = "completed"
GROUP BY "Progress"
```

### Recently Read Passages

```dataview
TABLE scripture_links as "Passages"
WHERE status = "completed"
SORT date DESC
LIMIT 7
```

---

## Consequences

### Positive

1. **Seamless Navigation**: One click from reading plan to Scripture text
2. **Standardized Solution**: Works for all BibleGateway-to-Obsidian generated content
3. **Simple Implementation**: Known structure means reliable link generation
4. **Backlinks Support**: Automatic bidirectional linking in Obsidian
5. **Dataview Integration**: Frontmatter links enable powerful queries
6. **Multiple Formats**: Users choose link display style that fits their workflow
7. **Graceful Degradation**: Warns but works even without Scripture files present
8. **No Breaking Changes**: Completely optional feature

### Negative

1. **Vendor Lock-in**: Only works with BibleGateway-to-Obsidian structure
2. **Chapter File Requirement**: Doesn't support other Bible vault organizations
3. **Link Proliferation**: Many chapters create many links (mitigated by format options)
4. **Path Dependency**: Users must maintain consistent folder structure

### Neutral

1. **External Dependency**: Requires users to generate Bible separately
2. **Folder Management**: Users need to organize vault with both Scripture and reading plans

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scripture folder missing | Medium | Warn user but continue; links work when files added |
| Book number mismatch | Low | Use standard Bible order (well-defined) |
| Folder name variations | Low | Document exact expected structure |
| Too many links (performance) | Low | Offer inline/hybrid formats to reduce link count |
| Path resolution issues | Low | Clear documentation with examples |

---

## Testing Strategy

### Unit Tests

1. **Book Number Lookup**:
   - All 66 books return correct numbers
   - Unknown books return 0 or None

2. **Link Generation**:
   - Single chapter generates one link
   - Chapter range generates multiple links
   - Correct folder and file paths

3. **Format Styles**:
   - Expanded format: One link per line
   - Inline format: Compact with chapter numbers
   - Hybrid format: Range header + bullet list

4. **Path Normalization**:
   - Windows backslashes converted to forward slashes
   - Trailing slashes removed
   - Relative paths preserved

### Integration Tests

1. **Full Plan Generation**:
   - 365-day plan with vault-bible option
   - Verify all links use correct format
   - Check frontmatter scripture_links field

2. **Multiple Formats**:
   - Generate with each format style
   - Verify correct markdown output

### Test Fixtures

Create test data:
```
tests/fixtures/
  └── test-scripture/
      ├── 01 - Genesis/
      │   ├── Genesis 1.md
      │   └── Genesis 2.md
      └── 40 - Matthew/
          └── Matthew 1.md
```

---

## Documentation Updates

### README.md

Add section:
```markdown
### Linking to Your Bible Vault

If you've generated Bible content using [BibleGateway-to-Obsidian](https://github.com/selfire1/BibleGateway-to-Obsidian),
you can automatically link your reading plan to Scripture files:

bash
# Single translation
bible-study-planner generate \
  --start-date 2025-01-01 \
  --scope complete \
  --vault-bible "Scripture"

# Multiple translations (specify which one)
bible-study-planner generate \
  --start-date 2025-01-01 \
  --scope complete \
  --vault-bible "Bible/ESV"


This generates clickable links like:
- **[[Bible/ESV/01 - Genesis/Genesis 1|Genesis 1]]**
- **[[Bible/ESV/01 - Genesis/Genesis 2|Genesis 2]]**

**Multiple Translation Support:**

If you maintain multiple Bible translations, organize them in subfolders:
```
Bible/
  ├── ESV/
  ├── NIV/
  └── WEB/
```

Then specify the translation in your command: `--vault-bible "Bible/ESV"`

**Link Formats:**
- `--vault-bible-format expanded` (default): One link per line
- `--vault-bible-format inline`: Compact with chapter numbers
- `--vault-bible-format hybrid`: Range header with bullet list

**Requirements:**
- Bible content generated by BibleGateway-to-Obsidian
- Standard folder structure: `{path}/{number} - {BookName}/{BookName} {chapter}.md`
```

### User Guide

Create detailed guide covering:
- How to generate Bible with BibleGateway-to-Obsidian
- Setting up folder structure
- Choosing link format
- Troubleshooting path issues
- Dataview query examples

---

## Success Metrics

1. **Functionality**: Links resolve correctly in Obsidian for all 66 books
2. **Usability**: Clear error messages for missing Scripture folder
3. **Format Options**: All three format styles work correctly
4. **Performance**: No noticeable slowdown in generation time
5. **Adoption**: Positive user feedback on feature
6. **Reliability**: <5% of users report linking issues

---

## References

- [BibleGateway-to-Obsidian](https://github.com/selfire1/BibleGateway-to-Obsidian)
- [Obsidian Wikilinks](https://help.obsidian.md/Linking+notes+and+files/Internal+links)
- [Obsidian Dataview Plugin](https://blacksmithgu.github.io/obsidian-dataview/)
- [Bible Book Order (Standard)](https://en.wikipedia.org/wiki/Books_of_the_Bible)

---

## Approval

- [ ] Feature Specification Approved
- [ ] Implementation Plan Approved
- [ ] Documentation Requirements Approved
- [ ] Ready for Development

**Approved By**: _________________  
**Date**: _________________

---

## Changelog

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-12-02 | 1.0 | Initial ADR for BibleGateway-to-Obsidian linking | Development Team |
