## Organization-Per-Customer-And-Partner Architecture

- Status: Accepted
- Date: 2024-12-28
- Context: User Service Architecture
- Decision: Organization-Per-Customer-And-Partner Model
- Consequences: Multi-tenancy and Scalability

### Context

The PalletCloud user service needs to handle different types of users (customers, partners, staff) while maintaining proper data isolation, access control, and scalability. We need to decide how to structure organizations and user relationships to support current requirements while maintaining scalability and flexibility for future growth.

Key considerations:
- Future Scalability: Individual customers may later add family members or employees
- Consistent Data Model: Unified approach across all user types simplifies queries and permissions
- Business Growth: Customers can transition to partners, partners can add staff
- Data Isolation: Each organization acts as a tenant boundary for future multi-tenancy features

### Decision

We have decided to create a separate organization for every customer and every partner in the system , implementing a strict organization-per-customer-And-Partner model.

Key architectural decisions:
1. **One Organization Per Customer**: Each customer gets their own organization entity
2. **Organization-Based Data Isolation**: All business data is scoped to organizations
3. **Customer Can Be Individual Or Company**: User with type customer can be individual or company
4. **Cross-Organization Super Admin**: Global admin users can manage across organizations using the `isSuperAdmin` flag

### Consequences

#### Positive
- **Strong Data Isolation**: Complete separation of customer data at the organization level
- **Clear Security Boundaries**: Access control is naturally scoped to organizations
- **Future Multi-Tenancy**: Easy to extend to full multi-tenant architecture
- **Scalable Partner Management**: Partners can be managed within customer organizations
- **Simplified Data Queries**: All queries naturally filtered by organization context
- **Compliance Friendly**: Easier to meet data residency and privacy requirements

#### Negative
- **Initial Overhead**: Every customer registration creates an organization
- **Storage Considerations**: Potential for many small organizations
- **Cross-Organization Queries**: More complex for global reporting (mitigated by superAdmin)
- **Migration Complexity**: Harder to merge organizations later if needed

---