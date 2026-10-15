# Use of DomPDF for Generating PDF Documents in Laravel Project

* Status: Done
* Deciders: Fuensanta Sansano Montoya and Tomás Raigal López
* Date: 2023-04-01

## Context and Problem Statement

In our Laravel project, we aim to provide users (parents, teachers, and students) with the ability to generate various types of documentation required for different situations, such as doctor appointments, school trips, and more. It is crucial that our system adheres to the regulations set forth by the Reglamento General de Protección de Datos (RGPD) in Spain, ensuring that no personal information is stored in the generated documents.

We need to select a suitable library for generating PDF documents that aligns with our project requirements, including compliance with data protection regulations.

## Decision Drivers

* Easy integration with Laravel framework
* Compliance with data protection regulations (RGPD)
* Adequate support for complex layouts and styling
* Good performance and stability
* Active community and ongoing development
* Licensing and cost considerations

## Considered Options

1. DomPDF
2. TCPDF
3. FPDF
4. mPDF

## Decision Outcome

Chosen option: DomPDF, because it provides a comprehensive solution for generating PDF documents in the Laravel framework, ensuring compliance with data protection regulations, and meeting our decision drivers.

### Positive Consequences

* **Integration with Laravel**: DomPDF is well-integrated with the Laravel framework, making it easy to use within our existing codebase and leveraging Laravel's features and functionalities.
* **Data Protection Compliance**: DomPDF allows us to generate PDF documents without storing any personal information, ensuring compliance with the RGPD and protecting the privacy of our users.
* **Layout and Styling**: DomPDF provides robust support for complex layouts and styling, allowing us to create visually appealing and professional-looking documents.
* **Performance and Stability**: DomPDF has a reputation for good performance and stability, enabling efficient and reliable generation of PDF documents.
* **Active Community and Development**: DomPDF benefits from an active community of developers and ongoing development, ensuring that it stays up-to-date with the latest technologies and security practices.
* **Licensing and Cost**: DomPDF is an open-source library released under the MIT license, making it cost-effective for our project.

### Negative Consequences

* **Alternative Libraries**: It is worth considering other libraries like TCPDF, FPDF, and mPDF, as they may also offer some advantages or features that could be beneficial for our specific use case.

## Alternatives Considered

### TCPDF

TCPDF is a popular PHP library for generating PDF documents. It provides extensive features and supports various functionalities. However, in our evaluation, we found that TCPDF's integration with Laravel may require additional effort and customization compared to DomPDF. Additionally, while TCPDF is a capable library, it may not offer specific features or optimizations that are critical for our project.

### FPDF

FPDF is another widely used PHP library for PDF generation. It is lightweight and easy to use, but it may lack certain advanced features and support for complex layouts and styling that we require for our project. Additionally, FPDF may not have the same level of community support and ongoing development as DomPDF.

### mPDF

mPDF is a PHP library that aims to provide a high degree of compatibility with HTML and CSS, making it easy to convert HTML content into PDF documents. While mPDF offers excellent HTML-to-PDF conversion capabilities, it may have limitations in terms of advanced styling options and support for complex layouts. Moreover, mPDF's integration with Laravel may require additional configuration and customization compared to DomPDF.

## Links

* [DomPDF GitHub Repository](https://github.com/dompdf/dompdf)
* [TCPDF GitHub Repository](https://github.com/tecnickcom/tcpdf)
* [FPDF Website](http://www.fpdf.org/)
* [mPDF GitHub Repository](https://github.com/mpdf/mpdf)
