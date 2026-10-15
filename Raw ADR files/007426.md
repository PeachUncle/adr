# ADR-016: Local Development Environment for GitHub Pages

## Status
Proposed

## Context
The CodeCompass project uses GitHub Pages for documentation, slideshow presentations, and interactive examples as outlined in previous ADRs (ADR-012, ADR-013, and ADR-014). While the automated deployment workflow handles production deployment, contributors need a way to preview and test changes locally before committing them. This helps ensure high-quality contributions and reduces the number of revisions needed during the review process.

A standardized local development environment ensures that all contributors can:
1. Preview changes to documentation, slides, and interactive components
2. Test for visual regressions or formatting issues
3. Verify interactive functionality works as expected
4. Develop new content efficiently with live-reloading
5. Ensure cross-browser and responsive design compatibility

Without a defined local development approach, contributors might use inconsistent methods, leading to unexpected issues in production or inefficient development workflows.

## Decision
We will implement a local development environment for GitHub Pages that:

1. Provides standardized setup scripts that:
   - Install all necessary dependencies (Ruby, Jekyll, Node.js, etc.)
   - Configure the development environment with proper versions
   - Set up local configuration files
   - Initialize required services and tools

2. Creates a set of development workflow scripts that:
   - Start a local development server with live reload capability
   - Watch for changes and rebuild content as needed
   - Generate test data or fixtures when required
   - Emulate GitHub Pages build processes locally
   - Validate content against defined standards
   - Run performance and accessibility checks

3. Implements a comprehensive documentation strategy including:
   - Clear installation instructions for different operating systems
   - Troubleshooting guides for common issues
   - Development workflow documentation
   - Testing procedures for various site components
   - Examples of common development tasks

4. Offers optional Docker-based setup that:
   - Provides a containerized development environment
   - Eliminates dependency conflicts with other projects
   - Ensures consistent behavior across all development machines
   - Simplifies onboarding for new contributors

5. Includes local environment configuration for:
   - Disabling production analytics
   - Using mock data for development
   - Flagging the environment as development
   - Supporting debugging tools and utilities

## Consequences
- **Positive**: Enables contributors to preview changes locally before submission
- **Positive**: Reduces the number of revisions needed during review
- **Positive**: Improves development efficiency with live reloading
- **Positive**: Ensures consistent environment across all contributors
- **Positive**: Makes it easier for new contributors to get started
- **Negative**: Requires maintenance of additional scripts and configuration
- **Negative**: Increases initial setup time for contributors
- **Negative**: May require updates when GitHub Pages dependencies change

## Implementation Approach

The local development environment would be structured as follows:

1. **Directory Structure**:
   ```
   /scripts/
     /setup/
       setup-linux.sh
       setup-macos.sh
       setup-windows.ps1
       check-dependencies.sh
     /dev/
       start-local-server.sh
       build-site.sh
       lint-content.sh
       validate-links.sh
     /docker/
       Dockerfile
       docker-compose.yml
   /docs/
     /development/
       CONTRIBUTING.md
       LOCAL_DEVELOPMENT.md
       TROUBLESHOOTING.md
       Docker.md
   ```

2. **Setup Scripts**:
   The setup scripts will automate the installation and configuration of all required dependencies:

   ```bash
   #!/bin/bash
   # setup-macos.sh
   
   echo "Setting up CodeCompass GitHub Pages development environment..."
   
   # Check for Homebrew and install if missing
   if ! command -v brew &> /dev/null; then
     echo "Installing Homebrew..."
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   fi
   
   # Install Ruby
   echo "Installing Ruby..."
   brew install ruby@3.2
   
   # Add Ruby to path
   echo 'export PATH="/usr/local/opt/ruby@3.2/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   
   # Install Jekyll and Bundler
   echo "Installing Jekyll and Bundler..."
   gem install jekyll bundler
   
   # Install Node.js and npm
   echo "Installing Node.js and npm..."
   brew install node
   
   # Navigate to project directory and install dependencies
   cd "$(dirname "$0")/../../"
   echo "Installing project dependencies..."
   cd docs
   bundle install
   npm install
   
   echo "Setup complete! You can now run the local development server with:"
   echo "scripts/dev/start-local-server.sh"
   ```

3. **Development Workflow Scripts**:
   These scripts will streamline the development process:

   ```bash
   #!/bin/bash
   # start-local-server.sh
   
   echo "Starting local development server..."
   
   # Navigate to project directory
   cd "$(dirname "$0")/../../"
   
   # Set development environment
   export JEKYLL_ENV=development
   
   # Start local server with live reload
   cd docs
   bundle exec jekyll serve --livereload --incremental
   ```

4. **Docker Configuration**:
   For those who prefer containerized development:

   ```dockerfile
   # Dockerfile
   FROM ruby:3.2-alpine
   
   # Install dependencies
   RUN apk add --no-cache build-base gcc cmake git nodejs npm
   
   # Set working directory
   WORKDIR /app
   
   # Install Jekyll and Bundler
   RUN gem install jekyll bundler
   
   # Copy project files
   COPY . .
   
   # Install dependencies
   RUN cd docs && bundle install && npm install
   
   # Expose port for Jekyll
   EXPOSE 4000
   
   # Command to start the server
   CMD ["sh", "-c", "cd docs && bundle exec jekyll serve --host=0.0.0.0 --livereload"]
   ```

5. **Development Documentation**:
   Clear documentation in the LOCAL_DEVELOPMENT.md file:

   ```markdown
   # Local Development
   
   This guide will help you set up a local development environment for the CodeCompass GitHub Pages.
   
   ## Prerequisites
   
   - Git
   - Basic familiarity with command line
   - Either:
     - Direct installation: Ruby, Node.js
     - Docker and Docker Compose (for containerized setup)
   
   ## Option 1: Direct Installation
   
   ### Automated Setup
   
   We provide scripts to automate the setup process:
   
   - Linux: `scripts/setup/setup-linux.sh`
   - macOS: `scripts/setup/setup-macos.sh`
   - Windows: `scripts/setup/setup-windows.ps1`
   
   Run the appropriate script for your operating system.
   
   ### Manual Setup
   
   If you prefer to set up manually, follow these steps:
   
   1. Install Ruby 3.2
   2. Install Jekyll and Bundler: `gem install jekyll bundler`
   3. Install Node.js and npm
   4. Navigate to the docs directory: `cd docs`
   5. Install dependencies: `bundle install && npm install`
   
   ## Option 2: Docker Setup
   
   1. Install Docker and Docker Compose
   2. Run: `docker-compose -f scripts/docker/docker-compose.yml up`
   
   ## Development Workflow
   
   - Start the local server: `scripts/dev/start-local-server.sh`
   - The site will be available at: http://localhost:4000
   - Changes to source files will automatically trigger a rebuild
   
   ## Testing Your Changes
   
   - Validate links: `scripts/dev/validate-links.sh`
   - Run linting: `scripts/dev/lint-content.sh`
   - Build the site: `scripts/dev/build-site.sh`
   
   ## Common Issues
   
   See TROUBLESHOOTING.md for solutions to common issues.
   ```

## Initial Implementation Tasks

1. Create basic directory structure for scripts and documentation
2. Develop setup scripts for major operating systems
3. Implement development workflow scripts
4. Create Docker configuration files
5. Write comprehensive documentation
6. Test setup on different operating systems
7. Add script references to main project README
8. Create troubleshooting guide based on initial testing feedback 