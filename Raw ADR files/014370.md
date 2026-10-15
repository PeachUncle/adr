# ADR-002: Unified Site Architecture

## Status
Accepted

## Context
Previously maintained two separate portfolio sites:
- Engineering portfolio on `main` branch (clintonlangosch.com)
- Technical writing portfolio on `main-tw` branch

This created maintenance overhead and missed opportunities to showcase the intersection of Clinton's technical writing and engineering expertise.

## Decision
Create a unified portfolio site with:
- Single homepage explaining dual expertise
- Specialized landing pages: `/technical-writing` and `/software-engineering`
- Shared pages with filtering: `/skills`, `/projects`, `/experience`
- Query parameter-based filtering: `?focus=writing|engineering|all`

## Rationale

### Benefits of Unified Approach:
1. **Professional Brand**: Shows full range of expertise
2. **Simplified Maintenance**: Single codebase, single deployment
3. **Better SEO**: More content on single domain
4. **Cross-pollination**: Writing skills enhance engineering roles and vice versa
5. **User Experience**: Visitors can explore both areas easily

### Site Structure:
```
/                          # Unified landing page
/technical-writing         # Writing-focused overview
/software-engineering      # Engineering-focused overview
/skills?focus=writing      # Filtered skills display
/projects?focus=engineering# Filtered projects display
/experience               # Work history (may add filtering later)
/about                    # Detailed background
```

### Filtering Strategy:
- URL-based state management with query parameters
- Vanilla JavaScript for filtering logic
- CSS transitions for smooth filtering animations
- Shareable filtered URLs

## Consequences

### Positive:
- Single maintenance burden
- Professional presentation of dual expertise
- Better content discoverability
- Simplified hosting and deployment

### Negative:
- Homepage design complexity (must clearly communicate both areas)
- Navigation UX must be intuitive
- Risk of confusing visitors about primary focus

### Implementation Requirements:
- Clear visual hierarchy on homepage
- Intuitive navigation between focus areas
- Effective filtering UX with smooth transitions
- Mobile-responsive design for both contexts