# ADR-002: Portfolio Performance Complete Backup Restoration Capability

**Date**: 2025-08-22  
**Status**: Accepted  
**Deciders**: Byron, Development Team  
**Consulted**: Portfolio Performance XML Schema Analysis  
**Informed**: Data Quality Team  

## Context

Analysis of the Portfolio Performance XML backup file (`BruceandSueWilliams_sample.xml`) reveals the complete data structure required for full PP instance restoration. The current transaction-centric architecture focuses on import and classification but needs extension to support complete PP backup generation.

**Key Discovery**: The PP XML backup contains everything needed to restore a complete Portfolio Performance instance:
- 53,625 lines of securities with complete price history
- Account and portfolio hierarchies with cross-references
- All transaction history with fees, taxes, and cross-entries
- User settings, bookmarks, and dashboard configurations

## Decision

We will extend the Security Master Service to provide **complete Portfolio Performance backup restoration capability** by:

1. **Expanding database schema** to capture all PP XML elements
2. **Creating PP XML export engine** that generates complete, restorable backup files
3. **Implementing bidirectional synchronization** between database and PP

### Complete PP XML Structure Analysis

#### **Root Client Structure:**
```xml
<client>
  <version>66</version>
  <baseCurrency>USD</baseCurrency>
  <securities>...</securities>
  <watchlists/>
  <accounts>...</accounts>  
  <portfolios>...</portfolios>
  <dashboards/>
  <properties>...</properties>
  <settings>...</settings>
</client>
```

#### **Securities Section:**
- **Securities Master**: ISIN, symbols, WKN, currency, feed configuration
- **Price History**: Complete daily price data (`<price t="2024-07-23" v="2624000000"/>`)
- **Security Attributes**: Notes, feed sources, ticker symbols

#### **Accounts & Portfolios Hierarchy:**
- **Accounts**: Deposit accounts with cash transactions
- **Portfolios**: Security holdings with reference to accounts
- **Cross-References**: Complex relationship between account and portfolio transactions

#### **Transaction Types:**
- **Account Transactions**: Cash deposits, withdrawals, fees
- **Portfolio Transactions**: BUY, SELL, DIVIDEND with share quantities
- **Cross-Entries**: Linked account/portfolio transaction pairs
- **Fee/Tax Units**: Granular transaction cost breakdown

#### **User Configuration:**
- **Settings**: Bookmarks, user preferences
- **Properties**: Display configurations, naming conventions
- **Dashboards**: Custom dashboard layouts

## Implementation Strategy

### Phase 1: Database Schema Extensions

#### **New Tables Required:**

```sql
-- PP Client Configuration
CREATE TABLE pp_client_config (
    id SERIAL PRIMARY KEY,
    version INTEGER NOT NULL,
    base_currency VARCHAR(3) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- PP Accounts (Deposit/Cash accounts)
CREATE TABLE pp_accounts (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    is_retired BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- PP Portfolios (Security holding accounts)
CREATE TABLE pp_portfolios (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    reference_account_id INTEGER REFERENCES pp_accounts(id),
    is_retired BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- PP Account Transactions (Cash movements)
CREATE TABLE pp_account_transactions (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL,
    account_id INTEGER REFERENCES pp_accounts(id),
    transaction_date DATE NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    security_id INTEGER REFERENCES securities_master(id),
    shares DECIMAL(18,8) DEFAULT 0,
    transaction_type VARCHAR(20) NOT NULL, -- BUY, SELL, DEPOSIT, etc.
    cross_entry_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- PP Portfolio Transactions (Security movements)
CREATE TABLE pp_portfolio_transactions (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL,
    portfolio_id INTEGER REFERENCES pp_portfolios(id),
    transaction_date DATE NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    security_id INTEGER REFERENCES securities_master(id),
    shares DECIMAL(18,8) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL, -- BUY, SELL, DIVIDEND
    -- Cross-reference to account transaction
    linked_account_transaction_id INTEGER REFERENCES pp_account_transactions(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- PP Transaction Units (Fees, Taxes, etc.)
CREATE TABLE pp_transaction_units (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER, -- Can reference either account or portfolio transaction
    transaction_type VARCHAR(20) NOT NULL, -- 'ACCOUNT' or 'PORTFOLIO'
    unit_type VARCHAR(10) NOT NULL, -- 'FEE', 'TAX'
    amount DECIMAL(15,2) NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Daily Price History
CREATE TABLE pp_security_prices (
    id SERIAL PRIMARY KEY,
    security_id INTEGER REFERENCES securities_master(id),
    price_date DATE NOT NULL,
    price_value BIGINT NOT NULL, -- PP stores as integer (multiply by 100000000)
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(security_id, price_date)
);

-- PP User Settings
CREATE TABLE pp_settings (
    id SERIAL PRIMARY KEY,
    setting_category VARCHAR(50) NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(setting_category, setting_key)
);

-- PP Bookmarks
CREATE TABLE pp_bookmarks (
    id SERIAL PRIMARY KEY,
    label VARCHAR(255) NOT NULL,
    pattern VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Phase 2: PP XML Export Engine

#### **XML Generation Service:**

```python
class PPXMLExportService:
    """Generate complete Portfolio Performance XML backup from database."""
    
    def generate_complete_backup(self) -> str:
        """Generate complete PP XML backup file."""
        
    def export_securities_section(self) -> str:
        """Export securities with complete price history."""
        
    def export_accounts_section(self) -> str:
        """Export accounts with all transactions and cross-references."""
        
    def export_portfolios_section(self) -> str:
        """Export portfolios with holdings and transaction history."""
        
    def export_settings_section(self) -> str:
        """Export user settings, bookmarks, and preferences."""
