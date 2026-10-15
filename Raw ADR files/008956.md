# ADR-004: JSON File Database Approach

## Status
Accepted

## Context

The DuperHeroes game requires persistent storage for:
- 50 superhero character definitions with detailed metadata
- Character attributes: names, powers, origins, trivia, difficulty levels
- Animal themes and emoji mappings for visual representation
- Hero inspiration sources for educational content
- Game difficulty balancing with easy/medium/hard categorization

Requirements for data storage include:
- Static hosting compatibility (no server-side database)
- Fast read access for game performance
- Version control friendly format for collaborative editing
- Simple data structure for easy maintenance and updates
- Offline functionality after initial load
- Small file size for quick loading

The character data is relatively stable with occasional additions but minimal real-time updates. The application is single-player with no need for user-generated content or real-time synchronization.

## Decision

We will use a single JSON file (`heroes.json`) as the primary data store for all character information, served as a static asset alongside the application.

The data structure includes:
- Flat array of hero objects for simple iteration
- Comprehensive metadata for each character
- Standardized field names for consistent access patterns
- Human-readable format for easy editing and review
- Embedded fallback data in application code for offline resilience

## Alternatives Considered

### Option 1: Traditional Relational Database (PostgreSQL/MySQL)
- **Description**: Server-hosted database with API endpoints for data access
- **Pros**: ACID compliance, complex queries, concurrent access, data integrity constraints
- **Cons**: Requires server infrastructure, conflicts with static hosting, unnecessary complexity for read-only data, hosting costs
- **Risk Level**: High

### Option 2: NoSQL Database (MongoDB/Firebase)
- **Description**: Cloud-hosted document database with JavaScript SDK
- **Pros**: Flexible schema, cloud scaling, real-time updates, modern development experience
- **Cons**: External service dependency, overkill for static data, potential costs, requires API keys
- **Risk Level**: Medium

### Option 3: CSV File Format
- **Description**: Comma-separated values file for character data
- **Pros**: Universal format, Excel compatibility, smaller file size, simple parsing
- **Cons**: No nested data support, poor readability for complex fields, limited data types, manual parsing required
- **Risk Level**: Low

### Option 4: Embedded JavaScript Data
- **Description**: Character data directly embedded in JavaScript code as objects/arrays
- **Pros**: No separate HTTP request, immediate availability, type safety
- **Cons**: Harder to edit, version control noise, large single file, no separation of concerns
- **Risk Level**: Low

### Option 5: Multiple JSON Files by Category
- **Description**: Separate JSON files for different character categories or difficulties
- **Pros**: Modular loading, smaller individual files, organized by category
- **Cons**: Multiple HTTP requests, complex loading logic, unnecessary complexity for 50 characters
- **Risk Level**: Low

### Option 6: YAML Format
- **Description**: YAML file for human-readable data definition
- **Pros**: More readable than JSON, supports comments, cleaner syntax
- **Cons**: Requires parsing library, less universal browser support, larger file size
- **Risk Level**: Medium

## Consequences

### Positive
- **Static hosting compatible**: Works perfectly with GitHub Pages and CDN deployment
- **Fast loading**: Single HTTP request loads all character data
- **Version control friendly**: Human-readable diffs for collaborative editing
- **Simple maintenance**: Direct file editing without database schemas or migrations
- **Offline capable**: Data cached in browser after first load
- **Universal compatibility**: Native JavaScript JSON parsing support
- **No external dependencies**: No database drivers or connection management
- **Cost effective**: No database hosting or API costs

### Negative
- **Scalability limitations**: Not suitable for large datasets or frequent updates
- **No query capabilities**: Must load entire dataset for any access
- **Memory usage**: All data loaded into browser memory simultaneously
- **Concurrent editing**: Risk of merge conflicts with simultaneous edits
- **No data validation**: No built-in schema enforcement or constraints
- **Limited relationships**: Difficult to model complex data relationships
- **Security**: No access control or data protection features

### Neutral
- **Performance**: Excellent for read operations, but no write optimization
- **Backup**: Version control serves as backup, but no point-in-time recovery
- **Data integrity**: Manual validation required, but simple data reduces error risk

## Implementation Notes

### File Structure
```json
{
  "heroes": [
    {
      "superhero_name": "Captain Canine",
      "real_name": "Steve Rover Rogers",
      "powers": "Super loyalty, frisbee shield mastery, patriotic tail wagging",
      "origin": "Golden retriever accidentally injected with Super Soldier Serum...",
      "trivia": "Uses a frisbee as his shield and can detect freedom from miles away",
      "animal_theme": "Dog",
      "hero_inspiration": "Captain America",
      "difficulty": "Easy"
    }
  ]
}
```

### Loading Strategy
- Primary: Fetch JSON file from static hosting
- Fallback: Embedded mock data for offline/error scenarios
- Caching: Browser automatically caches static JSON file
- Error handling: Graceful degradation to embedded data

### Data Management Workflow
1. Edit `heroes.json` directly in repository
2. Validate JSON syntax before committing
3. Test changes locally before production deployment
4. Use pull requests for collaborative review
5. Automatic deployment via GitHub Actions

### Performance Considerations
- File size monitoring (currently ~15KB for 50 characters)
- Gzip compression enabled via static hosting
- Minimize JSON file formatting for smaller size
- Consider lazy loading if dataset grows significantly

### Success Metrics
- JSON file load time under 500ms on 3G connections
- Zero data loading failures in production
- File size remains under 100KB
- Collaborative editing with minimal merge conflicts

### Future Migration Path
If the application grows beyond static requirements:
1. Maintain JSON file format compatibility
2. Add API layer while preserving existing data structure
3. Implement gradual migration with feature flags
4. Consider static site generators with build-time data processing

## References
- [JSON Specification](https://www.json.org/)
- [Fetch API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [Static Site Data Management Patterns](https://jamstack.org/generators/)