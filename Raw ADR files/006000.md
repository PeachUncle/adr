# ADR: Deploying Playwright for Web Scraping in Production

## Status

Accepted and Implemented

## Context

Our data provider v2 API uses Playwright to scrape football data from external websites. While Playwright works well in a development environment, deploying it reliably in a production environment presents several challenges:

1. Chromium browser requires specific system dependencies
2. Resource management is critical to prevent memory leaks
3. Error handling needs to be robust for unattended operation
4. Browser launch configuration differs between development and production
5. Browser executables must be correctly located and configured
6. Playwright requires specific system dependencies to run headless browsers
7. Railway.com uses container-based deployment
8. We need to ensure consistent and reliable scraping operations
9. The solution must be cost-effective and performance-optimized

## Decision

We will deploy our Playwright-based APIs to Railway.com using the official Microsoft Playwright Docker image:

1. Use the official Microsoft Playwright Docker image (`mcr.microsoft.com/playwright:v1.42.1-jammy`) as our base image
2. Configure our application to run on top of this image without needing manual dependency installation
3. Configure Playwright to run in headless mode in production
4. Implement appropriate resource allocation and timeouts
5. Create health check endpoints to monitor Playwright functionality
6. Set up error handling and monitoring specifically for scraping operations

## Technical Implementation

### Docker Configuration

- Create a Dockerfile with all necessary Chromium dependencies
- Install Playwright browsers during the Docker build process
- Set appropriate environment variables for Playwright in production

### Playwright Configuration

- Force headless mode in production environments
- Add appropriate browser arguments for container environments
- Set reasonable timeouts and retry mechanisms

### Resource Considerations

- Allocate sufficient memory for browser operations
- Implement request throttling to prevent overloading target websites
- Add caching where appropriate to reduce redundant scraping

## Consequences

### Positive

- Reliable and consistent web scraping in production
- Scalable solution that can handle increased load
- Docker ensures consistent runtime environment

### Negative

- Higher resource consumption compared to API-based approaches
- Potential for target website structure changes breaking scrapers
- Increased deployment complexity

### Mitigation Strategies

- Implement robust error handling and notifications
- Set up monitoring for scraper health and success rates
- Create a testing process for scrapers before deployment

## References

- [Playwright Docker Documentation](https://playwright.dev/docs/docker)
- [Railway.com Container Configuration](https://docs.railway.app/deploy/railway-up)
