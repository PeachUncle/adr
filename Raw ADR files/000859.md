# ADR 4: Database Design Decisions

## Context

In this ADR, we document the database design decisions related to the `onDelete` logic for relationships between key entities within the system.

## Decision

1. **Dish - Vendor Relationship:**

   - `onDelete: "CASCADE"`
   - Ensures that when a `Vendor` is deleted, associated `Dishes` are also deleted, maintaining data consistency.

2. **Order - User Relationship:**

   - `onDelete: "RESTRICT"`
   - Restricts deletion of a `User` if associated `Orders` exist, preventing accidental removal of user data.

3. **Order - OrderStatus Relationship:**

   - `onDelete: "CASCADE"`
   - Cascades deletion of associated `Orders` when an `OrderStatus` is deleted, ensuring that orders are removed when their status is no longer valid.

4. **OrderDish - Rating Relationship:**

   - `onDelete: "RESTRICT"`
   - Restricts deletion of a `Rating` if associated `OrderDishes` exist, maintaining data integrity for order ratings.

5. **User - Order Relationship:**

   - `onDelete: "RESTRICT"`
   - Restricts deletion of a `User` if associated `Orders` exist, avoiding orphaned order records.

6. **OrderDish - Dish Relationship:**

   - `onDelete: "CASCADE"`
   - Cascades deletion of associated `OrderDishes` when a `Dish` is deleted, ensuring consistency in order dish records.

7. **Role - RolePrivilege Relationship:**

   - `onDelete: "CASCADE"`
   - Cascades deletion of associated `RolePrivileges` when a `Role` is deleted, aligning with the role's lifecycle.

8. **Rating - OrderDish Relationship:**

   - `onDelete: "RESTRICT"`
   - Restricts deletion of a `Rating` if associated `OrderDishes` exist, preventing loss of rating data.

9. **Role - User Relationship:**

   - `onDelete: "RESTRICT"`
   - Restricts deletion of a `Role` if associated `Users` exist, maintaining user-role relationships.

10. **User - VendorUser Relationship:**

    - `onDelete: "RESTRICT"`
    - Restricts deletion of a `User` if associated `VendorUsers` exist, preventing removal of vendor-user relationships.

11. **Vendor - Dish Relationship:**

    - `onDelete: "CASCADE"`
    - Cascades deletion of associated `Dishes` when a `Vendor` is deleted, ensuring consistency in vendor-dish relationships.

12. **Vendor - VendorUser Relationship:**
    - `onDelete: "CASCADE"`
    - Cascades deletion of associated `VendorUser` when a `Vendor` is deleted, maintaining the integrity of vendor-user relationships.

## Consequences

- Ensures data integrity by preventing or appropriately cascading deletions based on entity relationships.
- Supports the expected behavior of the application and aligns with common database design practices.
- Allows for efficient management of entities, avoiding unintended data inconsistencies.

## Considerations

Considering the evolving nature of the project and a focus on deliverable features, audit-related rules, particularly those involving user record deletion, may be subject to change. Future iterations may introduce modifications to these rules as project requirements and priorities evolve. Further consideration and evaluation are planned for a later date.
