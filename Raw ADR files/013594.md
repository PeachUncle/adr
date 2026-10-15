# Architecture Decision Records (ADRs) for Pallet Storage Booking System

## ADR-001: Core Multi-Tenant Booking Architecture

**Status:** Accepted  
**Date:** Initial Design Phase  

### Context
We need to build a comprehensive pallet storage booking platform that supports:
- Multiple companies (tenants) operating facilities
- Complex slot-based inventory management
- Real-time availability tracking
- Multi-day booking capabilities
- Audit trails for all operations

### Decision
Implement a four-layer architecture:
1. **Organizational Layer** (Companies → Facilities)
2. **Inventory Layer** (Slots with capacity management)
3. **Booking Layer** (Reservations with status tracking)
4. **Billing Layer** (Invoices and receipts)

### Consequences
- **Positive:** Clean separation of concerns, scalable multi-tenancy
- **Negative:** Increased complexity in queries across layers
- **Mitigation:** Use proper indexing and query optimization

---

## ADR-002: Slot-Based Inventory Model

**Status:** Accepted  
**Date:** Initial Design Phase  

### Context
Traditional inventory systems track individual items, but pallet storage operates on:
- Time-based availability (daily slots)
- Capacity limits per day
- Hold/reservation mechanisms
- Multi-day booking spans

### Decision
Create a **Slots** model where:
- Each slot represents a facility's capacity for a specific date
- Track `capacity`, `occupied`, and `held` separately
- Support booking holds to prevent double-booking during checkout
- Enable multi-day bookings through date ranges

### Consequences
- **Positive:** Prevents overbooking, supports complex availability calculations
- **Negative:** Requires careful management of held vs occupied inventory
- **Risk:** Hold cleanup mechanisms needed to prevent permanent locks

---

## ADR-003: Booking Status Lifecycle with Audit Trail

**Status:** Accepted  
**Date:** Initial Design Phase  

### Context
Bookings go through multiple states and we need full auditability for:
- Customer service inquiries
- Financial reconciliation
- Dispute resolution
- Compliance requirements

### Decision
Implement status tracking with:
- Primary status field in `Bookings` table
- Complete audit trail in `BookingStatusHistory`
- Standard lifecycle: NEW → HELD → CONFIRMED → CANCELLED

### Consequences
- **Positive:** Full audit trail, clear status transitions
- **Negative:** Additional storage overhead
- **Mitigation:** Implement data retention policies for old audit records

---

## ADR-004: Flexible Feature-Based Pricing System

**Status:** Accepted  
**Date:** Iteration 2 - Feature Enhancement  

### Context
Initial schema was too rigid for real-world requirements:
- Different facilities offer different add-on services (CCTV, Cold Storage, 24/7 Access)
- Pricing models vary: flat fees, per-pallet charges, percentage surcharges
- Features need to be configurable per facility
- Historical pricing must be preserved for billing accuracy

### Decision
Introduce a comprehensive feature system:

```sql
Feature → FeaturePricing (time-bound pricing rules)
Facility → FacilityFeatures (available features per facility)
Booking → BookingFeatures (snapshot at booking time)
```

**Pricing Calculation Types:**
- `FLAT`: Fixed charge regardless of pallets/days
- `PALLET_PER_DAY`: Charge per pallet per day
- `PERCENTAGE_ON_BASE`: Percentage surcharge on base rate

### Consequences
- **Positive:** Highly flexible pricing, facility-specific feature menus
- **Negative:** Complex pricing calculations, multiple joins required
- **Risk:** Pricing snapshot integrity must be maintained

---

## ADR-005: Time-Bound Pricing with Historical Preservation

**Status:** Accepted  
**Date:** Iteration 2 - Pricing Enhancement  

### Context
Pricing changes frequently due to:
- Market conditions
- Seasonal demands
- Promotional campaigns
- Regulatory changes

We need to:
- Support price changes without affecting existing bookings
- Maintain historical accuracy for invoicing
- Handle promotional pricing
- Support multiple currencies

### Decision
Implement time-bound pricing tables:

**PricingBase:**
- `effectiveFrom` / `effectiveTo` date ranges
- Support for promotional rates
- Currency specification

**BookingPricing:**
- Snapshot pricing at booking confirmation
- Support rate changes mid-booking
- Detailed breakdown for transparency

### Consequences
- **Positive:** Price integrity, promotional flexibility, multi-currency support
- **Negative:** Complex price calculation logic
- **Mitigation:** Comprehensive testing of edge cases (rate changes, overlaps)

---

## ADR-006: Global Tax Configuration System

**Status:** Accepted  
**Date:** Iteration 2 - Tax Compliance  

### Context
Tax requirements vary by:
- Country and region
- Tax type (VAT, SST, Service Tax)
- Time periods (tax rate changes)
- Business operations location

