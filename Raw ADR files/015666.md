# 1. weasyprint as PDF rendering tool

Date: 2025-09-17

## Status

Accepted

## Context

We want to generate PDF files for published norms, court decisions, VwV & literature.
This step will happen during the publishing process to the NeuRIS portal and be called from the tools for the individual
document types.

We looked at different tools that can be used for this. The initial research is documented on [Confluence🔒](https://digitalservicebund.atlassian.net/wiki/spaces/VER/pages/1900019740/PDF+generation+options). From
this research we reduced the options to
- Open HTML to PDF
- Apache FOP
- weasyprint
- headless chromium (with puppeteer)

We looked at these options in more detail, especially in regard to:
- their maturity
- how complex generating files is
- if they can create accessible PDFs
- if they can create PDF/A files
- if they are actively maintained

We also tested that weasyprint is able to create PDF-files for very-long norms and norms with many images (using the BGB and StVO). It was able to do this in a reasonable time-frame.

## Decision

We decided to use **weasyprint**.

*Weasyprint* is able to create accessible PDF/A files, is actively maintained and mature. It is also simple to create good
PDF files as it is able to created them from an HTML-file and CSS. The rendering engine also supports modern CSS
features.

*Apache FOP* provides more flexibility in creating PDF files. But we would need to create an intermediate representation
in a custom dataformat, greatly increasing the complexity.

*Open HTML to PDF* is not actively maintained and does not support modern HTML and CSS features.

*Headless chromium (with puppeteer)* is not able to create PDF/A files, it's accessibility features are still
experimental, and it offers the fewest methods to influence the PDF generation.

## Consequences

We have decided for a tool and can start working on implementing the service. We can (mostly) use the existing HTML and
CSS files for creating the PDF files.

We can not influence every last detail of the PDF generation, if we want to have that flexibility in the future we should
switch to *Apache FOP*. But that comes with a lot more complexity.

We could still exchange the tool and use *Headless chromium (with puppeteer)* or another HTML to PDF converter tool. If
that tool does not support modern HTML and CSS features, like *Open HTML to PDF*, the effort to create new HTML and CSS
files is the same as the effort we now save by going with a tool that supports modern HTMl and CSS.

Our project will be using Python.