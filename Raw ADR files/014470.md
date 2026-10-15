# 6. End-to-End Testing Framework

## Status

Accepted

Date: 2025-07-01

## Context

As we start developing new services, we need to establish a robust end-to-end (E2E) testing strategy. 
The following aspects need to be considered:

1. Our platform will be built using domain services architecture, where business workflows often span multiple services
2. We need to ensure that features work correctly across service boundaries
3. Different services might have independent deployment cycles
4. Test execution needs to be flexible to support various CI/CD scenarios
5. Test organization should align with business features rather than technical boundaries

## Decision

We will implement a comprehensive E2E testing framework with the following key decisions:

1. **Technology Stack**
   - Go programming language
   - Ginkgo for BDD-style testing
   - Gomega for assertions
   - Native Go HTTP client for API testing

2. **Test Organization**
   - Organize tests by business features rather than services
   - Implement a feature-based directory structure
   - Use build tags for flexible test selection
   - Create shared test utilities and factories

3. **Build Tags Strategy**
   - Support multiple tag combinations for flexible test execution
   - Enable service-specific and feature-specific test runs
   - Ensure compatibility with different CI/CD pipelines

E2E tests should not cover all the possible scenarios, as those tests are expensive and slow to execute. Instead, 
they should cover the most important business flows and features, as those edge cases are more likely to be broken. 
Focus on value rather than on quantity.

## Consequences

### Positive

- Clear alignment with business domains from the project start
- Efficient test execution through build tags
- Strong foundation for maintainable test code
- Clear separation of test support code and actual tests
- Enhanced visibility of feature coverage
- Support for cross-service testing scenarios
- Only the necessary E2E tests are created and executed, saving time and resources

### Negative

- Initial setup effort for shared components
- Need for comprehensive documentation
- Learning curve for team members new to Ginkgo/Gomega
- Overhead in maintaining build tag combinations

### Neutral

- Regular maintenance of shared test utilities is required
- Ongoing documentation needs for build tags usage
- Need for periodic review of test organization
- Team training requirements for the chosen tools

## Implementation Notes

1. **Directory Structure**
   - Create a feature-based directory organization
   - Establish shared utilities for common functionality
   - Implement test data factories for each domain entity

2. **Build Tags Implementation**
   - Define standard tag combinations
   - Document tag usage patterns
   - Establish naming conventions

3. **Test Suite Structure**
   Each feature test directory must contain:

   a. Suite Test File (`suite_test.go`):
   ```go
   //go:build e2e || feature_name || service_name

   package featurename

   import (
       "testing"

       "github.com/onsi/ginkgo/v2"
       "github.com/onsi/gomega"
   )

   func TestFeatureE2E(t *testing.T) {
       gomega.RegisterFailHandler(ginkgo.Fail)
       ginkgo.RunSpecs(t, "Feature Name E2E Suite")
   }
   ```

   b. Feature Test Files (`feature_test.go`):
   ```go
   //go:build e2e || feature_name || service_name

   package featurename

   import (
       g "github.com/onsi/ginkgo/v2"
       . "github.com/onsi/gomega"
   )

   var _ = g.Describe("Feature Workflow", func() {
       g.It("completes the expected business flow", func() {
           // Test setup
           entity := factory.New()

           // Test steps with clear descriptions
           By("performing first action")
           response1, err := entity.Action1()
           Expect(err).NotTo(HaveOccurred())
           Expect(response1.Field).To(Equal(expectedValue))

           By("performing second action")
           response2, err := entity.Action2()
           Expect(err).NotTo(HaveOccurred())
           Expect(response2.Field).To(Equal(expectedValue))
       })
   })
   ```

4. **Best Practices**
   - Use descriptive BDD-style test descriptions
   - Structure tests as business workflows
   - Implement proper test data cleanup
   - Use factories for test data generation
   - Include clear test step descriptions using `By()`
   - Group related assertions together
   - Handle errors explicitly
   - Add sufficient timeouts for async operations
   - Document any test-specific requirements

5. **Test Folder and Files Organization**.
   ```
   e2e/
   ├── domain/                        # Domain specific code
   │   └── customer/                  # Customer domain
   │       ├── actions.go             # Customer domain actions
   │       ├── api.go                 # Customer API interface
   │       ├── factory.go             # Customer test data factory
   │       └── types.go               # Customer type definitions
   ├── features/                      # Feature tests
   │   └── authentication/            # Authentication feature tests
   │       ├── suite_test.go          # Test suite setup
   │       └── customer_registration_authentication_test.go  # Customer registration tests
   ├── pkg/                           # Shared packages
   │   └── api/                       # API clients
   ├── go.mod                         # Go module file
   ├── go.sum                         # Go dependencies checksum
   └── Makefile                       # Test execution commands
   ```

## Related Documents

- [Testing Strategy Overview](./../../global/0005-testing-strategy-and-types.md)
- [Ginkgo Documentation](https://onsi.github.io/ginkgo/)
- [Gomega Documentation](https://onsi.github.io/gomega/)

## Contributors

- Àlex Grau Roca