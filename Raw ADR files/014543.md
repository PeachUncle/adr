# 002. Testing Strategy

**Date**: 2025-12-17  
**Status**: Proposed  
**Deciders**: Development Team  
**Technical Story**: Enhance existing Vitest setup with E2E and visual regression tests

---

## Context and Problem Statement

Currently, the project has solid unit and integration tests using Vitest + jsdom for individual components (header, carousel, modal, form handlers, state management). Test coverage is good (~80%+), but there are gaps:

1. **No end-to-end (E2E) tests**: User flows (contact form submission, booking modal interaction) aren't tested in a real browser
2. **No visual regression tests**: CSS changes could break layouts without detection
3. **Incomplete tests**: Focus trapping in modal has commented-out tests
4. **Manual testing burden**: Each deployment requires manual QA across devices

We need to decide how to expand our testing strategy to increase confidence in deployments while balancing development speed and maintenance overhead.

---

## Decision Drivers

- **Confidence in deployments**: Need to catch regressions before users do
- **Development speed**: Tests shouldn't slow down iteration significantly
- **Maintenance cost**: Test suite should be maintainable by a small team
- **Real-world coverage**: Tests should reflect actual user interactions (not just mocked DOM)
- **Budget**: Prefer free/open-source tools; paid tools must provide clear ROI
- **CI/CD integration**: Tests should run automatically on pull requests

---

## Considered Options

1. **Expand Vitest tests only** (unit/integration focus)
2. **Add Playwright for E2E** (full browser testing)
3. **Add Cypress for E2E** (alternative to Playwright)
4. **Add Percy or Chromatic for visual regression** (screenshot comparison)
5. **Hybrid approach**: Vitest + Playwright + Percy

---

## Decision Outcome

**Chosen option**: **"Hybrid Approach: Vitest (existing) + Playwright (E2E) + Percy (visual regression)"** (Proposed)

**Rationale**: 
- **Vitest** remains the foundation for fast unit/integration tests
- **Playwright** provides real browser E2E testing with excellent developer experience and cross-browser support
- **Percy** automates visual regression testing, catching CSS issues humans might miss
- This covers the full testing pyramid: unit → integration → E2E → visual

### Consequences

#### Positive (Good) ✅

- **Comprehensive coverage**: Unit, integration, E2E, and visual tests
- **Catch bugs earlier**: Automated tests prevent regressions from reaching production
- **Cross-browser confidence**: Playwright tests Chrome, Firefox, Safari
- **Visual regression detection**: Percy catches unintended CSS changes automatically
- **Parallel execution**: Playwright runs tests in parallel (fast CI)
- **Great DX**: Playwright has excellent debugging tools (traces, videos, screenshots)
- **Free tiers available**: Percy free tier (5K screenshots/mo), Playwright is open-source

#### Negative (Bad) ⚠️

- **More complexity**: Three testing tools to maintain
- **Longer CI times**: E2E tests are slower than unit tests (adds 2-5 min to CI)
- **Flaky tests risk**: E2E tests can be flaky if not written carefully
- **Learning curve**: Team needs to learn Playwright API and best practices
- **Percy cost**: May exceed free tier as project grows ($149/mo for 25K screenshots)
- **Test maintenance**: More tests = more maintenance when features change

#### Neutral (Trade-offs) ⚖️

- **Test writing time**: E2E tests take longer to write than unit tests, but cover more
- **Debugging time**: E2E failures can be harder to diagnose, but Playwright's traces help

---

## Detailed Analysis of Options

### Option 1: Expand Vitest Tests Only

**Description**: Continue using Vitest + jsdom for all testing. Add more unit/integration tests to increase coverage. Use fake timers, mocks, and spies to simulate interactions.

**Pros**:
- ✅ **Fast execution**: Unit tests run in <1 second
- ✅ **No additional tools**: Use what we already have
- ✅ **Simple CI**: No browser setup needed
- ✅ **Easy to debug**: Test failures are clear and specific

**Cons**:
- ❌ **Not real browsers**: jsdom approximates browser behavior but isn't 100% accurate
- ❌ **Can't test visual issues**: No way to catch CSS regressions
- ❌ **Limited coverage**: Hard to test complex user flows end-to-end
- ❌ **False confidence**: Tests may pass but real browsers behave differently

**Estimated Effort**: Ongoing (no additional setup)  
**Technical Complexity**: Low  
**Ongoing Maintenance**: Low

---

### Option 2: Add Playwright for E2E

**Description**: Add Playwright for end-to-end testing in real browsers. Tests launch actual Chrome/Firefox/Safari instances and interact with the site like a real user.

**Pros**:
- ✅ **Real browsers**: Tests in actual Chrome, Firefox, Safari (not simulated)
- ✅ **Cross-browser testing**: Catch browser-specific bugs
- ✅ **User-centric**: Tests reflect real user flows (click, type, submit)
- ✅ **Excellent DX**: Trace viewer, screenshots, videos for debugging
- ✅ **Parallel execution**: Fast test runs (all browsers in parallel)
- ✅ **Open-source**: Free, no vendor lock-in
- ✅ **CI-friendly**: Easy to integrate with GitHub Actions

**Cons**:
- ❌ **Slower than unit tests**: E2E tests take seconds, not milliseconds
- ❌ **Flakiness risk**: Network/timing issues can cause intermittent failures
- ❌ **Setup complexity**: Requires browser binaries (handled by Playwright CLI)
- ❌ **Debugging overhead**: Failures can be harder to diagnose than unit tests

**Estimated Effort**: 1 week (setup, write 5-10 critical flows)  
**Technical Complexity**: Medium  
**Ongoing Maintenance**: Medium

