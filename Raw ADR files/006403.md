# ADR-024: CI/CD Pipeline Design

## Status
Proposed

## Date
2025-03-02

## Context
Our Aronim Bookstore application requires a robust, automated, and reliable Continuous Integration and Continuous Deployment (CI/CD) pipeline to streamline the development workflow, ensure code quality, and enable frequent, reliable deployments. We need a CI/CD pipeline design that:

- Automates build, test, and deployment processes
- Ensures consistent quality checks across all code changes
- Supports our development workflow and branching strategy
- Integrates with our containerization approach
- Enables rapid feedback to developers
- Supports different deployment environments (dev, test, staging, production)
- Implements proper security checks and compliance validations
- Provides visibility into the pipeline status and history
- Scales with our growing codebase and team
- Aligns with our overall architecture and technology choices

Without a well-defined CI/CD pipeline design, we risk inconsistent builds, unreliable deployments, quality issues reaching production, and inefficient development workflows.

## Decision
We will implement a comprehensive CI/CD pipeline using **GitHub Actions** with the following components and stages:

### 1. Pipeline Stages
- **Code Checkout**: Retrieve source code from the repository
- **Validation**: Lint code and validate basic structure
- **Build**: Compile code and generate artifacts
- **Unit Tests**: Run fast, isolated tests
- **Code Analysis**: Perform static code analysis and security scanning
- **Integration Tests**: Run tests involving multiple components
- **Container Build**: Create and scan Docker images
- **Artifact Publication**: Publish build artifacts and containers
- **Deployment**: Deploy to target environments
- **Acceptance Tests**: Run post-deployment validation
- **Promotion**: Promote artifacts between environments

### 2. Environment Strategy
- **Development**: Automatic deployment on main branch changes
- **Testing**: Automatic deployment after successful development deployment
- **Staging**: Manual approval before deployment
- **Production**: Manual approval with additional validation

### 3. Quality Gates
- Code coverage thresholds
- Security vulnerability scanning
- Performance benchmarks
- Compliance checks
- Code quality metrics

### 4. Security Measures
- Secret management using GitHub Secrets
- Dependency vulnerability scanning
- Container image scanning
- Infrastructure as Code validation
- Least privilege principle for deployments

### 5. Workflow Design
- Feature branch workflows with pull requests
- Environment-specific pipelines
- Reusable workflow components
- Parallel execution where possible
- Appropriate timeouts and retry strategies

## Implementation Approach

1. **Workflow Configuration**
   - Create GitHub Actions workflow files for each pipeline type
   - Implement reusable actions for common tasks
   - Configure environment-specific variables and secrets
   - Set up appropriate triggers for different workflows

2. **Build and Test Automation**
   - Configure Gradle build actions
   - Set up test runners with proper caching
   - Implement test result publishing
   - Configure code coverage reporting

3. **Deployment Automation**
   - Create deployment workflows for each environment
   - Implement infrastructure as code validation
   - Configure container deployment actions
   - Set up appropriate approval gates

4. **Monitoring and Notification**
   - Configure pipeline status notifications
   - Set up deployment tracking
   - Implement status badges and dashboards
   - Create alerting for pipeline failures

5. **Documentation and Standards**
   - Document pipeline architecture and workflows
   - Create standards for workflow files
   - Implement templates for common workflows
   - Provide developer guidelines for CI/CD

## Consequences

### Positive
- Faster feedback on code quality and build issues
- Consistent and reliable deployment process
- Reduced manual errors in the deployment process
- Better visibility into the deployment pipeline
- Improved code quality through automated checks
- More frequent and reliable releases
- Enhanced security through automated scanning
- Better developer experience and productivity
- Easier onboarding for new team members
- Support for scaling development teams

### Negative
- Initial setup complexity and learning curve
- Maintenance overhead for pipeline configurations
- Potential for pipeline bottlenecks as codebase grows
- Resource consumption for running comprehensive pipelines
- Need for careful management of secrets and credentials
- Potential false positives in automated checks
- Risk of over-reliance on automation without understanding

## Alternatives Considered

1. **Jenkins**
   - More customization options
   - Self-hosted with higher maintenance overhead
   - Rich plugin ecosystem
   - Steeper learning curve
   - More complex setup and maintenance

2. **GitLab CI/CD**
   - Integrated with GitLab platform
   - Would require migration from GitHub
   - Comprehensive feature set
   - Good container registry integration
   - Different permission model

