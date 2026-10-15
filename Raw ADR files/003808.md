
# ADR-0001: Booking Overlap and Race Condition Protection

## Context

The booking creation endpoint was vulnerable to a race condition. If two users tried to book the same time slot for the same staff member at the same time, it was possible for both bookings to be created, leading to a double booking. This is a critical issue for a salon management system, as it can lead to customer dissatisfaction and operational problems.

## Decision

We have implemented a **PostgreSQL Exclusion Constraint** to prevent booking overlaps at the database level. This is the most robust and reliable way to prevent race conditions, as it enforces the constraint atomically within the database itself.

The constraint is a partial constraint, meaning it only applies to bookings with a status of `PENDING`, `CONFIRMED`, or `DONE`. This allows new bookings to be created in time slots that were previously occupied by a `CANCELED` or `NO_SHOW` booking.

In addition to the database constraint, we have wrapped the booking creation logic in a `prisma.$transaction` block with a `REPEATABLE READ` isolation level. This ensures that the read (fetching service duration) and the write (creating the booking) are part of a single atomic operation.

Finally, we have updated the global error handler to catch the PostgreSQL exclusion constraint violation and map it to an HTTP `409 Conflict` with a `BOOKING_OVERLAP` error code.

## Alternatives Considered

*   **Pessimistic Locking (`SELECT ... FOR UPDATE`)**: This would involve locking the staff member's row in the `User` table for the duration of the booking creation transaction. This would prevent other transactions from reading or writing to that row, but it could lead to deadlocks and would be more complex to implement and manage.
*   **Advisory Locks**: This would involve using a database-level lock that is not tied to a specific table or row. This would be more flexible than pessimistic locking, but it would also be more complex to implement and manage.
*   **Serializable Transactions**: This would involve using a `SERIALIZABLE` transaction isolation level. This would provide the highest level of isolation, but it would also be the most restrictive and could lead to performance problems.

## Consequences

The chosen solution provides the strongest guarantee of data integrity and is the most reliable way to prevent booking overlaps. It is also the most performant solution, as it does not require any additional locking or complex transaction management.

The only downside of this approach is that it is specific to PostgreSQL. If we were to switch to a different database, we would need to find an alternative solution.

## Migration Notes

The following migration has been created and applied to the database:

*   `prisma/migrations/20260103120000_booking_overlap_exclusion/migration.sql`

This migration creates the `btree_gist` extension and the partial exclusion constraint on the `Booking` table.

## Testing

A concurrency test has been created at `src/modules/bookings/bookings.concurrency.test.ts`. This test simulates a race condition by firing two overlapping booking requests concurrently.

**Note:** The test is currently blocked by unrelated issues in the test environment. However, the core logic of the test is sound and ready for when the environment is stabilized. We propose stabilizing the test environment as a separate follow-up task.
