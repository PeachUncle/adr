# ADR-007: FluentValidation for Input Validation

**Date:** 2025-01-10
**Status:** Accepted
**Deciders:** Craig Banach
**Technical Story:** Implementing robust input validation while keeping DTOs simple

## Context

Need to validate user input in the API with requirements for:

- Complex validation rules (conditional, cross-field)
- Clean DTO classes without validation attributes
- Testable validation logic
- Clear separation between input validation and business rules
- Support for async validation scenarios

## Decision

Use FluentValidation for input validation at the controller layer:

1. **FluentValidation for all DTO validation** - separate validator classes
2. **Validation runs at controller entry** - before reaching service layer
3. **Simple DTOs** - no validation attributes, just properties
4. **Async validation (e.g., uniqueness checks) handled as business rules** - returns 409 Conflict, not validation errors

Example implementation:

```csharp
// Clean DTO
public record CreateTransactionDto(
    decimal Amount,
    string Description,
    string? Notes,
    DateTime TransactionDate,
    int CategoryId
);

// Separate validator
public class CreateTransactionDtoValidator : AbstractValidator<CreateTransactionDto>
{
    public CreateTransactionDtoValidator()
    {
        RuleFor(x => x.Amount)
            .GreaterThan(0).WithMessage("Amount must be greater than zero")
            .LessThanOrEqualTo(999999.99m).WithMessage("Amount cannot exceed £999,999.99");

        RuleFor(x => x.Description)
            .NotEmpty().WithMessage("Description is required")
            .MaximumLength(200).WithMessage("Description cannot exceed 200 characters");
    }
}
```

## Consequences

**Positive:**

- **Clean DTOs**: No attribute clutter
- **Powerful validation**: Complex rules, conditional logic, custom validators
- **Testable**: Validators can be unit tested independently
- **Reusable**: Validators can be composed and shared
- **Consistent**: All validation in one place per DTO
- **Good error messages**: Full control over error messaging

**Negative:**

- **Additional dependency**: FluentValidation package required
- **More classes**: Separate validator class for each DTO
- **Registration overhead**: Validators must be registered in DI container

**Neutral:**

- Validation is separate from domain model
- Different from built-in .NET validation approach
- Async uniqueness checks handled differently (as business rules)

## Implementation Guidelines

1. **One validator per DTO** in `Application/Validators` folder
2. **Register validators** in Program.cs: `services.AddValidatorsFromAssemblyContaining<CreateTransactionDtoValidator>()`
3. **Return 400** for validation failures, **409** for business rule conflicts
4. **No async validation** in validators - keep them fast and synchronous
5. **Test all validators** with both valid and invalid inputs

## Alternatives Considered

1. **Data Annotations**

   - Pros: Built-in, simple for basic validation
   - Cons: Limited power, clutters DTOs, poor testability
   - Rejected: Not flexible enough for complex rules

2. **Custom Validation Service**

   - Pros: Full control
   - Cons: Reinventing the wheel, more code to maintain
   - Rejected: FluentValidation is mature and well-tested

3. **Domain Model Validation Only**
   - Pros: All validation in one place
   - Cons: Invalid data reaches domain layer, poorer user experience
   - Rejected: Want to fail fast at API boundary

## References

- [FluentValidation Documentation](https://docs.fluentvalidation.net/)
- [FluentValidation Best Practices](https://docs.fluentvalidation.net/en/latest/best-practices.html)
- [Integration with ASP.NET Core](https://docs.fluentvalidation.net/en/latest/aspnet.html)