```

### Phase 3: Bidirectional Synchronization

#### **Import PP XML → Database:**
- Parse complete PP backup files
- Populate all PP-specific tables
- Maintain UUIDs and cross-references
- Import complete price history

#### **Export Database → PP XML:**
- Generate valid PP XML backup files
- Preserve all UUIDs and relationships
- Include complete transaction history
- Maintain PP schema compliance

## Rationale

### Benefits:

1. **Complete Data Sovereignty**: Full control over Portfolio Performance data
2. **Disaster Recovery**: Generate PP backups from database at any time
3. **Data Migration**: Move between PP instances seamlessly
4. **Advanced Analytics**: Query PP data with SQL for complex reporting
5. **Compliance**: Complete audit trail of all financial transactions
6. **Integration**: Connect PP data with external systems via database

### Business Impact:

- **Zero Data Loss**: Every PP data element preserved and restorable
- **Business Continuity**: Database becomes authoritative source for PP restoration
- **Scalability**: Support multiple PP instances from single database
- **Automation**: Scheduled backup generation and validation

## Consequences

### Positive:
- **Complete PP Backup Capability**: Generate full restoration files from database
- **Enhanced Data Quality**: Cross-validation between institution imports and PP data
- **Advanced Reporting**: SQL access to complete portfolio history
- **Future-Proof**: Independent of PP version changes

### Negative:
- **Increased Complexity**: Additional tables and relationships to maintain
- **Storage Requirements**: Complete price history storage
- **Processing Overhead**: XML generation for large portfolios

### Technical Considerations:
- **PP Version Compatibility**: Support multiple PP XML schema versions
- **UUID Management**: Preserve PP's internal UUID references
- **Price Data Volume**: Efficient storage and retrieval of daily price history
- **XML Validation**: Ensure generated XML passes PP import validation

## Implementation Timeline

### Phase 1: Schema Extension (2 weeks)
- Design and implement PP-specific tables
- Create migration scripts from current schema
- Implement PP XML parser for complete import

### Phase 2: XML Export Engine (3 weeks)  
- Build PP XML generation service
- Implement transaction cross-reference logic
- Add price history export functionality

### Phase 3: Integration & Testing (2 weeks)
- End-to-end backup/restore testing
- PP version compatibility validation
- Performance optimization for large datasets

## Success Criteria

1. **Round-trip Validation**: Import PP XML → Database → Export PP XML produces identical result
2. **PP Compatibility**: Generated XML backups successfully restore in Portfolio Performance
3. **Complete Data Preservation**: All PP elements (transactions, settings, prices) maintained
4. **Performance**: Generate backup for 10,000+ transactions within 30 seconds

## Related Decisions

- **ADR-001**: Transaction-Centric Architecture (foundation)
- **ADR-003**: Price Data Management Strategy (pending)
- **ADR-004**: PP Version Compatibility Matrix (pending)

## References

- Portfolio Performance XML Schema Documentation
- PP Backup/Restore Process Analysis
- Institution Transaction Import Requirements (ADR-001)
- Sample PP XML Backup Analysis (`BruceandSueWilliams_sample.xml`)