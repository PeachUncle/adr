---
sidebar_position: 1
title: ADR-018 Docusaurus Migration Plan
---

# ADR-018: Docusaurus Migration Plan

## Status
Proposed

## Context
Our current documentation site is built with Jekyll, which has presented several challenges:

1. Template processing issues in the simple static server
2. Complex setup requirements for local development
3. Limited interactive capabilities
4. Difficulty in maintaining and extending the documentation

Additionally, we want to create two interactive demos:
1. A Claude 3.7 Sonnet demo based on the original blog post about using Claude to understand large codebases
2. A CodeCompass demo with LiteLLM integration to show how to use multiple LLM models with a consistent interface

Docusaurus provides a modern documentation framework with React components, MDX support, and excellent search capabilities, making it ideal for our needs.

## Decision
We will migrate from Jekyll to Docusaurus for the following reasons:

1. **Better developer experience**:
   - Hot reloading during development
   - Simpler local development setup
   - Strong TypeScript support
   - React component integration

2. **Improved documentation features**:
   - Built-in versioning
   - Powerful search functionality
   - Better navigation and sidebar customization
   - Support for MDX (Markdown + JSX)

3. **Interactive capabilities**:
   - Ability to create interactive demos with React
   - Support for embedding live code examples
   - Integration with visualization libraries

4. **Better deployment options**:
   - Simplified GitHub Pages deployment
   - Static site generation with proper template processing
   - Consistent rendering between development and production

## Implementation Plan

### Phase 1: Project Setup and Cleanup
1. Initialize new Docusaurus project
2. Create directory structure for documentation
3. Remove unnecessary Jekyll files
4. Configure Docusaurus for our specific needs

### Phase 2: Content Migration
1. Migrate existing ADRs to Docusaurus format
2. Convert important content pages
3. Migrate and organize static assets
4. Set up Mermaid.js for diagrams

### Phase 3: Claude 3.7 Sonnet Demo
1. Create step-by-step tutorial for working with large codebases
2. Implement semantic chunking examples
3. Add interactive code examples
4. Document best practices

### Phase 4: CodeCompass with LiteLLM Demo
1. Implement a working CLI version of CodeCompass
2. Add LiteLLM integration
3. Create interactive web demo
4. Document usage with different models

### Phase 5: Deployment
1. Set up GitHub Actions for automatic deployment
2. Configure GitHub Pages
3. Implement preview deployments for pull requests
4. Document the deployment process

## Consequences
- **Positive**: Improved documentation experience for users
- **Positive**: Better developer experience for contributors
- **Positive**: Enhanced interactive capabilities
- **Positive**: Simplified maintenance and extensibility
- **Negative**: Requires migrating existing content
- **Negative**: Learning curve for contributors unfamiliar with React/Docusaurus

## Timeline
- Project Setup and Cleanup: 1-2 days
- Content Migration: 2-3 days
- Claude 3.7 Sonnet Demo: 2-3 days
- CodeCompass with LiteLLM Demo: 3-4 days
- Deployment: 1-2 days

Total estimated timeline: 9-14 days 