# ADR-0002: Booking State Machine Unification

## Problem
The booking lifecycle is inconsistent between panel (admin/private) and public booking flows. Panel creates bookings in `CONFIRMED`, public create is unimplemented, and the contract/test expectations are not aligned with runtime behavior.

## Current behavior
- Database defaults `Booking.status` to `CONFIRMED`.
- Panel create (`src/modules/bookings/bookings.service.ts`) always sets status to `CONFIRMED`.
- Confirm is only allowed from `PENDING` and is forbidden for `STAFF`.
- Cancel is allowed from `PENDING` or `CONFIRMED`; terminal states block further transitions.
- Public create is a placeholder; tests and contract expect auto-confirm vs pending based on settings.

## Final decision (Admin vs Public)
- **States**: `PENDING`, `CONFIRMED`, `DONE`, `CANCELED`, `NO_SHOW`.
- **Panel create**: Always creates `CONFIRMED` bookings. Panel is not used for `PENDING` creation.
- **Public create**: Depends on salon settings:
  - `allowOnlineBooking=false` -> reject with 403.
  - `onlineBookingAutoConfirm=true` -> `CONFIRMED`.
  - `onlineBookingAutoConfirm=false` -> `PENDING`.
- **Terminal states**: `DONE`, `CANCELED`, `NO_SHOW` (no further changes).

## State transition table

| Current State | Action / Trigger Endpoint | Next State | Allowed Roles |
| :--- | :--- | :--- | :--- |
| `(new)` | `POST /bookings` (Panel) | `CONFIRMED` | `MANAGER`, `RECEPTIONIST` |
| `(new)` | `POST /bookings` (Public, auto-confirm) | `CONFIRMED` | `Public` |
| `(new)` | `POST /bookings` (Public, manual-confirm) | `PENDING` | `Public` |
| `PENDING` | `POST /{id}/confirm` | `CONFIRMED` | `MANAGER`, `RECEPTIONIST` |
| `PENDING` | `POST /{id}/cancel` | `CANCELED` | `MANAGER`, `RECEPTIONIST` |
| `CONFIRMED` | `POST /{id}/complete` | `DONE` | `MANAGER`, `RECEPTIONIST` |
| `CONFIRMED` | `POST /{id}/no-show` | `NO_SHOW` | `MANAGER`, `RECEPTIONIST` |
| `CONFIRMED` | `POST /{id}/cancel` | `CANCELED` | `MANAGER`, `RECEPTIONIST` |

## Backward compatibility / migration notes
- No schema changes required; default `CONFIRMED` remains.
- Public booking creation becomes the only supported path for `PENDING` in MVP.

## Test plan
- Run booking public and management E2E tests to validate the public create path, state transitions, and idempotency behavior.