3. **Azure DevOps Pipelines**
   - Strong integration with Azure cloud
   - Good support for Windows environments
   - Comprehensive feature set
   - Different pricing model
   - Separate platform from code hosting

4. **CircleCI**
   - Simple configuration for common scenarios
   - Good parallelization support
   - Separate platform from code hosting
   - Different pricing model
   - Less integrated with our GitHub workflow

## Implementation Notes

### Main Workflow File

```yaml
# .github/workflows/main.yml
name: Main CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  validate:
    name: Validate Code
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle
      
      - name: Validate Gradle wrapper
        uses: gradle/wrapper-validation-action@v1
      
      - name: Check code style
        run: ./gradlew checkstyleMain checkstyleTest
      
      - name: Validate Gradle build
        run: ./gradlew validatePlugins

  build:
    name: Build and Unit Test
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle
      
      - name: Build with Gradle
        run: ./gradlew build
        
      - name: Run unit tests
        run: ./gradlew test
      
      - name: Publish Unit Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: build/test-results/**/*.xml
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: |
            build/libs/*.jar
            build/reports/

  code_analysis:
    name: Code Analysis
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle
      
      - name: Cache SonarCloud packages
        uses: actions/cache@v3
        with:
          path: ~/.sonar/cache
          key: ${{ runner.os }}-sonar
          restore-keys: ${{ runner.os }}-sonar
      
      - name: Analyze with SonarCloud
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        run: ./gradlew sonarqube
      
      - name: Run dependency vulnerability check
        run: ./gradlew dependencyCheckAnalyze
      
      - name: Upload vulnerability report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: vulnerability-report
          path: build/reports/dependency-check-report.html

  integration_test:
    name: Integration Tests
    needs: build
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle
      
      - name: Run integration tests
        run: ./gradlew integrationTest
        env:
          SPRING_DATASOURCE_URL: jdbc:postgresql://localhost:5432/testdb
          SPRING_DATASOURCE_USERNAME: test
          SPRING_DATASOURCE_PASSWORD: test
      
      - name: Publish Integration Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: build/test-results/integrationTest/**/*.xml

  container_build:
    name: Build and Scan Container
    needs: [code_analysis, integration_test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Download build artifact
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts
          path: build/libs/
      
      - name: Build Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: false
          tags: aronim-bookstore:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Scan Docker image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'aronim-bookstore:${{ github.sha }}'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
          ignore-unfixed: true
      
      - name: Login to GitHub Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Push Docker image
        if: github.event_name != 'pull_request'
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}:latest

  deploy_dev:
    name: Deploy to Development
    if: github.ref == 'refs/heads/develop'
    needs: container_build
    runs-on: ubuntu-latest
    environment:
      name: development
      url: https://dev.aronim-bookstore.example.com
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
      
      - name: Set Kubernetes context
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_DEV }}
      
      - name: Deploy to development
        run: |
          kubectl set image deployment/aronim-bookstore \
            app=ghcr.io/${{ github.repository }}:${{ github.sha }} \
            --namespace=development
      
      - name: Verify deployment
        run: |
          kubectl rollout status deployment/aronim-bookstore \
            --timeout=180s \
            --namespace=development

  deploy_staging:
    name: Deploy to Staging
    if: github.ref == 'refs/heads/main'
    needs: container_build
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.aronim-bookstore.example.com
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
      
      - name: Set Kubernetes context
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Deploy to staging
        run: |
          kubectl set image deployment/aronim-bookstore \
            app=ghcr.io/${{ github.repository }}:${{ github.sha }} \
            --namespace=staging
      
      - name: Verify deployment
        run: |
          kubectl rollout status deployment/aronim-bookstore \
            --timeout=180s \
            --namespace=staging
      
      - name: Run acceptance tests
        run: |
          ./gradlew acceptanceTest -Dtest.url=https://staging.aronim-bookstore.example.com

  deploy_production:
    name: Deploy to Production
    if: github.ref == 'refs/heads/main'
    needs: deploy_staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://aronim-bookstore.example.com
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
      
      - name: Set Kubernetes context
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_PROD }}
      
      - name: Deploy to production
        run: |
          kubectl set image deployment/aronim-bookstore \
            app=ghcr.io/${{ github.repository }}:${{ github.sha }} \
            --namespace=production
      
      - name: Verify deployment
        run: |
          kubectl rollout status deployment/aronim-bookstore \
            --timeout=180s \
            --namespace=production
```

