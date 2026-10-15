# ADR-0003: Terminology and Project Structure

## Status

Accepted

## Date

2024-10-18

## Context

Initial terms "theme" and "template" were ambiguous. The project structure was too deep (5 nested levels), making navigation difficult.

Early iterations:

```
# Version 1 (rejected)
themes/awesome_cv/templates/

# Version 2 (rejected)
themes/awesome_cv/latex/document_types/

# Version 3 (rejected)
templates/awesome_cv/latex/document_types/resume.tex.j2
```

## Options Considered

### Option 1: Deep Hierarchy

Keep separate directories for latex, document_types, sections.

**Pros:**

- Explicit categorization
- Room for future expansion

**Cons:**

- Hard to navigate (5+ levels deep)
- Over-engineered for current needs
- Confusing for newcomers

### Option 2: Flat Structure

Minimal nesting with clear naming.

**Pros:**

- Easy navigation
- Clear file locations
- Simple mental model

**Cons:**

- May need restructuring if project grows significantly

## Decision

### Terminology

| Term | Definition | Example |
|------|------------|---------|
| **Template** | A set of LaTeX styles | Awesome-CV, ModernCV |
| **Document type** | A kind of document | resume, cv, coverletter |
| **Section** | A reusable component | education, experience, skills |

### Structure

```
templates/awesome_cv/
├── awesome-cv.cls       # LaTeX class file
├── resume.tex.j2        # Document types (top level)
├── cv.tex.j2
├── coverletter.tex.j2
└── sections/            # Reusable sections
    ├── education.tex.j2
    ├── experience.tex.j2
    └── skills.tex.j2
```

Removed redundant `latex/` and `document_types/` levels.

## Consequences

### Positive

- 3 levels instead of 5
- Clear terminology in code and docs
- Easy for newcomers to understand
- Consistent naming across project

### Negative

- May need adjustment for very different template families
- Less explicit categorization

## API Alignment

Terminology is reflected in the API:

```python
# Template = awesome_cv, doc_type = resume
renderer = Renderer(template="awesome_cv")
renderer.render("resume", data)
renderer.list_document_types()  # ["resume", "cv", "coverletter"]
```

## References

- [KISS Principle](https://en.wikipedia.org/wiki/KISS_principle)
