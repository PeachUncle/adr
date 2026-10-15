# ADR 0004: Transfer Module Design and Implementation

## Status
Accepted

## Context
This ADR documents the design and implementation decisions for the Transfer module in the banking application. The Transfer module is responsible for securely executing money transfers between accounts, logging all related entries, and providing APIs for transfer history and details. The implementation uses Go (Gin, GORM) and PostgreSQL, following the overall architecture described in previous ADRs.

## Decision

### Module Responsibilities
- Execute money transfers between accounts as a single transaction (atomicity).
- Log each transfer and create corresponding debit/credit entries.
- Update account balances safely, avoiding deadlocks.
- Expose RESTful endpoints for:
  - Executing a transfer (`POST /api/v1/transfer/execute`)
  - Listing transfers for an account (incoming, outgoing, or all)
  - Retrieving transfer details by ID
- Enforce that only the account owner (authenticated user) can view or initiate transfers for their accounts.
- Secure all endpoints with JWT authentication.

### Go Implementation
- **DTOs**: `CreateTransferRequest`, `CreateTransferResponse` for API payloads.
- **Repository**: Implements `TransferTx` for transactional transfer logic, and `FindAllByAccountID` for history.
- **Service**: Orchestrates business logic, validates input, and calls repository methods.
- **Controller**: Handles HTTP requests, validates user/account ownership, and formats responses.
- **Router**: Registers endpoints and applies authentication middleware.

### Database Schema
- **Table**: `transfers` (see ADR 0001)
- **Fields**: `id`, `from_account_id`, `to_account_id`, `amount`, `created_at`
- **Associations**: Each transfer is linked to sender and receiver accounts. Entries are created for both accounts.
- **Constraints**: Amount must be positive. Foreign keys are enforced with cascading updates/deletes.

### Security
- All transfer operations require a valid JWT (see ADR 0002).
- The service checks that the authenticated user owns the account involved in the transfer.
- Input validation ensures only valid, positive amounts and existing accounts are used.

### API Endpoints
- `POST /api/v1/transfer/execute`: Initiate a transfer (requires JWT, body: `CreateTransferRequest`).
- `GET /api/v1/transfer?account_id=...&direction=...`: List transfers for an account (incoming, outgoing, or all).
- `GET /api/v1/transfer/{id}`: Get transfer details by ID.

### Rationale
- Transactional logic ensures atomicity and consistency for transfers and balance updates.
- Ownership checks and JWT security prevent unauthorized access.
- Modular separation (DTO, repository, service, controller) improves maintainability and testability.

## Consequences
- The Transfer module is robust, secure, and enforces business rules for money movement.
- The design supports extensibility for future features (e.g., scheduled transfers, transfer limits).
- Aligns with the overall architecture and security model of the application.

## References
- [ADR 0001: Database Design and Decisions](0001-database-design.md)
- [ADR 0002: User Authentication and Login Implementation](0002-user-authentication.md)
- [ADR 0003: Account Module Design and Database Decisions](0003-account-module.md)
- [GORM Documentation](https://gorm.io/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) 