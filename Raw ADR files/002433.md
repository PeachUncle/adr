# ADR-008: CI/CD and Deployment Strategy

## Status
Accepted

## Context
Lead Tracker requires a robust CI/CD pipeline for:
- Automated testing and quality gates before deployment
- Multi-environment deployment (development, staging, production)
- Database migration management across environments
- Docker image building and registry management
- Infrastructure as Code for reproducible deployments
- Rollback capabilities for failed deployments

## Decision
We will implement a **GitOps-based CI/CD pipeline** using GitHub Actions with Docker:

### Architecture Components:
1. **GitHub Actions** for CI/CD orchestration
2. **Multi-stage Docker builds** for optimized images
3. **Azure Container Registry** for image storage
4. **Environment-specific configurations** with secrets management
5. **Database migration automation** with EF Core
6. **Health check validation** before deployment completion

### Pipeline Structure:

#### 1. Continuous Integration Workflow
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  DOTNET_VERSION: '8.0.x'
  NODE_VERSION: '18.x'
  REGISTRY: leadtracker.azurecr.io
  API_IMAGE_NAME: leadtracker-api
  WEB_IMAGE_NAME: leadtracker-web

jobs:
  test-api:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: leadtracker_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4
    
    - name: Setup .NET
      uses: actions/setup-dotnet@v4
      with:
        dotnet-version: ${{ env.DOTNET_VERSION }}
        
    - name: Cache NuGet packages
      uses: actions/cache@v4
      with:
        path: ~/.nuget/packages
        key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj') }}
        restore-keys: |
          ${{ runner.os }}-nuget-
    
    - name: Restore dependencies
      run: dotnet restore api/LeadTracker.sln
      
    - name: Build
      run: dotnet build api/LeadTracker.sln --no-restore --configuration Release
      
    - name: Run unit tests
      run: dotnet test api/tests/LeadTracker.UnitTests --no-build --configuration Release --logger trx --collect:"XPlat Code Coverage"
      
    - name: Run integration tests
      run: dotnet test api/tests/LeadTracker.IntegrationTests --no-build --configuration Release --logger trx
      env:
        ConnectionStrings__DefaultConnection: "Host=localhost;Database=leadtracker_test;Username=postgres;Password=postgres"
        
    - name: Upload test results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-results-api
        path: |
          **/*.trx
          **/coverage.cobertura.xml

  test-web:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
        cache-dependency-path: web/package-lock.json
        
    - name: Install dependencies
      run: npm ci
      working-directory: web
      
    - name: Run linting
      run: npm run lint
      working-directory: web
      
    - name: Run type checking
      run: npm run type-check
      working-directory: web
      
    - name: Run unit tests
      run: npm run test:ci
      working-directory: web
      
    - name: Run E2E tests
      run: npm run test:e2e
      working-directory: web
      
    - name: Upload test results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-results-web
        path: web/test-results/

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: 'trivy-results.sarif'

  build-images:
    runs-on: ubuntu-latest
    needs: [test-api, test-web, security-scan]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ secrets.ACR_USERNAME }}
        password: ${{ secrets.ACR_PASSWORD }}
        
    - name: Extract metadata for API
      id: meta-api
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.API_IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
          
    - name: Extract metadata for Web
      id: meta-web
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.WEB_IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push API image
      uses: docker/build-push-action@v5
      with:
        context: api
        file: api/Dockerfile
        push: true
        tags: ${{ steps.meta-api.outputs.tags }}
        labels: ${{ steps.meta-api.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Build and push Web image
      uses: docker/build-push-action@v5
      with:
        context: web
        file: web/Dockerfile
        push: true
        tags: ${{ steps.meta-web.outputs.tags }}
        labels: ${{ steps.meta-web.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

#### 2. Deployment Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Environment

on:
  workflow_run:
    workflows: ["CI Pipeline"]
    branches: [main, develop]
    types: [completed]
    
env:
  REGISTRY: leadtracker.azurecr.io

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.head_branch == 'develop' }}
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      uses: azure/webapps-deploy@v2
      with:
        app-name: leadtracker-staging
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE_STAGING }}
        images: |
          ${{ env.REGISTRY }}/leadtracker-api:develop-${{ github.sha }}
          ${{ env.REGISTRY }}/leadtracker-web:develop-${{ github.sha }}
          
    - name: Run database migrations
      run: |
        docker run --rm \
          -e ConnectionStrings__DefaultConnection="${{ secrets.STAGING_CONNECTION_STRING }}" \
          ${{ env.REGISTRY }}/leadtracker-api:develop-${{ github.sha }} \
          dotnet ef database update
          
    - name: Run health checks
      run: |
        for i in {1..30}; do
          if curl -f ${{ secrets.STAGING_HEALTH_CHECK_URL }}; then
            echo "Health check passed"
            exit 0
          fi
          echo "Health check failed, retrying in 10 seconds..."
          sleep 10
        done
        echo "Health check failed after 5 minutes"
        exit 1

  deploy-production:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.head_branch == 'main' }}
    environment: production
    needs: [deploy-staging]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Create deployment
      uses: actions/github-script@v7
      id: deployment
      with:
        script: |
          const deployment = await github.rest.repos.createDeployment({
            owner: context.repo.owner,
            repo: context.repo.repo,
            ref: context.sha,
            environment: 'production',
            description: 'Deploy to production',
            auto_merge: false
          });
          return deployment.data.id;
          
    - name: Deploy to production
      uses: azure/webapps-deploy@v2
      with:
        app-name: leadtracker-production
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE_PRODUCTION }}
        images: |
          ${{ env.REGISTRY }}/leadtracker-api:latest
          ${{ env.REGISTRY }}/leadtracker-web:latest
          
    - name: Run database migrations
      run: |
        docker run --rm \
          -e ConnectionStrings__DefaultConnection="${{ secrets.PRODUCTION_CONNECTION_STRING }}" \
          ${{ env.REGISTRY }}/leadtracker-api:latest \
          dotnet ef database update
          
    - name: Warm up application
      run: |
        curl -X POST ${{ secrets.PRODUCTION_WARMUP_URL }} \
          -H "Authorization: Bearer ${{ secrets.WARMUP_TOKEN }}"
          
    - name: Update deployment status
      uses: actions/github-script@v7
      if: always()
      with:
        script: |
          const state = '${{ job.status }}' === 'success' ? 'success' : 'failure';
          await github.rest.repos.createDeploymentStatus({
            owner: context.repo.owner,
            repo: context.repo.repo,
            deployment_id: ${{ steps.deployment.outputs.result }},
            state: state,
            environment_url: '${{ secrets.PRODUCTION_URL }}'
          });
