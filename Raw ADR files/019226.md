# ADR-0006: CLI Command Structure and User Interaction Patterns

**Status**: Accepted
**Date**: 2025-08-05
**Context**: Travel Memory Journal needs intuitive CLI commands that enable quick memory capture and retrieval while maintaining excellent user experience for both novice and experienced users.

## Problem Statement
How should we structure CLI commands and user interactions to maximize usability, minimize learning curve, and ensure users can add memories in <30 seconds and find their first memory within 5 minutes?

## Decision Drivers
- **Business Requirements**: First memory added in <5 minutes, memory addition in <30 seconds
- **Technical Constraints**: Typer framework, local-only processing, travel domain focus
- **Team Constraints**: Simple implementation, comprehensive help system
- **Non-Functional Requirements**: Intuitive commands, clear feedback, error guidance

## Options Considered

### Option 1: Verb-Noun Command Structure (Recommended)
**Pros**:
- Intuitive and matches common CLI patterns (git, docker)
- Self-documenting command names
- Easy to extend with new functionality
- Natural grouping of related operations
- Follows Unix philosophy of small, composable tools

**Cons**:
- Slightly more verbose than single-word commands
- Requires users to learn command patterns

**Implementation Effort**: S (Small)
**Operational Complexity**: Low

### Option 2: Single-Word Commands
**Pros**:
- Shortest possible commands for speed
- Minimal typing required

**Cons**:
- Commands become unclear as functionality grows
- Hard to maintain semantic clarity
- Doesn't scale well with feature additions

**Why Not Chosen**: Sacrifices clarity and extensibility for minimal typing savings

### Option 3: Git-Style Subcommands
**Pros**:
- Very familiar pattern for developers
- Excellent for complex functionality

**Cons**:
- May be intimidating for non-technical users
- Overkill for our relatively simple command set

**Why Not Chosen**: Added complexity doesn't match our user base and functionality scope

## Decision
We will use **Verb-Noun Command Structure** with clear, travel-focused terminology.

**Rationale**: This structure provides the best balance of intuitiveness, extensibility, and clarity for our travel memory use case. Commands read like natural language and are self-documenting.

## Consequences
**Positive**:
- Commands are self-explanatory and discoverable
- Easy to add new functionality following established patterns
- Excellent help system integration with Typer
- Natural mental model for users (action + object)
- Supports both quick usage and exploratory learning

**Negative**:
- Slightly more typing than single-word commands
- Users must learn command structure rather than memorizing individual commands

**Implementation Notes**:
- Use clear, travel-focused terminology throughout
- Provide rich help text and examples for each command
- Include progress indicators for longer operations
- Use consistent output formatting across all commands
- Implement smart defaults to minimize required parameters

## Command Structure

### Core Commands

#### `add-memory` - Capture New Travel Memory
```bash
# Interactive mode (recommended for new users)
travel-journal add-memory

# Quick mode (for experienced users)
travel-journal add-memory --location "Paris, France" --date "2024-07-15" --description "Amazing day at the Louvre"

# With explicit tags
travel-journal add-memory -l "Tokyo" -d "2024-06-01" --description "Incredible sushi at Tsukiji" --tags "food,sushi,market"
```

**Design Rationale**: Most important command gets clearest name and multiple usage patterns

#### `list-memories` - Browse Memory Collection
```bash
# Show all memories (chronological)
travel-journal list-memories

# Filter by location
travel-journal list-memories --location "Japan"

# Filter by date range
travel-journal list-memories --since "2024-01-01" --until "2024-12-31"

# Filter by tags
travel-journal list-memories --tags "food,culture"
```

**Design Rationale**: Clear browsing with flexible filtering options

#### `search-memories` - Find Specific Memories
```bash
# Text search across descriptions
travel-journal search-memories "temple"

# Combined search with filters
travel-journal search-memories "delicious" --location "Italy" --tags "food"
```

**Design Rationale**: Dedicated search command for complex queries

#### `show-memory` - Display Memory Details
```bash
# Show specific memory by ID
travel-journal show-memory abc123

# Show with full tags and metadata
travel-journal show-memory abc123 --verbose
```

