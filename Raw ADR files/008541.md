# ADR-001: Microsoft Agent Framework Sequential Orchestration

**Date**: 2025-12-31  
**Status**: Accepted  
**Decision Makers**: Architecture Team  
**Technical Story**: CV Checker Agent Orchestration Pattern

## Context

CV Checker requires an orchestration pattern to coordinate multiple AI agents that analyze CVs against job descriptions. The application needs to:

- Parse and extract structured data from job descriptions
- Parse and extract structured data from Markdown CVs
- Perform comparative analysis between CV and job requirements
- Generate comprehensive match reports

Microsoft Agent Framework provides multiple orchestration patterns:
1. **Sequential Pattern**: Linear workflow with defined agent order
2. **Group Chat Pattern**: Multi-agent collaborative discussion
3. **Handoff Pattern**: Dynamic agent-to-agent transfer based on conditions

The choice of pattern affects system reliability, predictability, cost, and complexity.

## Decision

We will use **Microsoft Agent Framework's WorkflowBuilder with Sequential Pattern** for orchestrating the CV Checker agents.

The workflow consists of four agents executing in order:
1. **JobParser Agent**: Extracts requirements, skills, and experience from job descriptions
2. **CVParser Agent**: Extracts candidate information, skills, and experience from CVs
3. **Analyzer Agent**: Performs comparative analysis and scoring
4. **ReportGenerator Agent**: Creates formatted match reports

### Why Sequential Over Other Patterns

**Group Chat rejected** because:
- Unpredictable execution order increases latency
- Multi-agent discussions consume more tokens unnecessarily
- CV parsing doesn't benefit from collaborative reasoning
- Harder to debug and test deterministically

**Handoff rejected** because:
- CV analysis workflow is inherently linear
- No conditional branching needed in our use case
- Adds complexity without business value
- Makes error handling more complex

**Sequential chosen** because:
- Predictable execution flow matches business logic
- Each agent has clear input/output contract
- Lower token consumption (single-pass execution)
- Easier testing and debugging
- Better error isolation
- Matches ETL-style data processing pattern

## Implementation

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.workflows import WorkflowBuilder
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential

# Initialize Azure OpenAI client
client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-08-01-preview",
    azure_ad_token_provider=get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
)

# Define agents
job_parser_agent = AssistantAgent(
    name="JobParser",
    model_client=client,
    system_message="""Extract structured data from job descriptions:
    - Required skills (technical and soft)
    - Years of experience required
    - Education requirements
    - Key responsibilities
    Return JSON format."""
)

cv_parser_agent = AssistantAgent(
    name="CVParser",
    model_client=client,
    system_message="""Extract structured data from Markdown CVs:
    - Candidate skills
    - Years of experience per skill
    - Education history
    - Work experience
    Return JSON format."""
)

analyzer_agent = AssistantAgent(
    name="Analyzer",
    model_client=client,
    system_message="""Compare job requirements with candidate CV:
    - Calculate skill match percentage
    - Evaluate experience alignment
    - Identify gaps and strengths
    - Generate overall compatibility score
    Return structured analysis."""
)

report_generator_agent = AssistantAgent(
    name="ReportGenerator",
    model_client=client,
    system_message="""Generate comprehensive match report:
    - Executive summary
    - Detailed skill breakdown
    - Recommendations
    - Format as Markdown"""
)

# Build sequential workflow
workflow = WorkflowBuilder()

# Step 1: Parse job description
workflow.add_step(
    name="parse_job",
    agent=job_parser_agent,
    input_type=str,
    output_type=str
)

# Step 2: Parse CV
workflow.add_step(
    name="parse_cv",
    agent=cv_parser_agent,
    input_type=str,
    output_type=str,
    depends_on=["parse_job"]
)

# Step 3: Analyze compatibility
workflow.add_step(
    name="analyze",
    agent=analyzer_agent,
    input_type=str,
    output_type=str,
    depends_on=["parse_cv"]
)

# Step 4: Generate report
workflow.add_step(
    name="generate_report",
    agent=report_generator_agent,
    input_type=str,
    output_type=str,
    depends_on=["analyze"]
)

# Execute workflow
async def process_cv_check(job_description: str, cv_content: str) -> TaskResult:
    """Process CV against job description through sequential workflow."""
    combined_input = f"Job Description:\n{job_description}\n\nCV:\n{cv_content}"
    result = await workflow.run(task=combined_input)
    return result
```

## Consequences

### Positive

- **Predictable Performance**: Linear execution enables accurate latency estimation
- **Cost Efficiency**: Single-pass processing minimizes token consumption
- **Testability**: Each agent can be unit tested independently
- **Debugging**: Clear execution trace for troubleshooting
- **Monitoring**: Easy to track progress and identify bottlenecks
- **Error Handling**: Failed steps are easy to identify and retry
- **Scalability**: Parallel processing of multiple CV checks is straightforward

### Negative

- **Inflexibility**: Cannot dynamically adjust workflow based on runtime conditions
- **No Collaboration**: Agents cannot discuss or refine results together
- **Fixed Order**: Cannot skip steps even if earlier results are sufficient

### Mitigation Strategies

- Implement retry logic for individual failed steps
- Add validation between steps to catch errors early
- Use structured outputs (JSON) for clear contracts between agents
- Implement comprehensive logging at each step
- Create monitoring dashboards for workflow metrics

## Related Decisions

- ADR-002: Azure OpenAI Integration with Entra ID
- ADR-003: Hybrid Scoring Algorithm

## References

- [Microsoft Agent Framework Documentation](https://microsoft.github.io/autogen/)
- [WorkflowBuilder API Reference](https://microsoft.github.io/autogen/docs/reference/agentchat/agents/)
- [Azure OpenAI Service Best Practices](https://learn.microsoft.com/azure/ai-services/openai/concepts/best-practices)
