# ADR 02: Rounding and Tax Rules

## Status
**Approved** - 2025-01-31

## Context
The quotation system requires precise financial calculations with proper rounding and tax handling to ensure compliance with New Zealand business requirements and prevent calculation errors.

## Decision
We will implement the following rules for rounding and tax calculations:

### **Currency and Precision**
- **Currency**: NZD (New Zealand Dollar)
- **Decimal Places**: Two decimal places (0.00) for all monetary amounts
- **Rounding Method**: Standard half-up rounding at each calculation step

### **Tax Rules**
- **Default Tax Rate**: 15% GST (Goods and Services Tax)
- **Tax Application**: Applied to subtotal after discounts
- **Tax Exemptions**: Support for tax-exempt line items and services
- **Future Flexibility**: Architecture supports variable tax rates and exemptions

### **Rounding Implementation**
1. **Line Level**: Round each line item total to 2 decimal places
2. **Subtotal**: Sum of rounded line items (no additional rounding)
3. **Tax Calculation**: Round tax amount to 2 decimal places
4. **Grand Total**: Final rounded total

### **Numeric Types**
- **Prisma Decimal**: Use Prisma Decimal type for all monetary calculations
- **Precision**: Configure Decimal with appropriate precision for currency
- **No Floats**: Avoid floating-point arithmetic for financial calculations

## Consequences

### **Positive**
- **Accuracy**: Eliminates floating-point precision errors
- **Compliance**: Meets NZ GST requirements
- **Consistency**: Standardized rounding across all calculations
- **Auditability**: Clear calculation trail for financial records

### **Negative**
- **Complexity**: Requires careful implementation of rounding logic
- **Performance**: Decimal arithmetic slightly slower than float operations
- **Storage**: Decimal types use more storage than simple numeric types

### **Risks**
- **Rounding Accumulation**: Multiple rounding steps could compound errors
- **Tax Rate Changes**: Future GST rate changes require system updates
- **International Expansion**: Multi-currency support will need additional rules

## Implementation Notes

### **Future Considerations**
- **Variable Tax Rates**: Support for different tax rates by service type
- **Tax Exemptions**: Non-profit organizations, government entities
- **Multi-Currency**: Support for international customers
- **Exchange Rates**: Real-time currency conversion
- **Volume Discounts**: Tiered pricing based on project size

### **Validation Requirements**
- **Positive Quantities**: All quantities must be > 0
- **Valid Rates**: Hourly rates must be reasonable (> $0, < $1000)
- **Discount Limits**: Percentage discounts ≤ 100%
- **Tax Compliance**: Ensure tax calculations meet NZ requirements
- **Currency Format**: All amounts in NZD format (0.00)

### **Testing Requirements**
- **Unit Tests**: Test all calculation functions with known inputs/outputs
- **Property Tests**: Verify rounding invariants with random inputs
- **Edge Cases**: Test zero amounts, negative amounts, very small amounts
- **Performance Tests**: Ensure 1000+ calculations complete under 1 second
