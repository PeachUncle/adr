# 2. Interface Design Principles

## Status

Accepted

Date: 2025-06-25

## Context

Our Go domain services need a consistent approach to interface design that:

- Enables loose coupling between components
- Facilitates effective unit testing through mocking
- Provides clear contract boundaries between packages
- Follows Go best practices and idioms
- Supports efficient dependency injection
- Makes code evolution and maintenance easier

Without standardized interface design principles, we risk:

- Bloated interfaces that are difficult to implement and maintain
- Tight coupling between components
- Difficulty in testing due to complex dependencies
- Inconsistent patterns across different packages
- Poor separation of concerns

## Decision

We will adopt these interface design principles:

### 1. Consumer-Driven Interfaces

- Define interfaces in the package that uses them, not where they are implemented
- Keep interfaces focused on the consumer's needs
- Avoid exposing implementation details through interfaces

```go
// In the customers package that consumes refresh token functionality
type RefreshTokenService interface {
	Generate(ctx context.Context, input GenerateTokenInput) (GenerateTokenOutput, error)
	FindActiveToken(ctx context.Context, input FindActiveTokenInput) (FindActiveTokenOutput, error)
	Expire(ctx context.Context, input ExpireInput) (ExpireOutput, error)
}
```

### 2. Interface Segregation

- Keep interfaces small and focused on specific use cases
- Split large interfaces into smaller, more specific ones
- One interface should serve one type of client

```go
// Split token operations by client needs
type TokenGenerator interface {
	GenerateToken(id string, cfg Config) (string, error)
}

type TokenValidator interface {
	GetClaims(token string) (Claims, error)
}

// Combined interface when both capabilities are needed
type TokenService interface {
	TokenGenerator
	TokenValidator
}
```

### 3. Mock Generation

- Use go:generate with mockgen for automatic mock generation
- Place mocks in a separate 'mocks' subdirectory within the package
- Standardize mock naming patterns for consistency

```go
// Service defines the interface for JWT token operations
//
//go:generate mockgen -destination=./mocks/service_mock.go -package=jwt_mocks github.com/.../jwt Service
type Service interface {
	GenerateToken(id string, cfg Config) (string, error)
	GetClaims(token string) (Claims, error)
}
```

### 4. Error Handling

- Include error returns in interface methods for operations that can fail
- Define and export domain-specific error variables
- Use error wrapping to preserve context

```go
var (
	// ErrRefreshTokenNotFound indicates that the specified refresh token could not be found.
	ErrRefreshTokenNotFound = errors.New("refresh token not found")
	// ErrRefreshTokenAlreadyExists represents an error indicating a refresh token already exists.
	ErrRefreshTokenAlreadyExists = errors.New("refresh token already exists")
)

type Repository interface {
	FindActiveToken(ctx context.Context, token string) (Token, error)
}
```

## Consequences

### Positive

- Highly testable code through easy mocking
- Reduced coupling between components
- Clear contract boundaries
- Simplified testing setup
- Flexible implementation swapping
- Better separation of concerns
- Improved code maintainability

### Negative

- Additional interface and mock maintenance
- Initial overhead for setting up mock generation
- More files and types to manage
- Learning curve for interface design patterns

### Neutral

- Regular interface review is required as requirements evolve
- Need for tooling to manage mocks
- Interface design skills development

## Implementation Notes

### Testing with Mocks Example

```go
func TestService_Generate(t *testing.T) {
	tests := []refreshServiceTestCase[refresh.GenerateTokenInput, refresh.GenerateTokenOutput]{
		{
			name: "when the refresh token is generated and stored, then it returns the token",
			input: refresh.GenerateTokenInput{
				UserID: "fake-user-id",
				Role:   "fake-role",
			},
			mocksSetup: func(repo *refreshmocks.MockRepository) {
				repo.EXPECT().Create(gomock.Any(), gomock.Any()).DoAndReturn(
					func(_ context.Context, params refresh.CreateTokenParams) (refresh.Token, error) {
						// Assertions on mock input
						require.Equal(t, "fake-user-id", params.UserID)
						require.Equal(t, "fake-role", params.Role)

						// Return test data
						return refresh.Token{Token: "fake-token"}, nil
					})
			},
			want:    refresh.GenerateTokenOutput{Token: "fake-token"},
			wantErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			repo := refreshmocks.NewMockRepository(ctrl)
			if tt.mocksSetup != nil {
				tt.mocksSetup(repo)
			}

			service := refresh.NewService(logger, repo, clock.RealClock{})
			got, err := service.Generate(context.Background(), tt.input)

			assert.ErrorIs(t, err, tt.wantErr)
			assert.Equal(t, tt.want, got)
		})
	}
}
```

### Interface Implementation Example

```go
// Private implementation type
type service struct {
	logger *zap.Logger
	repo   Repository
	clock  clock.Clock
}

// Constructor returns the interface type
func NewService(logger *zap.Logger, repo Repository, clock clock.Clock) Service {
	return &service{
		logger: logger,
		repo:   repo,
		clock:  clock,
	}
}

// Method implementation
func (s *service) Generate(ctx context.Context, input GenerateTokenInput) (GenerateTokenOutput, error) {
	// Implementation details
}
```

## Related Documents

- [Dependency Injection and Service Initialization](./0003-dependency-injection-and-service-initialization.md)

## Contributors

- Àlex Grau Roca
