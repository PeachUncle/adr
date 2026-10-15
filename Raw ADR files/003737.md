# ADR-012: Assessment & Progress Tracking Architecture

## Status
Accepted

## Context

The SayZhong Mandarin learning application requires a sophisticated assessment and progress tracking system that can accurately measure learner proficiency across multiple domains of Mandarin learning. This system must support real-time assessment during lessons, comprehensive skill evaluations, and long-term progress tracking that feeds into the adaptive learning effectiveness framework (ADR-009).

### Mandarin-Specific Assessment Challenges

1. **Multi-Modal Assessment**: Mandarin learning requires assessment across listening, speaking, reading, writing, and phonetic understanding
2. **Tonal Accuracy**: Pronunciation assessment must evaluate tonal precision, a critical component of Mandarin
3. **Vocabulary Recognition**: Assessment of vocabulary understanding and usage in context
4. **Contextual Understanding**: Assessment of appropriate language use in communication contexts
5. **Progressive Complexity**: Assessment that adapts to HSK levels and learning progression
6. **Real-time Feedback**: Immediate assessment during interactive lessons for adaptive content delivery

### Integration Requirements

- **Learning Effectiveness Framework** (ADR-009): Provide assessment data for effectiveness analysis
- **Content Management System** (ADR-010): Assess against curriculum standards and content difficulty
- **User Interface Framework** (ADR-011): Deliver assessment feedback through adaptive UI components
- **AI Framework** (ADR-001): Leverage Semantic Kernel for intelligent assessment and feedback generation
- **Data Storage** (ADR-003): Store assessment data in Azure Data Lake for analytics
- **Performance Monitoring** (ADR-008): Track assessment system performance and response times

## Decision

We will implement a comprehensive, multi-layered assessment and progress tracking architecture that supports real-time formative assessment, periodic summative evaluation, and long-term progress analytics specifically designed for Mandarin language learning.

### Core Assessment Architecture

```python
# Assessment Models and Framework
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

class AssessmentType(Enum):
    FORMATIVE_REAL_TIME = "formative_real_time"  # During lesson interactions
    FORMATIVE_CHECKPOINT = "formative_checkpoint"  # End of lesson/section
    SUMMATIVE_SKILL = "summative_skill"  # Skill-specific comprehensive test
    SUMMATIVE_LEVEL = "summative_level"  # HSK level assessment
    DIAGNOSTIC = "diagnostic"  # Initial placement and skill gap identification
    ADAPTIVE = "adaptive"  # AI-driven adaptive assessment

class MandarinSkillDomain(Enum):
    LISTENING = "listening"
    SPEAKING = "speaking"
    READING = "reading"
    WRITING = "writing"
    PRONUNCIATION = "pronunciation"
    TONAL_ACCURACY = "tonal_accuracy"
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    CONVERSATION = "conversation"
    PHONETIC_UNDERSTANDING = "phonetic_understanding"

class ProficiencyLevel(Enum):
    BEGINNER = "beginner"
    HSK1 = "hsk1"
    HSK2 = "hsk2"
    HSK3 = "hsk3"
    HSK4 = "hsk4"
    HSK5 = "hsk5"
    HSK6 = "hsk6"
    ADVANCED = "advanced"
    NATIVE = "native"

@dataclass
class AssessmentCriteria:
    domain: MandarinSkillDomain
    expected_level: ProficiencyLevel
    success_threshold: float  # 0.0 - 1.0
    mastery_threshold: float  # 0.0 - 1.0
    weight: float  # Relative importance in overall assessment
    adaptive_parameters: Dict[str, any]

@dataclass
class AssessmentItem:
    item_id: str
    content_id: str  # Links to content from ADR-010
    item_type: str  # multiple_choice, fill_blank, pronunciation, conversation, etc.
    domain: MandarinSkillDomain
    difficulty_level: ProficiencyLevel
    expected_time_seconds: int
    criteria: List[AssessmentCriteria]
    item_content: Dict[str, any]  # Question, options, expected answers, etc.
    phonetic_context: Optional[str]
    metadata: Dict[str, any]

@dataclass
class AssessmentResponse:
    response_id: str
    assessment_item_id: str
    user_id: str
    session_id: str
    response_data: Dict[str, any]  # User's actual response
    timestamp: datetime
    response_time_seconds: float
    interaction_metadata: Dict[str, any]  # UI interactions, hesitations, etc.

@dataclass
class AssessmentResult:
    result_id: str
    assessment_item_id: str
    user_response: AssessmentResponse
    scores: Dict[MandarinSkillDomain, float]  # Domain-specific scores
    overall_score: float
    proficiency_indicators: Dict[ProficiencyLevel, float]  # Probability of proficiency levels
    detailed_feedback: Dict[str, any]
    areas_for_improvement: List[str]
    strengths: List[str]
    next_recommendations: List[str]
    confidence_level: float  # AI confidence in assessment
    processing_metadata: Dict[str, any]

@dataclass
class SkillProgressMetrics:
    domain: MandarinSkillDomain
    current_level: ProficiencyLevel
    level_progress: float  # Progress within current level (0.0 - 1.0)
    mastery_score: float  # Overall mastery of domain
    recent_trend: str  # improving, stable, declining
    skill_velocity: float  # Rate of improvement
    time_to_next_level: Optional[int]  # Estimated days
    historical_scores: List[Tuple[datetime, float]]
    milestone_achievements: List[str]

@dataclass
class ComprehensiveProgressReport:
    user_id: str
    report_date: datetime
    overall_proficiency: ProficiencyLevel
    skill_breakdown: Dict[MandarinSkillDomain, SkillProgressMetrics]
    learning_path_progress: Dict[str, float]  # Progress on different learning paths
    communication_competency_score: float
    study_statistics: Dict[str, any]  # Time spent, lessons completed, etc.
    achievement_unlocks: List[str]
    personalized_recommendations: List[str]
    comparative_analytics: Dict[str, any]  # Comparison to similar learners
```

