# ADR-007: LinkedIn Job Posting Web Scraping with Playwright

**Date**: 2026-01-01  
**Status**: Accepted  
**Decision Makers**: Architecture Team  
**Technical Story**: CV Checker Phase 2 - Automated Job Description Fetching

## Context

CV Checker Phase 2 requires the ability to automatically fetch job descriptions from LinkedIn URLs, eliminating the need for users to manually copy-paste job content. This feature significantly improves user experience by reducing friction in the CV analysis workflow.

### Business Requirements

- Users should be able to paste a LinkedIn job posting URL
- The system should automatically extract the job description text
- The extracted content should be passed to the JobParserAgent for structured analysis
- The feature should handle LinkedIn's dynamic, JavaScript-rendered content
- The solution should provide a fallback to manual input if scraping fails

### Technical Challenges

1. **No Public API**: LinkedIn does not provide a public API for accessing job posting content
2. **JavaScript Rendering**: LinkedIn job pages are dynamically rendered using JavaScript
3. **Anti-Bot Measures**: LinkedIn employs various anti-scraping protections
4. **Content Structure**: Job posting HTML structure may change over time
5. **Legal Considerations**: Web scraping must respect LinkedIn's Terms of Service and robots.txt
6. **Rate Limiting**: Need to avoid triggering LinkedIn's anti-abuse systems

## Decision

We will implement **server-side web scraping using Playwright** to extract job description text from LinkedIn URLs.

### Architecture Overview

```
User Input (LinkedIn URL)
    ↓
LinkedIn Scraper Service (Playwright)
    ↓
Raw Job Description Text
    ↓
JobParserAgent (existing)
    ↓
Structured Job Data
```

### Key Components

1. **LinkedIn Scraper Service**: New backend service using Playwright
2. **Unified Job Submission Endpoint**: Enhanced `POST /api/v1/jobs` endpoint accepting both `source_type: manual` and `source_type: linkedin_url`
3. **UI Toggle**: Frontend toggle between URL mode and manual input mode
4. **Fallback Strategy**: Graceful degradation to manual input on scraping failure
5. **No Database Storage (Phase 2)**: Scraped content returned directly to client; database integration deferred to Phase 3

## Options Considered

### Option 1: LinkedIn Official API (Not Available)

**Description**: Use LinkedIn's official API for job content access.

**Pros**:
- Legal and compliant
- Stable and reliable
- Official support
- No anti-bot issues

**Cons**:
- **Not available for job content** - LinkedIn doesn't provide public APIs for this use case
- Would require LinkedIn partnership program (not feasible for this project)
- High cost and access restrictions

**Decision**: **Rejected** - Not viable for our use case

### Option 2: Browser Extension (Client-Side Scraping)

**Description**: Develop a browser extension that scrapes LinkedIn while the user is on the page.

**Pros**:
- Executes in user's browser with their session
- Lower anti-bot detection risk
- No server-side infrastructure needed
- User's own authentication

**Cons**:
- **Poor UX**: Requires users to install extension
- **Platform limitations**: Separate extensions for Chrome, Firefox, Safari
- **Maintenance burden**: Multiple codebases
- **Adoption friction**: Users may not want to install extensions
- **Limited mobile support**: Doesn't work on mobile browsers
- **Deployment complexity**: Extension store approval process

**Decision**: **Rejected** - Too much friction for users

### Option 3: Server-Side with Requests/BeautifulSoup

**Description**: Use Python's requests library and BeautifulSoup for HTML parsing.

**Pros**:
- Lightweight and fast
- Low resource consumption
- Simple implementation
- Well-documented libraries

**Cons**:
- **Cannot handle JavaScript**: LinkedIn pages are dynamically rendered
- **Missing content**: Would only get static HTML skeleton
- **No interaction capability**: Cannot scroll, click, or wait for content
- **High failure rate**: Won't work for modern single-page applications

**Decision**: **Rejected** - Inadequate for JavaScript-rendered content

### Option 4: Server-Side with Playwright (CHOSEN)

**Description**: Use Playwright headless browser for server-side scraping.

**Pros**:
- **Full JavaScript support**: Executes JavaScript like a real browser
- **Wait for content**: Can wait for dynamic content to load
- **Interaction capable**: Can scroll, click, handle popups
- **Cross-browser support**: Chromium, Firefox, WebKit
- **Well-maintained**: Microsoft-backed project with active development
- **Better UX**: No browser extension required
- **Mobile support**: Works for all client platforms
- **Full control**: Server-side processing and error handling
- **Single codebase**: One implementation for all users

**Cons**:
- **Resource intensive**: Requires headless browser runtime
- **Anti-bot risk**: LinkedIn may detect and block automated browsers
- **Legal considerations**: Must respect Terms of Service
- **Maintenance**: LinkedIn UI changes require updates
- **Infrastructure**: Docker image size increase, deployment considerations

