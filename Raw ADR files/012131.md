# ADR-1: Frontend Technical Decisions

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-02
- **Feature:** 1-ai-textbook-frontend
- **Context:** This ADR documents the key architectural and design decisions made for the "Physical AI & Humanoid Robotics" Textbook Frontend, including core functionalities, data handling for personalization, blog presentation, authentication integration, and the overall design system. These decisions address the requirements laid out in the feature specification and implementation plan.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   **Translation Strategy:** Use the "Backend Proxy" pattern for fetching translations to ensure security, centralize API key management, and enable server-side caching for AI translation services.
-   **Personalization State:** Store the user's choice ("Beginner" vs "Programmer") in a "User Database" on the backend for cross-device persistence. Additionally, utilize "Local Storage" on the frontend for immediate, client-side persistence within a single browser session to enhance responsiveness and user experience.
-   **Blog Layout:** Implement a "Custom Layout" for the blog section with minor adjustments to the standard Docusaurus default. This allows for unique theming and branding while leveraging Docusaurus's core blog functionality.
-   **Authentication Integration:** The "Login/Signup" button will interact via "Direct Frontend to Backend API" calls for Better-Auth integration, providing granular control over the authentication flow and user experience.
-   **Design System (Theme):**
    -   **Primary Color:** Orange (chosen for its high-energy, robotics-inspired feel).
    -   **Dark Mode:** Orange accents on a Black background.
    -   **Light Mode:** Orange accents on a White background.
    -   **Rationale:** This custom theme creates a distinct brand identity for the textbook, differentiating it from the default Docusaurus blue, while meeting accessibility standards (contrast ratios). This decision intentionally deviates from the constitution's "standard Docusaurus styling (Infima)" to achieve specific branding goals, a tradeoff justified by the project's unique identity requirements.

## Consequences

### Positive

-   **Enhanced Security:** Backend proxy for translation protects API keys and provides a controlled translation environment.
-   **Improved User Experience:** Personalization choices persist across sessions and devices via the user database, with local storage providing immediate feedback.
-   **Distinct Brand Identity:** Custom Orange theme provides a unique and memorable visual appeal for the textbook, aligned with the robotics theme.
-   **Flexible Auth Integration:** Direct API calls allow for tailored authentication flows with Better-Auth.
-   **Maintainable Blog:** Leveraging Docusaurus blog functionality with minor custom adjustments balances uniqueness with ease of maintenance.

### Negative

-   **Increased Backend Dependency:** Translation and personalization features require a robust backend infrastructure.
-   **Frontend-Backend Coupling:** Direct API calls for authentication can lead to tighter coupling between frontend and backend.
-   **Custom Styling Overhead:** Deviating from standard Docusaurus Infima styling might require more custom CSS maintenance and careful accessibility validation.
-   **Accessibility Validation:** The custom orange theme requires rigorous testing to ensure it meets WCAG 2.1 AA contrast ratio accessibility standards.

## Alternatives Considered

-   **Translation Strategy Alternatives:**
    -   *Direct API Call (Rejected):* Higher risk of exposing API keys, potential for rate limit issues directly from frontend, less control over translation logic.
    -   *Pre-translated Content (Rejected):* Increased build times, lack of real-time translation flexibility, higher content management overhead for multiple languages.
-   **Personalization State Alternatives:**
    -   *Local Storage Only (Rejected):* User preferences would not sync across devices or browsers, leading to an inconsistent experience.
    -   *Session Storage Only (Rejected):* Preferences would be lost upon session end, negating the benefit of personalization.
-   **Blog Layout Alternatives:**
    -   *Standard Docusaurus Layout (Rejected):* Would not meet the requirement for a unique theming and distinct brand identity.
    -   *Fully Custom Layout (Rejected):* Would involve significantly more development and maintenance effort, potentially losing benefits of Docusaurus's built-in blog features.
-   **Authentication Integration Alternatives:**
    -   *OAuth/OpenID Connect Flow (Rejected):* While robust, a direct API integration was preferred for simpler initial integration with Better-Auth and more control over the user experience.
    -   *Docusaurus Plugin/Module (Rejected):* Lack of suitable existing plugins for Better-Auth, or insufficient flexibility for custom requirements.
-   **Design System (Theme) Alternatives:**
    -   *Standard Docusaurus Infima (Rejected):* Would not achieve the desired distinct brand identity and high-energy robotics feel.

## References

-   Feature Spec: `specs/1-ai-textbook-frontend/spec.md`
-   Implementation Plan: `specs/1-ai-textbook-frontend/plan.md`
-   Related ADRs: N/A
-   Evaluator Evidence: `history/prompts/1-ai-textbook-frontend/2-clarified-frontend-specification-ambiguities.spec.prompt.md` (for clarification questions on technical aspects)
    `history/prompts/1-ai-textbook-frontend/3-created-frontend-implementation-plan.plan.prompt.md` (for plan creation and constitution check discussion)
