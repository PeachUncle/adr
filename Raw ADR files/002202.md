# ADR-001: vnstock Integration Strategy

## Status
✅ **ACCEPTED** - Implemented in `libs/vnstock/`

## Context

The system requires reliable access to Vietnamese stock market data including prices, trading volumes, and news. Multiple data sources were evaluated for integration.

## Decision

Implement vnstock library as the primary data source with a custom wrapper layer.

## Rationale

### vnstock Library Advantages
- **Comprehensive Data**: Covers all Vietnamese stocks (HOSE, HNX, UPCOM)
- **Multiple Data Types**: Prices, volumes, news, company information
- **Active Maintenance**: Regular updates and bug fixes
- **Python Native**: Direct integration with our Python stack

### Wrapper Implementation Benefits
- **Rate Limiting**: Prevent API abuse and ensure stability
- **Caching**: Reduce redundant API calls and improve performance
- **Error Handling**: Standardized exception handling across the system
- **Data Validation**: Ensure data quality before processing

## Implementation Details

### Core Components ✅
```python
# libs/vnstock/vnstock_client.py
class VnstockClient:
    def __init__(self, source: str = 'VCI', rate_limit: float = 0.5)
    
    @cached(ttl=3600)
    def get_all_symbols(self) -> List[StockListing]
    
    def get_price_history(self, symbol: str, start: str, end: str, 
                         interval: str = '1D') -> List[StockPrice]
    
    def get_news(self, symbol: str) -> List[StockNews]
```

### Data Models ✅
```python
# libs/vnstock/models.py
@dataclass
class StockPrice:
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class StockNews:
    symbol: str
    title: str
    publish_date: datetime
    source: str
    url: Optional[str] = None
```

### Error Handling ✅
```python
# libs/vnstock/exceptions.py
class VnstockError(Exception): pass
class RateLimitError(VnstockError): pass
class DataNotFoundError(VnstockError): pass
```

## Consequences

### Positive
- **Reliable Data Source**: Established library with proven track record
- **Standardized Interface**: Consistent data access patterns
- **Performance Optimization**: Built-in caching and rate limiting
- **Error Resilience**: Comprehensive error handling

### Negative
- **External Dependency**: Reliance on third-party library
- **API Limitations**: Subject to vnstock's rate limits and availability
- **Data Format Constraints**: Must work within vnstock's data structures

## Alternatives Considered

### Direct Exchange APIs
- **Rejected**: Complex authentication, limited access, high costs

### Multiple Data Providers
- **Rejected**: Increased complexity, data consistency issues

### Web Scraping
- **Rejected**: Legal concerns, reliability issues, maintenance overhead

## Monitoring and Maintenance

### Performance Metrics ✅
- API response times
- Rate limit compliance
- Cache hit rates
- Error rates by exception type

### Maintenance Tasks
- Regular vnstock library updates
- Cache TTL optimization
- Rate limit adjustment based on usage patterns
- Error pattern analysis

## Future Considerations

### Potential Enhancements
- **Multiple Source Support**: Add backup data sources
- **Advanced Caching**: Implement distributed caching with Redis
- **Data Quality Monitoring**: Automated data validation and alerting
- **Historical Data Backfill**: Bulk historical data import capabilities

### Migration Strategy
If vnstock becomes unavailable:
1. Implement adapter pattern for alternative sources
2. Maintain existing interface contracts
3. Gradual migration with parallel data validation
4. Rollback capability to vnstock if needed