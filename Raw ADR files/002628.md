# ADR 002: Public API Pattern for UnifiedCollector

**Status**: Accepted
**Date**: November 2025
**Deciders**: Development Team
**Technical Story**: Integration tests revealed missing public API for collection methods

## Context and Problem Statement

The `UnifiedCollector` class orchestrates data collection from multiple sources (prices, Reddit, TikTok). During development, collection logic was implemented as private methods:
- `_collect_prices()`
- `_collect_reddit()`
- `_collect_tiktok()`

When writing integration tests, we discovered there was no way to test individual collectors in isolation without calling the full `collect_all()` method. Python convention dictates that underscore-prefixed methods are private and shouldn't be accessed from outside the class.

**The problem**: We had implementation without a designed public interface.

## Decision Drivers

1. **Testability**: Need to test each collector independently
2. **API clarity**: External code should have clear entry points
3. **Python conventions**: Respect `_private` method naming
4. **Backward compatibility**: Don't break existing code
5. **Return value consistency**: API should return structured data
6. **Scheduler integration**: Background tasks need individual collector access

## Considered Options

### Option 1: Make private methods public (remove underscore)
```python
def collect_prices(self, coin_symbols):
    """Now public, but returns (count, errors) tuple"""
    return self._collect_prices(coin_symbols)
```

### Option 2: Keep private, expose through properties
```python
@property
def price_collector(self):
    return self._collect_prices
```

### Option 3: Create public wrapper methods with structured returns
```python
def collect_prices(self, coin_symbols: List[str]) -> Dict:
    """Public API for price collection"""
    count, errors = self._collect_prices(coin_symbols)
    return {'count': count, 'errors': errors}
```

### Option 4: Violate Python conventions and test private methods directly
(Not viable - breaks encapsulation and maintainability)

## Decision Outcome

**Chosen option**: Option 3 (Public wrappers with structured dictionary returns)

**Rationale**:
- **Maintains encapsulation**: Private methods stay private
- **Consistent API**: All public methods return `Dict[str, int]`
- **Testable**: External code can call public methods
- **Self-documenting**: Return dictionaries are explicit
- **Future-proof**: Can add fields to return dict without breaking signature

## Implementation

### Public API Methods

```python
def collect_prices(self, coin_symbols: List[str]) -> Dict:
    """
    Public API for price collection

    Args:
        coin_symbols: List of coin symbols to collect prices for

    Returns:
        Dict with 'count' (number of prices collected) and 'errors' (number of errors)
    """
    count, errors = self._collect_prices(coin_symbols)
    return {'count': count, 'errors': errors}

def collect_reddit(self, coin_symbols: List[str]) -> Dict:
    """
    Public API for Reddit collection

    Args:
        coin_symbols: List of coin symbols to collect Reddit data for

    Returns:
        Dict with 'count' (number of posts collected) and 'errors' (number of errors)
    """
    count, errors = self._collect_reddit(coin_symbols)
    return {'count': count, 'errors': errors}

def collect_tiktok(self, coin_symbols: List[str]) -> Dict:
    """
    Public API for TikTok collection

    Args:
        coin_symbols: List of coin symbols to collect TikTok data for

    Returns:
        Dict with 'count' (number of videos collected) and 'errors' (number of errors)
    """
    count, errors = self._collect_tiktok(coin_symbols)
    return {'count': count, 'errors': errors}
```

### Usage Example

```python
# Integration test
collector = UnifiedCollector()

# Test price collection independently
result = collector.collect_prices(['DOGE', 'PEPE'])
assert result['count'] == 2
assert result['errors'] == 0

# Test Reddit collection independently
result = collector.collect_reddit(['DOGE'])
assert result['count'] > 0
```

### Before (No Public API):
```python
# Tests had to call collect_all() - couldn't test collectors independently
collector = UnifiedCollector()
total_records, total_errors = collector.collect_all()
# Can't tell which collector failed or succeeded
```