```

### Docker Configuration:

#### 1. Multi-stage API Dockerfile
```dockerfile
# api/Dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj files and restore dependencies
COPY ["LeadTracker.Api/LeadTracker.Api.csproj", "LeadTracker.Api/"]
COPY ["LeadTracker.Core/LeadTracker.Core.csproj", "LeadTracker.Core/"]
COPY ["LeadTracker.Infrastructure/LeadTracker.Infrastructure.csproj", "LeadTracker.Infrastructure/"]
RUN dotnet restore "LeadTracker.Api/LeadTracker.Api.csproj"

# Copy source code and build
COPY . .
WORKDIR "/src/LeadTracker.Api"
RUN dotnet build "LeadTracker.Api.csproj" -c Release -o /app/build

# Publish application
FROM build AS publish
RUN dotnet publish "LeadTracker.Api.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Copy published application
COPY --from=publish /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
ENTRYPOINT ["dotnet", "LeadTracker.Api.dll"]
```

#### 2. Multi-stage Web Dockerfile
```dockerfile
# web/Dockerfile
FROM node:18-alpine AS deps
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:18-alpine AS build
WORKDIR /app

# Copy package files and install all dependencies
COPY package*.json ./
RUN npm ci

# Copy source code and build
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Production image
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=build /app/public ./public
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### Environment Configuration:

#### 1. Docker Compose for Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: leadtracker
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__DefaultConnection=Host=postgres;Database=leadtracker;Username=postgres;Password=postgres
      - Redis__ConnectionString=redis:6379
      - JWT__SecretKey=${JWT_SECRET_KEY}
      - Email__SmtpHost=${SMTP_HOST}
      - Email__SmtpPort=${SMTP_PORT}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://api:8080
      - NEXTAUTH_URL=http://localhost:3000
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
    depends_on:
      api:
        condition: service_healthy

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
      - web

volumes:
  postgres_data:
  redis_data:
```

#### 2. Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: ${REGISTRY}/leadtracker-api:${API_TAG}
    restart: unless-stopped
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - ConnectionStrings__DefaultConnection=${DATABASE_CONNECTION_STRING}
      - Redis__ConnectionString=${REDIS_CONNECTION_STRING}
      - ApplicationInsights__InstrumentationKey=${APPINSIGHTS_KEY}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    image: ${REGISTRY}/leadtracker-web:${WEB_TAG}
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=${API_URL}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
      - web
```

### Database Migration Strategy:

#### 1. Migration Scripts
```csharp
// api/Scripts/migrate.sh
#!/bin/bash
set -e

echo "Starting database migration..."

# Wait for database to be ready
until dotnet ef database update --connection "$ConnectionStrings__DefaultConnection"; do
    echo "Database not ready, waiting 5 seconds..."
    sleep 5
done

echo "Database migration completed successfully"

# Run data seeding if needed
if [ "$ASPNETCORE_ENVIRONMENT" = "Development" ] || [ "$SEED_DATA" = "true" ]; then
    echo "Seeding development data..."
    dotnet run --project LeadTracker.Api -- --seed
fi
```

