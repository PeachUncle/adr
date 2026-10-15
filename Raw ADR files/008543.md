# ADR-003: Hybrid Scoring Algorithm

**Date**: 2025-12-31  
**Status**: Accepted  
**Decision Makers**: Architecture Team, Product Team  
**Technical Story**: CV-Job Match Scoring System

## Context

CV Checker needs to generate a match score between candidate CVs and job descriptions. The score must be:

- **Accurate**: Reflect true compatibility between candidate and role
- **Explainable**: Users can understand why a score was assigned
- **Consistent**: Similar CVs get similar scores for the same job
- **Nuanced**: Capture both literal matches and semantic understanding
- **Actionable**: Enable ranking and filtering of candidates

Potential approaches:

1. **Pure Deterministic**: Rule-based keyword matching and experience calculation
2. **Pure LLM**: Ask GPT to score holistically without structure
3. **Hybrid**: Combine deterministic metrics with LLM semantic analysis

## Decision

We will use a **Hybrid Scoring Algorithm** that combines deterministic metrics with LLM-powered semantic validation.

### Scoring Components

**1. Deterministic Component (60% weight)**
- **Skill Match Percentage (40%)**: Hard skills explicitly found in CV
- **Experience Alignment Percentage (20%)**: Years of experience match

**2. LLM Validation Component (40% weight)**
- **Semantic Analysis (25%)**: Contextual skill understanding and transferable skills
- **Cultural Fit & Soft Skills (15%)**: Communication style, leadership, collaboration

### Final Score Formula

```
FinalScore = (DeterministicScore × 0.60) + (LLMScore × 0.40)

Where:
  DeterministicScore = (SkillMatch × 0.667) + (ExperienceAlignment × 0.333)
  LLMScore = (SemanticAnalysis × 0.625) + (SoftSkillsMatch × 0.375)

Output: 0-100 scale
```

### Why Hybrid Over Pure Approaches

