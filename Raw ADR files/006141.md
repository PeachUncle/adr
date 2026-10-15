# For Cost Efficiency and Data Privacy, Use a Cloud-Hosted AI Model with Private Data Controls (e.g., AWS Bedrock, Azure OpenAI, OpenAI API, Google Vertex AI)

## Status
Proposed

## Date
2025-02-15

## Deciders
- Architectrons

---

## Context and Problem Statement

Certifiable, Inc. is integrating **AI-driven automation** for **grading certification exams** and **candidate authentication**. The solution must:

- **Ensure Data Privacy & Security** – **Test content and candidate responses must remain private** and **must not be used for training public LLMs**.
- **Provide Cost Efficiency** – AI services must be scalable **without incurring unnecessary operational overhead**.
- **Ensure Scalability & Performance** – AI processing must **support an increasing number of candidates** while maintaining **low-latency inference**.
- **Enable Explainability & Governance** – AI grading decisions must be **auditable and explainable** to ensure fairness.

To meet these requirements, **a cloud-hosted AI model with strict data privacy controls** (e.g., **Claude 3 Series, GPT-4o (o1) , Llama 3, Gemini 2, Mistral**) is chosen, accessed via **AWS Bedrock, OpenAI API, Azure OpenAI, and Google Vertex AI**. This ensures **test cases and grading data are not stored or used for public AI model training**.

---

## Decision Drivers

1. **Data Privacy & Security** – Certification test cases and responses **must not be stored or used to train external AI providers**.
2. **Cost Efficiency** – **Cloud-based AI services provide cost-effective scaling** compared to traditional manual grading.
3. **Scalability & Availability** – **Cloud AI services provide elastic scaling**, ensuring **low-latency inference** for large candidate volumes.
4. **Explainability & AI Governance** – AI-generated grading decisions must be **auditable, explainable, and bias-free**.

---

## Considered Options

1. **Cloud-Hosted AI Model with Private Data Controls (Claude 3, GPT-4o, Llama 3, Gemini 2.0, Mistral) – Chosen**  
   - **Models Used:** **Claude 3 (Sonnet, Opus, Haiku), GPT-4o, Llama 3, Gemini 2.0, Mistral 7B**
   - **Access via:** AWS Bedrock, OpenAI API, Azure OpenAI, Google Vertex AI  
2. **Third-Party API Integration**  
   - **Direct API calls to OpenAI (GPT-4 Turbo), Anthropic (Claude 3), Mistral, and Meta AI**  
3. **Hybrid Approach: Cloud AI with Local Processing for Additional Privacy Protections**  
4. **Traditional Manual Grading (Baseline Comparison)**  

---

## Decision Outcome

### Chosen option: "Cloud-Hosted AI Model with Private Data Controls" (Claude 3, GPT-4o, Llama 3, Gemini 2.0, Mistral)

#### Justification
- **Ensures test content remains private and does not contribute to public AI training datasets.**
- **More cost-efficient than manual grading**, eliminating the need for **large-scale human grading teams**.
- **Elastic scalability** ensures AI inference remains **fast and available** as demand grows.
- **Supports AI explainability tools for bias detection, transparency, and compliance audits**.

---

## Implementation Details: Cloud-Hosted AI Model

### AI in Aptitude Test Grading

#### ✅ Automated Short Answer Evaluation
- **Cloud-hosted LLM (AWS Bedrock Claude Sonet, OpenAI GPT-4o, Azure OpenAI)** evaluates short answers.
- AI **assigns an initial score** and **provides explainable feedback**.
- **Low-confidence cases** are flagged for **human review**.

#### ✅ Plagiarism & Similarity Detection
- **Semantic similarity analysis** detects copied responses using cloud AI APIs.
- Ensures test integrity by comparing responses against past submissions.

#### ✅ Adaptive Feedback Generation
- **Retrieval-Augmented Generation (RAG) ensures AI-generated feedback is based on expert-approved sources**.
- Example: _"Your response lacked detail on event-driven architectures. Consider how microservices communicate asynchronously."_

---

### AI in Architecture Submission Grading

#### ✅ AI-Assisted Architecture Review
- **Cloud AI services analyze diagrams, documents, and descriptions**.
- Uses **OCR + NLP (AWS Textract, Google Vision API, Azure Cognitive Services)** to interpret architecture diagrams.
- AI compares designs against **best practices for scalability, security, and resilience** from private knowledgebase

#### ✅ AI-Generated Initial Score & Comments
- AI assigns **preliminary scores with confidence ratings**.
- **High-confidence cases auto-graded**, **low-confidence cases flagged for human review**.

---

### AI in Certification Candidate Authentication

#### ✅ Fraud Prevention & Identity Verification
- **Cloud AI-powered facial recognition (AWS Rekognition, Azure Face API, OpenAI Vision API)** verifies candidate identity.
- **Real-time webcam analysis prevents impersonation and exam fraud**.

---

## AI Explainability & Compliance Tools

- **AWS SageMaker Clarify** – AI bias detection and explainability.
- **Azure Machine Learning Interpretability SDK** – Helps explain AI grading results.
- **Google Vertex AI Explainable AI** – Provides transparency in AI decision-making.
- **OpenAI API with Explainability Frameworks** – Allows deeper auditing of grading outcomes.

---

## Consequences

✅ **Benefits:**
- **More cost-efficient than manual grading.**
- **Prevents test content from being stored in public AI models.**
- **Ensures scalable, low-latency AI inference for real-time grading and verification.**
- **Supports AI explainability and governance tools for compliance audits.**

⚠️ **Risks:**
- **Cloud AI inference costs scale with usage**, requiring **cost monitoring**.
- **Requires strong data governance policies** to **prevent accidental data exposure**.
- **Dependency on cloud provider availability** (e.g., AWS, Azure, OpenAI).

---

## Pros and Cons of the Options

### Option 1: Cloud-Hosted AI Model with Private Data Controls **(Chosen)**
- ✅ **Good:** **Ensures data privacy while leveraging scalable AI models.**
- ✅ **Good:** **More cost-effective than manual grading.**
- ✅ **Good:** **Supports explainability tools for AI transparency.**
- ⚠️ **Neutral:** Requires **strong governance policies to prevent data exposure.**

### Option 2: Third-Party API Integration (OpenAI, Claude, Gemini, etc.)
- ✅ **Good:** **Easy to integrate and quick to deploy.**
- ❌ **Bad:** **Limited control over model usage policies.**
- ❌ **Bad:** **Risk of accidental exposure to public LLMs.**

### Option 3: Traditional Manual Grading (Baseline Comparison)
- ✅ **Good:** **Trusted grading accuracy.**
- ❌ **Bad:** **Not scalable, costly, slow.**

---
