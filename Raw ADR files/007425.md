# ADR-014: GitHub Actions for Automated Deployment

## Status
Proposed

## Context
The CodeCompass project will maintain a GitHub Pages site for documentation, interactive examples, and a slideshow presentation. To ensure this site remains current with the latest project changes and to minimize manual maintenance effort, we need an automated deployment process. GitHub Actions provides an integrated solution for continuous integration and deployment that can automatically build and publish the GitHub Pages site when relevant changes are made to the repository.

## Decision
We will implement a GitHub Actions workflow for automated deployment that:

1. Triggers site builds and deployments based on specific events:
   - Pushes to the main branch that affect documentation files
   - Merges of pull requests that modify ADRs or other documentation
   - Creation of new releases or tags
   - Scheduled rebuilds for dependency updates (weekly)
   - Manual triggers for immediate deployment when needed

2. Performs pre-deployment validation:
   - Link checking to prevent broken internal and external links
   - HTML validation to ensure standards compliance
   - Accessibility checks (WCAG compliance)
   - Markdown linting for consistent formatting
   - Image optimization for performance

3. Builds the GitHub Pages site with specialized processing:
   - Jekyll/Next.js compilation for static site generation
   - CSS processing with PostCSS for browser compatibility
   - JavaScript bundling and minification
   - Dynamic conversion of ADRs to presentation slides
   - Generation of search indices for site search functionality

4. Implements safe deployment practices:
   - Preview deployments for pull requests
   - Atomic deployments to prevent partial updates
   - Deployment versioning for rollback capability
   - Cache management for optimized build times
   - Build status notifications to relevant team members

5. Includes post-deployment verification:
   - Automated testing of critical site functionality
   - Performance measurement against established baselines
   - Screenshot capture for visual regression testing
   - Sitemap generation and search engine notification

## Consequences
- **Positive**: Ensures the GitHub Pages site is always current with project documentation
- **Positive**: Reduces manual effort required for site maintenance
- **Positive**: Enforces quality standards through automated validation
- **Positive**: Provides consistent build and deployment processes
- **Positive**: Enables preview of changes before they reach production
- **Negative**: Adds complexity to the repository configuration
- **Negative**: Requires maintenance of the CI/CD workflow itself
- **Negative**: May increase repository action minutes usage

## Implementation Approach

The GitHub Actions workflow would be structured as follows:

1. **Workflow Configuration**:
   ```yaml
   name: Deploy GitHub Pages
   
   on:
     push:
       branches: [ main ]
       paths:
         - 'docs/**'
         - 'README.md'
         - '.github/workflows/deploy-pages.yml'
     pull_request:
       paths:
         - 'docs/**'
         - 'README.md'
     release:
       types: [ published ]
     schedule:
       - cron: '0 2 * * 0'  # Weekly on Sundays at 2AM
     workflow_dispatch:  # Manual trigger
   ```

2. **Build Job Structure**:
   ```yaml
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout repository
           uses: actions/checkout@v3
         
         # Validation steps here
     
     build:
       needs: validate
       runs-on: ubuntu-latest
       steps:
         - name: Checkout repository
           uses: actions/checkout@v3
           
         # Build steps here
     
     deploy:
       if: github.event_name != 'pull_request'
       needs: build
       runs-on: ubuntu-latest
       permissions:
         pages: write
       steps:
         # Deployment steps here
   ```

3. **Validation Process**:
   - Markdown linting with markdownlint
   - Link checking with lychee
   - Accessibility testing with pa11y
   - HTML validation with html-validate

4. **Build Process**:
   - Setup Node.js and Ruby environments
   - Install dependencies
   - Process and transform ADRs into presentation format
   - Generate search index
   - Build static site with Jekyll or Next.js
   - Optimize assets

5. **Deployment Process**:
   - Configure GitHub Pages deployment
   - Deploy to GitHub Pages
   - Cache dependencies for future builds
   - Notify team of deployment status

## Workflow Implementation Example

```yaml
name: Deploy GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - 'README.md'
      - '.github/workflows/deploy-pages.yml'
  pull_request:
    paths:
      - 'docs/**'
      - 'README.md'
  release:
    types: [ published ]
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sundays at 2AM
  workflow_dispatch:  # Manual trigger

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install validation dependencies
        run: npm install -g markdownlint-cli lychee pa11y-ci html-validate
        
      - name: Lint Markdown files
        run: markdownlint docs/**/*.md
        
      - name: Check for broken links
        run: lychee docs/**/*.md --exclude linkedin.com
        
      - name: Validate HTML
        if: false  # Enable after site is built
        run: html-validate docs/_site/**/*.html
        
      - name: Check accessibility
        if: false  # Enable after site is built
        run: pa11y-ci docs/_site/**/*.html

  build:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true
          
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: |
          cd docs
          bundle install
          npm install
          
      - name: Generate presentation slides
        run: node docs/scripts/generate-slides.js
        
      - name: Build site
        run: |
          cd docs
          bundle exec jekyll build
          
      - name: Optimize images
        run: |
          cd docs/_site
          find . -type f -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" | xargs -P 4 -I {} npx imagemin-cli {} --out-dir=.
          
      - name: Upload build artifact
        uses: actions/upload-pages-artifact@v1
        with:
          path: docs/_site

  deploy:
    if: github.event_name != 'pull_request'
    needs: build
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
        
      - name: Notify team
        if: success()
        run: |
          curl -X POST -H "Content-Type: application/json" \
          -d '{"text":"🚀 GitHub Pages deployment successful! Check it out at ${{ steps.deployment.outputs.page_url }}"}' \
          ${{ secrets.NOTIFICATION_WEBHOOK_URL || 'https://example.com' }}
```

## Initial Implementation Tasks

1. Create basic GitHub Actions workflow file for GitHub Pages deployment
2. Set up validation tools for Markdown and link checking
3. Configure Jekyll or Next.js build process in the workflow
4. Implement automated slide generation from ADR content
5. Set up deployment process with appropriate permissions
6. Add notification system for deployment status
7. Create documentation for manual workflow triggering
8. Configure caching for optimized build performance 