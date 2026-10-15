# ADR-006: Anonymizing PII Data Before LLM Processing

### Date: 2024-09-30

### Status: Accepted

### Decision Maker: Engineering Team

### Context:

Clearview utilizes LLMs to process resume data for features like pre-screening and story generation. Resumes contain Personally Identifiable Information (PII) that needs to be protected. We need to decide whether to anonymize the resume before sending it to the LLM or rely on the LLM to anonymize the data.

### Decision:

We will anonymize the resume data by removing PII before sending it to the LLM. This will be handled by a separate anonymization layer within our application.

### Reasons:

- **Data Security and Privacy**: We prioritize the security and privacy of user data. Anonymizing PII before sending it to the LLM reduces the risk of unintended data exposure or persistence within the LLM's internal systems.
- 
- **LLM Agnosticism**: We aim to maintain flexibility in our choice of LLMs. By handling anonymization separately, we avoid relying on specific LLM providers for PII handling and ensure compatibility with future LLMs.
- 
- **Transparency and Control**: A separate anonymization layer gives us greater control and transparency over the process. We can clearly define and manage how PII is handled, ensuring compliance with data protection regulations and standards.
- 
- **Uncertainty about LLM Data Handling**: We are still uncertain about how LLMs store and process data internally. We prefer to err on the side of caution and minimize the amount of PII exposed to the LLM.

### Consequences:

- **Increased Development Effort**: Implementing a separate anonymization layer requires additional development effort.
- **Potential Performance Overhead**: The anonymization process may introduce a slight performance overhead.
- **Improved Data Security**: Reduced risk of PII leakage or misuse.
- **Enhanced Flexibility**: Facilitates easier integration with different LLMs.

### Alternatives Considered:

**Relying on LLM for Anonymization**: This was rejected due to concerns about data security, vendor lock-in, and lack of transparency in LLM data handling practices.

### Notes:

- The anonymization layer will be designed to be configurable and adaptable to handle different types of PII and anonymization techniques.
- We will regularly review and update our anonymization strategy to align with evolving best practices and data protection regulations.
- This ADR prioritizes data security and privacy by implementing a dedicated anonymization layer before LLM processing, ensuring greater control and flexibility in our application architecture.