### Assessment Processing Components

```python
# Abstract Assessment Processor Interface
class AssessmentProcessor(ABC):
    @abstractmethod
    async def process_assessment(
        self, 
        item: AssessmentItem, 
        response: AssessmentResponse
    ) -> AssessmentResult:
        pass
    
    @abstractmethod
    async def generate_feedback(
        self, 
        result: AssessmentResult
    ) -> Dict[str, any]:
        pass

# Domain-Specific Assessment Processors
class PronunciationAssessmentProcessor(AssessmentProcessor):
    """Processes pronunciation assessments with tonal analysis"""
    
    async def process_assessment(
        self, 
        item: AssessmentItem, 
        response: AssessmentResponse
    ) -> AssessmentResult:
        # Analyze audio response for:
        # - Tonal accuracy (4 tones + neutral)
        # - Phoneme accuracy
        # - Rhythm and intonation
        # - Native-like pronunciation
        pass
    
    async def analyze_tonal_accuracy(
        self, 
        audio_data: bytes, 
        expected_tones: List[int]
    ) -> Dict[str, float]:
        # AI-powered tonal analysis
        pass

class VocabularyAssessmentProcessor(AssessmentProcessor):
    """Processes vocabulary understanding and usage assessments"""
    
    async def process_assessment(
        self, 
        item: AssessmentItem, 
        response: AssessmentResponse
    ) -> AssessmentResult:
        # Analyze vocabulary responses for:
        # - Vocabulary understanding accuracy
        # - Contextual usage appropriateness
        # - Phonetic approximation understanding
        # - Tonal pattern recognition
        pass
    
    async def analyze_phonetic_understanding(
        self, 
        phonetic_data: List[Dict], 
        vocabulary_item: str
    ) -> Dict[str, float]:
        # Phonetic understanding and pronunciation analysis
        pass

class ConversationAssessmentProcessor(AssessmentProcessor):
    """Processes conversational and communication context assessments"""
    
    async def process_assessment(
        self, 
        item: AssessmentItem, 
        response: AssessmentResponse
    ) -> AssessmentResult:
        # Analyze conversation for:
        # - Appropriate language use
        # - Communication effectiveness
        # - Fluency and coherence
        # - Vocabulary range and accuracy
        pass

# Adaptive Assessment Engine
class AdaptiveAssessmentEngine:
    """AI-powered adaptive assessment using Semantic Kernel"""
    
    def __init__(self, semantic_kernel_service):
        self.sk = semantic_kernel_service
        self.assessment_processors = {
            MandarinSkillDomain.PRONUNCIATION: PronunciationAssessmentProcessor(),
            MandarinSkillDomain.VOCABULARY: VocabularyAssessmentProcessor(),
            MandarinSkillDomain.CONVERSATION: ConversationAssessmentProcessor(),
            # Additional processors...
        }
    
    async def select_next_assessment_item(
        self, 
        user_progress: ComprehensiveProgressReport,
        current_session_context: Dict[str, any]
    ) -> AssessmentItem:
        """AI-driven selection of next assessment item based on learner state"""
        pass
    
    async def adjust_difficulty(
        self, 
        recent_results: List[AssessmentResult]
    ) -> Dict[str, any]:
        """Dynamically adjust assessment difficulty based on performance"""
        pass

# Progress Tracking Engine
class ProgressTrackingEngine:
    """Comprehensive progress tracking and analytics"""
    
    async def update_skill_progress(
        self, 
        user_id: str, 
        assessment_results: List[AssessmentResult]
    ) -> Dict[MandarinSkillDomain, SkillProgressMetrics]:
        """Update skill-specific progress metrics"""
        pass
    
    async def generate_progress_report(
        self, 
        user_id: str, 
        time_period: Tuple[datetime, datetime]
    ) -> ComprehensiveProgressReport:
        """Generate comprehensive progress report"""
        pass
    
    async def predict_learning_trajectory(
        self, 
        user_progress: ComprehensiveProgressReport
    ) -> Dict[str, any]:
        """AI-powered prediction of learning trajectory and recommendations"""
        pass
    
    async def identify_learning_gaps(
        self, 
        user_progress: ComprehensiveProgressReport
    ) -> List[Dict[str, any]]:
        """Identify specific areas needing attention"""
        pass

# Real-time Assessment Coordinator
class RealTimeAssessmentCoordinator:
    """Coordinates real-time assessment during learning sessions"""
    
    async def process_interaction(
        self, 
        interaction_data: Dict[str, any]
    ) -> Optional[AssessmentResult]:
        """Process real-time learning interactions for immediate assessment"""
        pass
    
    async def trigger_checkpoint_assessment(
        self, 
        session_context: Dict[str, any]
    ) -> List[AssessmentItem]:
        """Trigger checkpoint assessments based on session progress"""
        pass
    
    async def provide_immediate_feedback(
        self, 
        assessment_result: AssessmentResult
    ) -> Dict[str, any]:
        """Provide immediate, actionable feedback to learner"""
        pass
```

