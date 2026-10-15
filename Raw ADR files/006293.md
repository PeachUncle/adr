# ADR 006: RAG vs Raw LLM

## Context

Certifiable's exam grading is currently performed by expert graders - humans with expert knowledge of architecture, who are able to weigh up the pros and cons of various approaches to architectural thinking for an assigned problem.

As people who also work in this space, we can see that any number of architectures might meet a certain set of business requirements, which will each have their own merits and downsides. Architecture, while not an entirely subjective discipline, teaches us that, as was famously ascribed to the Perl programming language, "there's more than one way to do it."

How, then, can we espouse creative solution design while also ensuring that a proposed design not only is sound from an architectural perspective, but also sufficiently meets the needs stated within the business problem?

Our initial solution to this kata relied extensively on RAG–a methodology that builds a knowledge base (presumably filled with great examples of solutions to a given problem) and then assesses similarity or difference to this known set. Upon further reflection, we find this approach limiting. This ADR covers off how our solution, and how we've arrived at it. 

## Decision

We **decided not to use RAG for grading of either exam** and opted for the approaches covered in [ADR 1](/adr/001-test-1-database.md) and [ADR 5](/adr/005-test-2-scoring.md). Why? 

**Exam 1 (short answer)** is comprised of short answer text responses to questions that, presumably, have a narrow range of acceptable answers. We believe that a sample of correct/incorrect responses of sufficient size would provide an LLM enough basis to determine correctness/confidence.

**Exam 2** is comprised of long form architecture documentation, including diagrams. Our solution has emphasised a multi-agent methodology, wherein agents wearing different "hats" or roles are asked to evaluate the response. Crucially, one of the "hats" is that of Technical Product Owner, who is briefed with the problem at hand to ensure we're not just passing *any good architecture*, but instead *any good architecture that meets the needs of the stated problem*. The final score is an aggregate of the agents' scores, which will reflect the different points of view by which an architecture can be evaluated for suitability–like having an Architecture Review Board, Information Security/pen testing, infrastructure experts, product owners, and developers all around the table chipping in.

Real-world architectural problems don't have one right answer - and so we've modelled the real world process by forgoing the creation of a knowledge base and, instead, evaluating each submission on its individual merits.

## Alternatives considered

Our initial solution design focussed around RAG - partially because it's an approach that lines up well conceptually, it was floated as a technology of interest in the first kata session and, being honest, partially because it's an application of AI which we're very familiar with.

Our path to removing RAG from our solution design started when one of our team members asked the group: what if most of the approved solutions happened to use AWS, as opposed to GCP or Azure? Won't this stack our knowledge base with AWS-centric designs and potentially disenfranchise submissions that rely on a different cloud offering, either because of personal preference/familiarity or some technical detail?

Choice of cloud providers is a fairly trivial (sometimes cosmetic, even) difference in many architectural designs but, taken to its logical extension, deploying AI-assisted grading that relied on patterns found in accepted solutions presents a risk of homogenising passing answers to fit into the mold of previously accepted answers. Just because 9/10 answers share similar hallmarks, it doesn't logically follow that the 10th, an outlier, doesn't have architectural merit.

So we found ourselves politely thanking RAG for its service in our draft kata submission, and have taken a different path–one that means we're placing more trust in reasoning models and the intelligence of our AI agents.

## Consequences

This approach is intuitively more frightening - we're walking an AI tightrope without the safety net of "known good responses." But we believe the risk can be mitigated. The most important requirements that emerge as consequences of this decision are:
* An extended period of testing/learning with the models and before rolling out changes to the exam questions - prompts and agent personas will need to be tweaked to ensure that grading matches up to expectations for the various personas
* Heightened importance of grading thresholds - along with the test/learning, grading will need to be calibrated properly to ensure that a passing grade sits at a level that expert graders are comfortable with.
* Heightened importance of confidence scoring - similarly, without concrete examples to compare against, the reasoning models will need to demonstrate high confidence in their assessment. Thresholds for confidence scoring may also require review/revision as the system is in use.
* Further underlining the importance of the expert grader failsafe - for use when AI graders aren't able to sufficiently assess submissions. 

## Returns

By avoiding a RAG implementation, we avoid the need for an extensive knowledge base, as well as the pipelines needed to sustain it. This effort/cost can instead be repurposed into creating adequately nuanced for the agent personas, which should be a one-time (or at least infrequent) cost.

We believe the overall impact of this decision will be

- **Reduced bias** → Demonstrably fewer answers rejected do to lack of similarity to previously accepted answers.
- **Increased diversity of solutions** → By extension, the set of accepted answers will include answers that possibly even the expert graders would not have considered.
- **Reduced operational cost** → A more incisive application of AI, rather than building a knowledge base to support RAG.

## Tradeoffs

- **More dependence on "intelligent" AI** → Unlike a RAG-based approach, which builds on existing knowledge and extends it to evaluate new answers, we are relying on our AI graders to extrapolate based on their "working knowledge" in their respective areas of expertise (imbued in their personas). We are placing an educated bet on the AI graders' ability to reason - but this must be accompanied by appropriate oversight and "checking the work" of the AI graders, either by spot checks of passed/failed exam questions or highlighting questions that result in disproportionately high pass/fail numbers for expert review
- **More involved setup for new exam questions** → The areas of focus highlighted in the "Consequences" section above imply a more thoughtful process around standing up a new exam question. This may include setting confidence/correctness scoring thresholds, assigning relevant agent personas, and weighting agent personas. This will be a slower, more involved process than simply uploading a set of previously accepted answers
- **Slower grading execution time** - reasoning models will, by definition, require longer to complete their execution. Even assuming very high run times, we believe the time required will still be considerably less than if the questions were graded by expert graders.

## Conclusion

By **moving from RAG to vanilla LLM** and using AI agents for scoring, we **reduce bias, increase answer diversity, improve answer quality, and increase overall confidence in exam grading and awarded certifications**. 
