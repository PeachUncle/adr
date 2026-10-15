# HTML for Human Readability and LaTeX for ATS-Friendly Resume Output

- **Status**: accepted
- **Deciders**: [Your Team Members] <!-- Replace with actual names -->
- **Date**: [YYYY-MM-DD] <!-- Use current date -->

## Context and Problem Statement

- **Business Goal**:
    - Generate resumes that are highly **customizable**, **professional**, and **functional for both humans and machines** (ATS parsing).
    - Use **HTML** to showcase design skills and provide a web-based, human-readable resume.
    - Use **LaTeX** to generate structured outputs optimized for ATS compliance in PDF format.

- **Technical Problem**:
    - Resume content is already stored in a structured JSON file.
    - The solution should minimize duplication of effort while allowing for two separate outputs:
        - A **modern, styled HTML resume** for human interaction, sharing, and web hosting.
        - A **structured LaTeX resume** to ensure ATS parsing compatibility.
    - Both outputs need to stay consistent and dynamic, pulling from the same data source.

- **Scope**: This decision impacts the resume generation pipeline and output format generation process.

---

## Decision Drivers

1. Showcase **HTML/CSS/JavaScript skills** through a web-based, customizable resume design.
2. Create a separate, **ATS-friendly resume** for systems that require text-heavy PDFs.
3. Use **JSON** as the single source of truth for easy synchronization across both formats.
4. Automate the process to minimize manual intervention and ensure consistency.

---

## Considered Options

1. **HTML for Human Readability + LaTeX for ATS-Friendliness.**
2. **LaTeX Only** for both human-readable and ATS-friendly resumes.
3. **Enhanced HTML Templates** to balance both human-readable and ATS-friendly designs.

---

## Alternatives Considered but Rejected Early

1. **LaTeX Only**:
    - **Reason eliminated**: LaTeX excels in ATS parsing but is less flexible when it comes to showcasing design skills or sharing work easily (e.g., for portfolios or web hosting).
    - Sharing or hosting a PDF-only resume limits interactivity and engagement with online visitors.

2. **Enhanced HTML Templates**:
    - **Reason eliminated**: Trying to balance human readability with text-heavy structures designed for ATS runs the risk of compromising flexibility and creativity.
    - CSS-based adjustments for ATS compliance can introduce additional complexity, requiring print-friendly CSS that might affect the overall design.

---

## Decision Outcome

- **Chosen Option**: **HTML for Human-Readable Resumes + LaTeX for ATS-Friendly Resumes**

    - **Reasoning**:
        1. This approach uses the strengths of both formats:
            - **HTML**: Customizable for visually appealing, human-readable resumes that showcase design skills.
            - **LaTeX**: Structured and optimized for machine parsing (ATS compliance) and PDF generation.
        2. By using JSON as the single source of truth, both outputs remain synchronized while minimizing duplication of effort.
        3. HTML resumes allow for easy sharing as URLs, while LaTeX PDFs ensure maximum compatibility across ATS systems.

### Positive Consequences
- Professional, modern HTML design highlights skills and creativity while being easy to share.
- ATS parsing is ensured with LaTeX's simple, structured output.
- Both formats stay in sync, with content dynamically generated from JSON.

### Negative Consequences
- Maintaining two separate templates (HTML + LaTeX) may require some additional effort.
- Familiarity with LaTeX is required for fine-tuning the ATS-focused template.

---

## Risks and Mitigations

- **Risk 1**: Maintaining two distinct templates could lead to inconsistencies in formatting or content.
    - **Mitigation**:
        - Use JSON as the single source of truth for all resume content.
        - Automate both HTML and LaTeX generation with a shared script or pipeline to ensure consistency.

- **Risk 2**: HTML output might not meet ATS compliance if the need arises later.
    - **Mitigation**:
        - Provide a fallback (e.g., plain-text export from JSON or a simplified LaTeX version).

- **Risk 3**: LaTeX requires domain knowledge for custom formatting.
    - **Mitigation**:
        - Start with pre-existing LaTeX templates like `moderncv` or `AltaCV` and only customize essentials.
        - Automate the LaTeX build process using tools like `pdflatex` or `tectonic`.

---

## Analysis of the Options

### Option 1: **HTML (Human) + LaTeX (ATS)**
- **Good, because**:
    - HTML/CSS is highly flexible, enabling fully customized, modern designs.
    - LaTeX provides structured, parseable outputs for ATS and simplifies creating PDFs.
    - JSON as the content source ensures consistency across both human-readable and machine-readable resumes.
    - Both formats can be generated dynamically, minimizing duplication of effort.
- **Bad, because**:
    - Two templates must be maintained (HTML and LaTeX), which adds complexity.

---

### Option 2: **LaTeX Only**
- **Good, because**:
    - Tailored for ATS parsing, with minimal adjustments needed for compliance.
    - Outputs professional, consistent PDFs with clear structures.
- **Bad, because**:
    - Lacks flexibility for showcasing creative or interactive designs.
    - Not easily shareable in digital-first forms like a web-hosted portfolio.
    - Requires familiarity with LaTeX for meaningful customization.

---

### Option 3: **Enhanced HTML Templates for Dual Purposes**
- **Good, because**:
    - One template for both human-readable and ATS-friendly outputs reduces duplication.
    - HTML/CSS allows flexibility in design.
- **Bad, because**:
    - Balancing creative designs with ATS compliance in pure HTML is complex and prone to errors.
    - Certain ATS systems that prefer PDFs might not parse HTML correctly.

---

## Final Decision

The decision is to adopt **HTML for human-readable resumes** and **LaTeX for ATS-friendly resumes**.

### Summary of the Approach

- Content for both templates will be dynamically generated from a structured JSON file.
- **Human-readable resume** will use a flexible HTML template styled with CSS (and optionally JavaScript frameworks like React or Astro for interactivity).
- **ATS-focused resume** will use a clean and structured LaTeX template to generate PDF outputs for better parsing.
- Automation in the build process will generate both outputs together, ensuring consistency between the two formats.

This approach strikes the right balance between creativity, ease of sharing, and ATS compatibility, while leveraging structured data for scalability.