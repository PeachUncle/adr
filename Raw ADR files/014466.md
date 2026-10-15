# 1. Unit Testing Standards and Mocking

## Status

Accepted

Date: 2025-07-01

## Context

As we implement our testing strategy and adopt TDD/BDD methodologies across our services, we need to establish 
consistent standards for unit testing and mocking. Without clear guidelines, our approach to unit testing and 
dependency mocking may diverge across teams and services, resulting in:

- Inconsistent code quality and test coverage
- Varying levels of test isolation and reliability
- Difficulty in understanding and maintaining tests
- Challenges in onboarding new team members to the testing approach
- Potential testing of implementation details rather than behavior

We need to establish a standardized approach to unit testing that ensures proper isolation, focuses on behavior 
verification, and facilitates our TDD/BDD workflow.

## Decision

We will adopt the following standards for unit testing and mocking across all services:

### Unit Test Structure

1. **Behavior-Oriented Testing**
   - Each test should verify a specific behavior, not implementation details
   - Test names must follow the "when [condition], then [expected result]" pattern
   - Tests should be self-documenting and serve as specifications

2. **Table-Driven Tests**
   - Use table-driven tests for related scenarios. Look at [ADR-0002: Table-Driven Tests 
     Implementation](0002-table-driven-tests-implementation.md) for more details
   - Each test case should have a descriptive name
   - Group test cases by related behavior

3. **Test Organization**
   - Follow Arrange-Act-Assert (AAA) pattern within tests
   - Use `t.Run()` for sub-tests to group related scenarios
   - Use build tags to separate unit tests from integration tests. Look at [ADR-0003: Build Tags for Test 
     Categorization](0003-build-tags-for-test-categorization.md) for more details

### Mocking Strategy

1. **Mocking Framework**
   - Use gomock as our standard mocking framework
   - Generate mocks using mockgen for all interfaces
   - Store mocks in a `mocks` subdirectory within each package

2. **Dependency Injection**
   - Design code with interfaces for all external dependencies
   - Use constructor injection to provide dependencies
   - Avoid global state and singletons that complicate testing

3. **Mock Verification**
   - Verify only behavior that matters to the test
   - Use `gomock.Any()` for parameters that are not relevant to the test
   - Set up expectations with the minimal specificity needed

### Custom Test Helpers

1. **Test Types**
   - Use generic test case structs for similar test patterns
   - Create helper functions for common test setup and assertions

2. **Test Data**
   - Use constants or factory functions for test data
   - Ensure test data is representative but minimal

## Consequences

### Positive

- Consistent, high-quality unit tests across all services
- Clear test isolation with properly mocked dependencies
- Tests that document system behavior and serve as living specifications
- Improved maintainability through standardized patterns
- Easier onboarding for new team members
- Reduced test fragility through proper mocking practices
- Better support for our TDD/BDD development workflow

### Negative

- Additional time investment in setting up proper test structures
- Need to generate and maintain mock implementations
- Potential overhead in writing tests for simple functions

### Neutral

- Need for continuous education and code reviews to maintain standards
- Regular revisiting of standards as the codebase and team evolves
- Balance between strict standards and pragmatic testing approaches

## Implementation Notes

### Table-Driven Test Example

```go
type customersServiceTestCase[I, W any] struct {
	name       string
	input      I
	mocksSetup func(repo *customersmocks.MockRepository, refreshService *refreshmocks.MockService,
		jwtService *jwtmocks.MockService)
	want    W
	wantErr error
}

func TestService_LoginCustomer(t *testing.T) {
	logger, _ := log.NewTest()

	tests := []customersServiceTestCase[customers.LoginCustomerInput, customers.LoginCustomerOutput]{
		{
			name: "when there is not an active customer with the same email, " +
				"then it should return an invalid credentials error",
			input: customers.LoginCustomerInput{
				Email:    "test@example.com",
				Password: "ValidPassword123",
			},
			mocksSetup: func(repo *customersmocks.MockRepository, _ *refreshmocks.MockService,
				_ *jwtmocks.MockService) {
				repo.EXPECT().FindByEmail(gomock.Any(), gomock.Any()).
					Return(customers.Customer{}, customers.ErrCustomerNotFound)
			},
			want:    customers.LoginCustomerOutput{},
			wantErr: customers.ErrInvalidCredentials,
		},
		// Additional test cases...
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			repo := customersmocks.NewMockRepository(ctrl)
			refreshService := refreshmocks.NewMockService(ctrl)
			jwtService := jwtmocks.NewMockService(ctrl)
			if tt.mocksSetup != nil {
				tt.mocksSetup(repo, refreshService, jwtService)
			}

			service := customers.NewService(logger, repo, refreshService, jwtService)

			// Act
			got, err := service.LoginCustomer(context.Background(), tt.input)

			// Assert
			assert.ErrorIs(t, err, tt.wantErr)
			assert.Equal(t, tt.want, got)
		})
	}
}
```

### Mock Generation and Usage

1. **Generate Mocks**

   Use mockgen to generate mocks for interfaces:

   ```bash
   # In Makefile or script
   mockgen -source=internal/customers/service.go -destination=internal/customers/mocks/service.go -package=customersmocks
   ```

2. **Test Setup with Mocks**

   ```go
   func TestFunction(t *testing.T) {
       // Setup controller
       ctrl := gomock.NewController(t)
       defer ctrl.Finish()

       // Create mock
       mockRepo := mocks.NewMockRepository(ctrl)

       // Set expectations
       mockRepo.EXPECT().
           FindByID(gomock.Any(), "123").
           Return(Entity{ID: "123", Name: "Test"}, nil)

       // Inject mock and test
       service := NewService(mockRepo)
       result, err := service.GetEntity(context.Background(), "123")

       // Assert results
       assert.NoError(t, err)
       assert.Equal(t, "Test", result.Name)
   }
   ```

3. **Helper Functions**

   ```go
   // setupTestEnv initializes the test environment with default values
   func setupTestEnv() log.Logger {
       gin.SetMode(gin.TestMode)
       logger, _ := log.NewTest()
       return logger
   }
   ```

### Best Practices for Mock Expectations

1. **Use Flexible Matchers When Appropriate**

   ```go
   // Instead of exact matches for all parameters
   mockRepo.EXPECT().
       Create(gomock.Any(), UserParams{Name: "John", Email: "john@example.com"}).
       Return(User{ID: "123"}, nil)

   // Use matchers for fields that do not matter in this test
   mockRepo.EXPECT().
       Create(gomock.Any(), gomock.Any()).
       DoAndReturn(func(_ context.Context, params UserParams) (User, error) {
           // Only verify what matters for this specific test
           assert.Equal(t, "John", params.Name)
           return User{ID: "123"}, nil
       })
   ```

2. **Set Up Expectations Only for What Matters**

   Only mock the methods that will be called in the test, and only verify the behavior that is relevant to the 
   current test case.

3. **Use DoAndReturn for Complex Logic**

   For cases where you need to inspect parameters or return dynamic values based on inputs, use `DoAndReturn` 
   instead of `Return`.

## Related Documents

   - [ADR-0005: Testing Strategy and Types](../../global/0005-testing-strategy-and-types.md)
   - [ADR-0006: Test-Driven Development and Behavior-Driven Development Adoption](../../global/0006-test-driven-development-and-behavior-driven-development-adoption.md)
   - [GoMock Documentation](https://github.com/golang/mock)
   - [Testify - Assertions and Mocking for Go](https://github.com/stretchr/testify)

## Contributors

- Àlex Grau Roca
