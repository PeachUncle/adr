# Architecture Decision Record (ADR)

## ADR 07: Using AI to Generate Architecture Questions for the Exam

### Status
- ACCEPTED

### Context
We are exploring opportunities to integrate Generative AI into the certification process. One critical aspect is the creation 
of high-quality examination questions that assess candidates’ knowledge and skills in software architecture. Automating 
the generation of these questions using AI can enhance scalability, reduce the manual workload on experts, and ensure a 
diverse and updated question pool that reflects current industry standards.

### Decision
To implement an AI-based approach for generating architecture exam questions, we will proceed with the following plan:

- Integration of Generative AI Models:
Utilize advanced Generative AI models, such as those available through Amazon Bedrock, to create a wide variety of 
architecture-related questions. This approach will leverage existing databases of architectural concepts, best practices, 
and industry standards to produce relevant and challenging questions.

- AWS Step Functions for Orchestration:
Implement AWS Step Functions to coordinate the workflow of generating questions. This will allow us to manage multiple 
calls to Bedrock in parallel and sequentially, ensuring efficient data retrieval and question generation processes.
  
- Retrieval-Augmented Generation (RAG):
Rather than fine-tuning a specific AI model, we will use the RAG capabilities similar to those employed in the Aptitude Test Grader.
This will involve retrieving expert-collated reference material to inform the question generation process, ensuring that the
generated content is rooted in high-quality, relevant resources.

- Dynamic Question Generation:
Enable the AI system to generate questions dynamically based on various parameters such as difficulty level, topic 
coverage, and current trends in software architecture. This flexibility will ensure that the examination remains relevant 
and comprehensive.

- Expert Review Mechanism:
Establish a review process where expert software architects evaluate AI-generated questions for clarity, accuracy, and 
relevance. This step will help maintain the integrity of the examination process and ensure that all questions adhere to 
consistently high standards.

- Feedback Loop for Continuous Improvement:
Create a mechanism to collect feedback on the effectiveness of AI-generated questions from both candidates and experts. 
This feedback will inform further iterations and improvements of the AI model, ensuring that it evolves based on real-world 
performance.

Guardrails:

- Quality Assurance Processes:
Establish strict guidelines for expert reviewers to follow when assessing AI-generated questions. This includes criteria for clarity, relevance, accuracy, and adherence to industry standards.

- Bias Mitigation:
Implement evaluation checks to ensure that the AI-generated questions do not exhibit biases against any group of candidates. Regular audits will be conducted to identify and address any emerging biases in the content generated.

- Data Governance:
Ensure compliance with data privacy regulations when utilizing reference materials for RAG. All training and retrieval data must be vetted for quality and relevance to prevent misinformation.

- Training and Support:
Provide training for expert reviewers on how to effectively evaluate AI-generated content, including understanding the limitations of AI and how to interpret its outputs.

Evaluations (Eval Metrics)

- Grading Accuracy of AI-Generated Questions:
Track how well the AI-generated questions perform when used in exams, comparing results against expert-reviewed standards and candidate outcomes.

- User Feedback Collection:
Implement a system for collecting qualitative feedback from candidates about the clarity and relevance of the questions, as well as their perceived fairness.

- Performance Monitoring:
Measure the efficiency of the question generation process, including time taken to generate questions and the computational resources utilized, ensuring that it remains cost-effective.

- Adaptability Assessments:
Regularly evaluate how well the AI system adapts to changes in exam requirements, feedback from candidates and experts, and shifts in the software architecture field.

- Review Consistency Metrics:
Assess the consistency of evaluations provided by expert reviewers on AI-generated questions. This will help ensure that there is alignment in grading and feedback standards across different reviewers.

### Alternatives Considered
- **Option 1:** Manual Question Creation:
Continuing to rely solely on expert architects for question generation was considered. However, this approach is not 
scalable and does not efficiently meet the projected demand. The manual process can be time-consuming and may lead to a 
static question pool.

- **Option 2:** Static Question Bank:
Using a static question bank that has not been updated was an alternative. This option risks producing outdated content 
and may not adequately assess the evolving landscape of software architecture, reducing the effectiveness of the certification.

- **Option 3:** Hybrid Approach with Limited AI Use:
A hybrid model where AI aids experts but does not generate full questions was also evaluated. While this could enhance 
efficiency, it may not fully leverage the capabilities of Generative AI to provide diverse and comprehensive question 
coverage.

### References

### Date
02/13/2025
