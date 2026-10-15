# ADR-004: Confidence-based grading process
## Context

Certifiable is incorporating AI to assist in grading while maintaining accuracy and fairness. A key challenge is determining when AI can autonomously grade an exam response versus when human intervention is required. This ADR defines how confidence levels guide the grading process and provides a cost analysis of AI-assisted grading.

Please see the [ADR on correctness scoring](/adr/002-scoring-thresholds.md) for more detail on this facet of scoring that corresponds to the confidence scoring described here.

## Decision

The grading system assigns two key scores to each answer:

- **Correctness Score (1-10)**: Measures how well an answer aligns with reference answers.
- **Confidence Score (1-10)**: Reflects the AI’s certainty in its correctness assessment.

These configurable thresholds are used to determine when AI grading is sufficient:

| Confidence Score | Decision              |
|------------------|-----------------------|
| 7-10             | Proceed to scoring    |
| 1-6              | Requires human review |

This approach ensures AI handles straightforward cases while human graders review ambiguous or complex answers.

The confidence score will be calculated differently for each test.

### Test 1
Since Certifiable is using a relational database with caching to store curated correct and incorrect answers, AI correctness scores will be tied to **semantic similarity to known high-quality responses**.

A secondary request (likely bundled with the first) will enable us to ascertain the LLM's confidence in its correctness assessment clearly.

Below is a simplified example of how the confidence-scoring prompt will be structured:

```plaintext
You're grading an exam answer based on similarity to known correct answers.

### Candidate Answer:
"{{candidate_answer}}"

### Reference Answers:
1. "{{known_good_answer_1}}"
2. "{{known_good_answer_2}}"
(...)
N. "{{known_good_answer_N}}"

You previously assigned a correctness score of "{{correctness_score}}" to this answer.

Now, assign a **confidence score** (1-10) reflecting your certainty in the correctness assessment above:

- **8-10 (high confidence)** → You are very certain. The answer closely matches reference answers with minimal ambiguity.
- **5-7** → You're somewhat confident, but there are minor ambiguities that a human grader might interpret differently.
- **1-4** → You're unsure or found multiple points of ambiguity, and human review is recommended.

Confidence Score (1-10):
```

### Test 2 
Since Certifiable is using a multi-perspective grading approach, the confidence score will be determined based on the **lowest score across the different agents**. This means that a single low confidence score will trigger human grading, so as to be as cautious as possible about reliance on AI agents when they themselves are uncertain of their conclusions.

## Options considered

1. **Fully Automated AI Grading**
   - AI assigns scores to all answers without human review.
   - Relies entirely on AI decision-making, without considering AI confidence levels.
   
2. **Hybrid Model with Confidence-Based Thresholds (Selected Approach)**
   - AI assigns scores but defers uncertain cases to human graders.
   - Balances efficiency with quality control.
   
3. **Human-Only Grading**
   - AI is not used, all grading is manual.
   - Ensures full human oversight but is resource-intensive.
   - Automatically discarded because it's unsustainable as a business model. 

## Pros

- **Efficiency Gains**: Reduces human workload by filtering out clear pass/fail cases.
- **Quality Control**: Confidence thresholds prevent unreliable AI decisions.
- **Scalability**: Supports increasing exam volumes without overwhelming human graders.
- **Cost Reduction**: 
  - Reduces grading expenses by automating a portion of the process.

## Cons

- **Potential AI Errors**: Some borderline cases may still be misclassified.
- **Ongoing Monitoring**: Requires regular tuning of confidence thresholds to maintain grading accuracy.
- **Infrastructure Costs**: AI processing costs, while lower than full human grading, still add to the operational cost.

## Conclusion

Confidence-based grading ensures a balance between automation and human oversight, maintaining grading quality while achieving substantial cost savings. By filtering out high-confidence pass and fail cases from the human grading queue, this approach reduces human grading workload while ensuring that nuanced or uncertain answers receive appropriate human review. This method supports Certifiable’s scalability while preserving certification credibility.
