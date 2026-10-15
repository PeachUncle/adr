# ADR-007: Google Doc Hero Fetcher Integration

## Status
Accepted

## Context
The DuperHeroes project originally used a static heroes.json file with a limited number (~20) of animal superhero characters. As the character roster grew to 190+ characters, manually maintaining the JSON file became cumbersome and error-prone. Content creators needed a more user-friendly way to add and update hero data without requiring technical knowledge of JSON formatting.

The team needed a solution that would:
- Allow non-technical content creators to easily add/edit heroes
- Maintain the static site architecture and GitHub Pages deployment
- Provide reliable fallback mechanisms for build failures
- Integrate seamlessly with existing CI/CD pipeline
- Support collaborative editing and version control of hero content

## Decision
Implement a Google Doc integration system that automatically fetches hero data during build time and converts it to the required JSON format.

**Core Components:**
1. **Google Doc Source**: Shared Google Document containing structured hero data
2. **Fetch Script**: Node.js utility (`scripts/fetch-heroes.js`) that parses Google Doc export
3. **Build Integration**: npm scripts and GitHub Actions workflow integration
4. **Fallback Strategy**: Preserve existing heroes.json if fetch fails

## Alternatives Considered

### Option 1: Content Management System (CMS)
- **Description**: Use a headless CMS like Strapi, Contentful, or Sanity
- **Pros**: 
  - Professional content management interface
  - Built-in validation and relationships
  - API-first design
  - Version history and collaboration features
- **Cons**: 
  - Adds complexity and hosting costs
  - Requires API key management
  - Overkill for simple character data
  - Introduces external dependency beyond GitHub
- **Risk Level**: Medium

### Option 2: GitHub-based Editing (Web Interface)
- **Description**: Use GitHub's web interface to edit JSON files directly
- **Pros**: 
  - No external dependencies
  - Built-in version control
  - Free with existing GitHub workflow
- **Cons**: 
  - Requires JSON knowledge from content creators
  - Error-prone manual editing
  - No real-time collaboration
  - Intimidating interface for non-technical users
- **Risk Level**: Low

### Option 3: Google Sheets Integration
- **Description**: Use Google Sheets with CSV export parsing
- **Pros**: 
  - Familiar spreadsheet interface
  - Good for structured data entry
  - Supports formulas and validation
- **Cons**: 
  - Limited rich text formatting
  - Harder to handle multi-line content
  - CSV parsing complexity
  - Less natural for narrative content
- **Risk Level**: Medium

### Option 4: Google Doc Integration (Chosen)
- **Description**: Parse hero data from a shared Google Document
- **Pros**: 
  - Familiar word processor interface
  - Supports rich text and formatting
  - Real-time collaboration features
  - Free with Google account
  - Natural for narrative content like character descriptions
  - Can handle both structured and unstructured content
- **Cons**: 
  - Requires parsing of unstructured text
  - Dependent on Google's export format stability
  - Limited data validation at source
- **Risk Level**: Low

## Consequences

### Positive
- Content creators can easily add/edit heroes without technical knowledge
- Real-time collaboration on hero content through Google Docs
- Maintains static site architecture and fast deployment
- Automatic data updates during build process
- Robust error handling and fallback mechanisms
- No additional hosting costs or API dependencies
- Natural format for rich character descriptions and lore

### Negative
- Requires Node.js and npm for local development
- Adds parsing complexity compared to direct JSON editing
- Dependent on Google Docs export format consistency
- Slightly longer build times due to external fetch
- Content creators must follow specific formatting conventions

### Neutral
- Character count increased from ~20 to 190+ heroes
- Build process now includes data fetching step
- Documentation updated to reflect new workflow
- Backup files automatically created during updates

## Implementation Notes

### Technical Implementation
- **Parser**: Flexible regex-based parsing supporting multiple format variations
- **Error Handling**: Comprehensive error catching with detailed logging
- **Validation**: Character data validation and required field checking
- **Backup Strategy**: Automatic backup creation before updates
- **npm Scripts**: 
  - `npm run fetch-heroes`: Manual data fetching
  - `npm run build:heroes`: Integrated build step
  - `npm run build`: Full build including hero data

### Content Format Conventions
- Numbered character entries (1., 2., etc.)
- Structured bullet points for character fields
- Support for both emoji and text-based animal themes
- Flexible field naming (powers/abilities, origin/story, etc.)
- Automatic difficulty level normalization

### Migration Strategy
- Existing heroes.json preserved as fallback
- Gradual rollout with manual verification
- Character data validated against existing game mechanics
- Emoji mapping maintained for animal theme extraction

### Monitoring and Success Metrics
- Build success rate with hero fetching enabled
- Character count verification in production
- Game functionality validation with new data
- Content creator feedback on editing experience

## References
- [Google Docs Text Export API](https://developers.google.com/docs/api/reference/rest/v1/documents/get)
- [GitHub Actions Node.js Setup](https://github.com/actions/setup-node)
- [Original Issue #1](https://github.com/ghelleks/duperheroes/issues/1)
- [Feature Branch: feature/google-doc-hero-fetcher](https://github.com/ghelleks/duperheroes/tree/feature/google-doc-hero-fetcher)