**Decision**: **CHOSEN** - Best balance of functionality, UX, and maintainability

### Option 5: Third-Party Scraping Services

**Description**: Use services like ScrapingBee, Bright Data, or Apify.

**Pros**:
- Managed infrastructure
- Handle anti-bot measures
- Rotating proxies
- Legal responsibility offloaded

**Cons**:
- **Recurring costs**: Per-request pricing can be expensive
- **External dependency**: Service availability and reliability
- **Data privacy**: Job data passes through third party
- **Vendor lock-in**: Hard to migrate away from
- **Latency**: Additional network hop
- **Cost scaling**: Unpredictable costs as usage grows

**Decision**: **Rejected** - Prefer in-house solution for cost and control

## Decision Rationale

### Why Playwright Over Alternatives

1. **Technical Capability**: Only Playwright can reliably handle LinkedIn's JavaScript-rendered content
2. **Microsoft Ecosystem Alignment**: Playwright is Microsoft-backed, aligning with our use of Microsoft Agent Framework and Azure
3. **Proven Track Record**: Widely used for web scraping and testing in production environments
4. **Future-Proof**: Active development and strong community support

### Server-Side vs Client-Side

**Server-side chosen because**:
- **Better UX**: No browser extension installation required
- **Universal access**: Works on all devices and browsers
- **Centralized control**: Easier to update and maintain scraping logic
- **Consistent behavior**: Same experience for all users
- **Error handling**: Server can implement robust retry and fallback logic

### Separation of Concerns

**Scraper extracts raw text only**:
- Let JobParserAgent handle structured extraction (single responsibility)
- Scraper focuses on: authentication, navigation, content extraction
- Parser focuses on: understanding job requirements, skill extraction, formatting

This separation ensures:
- Scraper changes don't affect parsing logic
- Can swap scraper implementation without changing agents
- Better testability of each component

### Error Handling and Fallback

**Graceful degradation strategy**:
```
LinkedIn URL input
    ↓
Attempt scraping
    ↓
Success? → Pass to JobParserAgent
    ↓
Failure? → Show manual input option
```

This ensures the application remains functional even when scraping fails.

## Implementation Considerations

### 1. Playwright Installation and Setup

```python
# requirements.txt
playwright==1.40.0

# Install browser binaries
playwright install chromium
```

**Docker considerations**:
```dockerfile
FROM python:3.11-slim

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

RUN pip install playwright
RUN playwright install chromium
```

### 2. Resource Requirements

- **Memory**: ~150-200MB per browser instance
- **CPU**: Moderate for page rendering
- **Disk**: ~200MB for Chromium browser binaries
- **Concurrency**: Limit to 5-10 concurrent browser instances

**Mitigation**: Implement browser instance pooling and request queuing

### 3. Anti-Scraping Mitigation

```python
# User agent rotation
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
]

# Request delays
await asyncio.sleep(random.uniform(1.0, 3.0))

# Viewport randomization
await page.set_viewport_size({
    "width": random.randint(1200, 1920),
    "height": random.randint(800, 1080)
})

# Stealth mode
await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    })
""")
```

### 4. Rate Limiting

**Backend implementation**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/scrape/linkedin")
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def scrape_linkedin(url: str):
    pass
```

### 5. Error Handling Patterns

```python
class LinkedInScraperError(Exception):
    """Base exception for scraping errors"""
    pass

class PageLoadTimeout(LinkedInScraperError):
    """Page failed to load within timeout"""
    pass

class ContentNotFound(LinkedInScraperError):
    """Job description content not found on page"""
    pass

class AntiBot Detected(LinkedInScraperError):
    """LinkedIn anti-bot challenge detected"""
    pass

# Error handling with fallback
try:
    content = await scrape_linkedin(url)
except LinkedInScraperError as e:
    logger.warning(f"Scraping failed: {e}")
    return {"error": str(e), "fallback": "manual_input"}
```

### 6. Deployment Considerations

**Azure App Service**:
- Use Linux App Service Plan (required for Playwright)
- Minimum B2 tier for adequate memory (3.5GB)
- Custom startup script to install Playwright browsers

**Docker**:
- Use multi-stage build to minimize image size
- Install only Chromium (not all browsers)
- Consider using playwright-python Docker base image

**Environment Variables**:
```bash
LINKEDIN_SCRAPER_TIMEOUT=30000  # 30 seconds
LINKEDIN_SCRAPER_HEADLESS=true
LINKEDIN_SCRAPER_MAX_CONCURRENT=5
```

### 7. Monitoring and Logging

```python
import structlog