**Pure Deterministic rejected** because:
- Cannot understand synonyms (React.js vs React vs ReactJS)
- Misses transferable skills (Java → C# backend experience)
- Ignores context (5 years Python in ML vs 5 years Python in web dev)
- Cannot evaluate soft skills or cultural fit
- Brittle to CV formatting variations

**Pure LLM rejected** because:
- Inconsistent scoring across identical inputs
- Black box decisions hard to explain
- No guarantee of objectivity
- Higher cost and latency
- Cannot validate correctness
- Vulnerable to prompt injection or gaming

**Hybrid chosen** because:
- **Consistency**: Deterministic base ensures reproducibility
- **Nuance**: LLM adds semantic understanding
- **Explainability**: Clear breakdown of score components
- **Validation**: Deterministic acts as sanity check on LLM
- **Cost-effective**: Reduces reliance on expensive LLM calls
- **Debuggability**: Can isolate issues to specific components
- **Trust**: Users trust combination of objective metrics + AI insight

## Implementation

### Deterministic Scorer

```python
from typing import Dict, List, Set
from dataclasses import dataclass
import re

@dataclass
class DeterministicScore:
    skill_match_percent: float
    experience_alignment_percent: float
    total_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_gaps: Dict[str, str]

class DeterministicScorer:
    """Calculate deterministic compatibility metrics."""
    
    def calculate_skill_match(
        self,
        required_skills: Set[str],
        candidate_skills: Set[str]
    ) -> tuple[float, List[str], List[str]]:
        """
        Calculate skill match percentage.
        
        Returns:
            (match_percentage, matched_skills, missing_skills)
        """
        # Normalize skills to lowercase for comparison
        required_normalized = {s.lower().strip() for s in required_skills}
        candidate_normalized = {s.lower().strip() for s in candidate_skills}
        
        # Find exact matches
        matched = required_normalized.intersection(candidate_normalized)
        missing = required_normalized - candidate_normalized
        
        if not required_normalized:
            return 100.0, [], []
        
        match_percent = (len(matched) / len(required_normalized)) * 100
        
        return (
            match_percent,
            list(matched),
            list(missing)
        )
    
    def calculate_experience_alignment(
        self,
        required_years: int,
        candidate_years: int,
        role_type: str = "general"
    ) -> tuple[float, Dict[str, str]]:
        """
        Calculate experience alignment percentage.
        
        Args:
            required_years: Minimum years required
            candidate_years: Candidate's years of experience
            role_type: Type of role (entry, mid, senior)
        
        Returns:
            (alignment_percentage, gaps_explanation)
        """
        gaps = {}
        
        if candidate_years >= required_years:
            # Over-qualified: 100% if within 2x requirement, else penalize
            if candidate_years <= required_years * 2:
                alignment = 100.0
            else:
                # Slight penalty for extreme over-qualification
                alignment = max(90.0, 100 - (candidate_years - required_years * 2) * 2)
                gaps["over_qualified"] = f"Candidate has {candidate_years - required_years} years beyond requirement"
        else:
            # Under-qualified: linear penalty
            shortage = required_years - candidate_years
            alignment = max(0.0, 100 - (shortage / required_years * 100))
            gaps["under_qualified"] = f"Missing {shortage} years of experience"
        
        return alignment, gaps
    
    def score(
        self,
        job_requirements: Dict,
        candidate_profile: Dict
    ) -> DeterministicScore:
        """
        Generate deterministic compatibility score.
        
        Args:
            job_requirements: {
                'required_skills': ['Python', 'FastAPI', 'Azure'],
                'required_years': 5,
                'role_type': 'senior'
            }
            candidate_profile: {
                'skills': ['Python', 'FastAPI', 'AWS', 'Docker'],
                'years_experience': 6
            }
        
        Returns:
            DeterministicScore with breakdown
        """
        # Calculate skill match
        skill_match, matched, missing = self.calculate_skill_match(
            set(job_requirements.get('required_skills', [])),
            set(candidate_profile.get('skills', []))
        )
        
        # Calculate experience alignment
        exp_align, exp_gaps = self.calculate_experience_alignment(
            job_requirements.get('required_years', 0),
            candidate_profile.get('years_experience', 0),
            job_requirements.get('role_type', 'general')
        )
        
        # Weighted combination (skill match more important)
        total = (skill_match * 0.667) + (exp_align * 0.333)
        
        return DeterministicScore(
            skill_match_percent=round(skill_match, 2),
            experience_alignment_percent=round(exp_align, 2),
            total_score=round(total, 2),
            matched_skills=matched,
            missing_skills=missing,
            experience_gaps=exp_gaps
        )
```

### LLM Semantic Validator

```python
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from typing import Dict
import json

@dataclass
class LLMScore:
    semantic_match_percent: float
    soft_skills_match_percent: float
    total_score: float
    reasoning: str
    transferable_skills: List[str]
    cultural_fit_notes: str

class LLMSemanticValidator:
    """LLM-powered semantic analysis and validation."""
    
    def __init__(self, openai_client: AzureOpenAIChatCompletionClient):
        self.client = openai_client
    
    async def validate_and_score(
        self,
        job_description: str,
        cv_content: str,
        deterministic_score: DeterministicScore
    ) -> LLMScore:
        """
        Perform semantic analysis and soft skills evaluation.
        
        Args:
            job_description: Full job posting text
            cv_content: Full CV markdown content
            deterministic_score: Pre-calculated deterministic metrics
        
        Returns:
            LLMScore with semantic and soft skills assessment
        """
        
        prompt = f"""You are an expert technical recruiter. Analyze this candidate's CV against the job requirements.

**DETERMINISTIC BASELINE**:
- Skill Match: {deterministic_score.skill_match_percent}%
- Matched Skills: {', '.join(deterministic_score.matched_skills)}
- Missing Skills: {', '.join(deterministic_score.missing_skills)}
- Experience Alignment: {deterministic_score.experience_alignment_percent}%

**JOB DESCRIPTION**:
{job_description}

**CANDIDATE CV**:
{cv_content}

Evaluate these aspects:

1. **Semantic Skill Match (0-100)**: 
   - Identify transferable skills not caught by keyword matching
   - Consider synonyms and related technologies
   - Evaluate depth of experience based on project descriptions
   
2. **Soft Skills & Cultural Fit (0-100)**:
   - Leadership and collaboration indicators
   - Communication style from CV writing
   - Problem-solving approach from project descriptions
   - Alignment with company values in job posting

Return JSON only:
{{
  "semantic_match_percent": <number>,
  "soft_skills_match_percent": <number>,
  "reasoning": "<brief explanation>",
  "transferable_skills": ["skill1", "skill2"],
  "cultural_fit_notes": "<observations>"
}}
"""

        response = await self.client.create(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for consistency
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Calculate weighted LLM score
        total = (
            result["semantic_match_percent"] * 0.625 +
            result["soft_skills_match_percent"] * 0.375
        )
        
        return LLMScore(
            semantic_match_percent=round(result["semantic_match_percent"], 2),
            soft_skills_match_percent=round(result["soft_skills_match_percent"], 2),
            total_score=round(total, 2),
            reasoning=result["reasoning"],
            transferable_skills=result["transferable_skills"],
            cultural_fit_notes=result["cultural_fit_notes"]
        )
```

### Hybrid Scorer Integration

```python
@dataclass
class HybridScore:
    final_score: float
    deterministic_component: DeterministicScore
    llm_component: LLMScore
    grade: str  # A+, A, B+, B, C+, C, D, F
    
    def to_dict(self) -> Dict:
        """Convert to detailed JSON report."""
        return {
            "final_score": self.final_score,
            "grade": self.grade,
            "breakdown": {
                "deterministic": {
                    "weight": "60%",
                    "score": self.deterministic_component.total_score,
                    "skill_match": self.deterministic_component.skill_match_percent,
                    "experience_alignment": self.deterministic_component.experience_alignment_percent,
                    "matched_skills": self.deterministic_component.matched_skills,
                    "missing_skills": self.deterministic_component.missing_skills
                },
                "llm_semantic": {
                    "weight": "40%",
                    "score": self.llm_component.total_score,
                    "semantic_match": self.llm_component.semantic_match_percent,
                    "soft_skills": self.llm_component.soft_skills_match_percent,
                    "transferable_skills": self.llm_component.transferable_skills,
                    "reasoning": self.llm_component.reasoning
                }
            }
        }

class HybridScorer:
    """Hybrid scoring combining deterministic and LLM approaches."""
    
    def __init__(self, openai_client: AzureOpenAIChatCompletionClient):
        self.deterministic_scorer = DeterministicScorer()
        self.llm_validator = LLMSemanticValidator(openai_client)
    
    async def score(
        self,
        job_description: str,
        cv_content: str,
        job_requirements: Dict,
        candidate_profile: Dict
    ) -> HybridScore:
        """
        Generate hybrid compatibility score.
        
        Returns:
            HybridScore with full breakdown
        """
        # Step 1: Deterministic scoring
        det_score = self.deterministic_scorer.score(
            job_requirements,
            candidate_profile
        )
        
        # Step 2: LLM semantic validation
        llm_score = await self.llm_validator.validate_and_score(
            job_description,
            cv_content,
            det_score
        )
        
        # Step 3: Weighted combination
        final = (det_score.total_score * 0.60) + (llm_score.total_score * 0.40)
        
        # Step 4: Assign letter grade
        grade = self._calculate_grade(final)
        
        return HybridScore(
            final_score=round(final, 2),
            deterministic_component=det_score,
            llm_component=llm_score,
            grade=grade
        )
    
    def _calculate_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 95: return "A+"
        elif score >= 90: return "A"
        elif score >= 85: return "B+"
        elif score >= 80: return "B"
        elif score >= 75: return "C+"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"
```

### Usage Example

```python
# Initialize scorer
hybrid_scorer = HybridScorer(openai_client)

# Score candidate
result = await hybrid_scorer.score(
    job_description=job_posting_text,
    cv_content=cv_markdown,
    job_requirements={
        'required_skills': ['Python', 'FastAPI', 'Azure', 'Docker'],
        'required_years': 5,
        'role_type': 'senior'
    },
    candidate_profile={
        'skills': ['Python', 'FastAPI', 'AWS', 'Kubernetes'],
        'years_experience': 6
    }
)

print(f"Final Score: {result.final_score} ({result.grade})")
print(json.dumps(result.to_dict(), indent=2))
```

## Consequences

### Positive

- **Balanced Accuracy**: Combines objectivity with semantic understanding
- **Explainability**: Users see both hard metrics and AI reasoning
- **Consistency**: Deterministic base prevents wild score variations
- **Cost Efficient**: Reduces reliance on expensive LLM-only scoring
- **Debuggable**: Can test and validate each component independently
- **Tunable**: Weights can be adjusted based on user feedback
- **Fair**: Reduces bias through structured evaluation
- **Actionable**: Detailed breakdown enables candidate improvement

### Negative

- **Complexity**: Two scoring systems to maintain and test
- **Latency**: LLM call adds delay (mitigated by async processing)
- **Potential Disagreement**: Deterministic and LLM scores may conflict
- **Weight Calibration**: Requires tuning based on real-world feedback
- **LLM Costs**: Still incurs API costs for semantic analysis

### Mitigation Strategies

- **Caching**: Cache LLM results for identical CV-job pairs
- **Batch Processing**: Process multiple CVs asynchronously
- **Monitoring**: Track score distribution and flag anomalies
- **A/B Testing**: Experiment with different weight configurations
- **Feedback Loop**: Collect user ratings to refine algorithm
- **Timeout Handling**: Fall back to deterministic-only if LLM times out

### Calibration and Tuning

Initial weights (60/40) can be adjusted based on:
- User satisfaction surveys
- Comparison with human recruiter assessments
- False positive/negative rates
- Candidate diversity metrics

## Related Decisions

- ADR-001: Microsoft Agent Framework Sequential Orchestration
- ADR-002: Azure OpenAI Integration with Entra ID

## References

- [Hybrid AI Systems](https://arxiv.org/abs/2108.07732)
- [Azure OpenAI Best Practices](https://learn.microsoft.com/azure/ai-services/openai/concepts/best-practices)
- [Explainable AI in Recruitment](https://www.brookings.edu/research/auditing-employment-algorithms-for-discrimination/)