### After (Clean Public API):
```python
# Tests can call individual collectors
collector = UnifiedCollector()

price_result = collector.collect_prices(['DOGE'])
assert price_result['count'] > 0

reddit_result = collector.collect_reddit(['DOGE'])
assert reddit_result['count'] > 0
```

## Consequences

### Positive
- ✅ **Testable**: Each collector can be tested independently
- ✅ **Clear API**: Public methods have docstrings and type hints
- ✅ **Structured returns**: Dictionary returns are self-documenting
- ✅ **Maintainable**: Private implementation can change without affecting API
- ✅ **Scheduler-friendly**: Background tasks can call specific collectors

### Negative
- ❌ **Code duplication**: Three similar wrapper methods
- ❌ **Extra layer**: Additional function call overhead (negligible)

### Neutral
- 🔧 **Breaking change**: None - new methods, didn't change existing `collect_all()`
- 🔧 **Performance**: No measurable impact (wrapper overhead < 1ms)

## Testing Impact

This change enabled 15 previously failing tests to pass:

### Tests Now Possible:
```python
def test_collect_prices_returns_correct_count():
    """Test price collection returns count"""
    collector = UnifiedCollector()
    result = collector.collect_prices(['DOGE', 'PEPE'])
    assert 'count' in result
    assert 'errors' in result
    assert result['count'] == 2

def test_collect_reddit_handles_errors():
    """Test Reddit collection error handling"""
    collector = UnifiedCollector()
    result = collector.collect_reddit(['INVALID_COIN'])
    assert result['errors'] > 0

def test_collect_tiktok_respects_max_videos():
    """Test TikTok collection limits"""
    collector = UnifiedCollector(scraper_config={'max_videos': 5})
    result = collector.collect_tiktok(['DOGE'])
    assert result['count'] <= 5
```

## Design Principles Reinforced

### 1. Test-Driven Development
Writing tests exposed the missing API. Tests drove design improvement.

### 2. API-First Design
Public interface should be designed consciously, not as an afterthought.

### 3. Encapsulation
Implementation details (`_private` methods) hidden from users.

### 4. Self-Documenting Code
Return dictionaries with named keys are clearer than tuples.

### 5. Consistency
All three collectors follow the same pattern:
- Take `List[str]` (coin symbols)
- Return `Dict[str, int]` (count and errors)

## Related Decisions

- [ADR-003: Test Coverage Strategy](./003-test-coverage-strategy.md) - Defines what to test
- [Future] ADR on error handling patterns across collectors

## Lessons Learned

### 1. Design APIs Before Implementation
We implemented collection logic first, API second. Should be reversed.

### 2. Tests Reveal Design Flaws
The lack of public API wasn't obvious until we tried to test it.

### 3. Python Conventions Matter
Respecting `_private` naming prevents future maintenance headaches.

### 4. Consistent Return Types Simplify Testing
All collectors returning the same structure makes tests predictable.

## Future Enhancements

### Enhanced Return Structure
Could expand return dictionary in the future without breaking compatibility:
```python
return {
    'count': 10,
    'errors': 0,
    'duration': 2.5,      # seconds
    'quality_score': 95,   # 0-100
    'timestamp': datetime.now()
}
```

### Async API (Future Consideration)
```python
async def collect_prices_async(self, coin_symbols: List[str]) -> Dict:
    """Async version for concurrent collection"""
    pass
```

## References

- Implementation: `/collectors/unified_collector.py`
- Tests: `/tests/integration/test_unified_collector.py`
- Python naming conventions: PEP 8
- API design principles: "Design Patterns" by Gang of Four

## Revision History

- **November 26, 2025**: Tests revealed missing public API
- **November 27, 2025**: Public methods implemented
- **November 27, 2025**: 15 tests converted to use new API (all passing)
- **November 28, 2025**: ADR documented