logger = structlog.get_logger()

# Log scraping attempts
logger.info("linkedin_scrape_started", url=url)

# Log success/failure rates
logger.info("linkedin_scrape_completed", 
    url=url, 
    duration_ms=duration,
    content_length=len(content)
)

# Alert on high failure rate
if failure_rate > 0.5:
    logger.error("linkedin_scrape_high_failure", rate=failure_rate)
```

## Consequences

### Positive Consequences

1. **Improved User Experience**:
   - Users can analyze jobs with a single URL paste
   - Eliminates error-prone copy-paste workflow
   - Faster job analysis initiation

2. **Full Control**:
   - In-house implementation enables quick fixes
   - Can customize extraction logic for LinkedIn changes
   - No third-party dependencies for core functionality

3. **Cost Effective**:
   - No per-request API costs
   - Predictable infrastructure costs
   - Scales with existing Azure resources

4. **Future Flexibility**:
   - Can extend to other job boards (Indeed, Glassdoor)
   - Can add authentication support if needed
   - Foundation for additional scraping features

5. **Better Error Handling**:
   - Server-side retry logic
   - Comprehensive logging and monitoring
   - Graceful fallback to manual input

### Negative Consequences

1. **Legal and Compliance Risks**:
   - **Risk**: LinkedIn Terms of Service may prohibit scraping
   - **Mitigation**: 
     - Document legal review process
     - Implement robots.txt checking
     - Add prominent disclaimer about usage
     - Consider implementing authentication flow (user's own LinkedIn session)
     - Monitor LinkedIn's legal communications

2. **Maintenance Burden**:
   - **Risk**: LinkedIn UI changes break scraping logic
   - **Mitigation**:
     - Use robust CSS selectors (data attributes, not styling classes)
     - Implement multiple fallback selectors
     - Add automated testing against live LinkedIn pages
     - Set up monitoring alerts for scraping failures
     - Document selector update process

3. **Anti-Bot Detection**:
   - **Risk**: LinkedIn may detect and block automated access
   - **Mitigation**:
     - Implement rate limiting (5 requests/minute)
     - Add random delays between requests
     - Rotate user agents and viewport sizes
     - Use residential proxy rotation (future enhancement)
     - Monitor block rates and adjust strategy

4. **Infrastructure Requirements**:
   - **Risk**: Increased memory and CPU usage
   - **Mitigation**:
     - Implement browser instance pooling
     - Set maximum concurrent scraping limit
     - Use request queuing for peak loads
     - Monitor resource usage and scale accordingly

5. **Reliability Concerns**:
   - **Risk**: Network issues, timeout failures, content changes
   - **Mitigation**:
     - Always provide manual input fallback
     - Implement comprehensive retry logic
     - Set reasonable timeouts (30 seconds)
     - Cache successful responses (optional future)
     - Provide clear error messages to users

### Neutral Consequences

1. **Development Complexity**: Moderate increase in codebase complexity
2. **Testing Requirements**: Need integration tests against live LinkedIn (use staging URLs)
3. **Documentation**: Must document legal considerations and limitations
4. **Monitoring**: Requires additional observability instrumentation

## Alternatives for Future

### Monitor LinkedIn API Availability

- Regularly check for new LinkedIn API offerings
- If official API becomes available, migrate to it immediately
- Build abstraction layer to make future migration easier

### Evaluate Third-Party Services

**Consider third-party services if**:
- Scraping reliability drops below 80%
- LinkedIn implements stronger anti-bot measures
- Maintenance burden exceeds 1 day/week
- Legal concerns escalate

**Services to evaluate**:
- ScrapingBee
- Bright Data
- Apify

### User Authentication Flow

**Future enhancement**:
- Allow users to authenticate with their own LinkedIn account
- Use user's session for scraping (lower detection risk)
- Respects user's data access rights

### Job Board Expansion

**Apply pattern to other platforms**:
- Indeed.com
- Glassdoor
- Monster.com
- Company career pages

## Implementation Plan

### Phase 1: Core Scraping Service
- [ ] Add Playwright dependency
- [ ] Create LinkedInScraperService
- [ ] Implement basic scraping logic
- [ ] Add error handling and fallbacks
- [ ] Unit tests with mocked browser

### Phase 2: API Integration
- [ ] Create `/api/scrape/linkedin` endpoint
- [ ] Add rate limiting
- [ ] Implement request validation
- [ ] Add monitoring and logging
- [ ] Integration tests

### Phase 3: Frontend Integration
- [ ] Add URL/Manual input toggle
- [ ] Implement URL validation
- [ ] Add loading states
- [ ] Handle error display
- [ ] Add fallback UI flow

### Phase 4: Production Readiness
- [ ] Dockerfile updates
- [ ] Azure deployment configuration
- [ ] Performance testing
- [ ] Legal disclaimer
- [ ] Documentation

## Related Decisions

- ADR-001: Microsoft Agent Framework Sequential Orchestration (JobParserAgent integration)
- ADR-005: FastAPI Backend Architecture (API endpoint implementation)
- ADR-006: Frontend Technology Stack (UI toggle implementation)

## References

- [Playwright Python Documentation](https://playwright.dev/python/)
- [Playwright Best Practices](https://playwright.dev/python/docs/best-practices)
- [Web Scraping Legal Considerations](https://www.eff.org/issues/coders/vulnerability-reporting-faq)
- [LinkedIn robots.txt](https://www.linkedin.com/robots.txt)
- [FastAPI Rate Limiting](https://slowapi.readthedocs.io/)
- [Azure App Service Linux](https://learn.microsoft.com/azure/app-service/quickstart-python)

## Appendix: Sample Implementation

### Scraper Service

```python
from playwright.async_api import async_playwright, Browser, Page
import structlog

