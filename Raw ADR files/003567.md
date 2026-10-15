---
status: proposed
date: 2024-12-11
decision-makers: Michael Ogunrinde, James Bateman, Cory-Newman
---

# Testing Strategy for AML System

## Context and Problem Statement

The AML system needs a comprehensive testing strategy to ensure security, accessibility, functionality, and reliability. We need to determine the most effective combination of testing approaches for both frontend and backend components, covering automated testing, security testing, accessibility testing, and manual verification processes.

## Decision Drivers

* Must ensure system security
* Need to verify accessibility compliance
* Must validate API functionality
* Should catch bugs early in development
* Must protect sensitive user data
* Should support continuous integration
* Must provide adequate test coverage
* Should enable rapid development feedback

## Considered Options

### Frontend Testing

* Google Lighthouse for accessibility
* Other accessibility testing tools (Wave, aXe)
* Jest with React Testing Library
* Security scanning tools

### Backend Testing

* Bruno for API testing
* Other API testing tools (Postman, Insomnia)
* Unit testing frameworks
* Manual testing procedures
* Security testing tools

## Decision Outcome

Chosen approach: "Multi-layered Testing Strategy with Specific Tools", because:

1. Google Lighthouse provides comprehensive accessibility metrics
2. OWASP ZAP offers thorough security scanning
3. Bruno enables effective API testing
4. Manual testing catches edge cases
5. Combination covers all critical areas
6. Tools are well-documented and reliable
7. Free and open-source solutions

### Planned Testing Approach

1. Frontend Testing:
   * Accessibility Testing
     * Google Lighthouse automated scans
     * Performance metrics
     * Best practices validation
     * SEO assessment
     * Manual accessibility review

   * Security Testing
     * OWASP ZAP security scans
     * Penetration testing
     * Authentication testing
     * Manual security testing

   * Functional Testing
     * Component testing
     * User flow validation
     * Cross-browser testing
     * Responsive design verification

2. Backend Testing:
   * API Testing
     * Bruno for API endpoint testing
     * Request/response validation
     * Error handling verification
     * Authentication testing

   * Security Testing
     * Input validation testing
     * Authorization testing
     * Rate limiting verification
     * Brute force attack testing

   * Manual Testing
     * Integration testing
     * Edge case validation
     * Error scenario testing
     * Performance assessment

### Consequences

* Good, because Lighthouse provides clear accessibility metrics
* Good, because ZAP offers comprehensive security scanning
* Good, because Bruno enables structured API testing
* Bad, because automated tools may have false positives
* Bad, because manual testing requires significant time

### Confirmation

We will validate this strategy through:

1. Regular Lighthouse accessibility reports
2. ZAP security scan results
3. Bruno API test coverage
4. Manual test results
5. Overall system quality metrics

## Pros and Cons of the Options

### Google Lighthouse

* Good, because of comprehensive accessibility checks
* Good, because of performance insights
* Good, because of built-in best practices
* Bad, because of potential inconsistency across runs
* Bad, because some metrics need manual verification

### OWASP ZAP

* Good, because of thorough security scanning
* Good, because of automated vulnerability detection
* Bad, because of false positives
* Bad, because of complex configuration
* Neutral, because requires security expertise

### Bruno API Testing

* Good, because of structured API testing
* Good, because of clear request/response validation
* Bad, because of setup requirements
* Bad, because of learning curve
* Neutral, because of specific use case

## More Information

Implementation requirements:

1. Testing Setup:
   * Google Lighthouse configuration
   * ZAP scan settings
   * Bruno test collections
   * Manual test cases
   * Testing environments

2. Testing Procedures:
   * Regular accessibility audits
   * Security scan schedule
   * API test execution
   * Manual testing checklist
   * Bug reporting process

3. Team Requirements:
   * Tool training
   * Testing responsibilities
   * Documentation standards
   * Review process
   * Communication protocols