#### 2. Migration Validation
```csharp
public class MigrationValidator
{
    public static async Task ValidateMigrationsAsync(LeadTrackerDbContext context)
    {
        var pendingMigrations = await context.Database.GetPendingMigrationsAsync();
        
        if (pendingMigrations.Any())
        {
            throw new InvalidOperationException($"Database has pending migrations: {string.Join(", ", pendingMigrations)}");
        }
        
        // Validate critical tables exist
        var criticalTables = new[] { "Organizations", "Users", "Leads", "Stages" };
        
        foreach (var table in criticalTables)
        {
            var exists = await context.Database.ExecuteSqlRawAsync($"SELECT 1 FROM information_schema.tables WHERE table_name = '{table}'");
            if (exists == 0)
            {
                throw new InvalidOperationException($"Critical table {table} does not exist");
            }
        }
    }
}
```

### Infrastructure as Code:

#### 1. Terraform Configuration
```hcl
# infra/main.tf
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "leadtracker-tfstate-rg"
    storage_account_name = "leadtrackertfstate"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "leadtracker-${var.environment}-rg"
  location = var.location
  
  tags = {
    Environment = var.environment
    Application = "LeadTracker"
  }
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = "leadtracker-${var.environment}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  
  os_type  = "Linux"
  sku_name = var.app_service_sku
}

# Container Registry
resource "azurerm_container_registry" "main" {
  name                = "leadtracker${var.environment}acr"
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  sku                = "Standard"
  admin_enabled      = true
}

# PostgreSQL Database
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "leadtracker-${var.environment}-db"
  resource_group_name    = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  version               = "15"
  administrator_login    = var.db_admin_username
  administrator_password = var.db_admin_password
  
  storage_mb = 32768
  sku_name   = var.db_sku_name
  
  backup_retention_days = 7
  geo_redundant_backup_enabled = var.environment == "production"
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "leadtracker-${var.environment}-ai"
  location           = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type   = "web"
}
```

### Rollback Strategy:

#### 1. Blue-Green Deployment Script
```bash
#!/bin/bash
# scripts/blue-green-deploy.sh

set -e

ENVIRONMENT=$1
NEW_VERSION=$2
HEALTH_CHECK_URL=$3

if [ -z "$ENVIRONMENT" ] || [ -z "$NEW_VERSION" ] || [ -z "$HEALTH_CHECK_URL" ]; then
    echo "Usage: $0 <environment> <version> <health-check-url>"
    exit 1
fi

echo "Starting blue-green deployment for $ENVIRONMENT with version $NEW_VERSION"

# Deploy to staging slot
az webapp deployment slot create --name "leadtracker-$ENVIRONMENT" --resource-group "leadtracker-$ENVIRONMENT-rg" --slot "staging"

az webapp config container set --name "leadtracker-$ENVIRONMENT" --resource-group "leadtracker-$ENVIRONMENT-rg" --slot "staging" \
    --docker-custom-image-name "leadtracker.azurecr.io/leadtracker-api:$NEW_VERSION"

# Wait for staging slot to be ready
echo "Waiting for staging slot to be ready..."
for i in {1..30}; do
    if curl -f "$HEALTH_CHECK_URL-staging"; then
        echo "Staging slot is healthy"
        break
    fi
    sleep 10
done

# Swap slots
echo "Swapping production and staging slots..."
az webapp deployment slot swap --name "leadtracker-$ENVIRONMENT" --resource-group "leadtracker-$ENVIRONMENT-rg" --slot "staging" --target-slot "production"

# Verify production health
echo "Verifying production health..."
for i in {1..30}; do
    if curl -f "$HEALTH_CHECK_URL"; then
        echo "Production deployment successful"
        exit 0
    fi
    sleep 10
done

# Rollback if health check fails
echo "Production health check failed, rolling back..."
az webapp deployment slot swap --name "leadtracker-$ENVIRONMENT" --resource-group "leadtracker-$ENVIRONMENT-rg" --slot "production" --target-slot "staging"

echo "Rollback completed"
exit 1
```

## Consequences

### Positive:
- **Automated Quality Gates**: Comprehensive testing before deployment
- **Consistent Deployments**: Infrastructure as Code ensures reproducibility
- **Fast Rollbacks**: Blue-green deployment enables quick recovery
- **Security**: Vulnerability scanning and secrets management
- **Monitoring**: Health checks and deployment tracking

### Negative:
- **Complexity**: Multiple tools and configurations to maintain
- **Cost**: Additional infrastructure for staging and monitoring
- **Dependencies**: Reliance on cloud provider services

### Implementation Checklist:
- [ ] Set up GitHub Actions workflows for CI/CD
- [ ] Configure Docker multi-stage builds
- [ ] Create environment-specific configurations
- [ ] Implement database migration automation
- [ ] Set up container registry and image management
- [ ] Configure infrastructure as code with Terraform
- [ ] Implement health checks and monitoring
- [ ] Create rollback procedures and documentation
- [ ] Set up secrets management and security scanning
- [ ] Test deployment pipeline end-to-end