logger = structlog.get_logger()

class LinkedInScraperService:
    """Service for scraping LinkedIn job postings."""
    
    def __init__(self):
        self.browser: Browser | None = None
        self.timeout = 30000  # 30 seconds
    
    async def initialize(self):
        """Initialize browser instance."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
    
    async def scrape_job_description(self, url: str) -> str:
        """
        Extract job description text from LinkedIn URL.
        
        Args:
            url: LinkedIn job posting URL
            
        Returns:
            Raw job description text
            
        Raises:
            LinkedInScraperError: If scraping fails
        """
        if not self.browser:
            await self.initialize()
        
        page: Page = await self.browser.new_page()
        
        try:
            # Navigate to job posting
            logger.info("linkedin_scrape_started", url=url)
            await page.goto(url, timeout=self.timeout)
            
            # Wait for job description to load
            await page.wait_for_selector(
                '.description__text, .show-more-less-html__markup',
                timeout=self.timeout
            )
            
            # Extract text content
            content = await page.evaluate('''() => {
                const selectors = [
                    '.description__text',
                    '.show-more-less-html__markup',
                    '[class*="description"]'
                ];
                
                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        return element.innerText;
                    }
                }
                
                return null;
            }''')
            
            if not content:
                raise ContentNotFound("Job description not found on page")
            
            logger.info("linkedin_scrape_completed", 
                url=url, 
                content_length=len(content)
            )
            
            return content
            
        except Exception as e:
            logger.error("linkedin_scrape_failed", url=url, error=str(e))
            raise LinkedInScraperError(f"Failed to scrape LinkedIn job: {e}")
        
        finally:
            await page.close()
    
    async def close(self):
        """Close browser instance."""
        if self.browser:
            await self.browser.close()
```

### FastAPI Endpoint (Unified Job Submission)

```python
from fastapi import APIRouter, HTTPException, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

class JobSubmissionRequest(BaseModel):
    source_type: Literal["manual", "linkedin_url"]
    content: Optional[str] = None  # Required for manual
    url: Optional[str] = None       # Required for linkedin_url

@router.post("/api/v1/jobs")
@limiter.limit("5/minute")  # Applied only to linkedin_url source_type
async def submit_job(
    request: JobSubmissionRequest,
    scraper: LinkedInScraperService = Depends(get_linkedin_scraper)
):
    """
    Submit job description (manual text or LinkedIn URL).
    
    Rate limit: 5 requests per minute per IP (linkedin_url only).
    """
    if request.source_type == "manual":
        if not request.content or len(request.content.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Job description must be at least 50 characters"
            )
        return {
            "job_id": str(uuid.uuid4()),
            "content": request.content,
            "source_type": "manual",
            "fetch_status": "not_applicable"
        }
    
    elif request.source_type == "linkedin_url":
        if not request.url:
            raise HTTPException(
                status_code=400,
                detail="URL is required for linkedin_url source type"
            )
        
        # Validate LinkedIn URL
        if not request.url.startswith("https://") or "linkedin.com/jobs/view/" not in request.url:
            raise HTTPException(
                status_code=400,
                detail="Invalid LinkedIn job URL"
            )
        
        try:
            content = await scraper.scrape_job_description(request.url)
            
            # Log warning if content is unusually short
            if len(content) < 50:
                logger.warning(f"Short LinkedIn content: {len(content)} chars from {request.url}")
            
            return {
                "job_id": str(uuid.uuid4()),
                "content": content,
                "source_type": "linkedin_url",
                "source_url": request.url,
                "fetch_status": "success"
            }
        except LinkedInScraperError as e:
            logger.warning("scraping_failed_fallback", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "fallback": "manual_input"
            }
```