### Pull Request Workflow

```yaml
# .github/workflows/pull_request.yml
name: Pull Request Checks

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  validate:
    name: Validate Pull Request
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle
      
      - name: Build and test
        run: ./gradlew build test
      
      - name: Check code style
        run: ./gradlew checkstyleMain checkstyleTest
      
      - name: Run static code analysis
        run: ./gradlew sonarqube
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      
      - name: Run dependency vulnerability check
        run: ./gradlew dependencyCheckAnalyze
      
      - name: Build Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: false
          tags: aronim-bookstore:pr-${{ github.event.pull_request.number }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Scan Docker image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'aronim-bookstore:pr-${{ github.event.pull_request.number }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          ignore-unfixed: true
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
```

### Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  release:
    types: [published]

jobs:
  build:
    name: Build Release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle
      
      - name: Extract release version
        id: get_version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT
      
      - name: Build with Gradle
        run: ./gradlew build -Pversion=${{ steps.get_version.outputs.VERSION }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ steps.get_version.outputs.VERSION }}
            ghcr.io/${{ github.repository }}:latest
      
      - name: Create GitHub release assets
        uses: softprops/action-gh-release@v1
        with:
          files: |
            build/libs/*.jar
            build/distributions/*.zip
```

### Scheduled Security Scan

```yaml
# .github/workflows/security_scan.yml
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM

jobs:
  security_scan:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle
      
      - name: Run dependency vulnerability check
        run: ./gradlew dependencyCheckAnalyze
      
      - name: Pull latest Docker image
        run: docker pull ghcr.io/${{ github.repository }}:latest
      
      - name: Scan Docker image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'ghcr.io/${{ github.repository }}:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH,MEDIUM'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run CodeQL analysis
        uses: github/codeql-action/analyze@v2
```

## Branching and Deployment Strategy

Our CI/CD pipeline will be built around the following branching strategy:

1. **Feature Branches**
   - Created for each new feature or bug fix
   - Named using the pattern `feature/XXX-description` or `bugfix/XXX-description`
   - Pull request required for merging into `develop`
   - Basic validation, build, and tests run on pull request

2. **Develop Branch**
   - Main integration branch for development work
   - Automatic deployment to development environment
   - All tests run on this branch
   - Regular integration of feature branches

3. **Main Branch**
   - Represents production-ready code
   - Protected branch requiring pull request and approvals
   - Automatic deployment to staging environment
   - Manual approval required for production deployment
   - Tagged for releases

4. **Release Branches**
   - Created for release preparation
   - Named using the pattern `release/vX.Y.Z`
   - Used for final testing and stabilization
   - Merged into `main` and back into `develop` when complete

This strategy ensures that:
- Development work is isolated in feature branches
- Integration happens continuously in the develop branch
- Production deployments are controlled and validated
- Releases are properly versioned and tracked

## Environment Progression

Our deployment pipeline will follow this environment progression:

1. **Development**
   - Automatic deployment from the `develop` branch
   - Used for integration testing and feature demonstration
   - Refreshed with each successful build
   - May contain partial features and in-progress work

2. **Staging**
   - Automatic deployment from the `main` branch (with approval)
   - Production-like environment for final validation
   - Complete features only
   - Used for acceptance testing and performance validation
   - Data subset similar to production

3. **Production**
   - Manual deployment from the `main` branch after staging validation
   - Requires additional approval step
   - Zero-downtime deployment strategy
   - Careful monitoring during and after deployment
   - Rollback plan for each deployment

## Compliance Verification
- Regular audits of pipeline security
- Verification of secret and credential management
- Testing of rollback procedures
- Performance monitoring of pipeline execution
- Review of quality gate effectiveness
- Validation of deployment success rates
- Documentation review of CI/CD practices

## References
- GitHub Actions Documentation: https://docs.github.com/en/actions
- CI/CD Best Practices: https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment
- Trunk-Based Development: https://trunkbaseddevelopment.com/
- DevSecOps Pipeline Design: https://owasp.org/www-project-devsecops-guideline/
- Pipeline Security Best Practices: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions
- Kubernetes Deployment Strategies: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy
- Gradle CI Setup: https://docs.gradle.org/current/userguide/github_actions.html
