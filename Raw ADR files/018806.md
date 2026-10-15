# ADR-0002: Landing Page Design and Structure

## Decision
Implement a single-component landing page using inline CSS and a clean, responsive design for MEA Fusion's business presence.

## Context
MEA Fusion needed a professional landing page to showcase services, establish credibility, and provide contact information for potential clients interested in Power Platform solutions.

## Decision Details

### Structure
- **Single React component** (`/src/components/LandingPage.jsx`) for simplicity
- **Inline CSS** to avoid external dependencies and keep the bundle lightweight
- **Services array** in code for easy future extensibility
- **Mobile-first responsive design** using CSS Grid and Flexbox

### Styling Choices
- **MEA Fusion brand colors**: Red (#dc2626) for titles/buttons, Green (#16a34a) for subtitles, Black (#000000) for body text
- **White background** with clean minimalist layout
- **Card-based services grid** with hover effects for interactivity
- **Smooth scrolling anchor navigation** for CTA button

### Content Strategy
- **Hero section**: Logo, compelling headline "Audit Smart, Implement Smarter", clear value proposition
- **Services showcase**: 7 core service areas with descriptions
- **Trust indicators**: MVP credentials, multi-industry experience, DevOps expertise
- **Contact flow**: Email link with placeholder for future form integration

## Consequences

### Positive
- Fast loading with minimal dependencies
- Easy to customize services, colors, and content
- Professional appearance establishing credibility
- Responsive design works across all devices
- Clear conversion path via Contact CTA

### Negative
- Inline CSS makes component file larger
- Limited styling reusability across other components
- Manual updates required for content changes (no CMS)

## Alternatives Considered
- External CSS framework (rejected: adds dependency overhead)
- Separate CSS files (rejected: complicates deployment to Power Pages)
- Multi-page routing (rejected: unnecessary complexity for landing page)