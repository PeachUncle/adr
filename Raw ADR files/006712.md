# ADR-002: European Central Bank (ECB) Integration for Exchange Rates

## Status
Accepted

## Context
The b-ro finance application needs to support multi-currency accounts and provide accurate exchange rate conversion for:
- Portfolio aggregation across different currencies
- Historical transaction reporting in a common currency
- Real-time currency conversion for user insights

Key requirements:
1. **Reliable data source**: Free, official, and regularly updated exchange rates
2. **Historical data**: Access to past exchange rates for transaction analysis
3. **Automatic updates**: Daily fetching without manual intervention
4. **Performance**: Fast conversions without impacting user experience
5. **Accuracy**: Precise decimal handling for financial calculations

Evaluated options:
- **European Central Bank (ECB)**: Free XML feeds, EUR-based, official EU data, historical archive
- **Open Exchange Rates**: Free tier limited (1000 requests/month), USD-based
- **Fixer.io**: Formerly free, now paid only
- **CurrencyLayer**: Free tier very limited (100 requests/month)

## Decision
We will use the **European Central Bank (ECB)** as our primary exchange rate data source with the following implementation:

### 1. Data Source Configuration
- **90-Day Feed**: `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml`
  - Updated daily (around 16:00 CET)
  - Fast download (< 50KB)
  - Covers recent trading days
  
- **Historical Feed**: `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml`
  - Complete history since 1999
  - Larger file (~6MB)
  - Used only for gap-filling

### 2. Exchange Rate Strategy
- **Base Currency**: EUR (all ECB rates are EUR-based)
- **Direct Conversion**: For EUR ↔ XXX pairs, use ECB rate directly
- **Triangular Arbitrage**: For non-EUR pairs (e.g., USD ↔ GBP)
  ```
  USD → GBP rate = (EUR → GBP rate) / (EUR → USD rate)
  ```
  
### 3. Update Schedule
- **Daily Updates**: Background job runs at 03:00 UTC
  - Fetches 90-day feed first
  - Detects gaps in database
  - Backfills from historical feed if needed
  - Excludes weekends (no ECB data published)
  
- **Retry Logic**: Exponential backoff (3 attempts)
  - 1st retry: 5 seconds
  - 2nd retry: 15 seconds
  - 3rd retry: 45 seconds

### 4. Data Storage
- **Database Table**: `ExchangeRates`
  ```sql
  CREATE TABLE ExchangeRates (
      Id INTEGER PRIMARY KEY,
      Date DATE NOT NULL,
      BaseCurrency NVARCHAR(3) NOT NULL,  -- Always 'EUR'
      TargetCurrency NVARCHAR(3) NOT NULL,
      Rate DECIMAL(18,6) NOT NULL,
      Source NVARCHAR(20) NOT NULL,  -- 'ECB90Day' or 'ECBHistorical'
      CreatedAt DATETIME NOT NULL,
      UNIQUE(Date, TargetCurrency)
  );
  ```

- **Transaction Rates**: Store exchange rate at transaction creation
  ```sql
  ALTER TABLE Transactions ADD ExchangeRateToEUR DECIMAL(18,6) NULL;
  ```
  - Preserves historical accuracy
  - Computed property `ConvertedAmountEUR` for reporting

### 5. Caching Strategy
- **In-Memory Cache**: `IMemoryCache` with 1-hour TTL
- **Cache Keys**:
  - `exchange_rate_{from}_{to}_{date}` - Specific rate
  - `latest_rates` - All latest rates
  - `supported_currencies` - Available currencies
  
- **Cache Invalidation**: Automatic expiry, no manual clearing

### 6. Supported Currencies
ECB provides ~40 currencies including:
- Major: USD, GBP, CHF, JPY, CNY, CAD, AUD
- European: SEK, NOK, DKK, PLN, CZK, HUF
- Others: INR, BRL, ZAR, KRW, SGD, HKD

### 7. Error Handling
- **Network Failures**: Retry with backoff, log and continue
- **Missing Rates**: Return null, allow graceful degradation
- **Invalid Data**: Validate XML structure, skip malformed entries
- **Database Conflicts**: Upsert logic (update if exists)

## Consequences

### Positive
✅ **Free Forever**: ECB data is public, no API keys or quotas  
✅ **Official Source**: European Union official data, high trust  
✅ **Historical Archive**: Complete data back to 1999  
✅ **Simple Integration**: XML format, no authentication  
✅ **EUR Base**: Natural fit for European finance application  
✅ **Daily Updates**: Automatic with background job  
✅ **Performance**: Caching reduces database queries  
✅ **Accuracy**: 6 decimal places (e.g., 1.234567)  
✅ **Triangular Arbitrage**: Support any currency pair

### Negative
❌ **EUR-Centric**: All conversions go through EUR (not direct USD→GBP from source)  
❌ **Weekend Gaps**: No data on Saturdays/Sundays  
❌ **Delayed Updates**: ECB publishes around 16:00 CET (not real-time)  
❌ **Limited Currencies**: ~40 currencies (no exotic currencies like BTN, AOA)  
❌ **No Intraday Rates**: One rate per day only  
❌ **XML Parsing**: More complex than JSON (but manageable)

### Mitigations
- **Weekend Handling**: Gap detection skips Saturdays/Sundays
- **Missing Currencies**: Allow manual rate entry for unsupported currencies (future)
- **Stale Data**: Use latest available rate if historical date missing
- **Triangular Error**: Small rounding errors acceptable for personal finance

## Alternatives Considered

### 1. Open Exchange Rates
- **Pros**: JSON API, USD-based, many currencies
- **Cons**: Free tier limited to 1000 requests/month, requires API key
- **Rejected**: Quota too restrictive for background job

### 2. Fixer.io
- **Pros**: Good documentation, EUR-based
- **Cons**: No longer has free tier
- **Rejected**: Paid service not suitable

### 3. Manual Entry
- **Pros**: No external dependency
- **Cons**: High maintenance, error-prone
- **Rejected**: Not sustainable

### 4. Cryptocurrency APIs (CoinGecko, etc.)
- **Pros**: Real-time, free
- **Cons**: Volatile, not suitable for fiat currencies
- **Rejected**: Different use case

## Implementation Notes

### Background Job Configuration
```csharp
// Program.cs
builder.Services.AddHostedService<ExchangeRateUpdateJob>();
```

### Currency Service Usage
```csharp
// Get rate for specific date
var rate = await currencyService.GetRateAsync(
    DateOnly.FromDateTime(DateTime.Today), 
    "USD", 
    "EUR");

// Convert amount
var converted = await currencyService.ConvertAmountAsync(
    100.00m, 
    "USD", 
    "GBP", 
    DateOnly.FromDateTime(DateTime.Today));
```

### Portfolio Aggregation
```csharp
// Get total portfolio value in EUR
var total = await aggregationService.GetTotalBalanceInCurrencyAsync("EUR");
```

## Related
- [ADR-001](ADR-001-angular-20-ng-matero.md): Frontend framework selection
- [Building Block View](../05_building_block_view/finance_domain.md): Finance domain architecture
- [Cross-Cutting Concepts](../08_cross_cutting_concepts/currency_conversion.md): Currency conversion strategy

## References
- ECB Exchange Rates: https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html
- ECB XML Feeds: https://www.ecb.europa.eu/stats/eurofxref/
- ISO 4217 Currency Codes: https://www.iso.org/iso-4217-currency-codes.html

## Decision Date
2025-11-09

## Decision Makers
- Marcel Barner (Developer)

## Reviewed
- 2025-11-09: Initial decision and implementation
