# ADR-003: Multi-Currency Support and FX Rate Management

## Status
**Approved** - January 2025

## Context
Pivotal Flow needs to support multi-currency quotes and invoices for international clients. The system must handle:
- Multiple currencies with proper decimal place rounding
- Exchange rate management with source tracking
- FX rate resolution with fallback strategies
- Currency validation and governance
- Reporting currency conversion without persisting converted totals

## Decision
Implement a comprehensive multi-currency system with the following architecture:

### 1. Currency Management
- **Currency Table**: Store ISO 4217 currency codes with decimal places
- **Typed Columns Only**: All monetary values stored in typed decimal columns
- **JSONB for Metadata**: Only display notes and non-monetary metadata in JSONB
- **Decimal Places**: Support different rounding per currency (e.g., JPY = 0, USD = 2)

### 2. FX Rate Management
- **FX Rate Table**: Store exchange rates with source and effective date
- **Rate Resolution**: Get rate as of specific date with fallback to most recent
- **Inverse Rate Fallback**: If direct rate not found, calculate from inverse rate
- **Source Tracking**: Track rate source (RBNZ, ECB, manual, etc.)
- **Verification**: Mark rates as verified/unverified

### 3. Quote and Invoice Currency Support
- **Transactional Currency**: Store all monetary values in the quote/invoice currency
- **FX Rate Snapshot**: Store FX rate ID used at creation time
- **Display Conversion**: Show converted amounts in responses without persisting
- **Currency Validation**: Ensure currency exists and is active

### 4. Calculator Extensions
- **Currency Decimals**: Accept currency decimal places for proper rounding
- **FX Conversion Helper**: `convertMoney()` function for display conversion
- **Rounding Strategy**: Half-up rounding to currency-specific decimal places

### 5. Metrics and Monitoring
- **FX Lookup Metrics**: Track lookup success/failure rates
- **Conversion Duration**: Monitor FX conversion performance
- **Prometheus Counters**: `pivotal_fx_lookup_total`, `pivotal_fx_miss_total`

## Consequences

### Positive
- **Accurate Calculations**: Currency-specific rounding prevents precision errors
- **Audit Trail**: FX rate snapshots provide historical accuracy
- **Flexible Display**: Support multiple reporting currencies without data duplication
- **Performance**: Efficient rate lookup with caching and fallbacks
- **Compliance**: Proper source tracking for regulatory requirements

### Negative
- **Complexity**: Additional tables and logic for currency management
- **Data Volume**: FX rate history can grow large over time
- **Validation**: Need to ensure currency codes are valid ISO 4217 codes

### Risks
- **Rate Availability**: Missing FX rates could block quote creation
- **Rounding Differences**: Different rounding strategies between currencies
- **Historical Accuracy**: FX rate changes affect historical data interpretation

## Implementation Details

### Schema Changes
```sql
-- Currency table with decimal places
CREATE TABLE currencies (
  code VARCHAR(3) PRIMARY KEY, -- ISO 4217 code
  name VARCHAR(100) NOT NULL,
  symbol VARCHAR(10),
  decimals INTEGER NOT NULL DEFAULT 2, -- Decimal places for rounding
  is_active BOOLEAN NOT NULL DEFAULT true
);

-- FX rates with source tracking
CREATE TABLE fx_rates (
  id TEXT PRIMARY KEY,
  base_currency VARCHAR(3) NOT NULL REFERENCES currencies(code),
  quote_currency VARCHAR(3) NOT NULL REFERENCES currencies(code),
  rate DECIMAL(15,6) NOT NULL,
  effective_from DATE NOT NULL,
  source VARCHAR(50) NOT NULL, -- RBNZ, ECB, manual, etc.
  verified BOOLEAN NOT NULL DEFAULT false,
  UNIQUE(base_currency, quote_currency, effective_from)
);
```

### Calculator Updates
```typescript
// Currency-specific rounding
function roundToCurrencyDecimals(decimal: Decimal, decimals: number): Decimal {
  return decimal.toDecimalPlaces(decimals, Decimal.ROUND_HALF_UP);
}

// FX conversion helper
function convertMoney(
  money: MoneyAmount, 
  targetCurrency: string, 
  exchangeRate: number,
  targetDecimals: number
): MoneyAmount {
  return {
    amount: roundToCurrencyDecimals(money.amount.times(exchangeRate), targetDecimals),
    currency: targetCurrency
  };
}
```

### Repository Pattern
```typescript
class CurrencyRepository {
  async getFxRate(baseCurrency: string, quoteCurrency: string, asOfDate: Date): Promise<FxRate | null>
  async getFxRateWithFallback(baseCurrency: string, quoteCurrency: string, asOfDate: Date): Promise<FxRate | null>
  async getCurrencyDecimals(currencyCode: string): Promise<number>
  async validateCurrency(currencyCode: string): Promise<boolean>
}
```

## Examples

### Quote Creation in AUD
```typescript
// Get currency decimals for AUD (2 decimal places)
const audDecimals = await currencyRepo.getCurrencyDecimals('AUD');

// Get FX rate for AUD/NZD as of quote date
const fxRate = await currencyRepo.getFxRateWithFallback('AUD', 'NZD', quoteDate);

// Calculate quote with AUD decimals
const calculation = calculateQuote(input, audDecimals);

// Store quote with AUD currency and FX rate snapshot
const quote = await createQuote({
  ...calculation,
  currency: 'AUD',
  fxRateId: fxRate.id,
  exchangeRate: fxRate.rate
});
```

### Display Conversion
```typescript
// Convert for display without persisting
const displayAmount = convertMoney(
  { amount: new Decimal('1000.00'), currency: 'AUD' },
  'NZD',
  fxRate.rate,
  2 // NZD decimals
);
// Result: { amount: new Decimal('1080.50'), currency: 'NZD' }
```

## Monitoring

### Prometheus Metrics
```typescript
// FX lookup counters
const fxLookupTotal = new Counter({
  name: 'pivotal_fx_lookup_total',
  help: 'Total FX rate lookups',
  labelNames: ['base_currency', 'quote_currency', 'result']
});

const fxMissTotal = new Counter({
  name: 'pivotal_fx_miss_total', 
  help: 'Total FX rate misses',
  labelNames: ['base_currency', 'quote_currency']
});

// FX conversion duration histogram
const fxConversionDuration = new Histogram({
  name: 'pivotal_fx_conversion_duration_ms',
  help: 'FX conversion duration in milliseconds',
  labelNames: ['base_currency', 'quote_currency']
});
```

## Testing Strategy

### Unit Tests
- Currency decimal place validation
- FX rate resolution with fallbacks
- Rounding accuracy per currency
- Conversion helper functions

### Integration Tests
- Quote creation in different currencies
- FX rate lookup and fallback scenarios
- Currency validation in quote/invoice flows

### Property Tests
- Non-negative totals invariant
- Rounding consistency across currencies
- FX conversion reversibility

## Related ADRs
- ADR-001: Database Schema Design
- ADR-002: JSONB Usage Guidelines
- ADR-004: Performance Budgets

## References
- [ISO 4217 Currency Codes](https://en.wikipedia.org/wiki/ISO_4217)
- [Decimal.js Documentation](https://mikemcl.github.io/decimal.js/)
- [PostgreSQL Decimal Type](https://www.postgresql.org/docs/current/datatype-numeric.html)
