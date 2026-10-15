# Architecture Decision Record (ADR)

## ADR 10: AI Agent to Monitor Candidates for Cheating

### Status
- REJECTED
  
### Context
It is very important that the certification process for applicants can be trusted and includes appropriate guardrails and evals. There is a very real possibility that
candidates could use search engines or even AI to cheat during the assessments. An AI-driven monitoring system could 
provide real-time insights into candidate behaviour, flagging potential cheating without disrupting the user experience.

Common Cheating Indicators could include:

Identical Answer Patterns: Looking for candidates with identical answers, especially in multiple-choice questions.
Unusual Score Patterns: Identifying scores that are significantly higher or lower than expected, based on historical data.
Time Spent on Questions: Analysing how much time students spent on each question. Extremely fast completions may indicate cheating, especially if paired with high scores.
Answer Consistency: Examine the consistency of answers. If a candidate changes answers frequently or has inconsistent scoring across similar questions, it may be suspicious.
Response Time Anomalies: Sudden spikes or reductions in response times, compared to peers, might indicate irregular behavior.

### Decision
While implementing this could be very valuable, we are not recommending it for MVP, in the future we could implement an AI agent that utilizes machine learning algorithms to monitor candidates during assessments, analyse behavioral patterns, and identify anomalies that may indicate cheating. 
The system will ensure a seamless user experience for applicants while providing certifiers with valuable insights and alerts. As this is not recommended for the MVP, it is a future feature that will add value and help build the reputation of the company as we grow.

### Alternatives Considered
**Option 1:** Real-Time AI Monitoring  

**Description**: Implement an AI system that analyses candidates' video feeds and interactions during assessments to detect 
suspicious behavior or anomalies in real time. This option would involve collecting video and interaction data and using
that to create a dataset. We would then need to label a dataset of normal and suspicious behaviors to train the AI model.
Frameworks such as TensorFlow or PyTorch could be used to develop AI algorithms to develop our model which could then be
trained using our labelled dataset. Alerts could be added to notify when suspicious behaviour is detected. An important eval would 
involve measuring the rate of false positives (e.g., legitimate candidates flagged for suspicious behavior) to ensure the 
system's accuracy and to refine the algorithms used for detection.

**Pros**:  
Immediate feedback and alerts for certifiers.
Enhanced detection of cheating through behavior analysis.  

**Cons**:  
Requires significant processing power and resources.
Time-consuming to gather and label a dataset to train the AI model.
Potential concerns regarding privacy and data security.
Candidates may feel anxious or scrutinized during assessments.

**Option 2:** Post-Assessment Analysis  

**Description:** Use AI to analyze data from completed assessments, reviewing patterns and inconsistencies in results after
the fact. This option would involve collecting data from completed assessments, including:
  * Individual test scores
  * Answer choices for multiple-choice questions
  * Time taken per question
  * Previous assessment performance  

  The data would then need organised in a structured format for analysis, then cleaned and transformed before statistical analysis could be performed. 
  We could also use anomaly detection and classification models to identify unusual patterns. Results would need validated and verfied before 
  notification of results.  

  **Pros:**  
  Less intrusive for applicants during the assessment.
  Lower resource demands during the examination.
  Potential to improve overall test design based on insights gained.  

  **Cons:**  
  Cheating may go undetected during the assessment, leading to compromised results.
  Delayed feedback for certifiers, which may affect their decision-making.
  Limited ability to intervene in real time.
  

**Option 3:** Manual Approach  

**Description:**  
Use human experts to monitor candidates in real-time during assessments, ensuring compliance with 
testing standards and observing for any potential cheating behavior.  

**Pros:**    
Direct observation allows for immediate intervention if suspicious behavior is detected.
Enhances trust in the integrity of the certification process through human oversight.
Provides a personal touch that may enhance applicant comfort and confidence during the assessment.  

**Cons:**   
Resource-intensive, requiring a larger pool of trained experts and increased operational costs.
Potential for human error or bias in monitoring, which could affect the reliability of cheating detection.
Limited scalability, especially for large-scale assessments, as expert availability may become a bottleneck.
May create a stressful environment for candidates, impacting their performance.

### References
[AI Cheating Tips to Avoid and Detect](https://screenapp.io/blog/how-to-avoid-and-detect-ai-cheating-with-exam-assignments-and-essays#:~:text=Proctoring%20software%20can%20monitor%20a,background%2C%20like%20an%20AI%20program.)  
[Can AI Be Used to Cheat on Multiple-Choice Exams?](https://www.insidehighered.com/news/tech-innovation/artificial-intelligence/2024/08/30/professor-finds-way-see-if-students-used-ai)

### Date
02/12/2025

### Date to revisit
Post MVP - 02/12/2026