### Assessment Data Storage Schema

```yaml
# Azure Data Lake Assessment Data Structure
assessment_data/
├── raw_responses/
│   ├── year=2024/
│   │   ├── month=01/
│   │   │   ├── day=01/
│   │   │   │   ├── audio_responses/
│   │   │   │   ├── text_responses/
│   │   │   │   ├── interaction_logs/
│   │   │   │   └── session_metadata/
├── processed_results/
│   ├── skill_assessments/
│   ├── comprehensive_reports/
│   ├── progress_snapshots/
│   └── analytics_aggregates/
├── assessment_items/
│   ├── by_domain/
│   ├── by_level/
│   ├── adaptive_pools/
│   └── phonetic_context/
├── progress_tracking/
│   ├── individual_progress/
│   ├── cohort_analytics/
│   ├── skill_trajectories/
│   └── predictive_models/
└── feedback_optimization/
    ├── feedback_effectiveness/
    ├── assessment_validity/
    └── communication_appropriateness/
```

### Integration with Learning Effectiveness Framework

```python
# Assessment Data Provider for Learning Effectiveness
class AssessmentEffectivenessProvider:
    """Provides assessment data to learning effectiveness framework"""
    
    async def get_effectiveness_indicators(
        self, 
        user_id: str, 
        time_period: Tuple[datetime, datetime]
    ) -> Dict[str, any]:
        """Provide assessment-based effectiveness indicators"""
        return {
            'skill_improvement_rates': await self._calculate_improvement_rates(user_id, time_period),
            'mastery_progression': await self._calculate_mastery_progression(user_id, time_period),
            'assessment_engagement': await self._calculate_engagement_metrics(user_id, time_period),
            'difficulty_adaptation_success': await self._calculate_adaptation_success(user_id, time_period),
            'cultural_competency_growth': await self._calculate_cultural_growth(user_id, time_period)
        }
    
    async def identify_content_effectiveness(
        self, 
        content_ids: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Analyze content effectiveness based on assessment outcomes"""
        pass
    
    async def provide_adaptive_recommendations(
        self, 
        assessment_patterns: Dict[str, any]
    ) -> List[Dict[str, any]]:
        """Provide recommendations for adaptive lesson planning"""
        pass
```

