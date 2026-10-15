# ADR-002: Documentation as Code with JSDoc and Mermaid

## Status
Accepted

## Context
Documentation often becomes outdated as code evolves. We need a way to:
- Keep documentation synchronized with code by making sure it is reviewed and evolved
as code changes
- Generate visual diagrams from code to provide a map of the architecture, flow, and

data structures
- Provide appropriate developer documentation for the code itself

## Decision
We will embed documentation directly in code using:
- JSDoc comments for API documentation
- Mermaid diagrams in JSDoc for visual representations
- Markdown files in the repository for high-level docs
- ADRs for architectural decisions

## Implementation

### JSDoc with Mermaid
` ``javascript
/**
* @fileoverview Die class for simulating dice rolls
* @mermaid
* classDiagram
* class Die {
* -sides: number
* -currentValue: number
* +constructor(sides: number)
* +roll(): number
* +getValue(): number
* }
*/
` ``

### File Structure
` ``
src/
├── domain/
│ ├── Die.js # Single die implementation
│ ├── DiceSet.js # Collection of dice
│ └── DiceNotation.js # Parse dice notation strings
├── application/
│ ├── DiceRoller.js # Main rolling logic
│ └── Statistics.js # Track roll history
└── presentation/
├── renderers/ # Different display strategies
└── cli/ # Command-line interface
` ``

## Consequences

### Positive
- Documentation stays close to code
- Changes are reviewed together
- Visual diagrams from code
- Single source of truth
- Can eventually be used to generate documentation website(s)

### Negative
- Requires discipline to maintain
- JSDoc can make files longer and may obscure code
- Learning curve for Mermaid syntax and concern that maybe it isn't the correct thing
to adopt
- Need tooling for generation

## Tools and Workflow
1. Write JSDoc comments with all public APIs
2. Include @mermaid tags for diagrams
3. Review documentation with code in PRs (future)
4. Run documentation generator (future)
5. Deploy documentation to GitHub Pages or other (future)

## Examples to Follow
- Every class should have a @class tag
- Every public method needs @param and @returns
- Complex logic should have @example
- State machines use @mermaid stateDiagram
- Class relationships use @mermaid classDiagram