**Key Flows to Test**:
1. **Contact form submission** (fill form, submit, see success message)
2. **Booking modal** (open modal, interact with calendar, close)
3. **Mobile navigation** (toggle menu, click links, scroll)
4. **Carousel interactions** (auto-advance, manual navigation, pause on hover)
5. **Form validation** (submit with invalid data, see errors)

---

### Option 3: Add Cypress for E2E

**Description**: Similar to Playwright, Cypress is an E2E testing framework that runs tests in real browsers. Known for its developer-friendly API and time-travel debugging.

**Pros**:
- ✅ **Real browsers**: Tests in actual browsers
- ✅ **Great DX**: Time-travel debugging, automatic waits, clear error messages
- ✅ **Large community**: Lots of plugins, tutorials, support
- ✅ **Built-in dashboard**: Cypress Cloud (paid) offers test recording and analytics

**Cons**:
- ❌ **Chromium-only by default**: Multi-browser testing requires paid Cypress Cloud
- ❌ **Slower than Playwright**: Serial test execution (one at a time)
- ❌ **More opinionated**: Cypress has more constraints on how tests are written
- ❌ **Network stubbing complexity**: Harder to intercept/mock network requests

**Estimated Effort**: 1 week (similar to Playwright)  
**Technical Complexity**: Medium  
**Ongoing Maintenance**: Medium

---

### Option 4: Add Percy or Chromatic for Visual Regression

**Description**: Visual regression testing tools take screenshots of pages/components and compare them to baseline images. Differences are flagged for review.

**Percy (Recommended)**:
- **Free tier**: 5,000 screenshots/month
- **Paid**: $149/mo for 25K screenshots
- **Integration**: Works with Playwright, Cypress, Storybook
- **Features**: Side-by-side diffs, responsive screenshots, review workflow

**Chromatic**:
- **Free tier**: 5,000 snapshots/month
- **Paid**: $149/mo for 35K snapshots
- **Integration**: Primarily for Storybook, also Playwright
- **Features**: UI component explorer, collaboration tools

**Pros**:
- ✅ **Catches visual regressions**: Detects unintended CSS changes
- ✅ **Automated review**: Visual diff workflow (approve/reject changes)
- ✅ **Responsive testing**: Test multiple screen sizes automatically
- ✅ **Low maintenance**: Baselines update when approved
- ✅ **CI integration**: Comments on PRs with visual diffs

**Cons**:
- ❌ **Cost**: Free tier may not be enough as site grows
- ❌ **False positives**: Dynamic content (dates, random IDs) can trigger diffs
- ❌ **Baseline management**: Keeping baselines up-to-date requires discipline
- ❌ **Vendor dependency**: Tied to Percy/Chromatic platform

**Estimated Effort**: 3 days (integrate, define baseline screenshots)  
**Technical Complexity**: Low  
**Ongoing Maintenance**: Low (mostly reviewing diffs)

---

### Option 5: Hybrid Approach (Recommended)

**Description**: Use all three approaches for comprehensive coverage:
- **Vitest**: Unit/integration tests (fast feedback on logic)
- **Playwright**: E2E tests (critical user flows in real browsers)
- **Percy**: Visual regression tests (catch CSS issues)

**Test Pyramid**:
```
       /\
      /  \    E2E (5-10 tests)
     /____\   
    /      \  Integration (20-30 tests)
   /________\ 
  /          \ Unit (50+ tests)
 /____________\
```

**Pros**:
- ✅ **Full coverage**: Logic, user flows, and visuals all tested
- ✅ **Right tool for each job**: Fast unit tests, comprehensive E2E, automated visual QA
- ✅ **High confidence**: Multiple layers catch different types of bugs

**Cons**:
- ❌ **Complexity**: Three tools to learn and maintain
- ❌ **CI time**: Longer pipeline (5-7 minutes total)
- ❌ **Cost**: Percy may require paid plan eventually

**Estimated Effort**: 2 weeks (setup all tools, write tests)  
**Technical Complexity**: Medium-High  
**Ongoing Maintenance**: Medium

---

## More Information

### Related Decisions
- Related to [tech-stack.md - Testing Infrastructure](../tech-stack.md#5-testing-infrastructure-enhancements)
- May inform [ADR-003: Student Portal Architecture](003-student-portal-architecture.md) (testing strategy for new features)

### Research & References
- [Playwright Documentation](https://playwright.dev/)
- [Percy Documentation](https://docs.percy.io/)
- [Chromatic Documentation](https://www.chromatic.com/docs/)
- [Testing Trophy vs Pyramid](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- [Playwright vs Cypress Comparison](https://playwright.dev/docs/why-playwright)

### Validation Plan
If we choose the hybrid approach:

**Phase 1: Playwright (Week 1)**
- [ ] Install Playwright
- [ ] Write 5 critical E2E tests (contact form, modal, navigation)
- [ ] Integrate with GitHub Actions
- [ ] Run on every PR

**Phase 2: Percy (Week 2)**
- [ ] Set up Percy account (free tier)
- [ ] Capture baselines for key pages (homepage, services, testimonials)
- [ ] Test responsive layouts (mobile, tablet, desktop)
- [ ] Enable PR comments with visual diffs

**Phase 3: Expand Coverage (Ongoing)**
- [ ] Add E2E tests for new features
- [ ] Update visual baselines when designs change
- [ ] Monitor CI times, optimize if >7 minutes

**Success Metrics**:
- Zero visual regressions reach production (caught by Percy)
- <5% flaky test rate (E2E tests are reliable)
- CI completes in <7 minutes (acceptable overhead)
- Developer satisfaction: Tests help more than they hinder

**Review Date**: Q2 2026 - Evaluate test coverage, CI times, Percy costs

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-12-17 | Initial proposal | Development Team |
| TBD | Decision pending implementation of Phase 1 | - |