## Rationale

### Multi-Modal Assessment Approach
- **Comprehensive Evaluation**: Addresses all aspects of Mandarin learning
- **Real-time Adaptation**: Enables immediate adjustment of learning content
- **Phonetic Integration**: Ensures pronunciation understanding and phonetic context awareness

### AI-Powered Assessment Processing
- **Intelligent Analysis**: Leverages Semantic Kernel for sophisticated assessment analysis
- **Adaptive Difficulty**: Dynamically adjusts assessment difficulty based on learner performance
- **Personalized Feedback**: Provides tailored feedback and recommendations

### Domain-Specific Processors
- **Specialized Analysis**: Each domain (pronunciation, vocabulary, conversation) has specialized processing
- **Accuracy**: Domain-specific expertise ensures accurate assessment
- **Scalability**: Modular design allows for easy addition of new assessment types

### Progress Tracking Integration
- **Holistic View**: Combines assessment data with learning interactions for comprehensive progress tracking
- **Predictive Analytics**: Uses AI to predict learning trajectories and identify gaps
- **Actionable Insights**: Provides specific, actionable recommendations for improvement

## Implementation Plan

### Phase 1: Core Assessment Framework (Weeks 1-3)
1. Implement basic assessment models and interfaces
2. Create assessment item management system
3. Develop basic response processing capabilities
4. Integrate with Azure Data Lake storage

### Phase 2: Domain-Specific Processors (Weeks 4-8)
1. Implement pronunciation assessment with tonal analysis
2. Develop vocabulary understanding and usage assessment
3. Create conversation and communication context assessment
4. Build vocabulary and grammar assessment processors

### Phase 3: Adaptive Assessment Engine (Weeks 9-12)
1. Implement AI-powered assessment item selection
2. Develop adaptive difficulty adjustment algorithms
3. Create personalized feedback generation system
4. Integrate with Semantic Kernel AI framework

### Phase 4: Progress Tracking System (Weeks 13-16)
1. Build comprehensive progress tracking engine
2. Implement skill progression analytics
3. Develop predictive learning trajectory modeling
4. Create comparative analytics and benchmarking

### Phase 5: Real-time Integration (Weeks 17-20)
1. Implement real-time assessment coordination
2. Integrate with UI framework for immediate feedback
3. Develop learning effectiveness integration
4. Create comprehensive reporting and analytics dashboard

## Success Metrics

### Assessment Accuracy
- **Prediction Accuracy**: >90% accuracy in predicting learner proficiency levels
- **Communication Appropriateness**: >95% accuracy in communication context assessment
- **Tonal Assessment**: <5% error rate in tonal accuracy measurement

### Learning Effectiveness
- **Skill Improvement**: 25% faster skill progression compared to traditional assessment methods
- **Engagement**: >80% learner satisfaction with assessment feedback
- **Retention**: 20% improvement in knowledge retention through adaptive assessment

### System Performance
- **Response Time**: <2 seconds for real-time assessment processing
- **Throughput**: Support >10,000 concurrent assessment sessions
- **Availability**: 99.9% system uptime

### Data Quality
- **Completeness**: >98% complete assessment data capture
- **Accuracy**: <2% data processing error rate
- **Timeliness**: Real-time assessment results delivered within 1 second

## Risks and Mitigation

### Assessment Bias
- **Risk**: Linguistic or phonetic bias in assessment algorithms
- **Mitigation**: Diverse training data, linguistic expert review, bias detection algorithms

### Privacy Concerns
- **Risk**: Sensitive learner assessment data exposure
- **Mitigation**: End-to-end encryption, privacy-preserving analytics, minimal data retention

### Assessment Validity
- **Risk**: Assessment may not accurately reflect real-world language competency
- **Mitigation**: Validation studies, expert linguist review, real-world testing scenarios

### Technical Complexity
- **Risk**: Complex multi-modal assessment may be difficult to implement and maintain
- **Mitigation**: Modular architecture, comprehensive testing, gradual rollout

## Related ADRs
- ADR-001: AI Framework using Semantic Kernel
- ADR-003: Data Storage with Azure Data Lake
- ADR-008: Performance Monitoring and Optimization
- ADR-009: Learning Effectiveness Feedback Loop
- ADR-010: Content Management & Curriculum Architecture
- ADR-011: User Interface & Learning Experience Architecture