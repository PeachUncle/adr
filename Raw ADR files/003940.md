# ADR-001: Business Model - Transportation Services Provider

**Date**: 2025-10-24
**Status**: Accepted
**Deciders**: Product, Engineering

## Context

Initial implementation incorrectly positioned Southern Haulers as a TMS SaaS platform provider. After reviewing southernhaulers.net and competitive landscape, the correct business model is:

**Southern Haulers is a transportation services provider (carrier/broker)**, not a software vendor.

## Business Model

### Core Services
1. **Container Drayage**: Port-to-door and door-to-port container transport
2. **Agricultural Hauling**: Bulk agricultural product transportation (primary specialization)
3. **Warehousing & Transloading**: 300+ container storage capacity, on-site transloading
4. **Refrigerated Transport**: Temperature-controlled freight services

### Geographic Focus
- Southeastern United States (primary)
- South Georgia base of operations
- Port coverage: Savannah, Charleston, Jacksonville

### Target Customers
- Agricultural shippers (peanuts, pecans, cotton, feed, fertilizer)
- Importers/exporters requiring drayage services
- Manufacturers needing warehousing/transloading
- Shippers requiring refrigerated transport

### Revenue Model
- Per-mile rates for truckload services
- Container drayage fees (pickup/delivery)
- Warehousing/storage fees (per day/per container)
- Transloading service fees
- Accessorial charges (detention, TMF, per-diem, etc.)

## Technology Role

The TMS platform is **internal operations infrastructure**, NOT a product:
- Manages Southern Haulers' own fleet operations
- Dispatch, driver management, shipment tracking
- Quote-to-booking workflow (CPQ)
- Customer portal for shipment visibility
- Driver/carrier lease-on portal

## Competitive Positioning

### Direct Competitors
- GoDrayage (Miami)
- Southern Cartage (Miami)
- American Transport Inc. (Charleston)
- Harbor Transport (Southeast)

### Differentiation
1. **Agricultural Specialization**: Deep expertise in ag commodity handling
2. **Integrated Warehousing**: 300+ container capacity + transloading on-site
3. **Technology-Enabled**: Real-time tracking, automated scheduling, customer portal
4. **Lease-On Program**: Scalable capacity via owner-operator network
5. **Compliance-First**: FMCSA, TWIC, Truth-in-Leasing, safety standards

## Website Content Strategy

### Home Page Focus
- **Hero**: "Premier Agricultural & Container Drayage Services in the Southeast"
- **Services**: Container Drayage, Agricultural Hauling, Warehousing, Refrigerated
- **Proof Points**: Container capacity, on-time delivery %, geographic coverage
- **CTAs**: Get Quote, Track Shipment, Become a Driver

### Service Pages
1. `/services/container-drayage` - Port drayage, last-mile delivery
2. `/services/agricultural-hauling` - Bulk ag commodities, specialized equipment
3. `/services/warehousing` - Storage, transloading, cross-docking
4. `/services/refrigerated` - Temp-controlled transport

### Portals
- **Shipper Portal** (`/portal`): Track shipments, request quotes, view invoices
- **Driver Portal** (`/drivers`): Lease-on application, load assignments, documents
- **Admin Portal** (`/admin`): Internal dispatch, billing, operations

## Decision

Rebuild website to reflect transportation services provider positioning:
1. Remove all "TMS SaaS platform" language
2. Focus on transportation services we provide (not software we sell)
3. Highlight container drayage + agricultural hauling specialization
4. Position technology as operational advantage (not product)
5. Create service-specific landing pages
6. Build shipper portal for shipment tracking
7. Build driver portal for lease-on program

## Consequences

### Positive
- Accurate market positioning
- Clear value proposition for shippers
- Competitive differentiation via ag specialization + warehousing
- Technology as operational advantage

### Negative
- Need to rewrite all marketing copy
- Adjust CLAUDE.md to reflect correct business model
- Refactor customer portal UI/UX for shipper tracking (not TMS management)

## References
- southernhaulers.net (current site)
- Penske Logistics dedicated transportation
- GoDrayage, Southern Cartage (competitors)
- CLAUDE.md (to be updated)