#### `process-memory` - Extract Tags from Description
```bash
# Process specific memory
travel-journal process-memory abc123

# Process all untagged memories
travel-journal process-memory --all-untagged
```

#### `top-memory` - Find Most Tagged Memory
```bash
travel-journal top-memory
```

### User Experience Design

#### Interactive Mode
- **Purpose**: Guide new users through memory creation
- **Features**: Step-by-step prompts, validation, examples
- **Triggered**: When required parameters missing

```
🌍 Let's add a new travel memory!

📍 Where were you? (e.g., "Paris, France"): _
📅 What date was this? (YYYY-MM-DD or "today"): _
📝 Tell me about this memory: _
🏷️  Want to add tags manually? (y/N): _

✨ Processing your memory for automatic tags...
🎯 Found tags: museum, art, culture
💾 Memory saved successfully!
```

#### Quick Mode
- **Purpose**: Fast memory capture for experienced users  
- **Features**: All parameters via flags, minimal prompts
- **Triggered**: When all required parameters provided

```bash
travel-journal add-memory -l "Rome" -d "today" --description "Incredible pasta at small trattoria near Pantheon"
✨ Processing tags... Found: food, italian, restaurant
💾 Memory saved! ID: def456
```

#### Progress Indicators
- Show progress for operations >2 seconds
- Clear feedback for all state changes
- Consistent emoji use for visual recognition

#### Error Handling UX
```
❌ Error: Date format not recognized: "yesterday"
💡 Try: 
   - "2024-07-15" (YYYY-MM-DD)
   - "today" 
   - "2024-07-15"
```

### Help System Design

#### Built-in Examples
```bash
travel-journal add-memory --help

Usage: travel-journal add-memory [OPTIONS]

Add a new travel memory to your collection.

Examples:
  # Interactive mode (great for beginners)
  travel-journal add-memory
  
  # Quick capture
  travel-journal add-memory -l "Tokyo" -d "today" --description "Amazing ramen in Shibuya"
  
  # With manual tags
  travel-journal add-memory -l "Barcelona" -d "2024-06-15" --description "Gaudi architecture tour" --tags "architecture,culture,walking"

Options:
  -l, --location TEXT     Where this memory happened
  -d, --date TEXT        When this happened (YYYY-MM-DD or "today")
  --description TEXT      Describe your memory
  --tags TEXT            Manual tags (comma-separated)
  --help                 Show this message and exit.
```

#### Command Discovery
```bash
travel-journal --help

🌍 Travel Memory Journal - Capture and relive your adventures

Commands:
  add-memory      📝 Add a new travel memory
  list-memories   📋 Browse your memory collection  
  search-memories 🔍 Search through your memories
  show-memory     👁️  Display detailed memory information
  process-memory  🏷️  Extract tags from memory descriptions
  top-memory     🏆 Find your memory with the most tags

Get started:
  travel-journal add-memory    # Add your first memory!

For detailed help on any command:
  travel-journal [COMMAND] --help
```

### Output Formatting Standards

#### Consistent Visual Language
- ✅ Success operations
- ❌ Errors
- 💡 Tips and suggestions
- 🔄 Processing operations
- 📍 Location references
- 📅 Date references
- 🏷️ Tag references

#### Table Formatting for Lists
```
ID      Date        Location           Tags               Description
───────────────────────────────────────────────────────────────────
abc123  2024-07-15  Paris, France     museum, art        Amazing day at the Louvre...
def456  2024-07-14  Rome, Italy       food, italian      Incredible pasta at small...
```

## Implementation Guidelines

### Parameter Naming Conventions
- Use full words over abbreviations where reasonable
- Provide short aliases for frequently used options
- Maintain consistency across all commands

### Validation and Feedback
- Validate inputs immediately with clear error messages
- Provide suggestions for common mistakes
- Show what the system understood/processed

### Performance Considerations
- Show progress for operations >2 seconds
- Provide early feedback while processing continues
- Use caching to make repeated operations fast

### Accessibility
- Support screen readers with clear text output
- Avoid relying solely on color for information
- Provide both brief and verbose output modes