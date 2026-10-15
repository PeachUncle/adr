# ADR 001: TikTok Selector Migration from ID to data-e2e Attributes

**Status**: Accepted
**Date**: November 2025
**Deciders**: Development Team
**Technical Story**: TikTok HTML structure change broke video scraping

## Context and Problem Statement

Our TikTok scraper relied on HTML `id` attributes to locate video containers:
- `#challenge-item-list` for the main container
- `#column-item-video-container-{n}` for individual videos

On November 26, 2025, the scraper stopped returning videos without any error messages. Investigation revealed that TikTok had migrated their frontend to use `data-e2e` attributes instead of `id` attributes for the same elements.

This presented a decision point: **How should we adapt our selectors to be more resilient to future changes?**

## Decision Drivers

1. **Immediate fix needed**: Scraper was non-functional
2. **Future resilience**: TikTok will likely change again
3. **Maintainability**: Selectors should be easy to update
4. **Performance**: Selector changes shouldn't impact speed
5. **Compatibility**: Must work with our existing Selenium infrastructure

## Considered Options

### Option 1: Update to data-e2e attributes
```python
container = driver.find_element(By.CSS_SELECTOR, '[data-e2e="challenge-item-list"]')
```

### Option 2: Use XPath with multiple fallbacks
```python
container = driver.find_element(By.XPATH,
    "//div[@id='challenge-item-list' or @data-e2e='challenge-item-list']")
```

### Option 3: Use class-based selectors
```python
container = driver.find_element(By.CLASS_NAME, 'DivItemContainer')
```

### Option 4: Switch to TikTok API
(Not viable - TikTok doesn't offer a public API for hashtag searches)

## Decision Outcome

**Chosen option**: Option 1 (Update to data-e2e attributes)

**Rationale**:
- `data-e2e` attributes are specifically for end-to-end testing
- More stable than class names (which change for styling)
- Cleaner than XPath fallbacks (less complexity)
- TikTok's use of `data-e2e` suggests these are intentionally stable selectors

## Implementation

### Before (Broken):
```python
def scrape_hashtag(self, hashtag: str, max_results: int = 100):
    container = self.driver.find_element(By.ID, 'challenge-item-list')
    videos = self.driver.find_elements(By.ID, 'column-item-video-container-*')
```

### After (Working):
```python
def scrape_hashtag(self, hashtag: str, max_results: int = 100):
    container = self.wait_for_element(
        By.CSS_SELECTOR,
        '[data-e2e="challenge-item-list"]'
    )
    videos = container.find_elements(
        By.CSS_SELECTOR,
        '[data-e2e="search-video-item"]'
    )
```

### Changes Required:
1. Updated `scrape_hashtag()` method in `tiktok_scraper.py`
2. Modified `_extract_videos_from_page()` to use new selectors
3. Updated all related tests to match new selector strategy

## Consequences

### Positive
- ✅ Scraper functional again immediately
- ✅ `data-e2e` attributes more semantically meaningful
- ✅ Simpler selector syntax than XPath
- ✅ Tests pass with new selectors

### Negative
- ❌ TikTok can still change `data-e2e` values in the future
- ❌ No automatic fallback if selectors break again
- ❌ Requires manual monitoring to detect breakage

### Neutral
- 🔧 Performance identical (CSS selectors vs. ID selectors)
- 🔧 Code complexity unchanged (same number of selector calls)

## Lessons Learned

1. **Web scraping is inherently fragile**: Websites change without notice
2. **Monitoring is critical**: We need automated tests to detect breakage
3. **Graceful degradation**: Scraper should log warnings, not crash silently
4. **Documentation matters**: `data-e2e` suggests testing-oriented stability

## Mitigation Strategies

To reduce future impact of selector changes:

### 1. Automated Selector Health Checks
```python
def verify_selectors(self) -> bool:
    """Check if expected selectors exist on page"""
    try:
        container = self.driver.find_element(
            By.CSS_SELECTOR, '[data-e2e="challenge-item-list"]'
        )
        return container is not None
    except NoSuchElementException:
        logger.error("TikTok selectors have changed!")
        return False
```

### 2. Multiple Selector Fallbacks (Future Enhancement)
```python
SELECTORS = {
    'container': [
        '[data-e2e="challenge-item-list"]',  # Current
        '#challenge-item-list',              # Legacy
        '.challenge-item-list-container'     # Fallback
    ]
}
```

### 3. Visual Regression Testing
Take screenshots of successful scrapes. Compare future scrapes visually to detect HTML changes.

### 4. Monitoring and Alerting
- Log selector lookup failures
- Alert if zero videos returned (unusual)
- Track success rate over time

## Related Decisions

- [ADR-002: Public API Pattern](./002-public-api-pattern.md) - Testing revealed this need
- [Future] ADR on web scraping resilience strategy

## References

- TikTok scraper implementation: `/scrapers/tiktok_scraper.py`
- Related tests: `/tests/unit/test_tiktok_scraper.py`
- Issue tracking: GitHub #47 "TikTok scraper returning zero videos"
- Selenium By documentation: https://www.selenium.dev/documentation/webdriver/elements/locators/

## Revision History

- **November 26, 2025**: Initial decision
- **November 27, 2025**: Implementation complete, tests passing
- **November 28, 2025**: ADR documented
