# ADR-012: GitHub Pages Slideshow for Project Explanation

## Status
Proposed

## Context
The CodeCompass project introduces innovative approaches to codebase management using AI, but these concepts can be complex and difficult to grasp through traditional documentation alone. To improve onboarding, increase project visibility, and effectively communicate our architecture decisions to a wider audience, we need a more engaging and visual presentation format.

GitHub Pages offers a free, integrated hosting solution that allows us to create interactive web content directly from our repository. By leveraging this platform, we can create a compelling slideshow presentation that explains the project's concepts, architecture, and benefits in a more accessible format.

## Decision
We will implement a comprehensive slideshow deployed on GitHub Pages that:

1. Provides a visual overview of the CodeCompass project, explaining:
   - The problem space and motivation
   - Core architectural components (semantic chunking, differential updates, etc.)
   - The various tools and environments we support
   - Implementation approaches and examples
   - Benchmark results and performance metrics

2. Uses a modern, responsive slideshow framework such as Reveal.js that:
   - Works well on both desktop and mobile devices
   - Supports code highlighting for technical examples
   - Allows for interactive elements and animations
   - Enables easy navigation between slides

3. Incorporates visual elements to enhance understanding:
   - Diagrams of the architectural components
   - Workflow illustrations
   - Comparison charts for different AI environments
   - Visual representations of benchmarking results

4. Includes interactive demonstrations where appropriate:
   - Before/after examples of semantic chunking
   - Cost savings calculations using the caching system
   - Interactive examples of the hybrid architecture decision flow

5. Is automatically generated and deployed through GitHub Actions when:
   - ADRs are updated or added
   - The main README is modified
   - Release milestones are reached

## Consequences
- **Positive**: Provides a more engaging and accessible introduction to the project
- **Positive**: Helps potential users and contributors quickly understand the project's value
- **Positive**: Serves as a presentation tool for demonstrations and meetups
- **Positive**: Improves project visibility and adoption through shareable content
- **Positive**: Creates a unified visual language for explaining complex concepts
- **Negative**: Requires ongoing maintenance to keep in sync with project changes
- **Negative**: Adds complexity to the CI/CD pipeline for deployment
- **Negative**: Creation of quality visual assets requires additional design resources

## Implementation Approach

The GitHub Pages slideshow would be structured as follows:

1. **Technical Implementation**:
   - Repository: Stored in the `/docs/slideshow` directory
   - Framework: Reveal.js for responsive slide presentation
   - Build Process: Jekyll or Next.js for content generation
   - Deployment: GitHub Actions workflow for automatic deployment

2. **Content Organization**:
   - Introduction: Project overview and problem statement
   - Architecture: Visual explanation of key architectural decisions
   - Components: Detailed slides on each core component
   - Benchmarks: Visual representation of performance metrics
   - Getting Started: Quick-start guide with visual aids
   - Roadmap: Timeline visualization of upcoming features

3. **Visual Design Elements**:
   - Consistent color scheme matching project branding
   - Custom diagrams explaining technical concepts
   - Animated transitions to illustrate state changes
   - Code snippets with syntax highlighting
   - Interactive elements for exploring different configurations

4. **Automation and Integration**:
   - Automated generation of slides from ADR content
   - Integration with GitHub project metrics
   - Automatic versioning to match repository releases
   - QR code generation for printed materials

## Example Slide Deck Outline

```
1. Introduction
   - Title: "CodeCompass: AI-Powered Codebase Management"
   - Problem: "Understanding large codebases is challenging"
   - Solution: "Claude 3.7 Sonnet + intelligent tooling"

2. Core Architecture
   - Visual diagram of the complete system
   - Key components and their relationships
   - Data flow visualization

3. Semantic Chunking (ADR-001)
   - Visualization of chunking process
   - Before/after examples
   - Performance metrics

4. Differential Updates (ADR-002)
   - Animation of update process
   - Token savings visualization
   - Integration with CI/CD

5. Hybrid Architecture (ADR-003)
   - Decision flow diagram
   - Cost comparison charts
   - Example scenarios

6. Caching System (ADR-004)
   - Cache hit/miss visualization
   - Cost savings calculator
   - Implementation examples

7. Development Environment Comparison (ADR-010)
   - Interactive comparison of different environments
   - Feature matrix visualization
   - Performance benchmark charts

8. Getting Started
   - Installation process visualization
   - First steps walkthrough
   - Common usage patterns

9. Community & Roadmap
   - Timeline visualization
   - Contribution opportunities
   - Future vision
```

## Initial Implementation Plan

1. Create the basic slideshow structure using Reveal.js
2. Develop templates for different slide types (concept explanation, code examples, etc.)
3. Create initial content for core architectural concepts
4. Design key diagrams and visual elements
5. Implement automation for keeping slides in sync with documentation
6. Set up GitHub Actions workflow for automatic deployment
7. Create guidelines for adding/updating slides as the project evolves 