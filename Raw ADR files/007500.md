# ADR-011 – Price Calculation System: Age-Based and Student Discounts with Zone Pricing

**Status:** Accepted  
**Date:** 2025-11-24  
**Author:** Niklas Häll

---

## Context

The ticketing system requires a flexible pricing model that supports different user categories (children, students, pensioners, standard users) with appropriate discounts. The system must calculate ticket prices based on:
- User age (for child and pensioner discounts)
- Student status (for student discounts)
- Zone selection (each zone costs one ticket)
- Future extensibility for region-based pricing

The pricing model should be transparent, easy to maintain, and allow for automatic price calculation during ticket creation without requiring manual price entry. Additionally, the system should handle cases where users do not provide age information (defaulting to standard pricing).

---

## Decision

We implement a **price modifier system** with centralized calculation logic. The system uses decimal multipliers (0.0, 0.5, 1.0) applied to a base price per zone, rather than storing fixed price tiers or roles. This approach provides flexibility and makes future price adjustments easier.

**Implementation Details:**
- **Price Modifiers:**
  - `0.0` (Free) – Children under 12 years
  - `0.5` (50% discount) – Students (12-65 years with student flag) or Pensioners (65+ years)
  - `1.0` (Full price) – Standard users (12-65 years, non-student)
- **User Attributes:**
  - `DateOfBirth` (nullable DateTime) – Used to calculate age for child/pensioner discounts
  - `IsStudent` (bool) – Student status flag for discount eligibility
- **Booking Attributes:**
  - `Zone` (string) – Zone selection (Zone A, B, C, D)
  - `Region` (string) – Reserved for future use (empty for now)
  - `PriceModifier` (decimal) – Calculated modifier stored with booking
  - `BasePrice` (decimal) – Base price per zone (configurable, default: 20 SEK)
  - `TotalPrice` (decimal) – Final calculated price (BasePrice × PriceModifier)
- **Calculation Logic:**
  - `PriceCalculationHelper` – Static helper class with centralized calculation methods
  - Age calculation handles null `DateOfBirth` gracefully (defaults to standard pricing)
  - Price calculation occurs automatically during booking creation in `BookingsController`
  - Each zone costs one ticket (extensible to multiple zones per ticket in future)

**Null Handling:**
- If `DateOfBirth` is null: Returns `0.5m` if student, otherwise `1.0m` (standard pricing)
- Users without age information pay full price unless they have student status
- This encourages users to provide age information to receive appropriate discounts

---

## Consequences

**Advantages:**
- **Flexibility** – Price modifiers (0.0, 0.5, 1.0) are easy to adjust without changing business logic. New discount categories can be added by extending the calculation logic.
- **Transparency** – Price modifier and total price are stored with each booking, providing audit trail and transparency for users and administrators.
- **Automatic Calculation** – Prices are calculated automatically during booking creation, reducing manual errors and ensuring consistency.
- **Extensibility** – Zone-based pricing is ready for expansion to multiple zones per ticket. Region field is reserved for future region-based pricing logic.
- **User-Friendly** – Age is optional; users can still create tickets without providing age (defaults to standard pricing). Student discount works independently of age.
- **Centralized Logic** – `PriceCalculationHelper` provides a single source of truth for price calculations, making maintenance and testing easier.
- **GDPR-Friendly** – Age information is optional, reducing data collection requirements while still enabling discounts for users who provide it.

**Disadvantages:**
- **Base Price Configuration** – Base price per zone is configurable via `appsettings.json` (`Pricing:BasePricePerZone`, default: 20 SEK). Can be moved to Azure App Configuration for runtime adjustment without code deployment (future enhancement).
- **Single Zone Per Ticket** – Current implementation assumes one zone per ticket. Multiple zones per ticket requires additional logic (future enhancement).
- **No Price History** – If base prices change, existing bookings retain their original prices (may be desired behavior for audit purposes).
- **Age Calculation Edge Cases** – Age calculation based on date of birth may have edge cases around leap years and time zones (currently uses UTC dates).

---

## Risks / Mitigations

- **Risk:** Base price changes require code deployment.  
  **Mitigation:** Base price is configurable via `appsettings.json` (`Pricing:BasePricePerZone`). For runtime adjustment without code deployment, can be moved to Azure App Configuration with sentinel key pattern for hot-reload (future enhancement).

- **Risk:** Age calculation may be inaccurate for users near age boundaries (e.g., turning 12 or 65).  
  **Mitigation:** Current implementation uses precise date calculation. Consider adding explicit age verification for critical discounts if required by business rules.

- **Risk:** Users may abuse student discount by checking the student flag without verification.  
  **Mitigation:** Student status is currently a simple boolean flag. Future enhancement: Add student verification (e.g., student ID validation, integration with student registry).

- **Risk:** Multiple zones per ticket not yet implemented, limiting ticket flexibility.  
  **Mitigation:** Zone field is stored as string, allowing future expansion. Region field is reserved for future use. Implementation can be extended when business requirements are defined.

---

## Alternatives

- **Fixed Price Tiers with Roles** – Rejected. Storing price tiers as user roles (e.g., "Child", "Student", "Pensioner") would mix authorization roles with pricing logic, creating confusion and maintenance issues.

- **Database-Stored Price Rules** – Rejected. Storing price calculation rules in the database adds complexity and requires database queries for every price calculation. Current approach is simpler and more performant.

- **External Pricing Service** – Rejected. For MVP, an external service adds unnecessary complexity and latency. Can be considered for future if pricing rules become very complex or need real-time updates.

- **Percentage-Based Discounts Instead of Multipliers** – Rejected. Multipliers (0.0, 0.5, 1.0) are mathematically equivalent to percentages but simpler to work with and more intuitive for developers.

- **Mandatory Age Information** – Rejected. Requiring age information would reduce user privacy and GDPR compliance. Optional age with default to standard pricing provides better user experience while still enabling discounts.

---

## References

- [Week 5 Journal - Ticket Management Enhancements](../journal/week_five.md)
- [PriceCalculationHelper.cs](../../src/web/Ticketing.Web/Helpers/PriceCalculationHelper.cs)
- [Booking Contract](../../src/shared/Ticketing.Contracts/Bookings/Booking.cs)
- [User Contract](../../src/shared/Ticketing.Contracts/Users/User.cs)