### Decision
Create `GlobalTax` table with:
- Time-bound tax rates
- Geographic specificity (country/region)
- Multiple tax types support
- Automatic application based on facility location

### Consequences
- **Positive:** Automated tax compliance, geographic flexibility
- **Negative:** Complex tax calculation logic
- **Risk:** Tax law changes require prompt updates

---

## ADR-007: Comprehensive Billing Layer

**Status:** Accepted  
**Date:** Initial Design + Enhancement  

### Context
Financial operations require:
- Clear separation between booking value and payment collection
- Support for partial payments
- Multiple payment methods
- Deposit and balance billing
- Receipt generation for compliance

### Decision
Implement separate `Invoices` and `Receipts` tables:

**Invoices:**
- Link to bookings
- May split booking total (deposit/balance)
- Due date tracking

**Receipts:**
- Track actual payments against invoices
- Support partial and multiple payments
- Payment method and reference tracking

### Consequences
- **Positive:** Financial transparency, flexible payment handling
- **Negative:** Additional complexity in payment reconciliation
- **Benefit:** Clear audit trail for financial operations

---

## ADR-008: Facility Media Management

**Status:** Accepted  
**Date:** Iteration 3 - Media Enhancement  

### Context
Facilities need rich media presentation:
- Multiple photos per facility
- Video tours
- Document attachments (certifications, floor plans)
- Media updates without facility record changes

### Decision
Create dedicated `FacilityMedia` table:
- External file storage references
- Multiple media per facility
- Soft delete capability
- Separate media lifecycle from facility data

### Consequences
- **Positive:** Rich facility presentation, flexible media management
- **Negative:** Additional storage and bandwidth costs
- **Consideration:** CDN integration for performance optimization

---

## ADR-009: Database Design Principles

**Status:** Accepted  
**Date:** Throughout Development  

### Context
Ensure consistent, maintainable database design across all iterations.

### Decision
Adopt standard patterns:

**ID Strategy:**
- Auto-increment primary keys (`id`)
- Business-friendly unique identifiers (`entityId`)
- Proper foreign key relationships

**Audit Fields:**
- Soft delete with `isDeleted` flags
- Timestamp tracking (`createdAt`, `updatedAt`)
- Unix timestamp fields for external integrations
- Creator/modifier tracking where needed

**Indexing Strategy:**
- Primary business keys
- Foreign key relationships
- Query optimization for common access patterns
- Date range queries for time-bound data

### Consequences
- **Positive:** Consistent patterns, optimized queries, data integrity
- **Negative:** Storage overhead from audit fields
- **Benefit:** Simplified debugging and data recovery

---

## ADR-010: Data Model Evolution Strategy

**Status:** Accepted  
**Date:** Ongoing  

### Context
The system has evolved from a simple booking model to a comprehensive platform. Future enhancements are expected.

### Decision
Maintain backward compatibility while enabling feature growth:

**Migration Strategy:**
- Preserve existing data integrity
- Add new features through additional tables
- Use junction tables for flexible relationships
- Snapshot critical data to prevent historical corruption

**Extension Points:**
- Feature system allows new add-on services
- Pricing system supports new calculation methods
- Tax system accommodates regulatory changes
- Media system supports new content types

### Consequences
- **Positive:** Future-proof architecture, safe evolution
- **Negative:** Technical debt accumulation over time
- **Mitigation:** Regular architecture reviews and refactoring cycles

---

## Current System Overview

### Core Entities and Relationships

```
Companies (1) → (*) Facilities (1) → (*) Slots
                    ↓
                FacilityFeatures ← Feature
                    ↓              ↓
                FacilityMedia    FeaturePricing

Slots (1) → (*) Bookings → BookingPricing
           ↓              → BookingFeatures
        BookingHolds      → BookingStatusHistory
                         → Invoices → Receipts

PricingBase → BookingPricing
GlobalTax (applied during booking calculation)
```

### Key Design Patterns

1. **Time-Bound Data:** `effectiveFrom`/`effectiveTo` patterns
2. **Soft Deletes:** `isDeleted` flags throughout
3. **Audit Trails:** Status history and timestamp tracking
4. **Snapshots:** Preserve pricing at booking time
5. **Junction Tables:** Flexible many-to-many relationships

### Business Logic Flow

1. **Facility Setup:** Company → Facility → Features → Pricing
2. **Availability:** Slot capacity - occupied - held = available
3. **Booking:** Hold → Feature selection → Price calculation → Confirmation
4. **Billing:** Invoice generation → Payment collection → Receipt tracking

### Technology Decisions

- **Database:** MySQL with Prisma ORM
- **Pricing:** Decimal precision for financial calculations
- **Timestamps:** Unix timestamps for external integrations
- **JSON:** Flexible data storage for variable structures (open hours)
