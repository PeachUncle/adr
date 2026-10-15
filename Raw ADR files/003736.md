# ADR-011: User Interface & Learning Experience Architecture

**Status:** Proposed  
**Date:** 2025-05-27  
**Deciders:** SayZhong Development Team  
**Technical Story:** User Interface & Learning Experience Framework for Mandarin Learning

## Context

The SayZhong application requires a comprehensive user interface and learning experience architecture that enables effective Mandarin language learning through engaging, adaptive, and phonetic-aware interactions. This architecture must seamlessly integrate with the content management system (ADR-010) and respond dynamically to learning effectiveness feedback (ADR-009).

### Key Requirements

1. **Mandarin-Specific UI Elements**: Tone visualization, pinyin input, and phonetic English pronunciation guides
2. **Adaptive Learning Interface**: Dynamic UI adaptation based on learner performance and preferences
3. **Multi-Modal Learning Support**: Visual, auditory, kinesthetic learning modalities
4. **Progress Visualization**: Real-time progress tracking and skill tree navigation
5. **Assessment Integration**: Seamless assessment experiences with immediate feedback
6. **Accessibility & Internationalization**: Support for diverse learners and accessibility needs

### Related ADRs

- **ADR-001**: AI Framework Architecture (intelligent UI recommendations)
- **ADR-008**: Performance & Scalability (responsive UI delivery)
- **ADR-009**: Learning Effectiveness Feedback Loop (adaptive UI behavior)
- **ADR-010**: Content Management & Curriculum (content presentation)

## Decision

We will implement a component-based, adaptive user interface architecture consisting of:

1. **Learning Session Interface Layer**: Interactive components for different content types
2. **Adaptive UI Framework Layer**: Dynamic interface adaptation and personalization
3. **Progress & Navigation Layer**: Learning progress visualization and curriculum navigation
4. **Assessment & Feedback Layer**: Assessment interfaces and real-time feedback systems
5. **Accessibility & Localization Layer**: Universal design and internationalization support

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              Accessibility & Localization Layer            │
├─────────────────────────────────────────────────────────────┤
│     Assessment &        │    Progress & Navigation         │
│     Feedback Layer      │    - Skill Tree Visualization    │
│     - Real-time Tests   │    - Progress Tracking          │
│     - Immediate Feedback│    - Learning Path Navigation    │
├─────────────────────────────────────────────────────────────┤
│                 Adaptive UI Framework Layer                 │
│  - Personalization Engine  - Layout Adaptation             │
│  - Learning Style Support  - Phonetic English Integration  │
├─────────────────────────────────────────────────────────────┤
│              Learning Session Interface Layer               │
│  - Vocabulary UI   - Conversation UI   - Pronunciation UI  │
│  - Grammar UI      - Assessment UI     - Media Content     │
├─────────────────────────────────────────────────────────────┤
│                     UI State Management                     │
│              (ADR-002 State Management Strategy)            │
└─────────────────────────────────────────────────────────────┘
```

## Learning Session Interface Layer

### Vocabulary Learning Interface

```python
@dataclass
class VocabularyUIConfig:
    """Configuration for vocabulary learning interface."""
    display_mode: str           # flashcard, list, game, immersive
    tone_visualization: str     # color_coded, contour_lines, audio_wave
    pinyin_display: str         # tone_marks, numeric, both, hidden
    phonetic_english_display: str # always, hover, click, hidden
    audio_playback: str         # auto, on_click, on_hover
    example_sentences: bool
    difficulty_indicators: bool
    progress_indicators: bool

@dataclass
class VocabularyUIComponent:
    """Vocabulary learning UI component specification."""
    component_id: str
    vocabulary_item: str        # VocabularyItem ID
    ui_config: VocabularyUIConfig
    interaction_state: 'VocabularyInteractionState'
    personalization: 'UIPersonalization'
    
    # UI Elements
    vocabulary_display: 'VocabularyDisplayElement'
    pronunciation_player: 'AudioPlayerElement'
    definition_panel: 'DefinitionPanelElement'
    example_carousel: 'ExampleCarouselElement'
    tone_visualizer: 'ToneVisualizationElement'
    progress_indicator: 'ProgressIndicatorElement'
    phonetic_english_panel: 'PhoneticEnglishElement'
    
    # Interaction Handlers
    pronunciation_practice: 'PronunciationPracticeHandler'
    recall_testing: 'RecallTestingHandler'

@dataclass
class VocabularyInteractionState:
    """State tracking for vocabulary learning interactions."""
    current_learning_phase: str    # introduction, practice, testing, review
    attempts_count: int
    success_rate: float
    time_spent: int               # seconds
    pronunciation_attempts: int
    help_requests: int
    phonetic_english_viewed: bool
    example_sentences_reviewed: int
    last_interaction: datetime
```

### Conversation Learning Interface

```python
@dataclass
class ConversationUIConfig:
    """Configuration for conversation learning interface."""
    interaction_mode: str        # guided, free_form, role_play
    speaker_visualization: str   # avatars, photos, names_only
    dialogue_display: str        # sequential, parallel, immersive
    phonetic_coaching: str       # inline, popup, sidebar
    pronunciation_feedback: str  # real_time, post_interaction, disabled
    translation_assistance: str  # hover, click, hidden
    scenario_immersion: str      # basic, enhanced, full_vr
    
@dataclass
class ConversationUIComponent:
    """Conversation learning UI component specification."""
    component_id: str
    conversation_content: str    # ConversationContent ID
    ui_config: ConversationUIConfig
    interaction_state: 'ConversationInteractionState'
    
    # UI Elements
    dialogue_display: 'DialogueDisplayElement'
    speaker_panel: 'SpeakerPanelElement'
    phonetic_coach: 'PhoneticCoachElement'
    pronunciation_recorder: 'PronunciationRecorderElement'
    scenario_background: 'ScenarioBackgroundElement'
    progress_tracker: 'ConversationProgressElement'
    
    # Interaction Handlers
    dialogue_practice: 'DialoguePracticeHandler'
    role_switching: 'RoleSwitchingHandler'
    phonetic_guidance: 'PhoneticGuidanceHandler'
    pronunciation_analysis: 'PronunciationAnalysisHandler'

@dataclass
class DialogueDisplayElement:
    """Dialogue display UI element."""
    display_style: str           # chat_bubble, script, immersive
    text_size: str              # small, medium, large, adaptive
    tone_coloring: bool         # Color-code tones
    translation_overlay: bool   # Show/hide translations
    pronunciation_hints: bool   # Show pronunciation guidance
    phonetic_english: bool      # Show English phonetic approximations
```

### Pronunciation Learning Interface

```python
@dataclass
class PronunciationUIConfig:
    """Configuration for pronunciation learning interface."""
    feedback_mode: str           # visual, auditory, haptic, combined
    tone_visualization: str      # contour, wave, color, animation
    comparison_display: str      # side_by_side, overlay, sequential
    feedback_detail: str         # basic, detailed, expert
    recording_quality: str       # standard, high, studio
    phonetic_english: bool       # Show English phonetic approximations
    
@dataclass
class PronunciationUIComponent:
    """Pronunciation learning UI component specification."""
    component_id: str
    pronunciation_content: str   # PronunciationContent ID
    ui_config: PronunciationUIConfig
    interaction_state: 'PronunciationInteractionState'
    
    # UI Elements
    tone_visualizer: 'ToneVisualizationElement'
    audio_recorder: 'AudioRecorderElement'
    waveform_display: 'WaveformDisplayElement'
    mouth_position_guide: 'MouthPositionElement'
    feedback_panel: 'PronunciationFeedbackElement'
    comparison_viewer: 'AudioComparisonElement'
    phonetic_guide: 'PhoneticEnglishElement'
    
    # Interaction Handlers
    pronunciation_analysis: 'PronunciationAnalysisHandler'
    tone_recognition: 'ToneRecognitionHandler'
    feedback_generation: 'FeedbackGenerationHandler'

@dataclass
class ToneVisualizationElement:
    """Tone visualization UI element."""
    visualization_type: str      # contour_line, color_gradient, animation
    real_time_display: bool
    target_overlay: bool         # Show target tone pattern
    difference_highlighting: bool # Highlight tone differences

@dataclass
class PhoneticEnglishElement:
    """English phonetic approximation UI element."""
    display_style: str           # inline, tooltip, separate_panel
    approximation_quality: str   # basic, detailed, regional
    show_tone_hints: bool        # Include tone direction in phonetics
```

## Adaptive UI Framework Layer

### Personalization Engine

```python
@dataclass
class UIPersonalization:
    """User interface personalization configuration."""
    user_id: str
    learning_style: str          # visual, auditory, kinesthetic, mixed
    interface_complexity: str    # beginner, intermediate, advanced
    accessibility_needs: List[str] # screen_reader, high_contrast, etc.
    language_preferences: List[str] # UI language preferences
    font_preferences: 'FontPreferences'
    color_preferences: 'ColorPreferences'
    animation_preferences: 'AnimationPreferences'
    feedback_preferences: 'FeedbackPreferences'
    layout_preferences: 'LayoutPreferences'
    
@dataclass
class FontPreferences:
    """Font and typography preferences."""
    chinese_font_family: str
    pinyin_font_family: str
    ui_font_family: str
    base_font_size: int         # pixels
    font_weight: str           # normal, bold, light
    character_spacing: float   # letter-spacing multiplier
    line_height: float         # line-height multiplier

@dataclass
class AdaptiveUIEngine:
    """Engine for dynamic UI adaptation."""
    
    async def adapt_interface(
        self,
        user_profile: UIPersonalization,
        learning_context: 'LearningContext',
        performance_data: 'PerformanceData'
    ) -> 'UIAdaptation':
        """Adapt interface based on user and context."""
        pass
    
    async def optimize_layout(
        self,
        content_type: str,
        device_constraints: 'DeviceConstraints',
        user_preferences: UIPersonalization
    ) -> 'LayoutConfiguration':
        """Optimize layout for content and device."""
        pass
    
    async def adjust_difficulty_presentation(
        self,
        current_difficulty: float,
        user_performance: float,
        stress_indicators: Dict[str, float]
    ) -> 'DifficultyPresentation':
        """Adjust how difficulty is presented to user."""
        pass
```

## Progress & Navigation Layer

### Skill Tree Visualization

```python
@dataclass
class SkillTreeUIConfig:
    """Configuration for skill tree visualization."""
    visualization_style: str     # tree, graph, path, game_map
    node_representation: str     # circles, icons, cards, 3d_objects
    connection_style: str        # lines, paths, bridges, portals
    progress_animation: bool
    mastery_celebration: bool
    prerequisite_highlighting: bool
    
@dataclass
class SkillTreeComponent:
    """Skill tree visualization component."""
    component_id: str
    skill_tree: str             # SkillTree ID
    ui_config: SkillTreeUIConfig
    user_progress: 'UserProgressState'
    
    # UI Elements
    skill_nodes: List['SkillNodeElement']
    connection_paths: List['ConnectionPathElement']
    progress_overlay: 'ProgressOverlayElement'
    navigation_controls: 'NavigationControlsElement'
    achievement_display: 'AchievementDisplayElement'
    
    # Interaction Handlers
    node_selection: 'NodeSelectionHandler'
    progress_navigation: 'ProgressNavigationHandler'
    achievement_celebration: 'AchievementCelebrationHandler'

@dataclass
class SkillNodeElement:
    """Individual skill node in the tree."""
    node_id: str
    skill_name: str
    mastery_level: float        # 0.0 to 1.0
    accessibility_status: str   # locked, available, completed
    visual_style: 'NodeVisualStyle'
    interaction_state: 'NodeInteractionState'
```

### Learning Progress Dashboard

```python
@dataclass
class ProgressDashboardConfig:
    """Configuration for learning progress dashboard."""
    dashboard_style: str         # minimal, detailed, gamified
    metric_display: str         # charts, gauges, progress_bars
    time_frame: str             # daily, weekly, monthly, all_time
    comparison_mode: str        # self, peers, goals
    celebration_frequency: str   # every_achievement, milestones, major_goals
    
@dataclass
class ProgressDashboardComponent:
    """Learning progress dashboard component."""
    component_id: str
    user_progress: 'UserProgressState'
    ui_config: ProgressDashboardConfig
    
    # UI Elements
    overall_progress: 'OverallProgressElement'
    skill_breakdown: 'SkillBreakdownElement'
    streak_tracker: 'StreakTrackerElement'
    achievement_gallery: 'AchievementGalleryElement'
    goal_tracker: 'GoalTrackerElement'
    phonetic_milestones: 'PhoneticMilestonesElement'
    
    # Interaction Handlers
    goal_setting: 'GoalSettingHandler'
    progress_sharing: 'ProgressSharingHandler'
    achievement_exploration: 'AchievementExplorationHandler'
```

## Assessment & Feedback Layer

### Assessment Interface Framework

```python
@dataclass
class AssessmentUIConfig:
    """Configuration for assessment interfaces."""
    assessment_style: str        # formal, conversational, gamified
    feedback_timing: str         # immediate, deferred, end_of_session
    feedback_detail: str         # basic, detailed, expert
    phonetic_assessment: bool    # Include phonetic understanding
    adaptive_difficulty: bool    # Adjust difficulty in real-time
    
@dataclass
class AssessmentUIComponent:
    """Assessment interface component."""
    component_id: str
    assessment_content: str      # AssessmentContent ID
    ui_config: AssessmentUIConfig
    assessment_state: 'AssessmentState'
    
    # UI Elements
    question_display: 'QuestionDisplayElement'
    answer_input: 'AnswerInputElement'
    feedback_panel: 'FeedbackPanelElement'
    progress_indicator: 'AssessmentProgressElement'
    phonetic_context: 'PhoneticAssessmentElement'
    
    # Interaction Handlers
    answer_validation: 'AnswerValidationHandler'
    feedback_generation: 'FeedbackGenerationHandler'
    adaptive_adjustment: 'AdaptiveAdjustmentHandler'

@dataclass
class QuestionDisplayElement:
    """Question display UI element."""
    question_type: str           # multiple_choice, audio_match, tone_recognition
    media_integration: bool      # Audio/video support
    phonetic_context_display: bool
    hint_system: bool
    accessibility_features: List[str]
```

### Real-Time Feedback System

```python
@dataclass
class FeedbackUIConfig:
    """Configuration for real-time feedback."""
    feedback_modality: str       # visual, auditory, haptic, combined
    feedback_intensity: str      # subtle, moderate, prominent
    feedback_frequency: str      # continuous, periodic, on_error
    phonetic_feedback: bool      # Include phonetic understanding
    
@dataclass
class RealTimeFeedbackComponent:
    """Real-time feedback component."""
    component_id: str
    feedback_config: FeedbackUIConfig
    current_interaction: 'InteractionContext'
    
    # UI Elements
    visual_feedback: 'VisualFeedbackElement'
    audio_feedback: 'AudioFeedbackElement'
    haptic_feedback: 'HapticFeedbackElement'
    progress_indicators: 'ProgressIndicatorElement'
    encouragement_display: 'EncouragementElement'
    
    # Feedback Handlers
    pronunciation_feedback: 'PronunciationFeedbackHandler'
    tone_feedback: 'ToneFeedbackHandler'
    phonetic_feedback: 'PhoneticFeedbackHandler'
```

## Accessibility & Localization Layer

### Accessibility Framework

```python
@dataclass
class AccessibilityConfig:
    """Accessibility configuration."""
    screen_reader_support: bool
    high_contrast_mode: bool
    font_scaling: float          # 0.5 to 3.0
    color_blind_support: bool
    motion_sensitivity: str      # none, reduced, normal
    keyboard_navigation: bool
    voice_commands: bool
    subtitle_support: bool
    
@dataclass
class AccessibilityComponent:
    """Accessibility support component."""
    component_id: str
    accessibility_config: AccessibilityConfig
    
    # Accessibility Features
    screen_reader_annotations: 'ScreenReaderAnnotations'
    keyboard_shortcuts: 'KeyboardShortcuts'
    color_alternatives: 'ColorAlternatives'
    motion_alternatives: 'MotionAlternatives'
    voice_interface: 'VoiceInterface'
    
@dataclass
class ScreenReaderAnnotations:
    """Screen reader support annotations."""
    pinyin_descriptions: bool
    tone_descriptions: bool
    phonetic_context_descriptions: bool
    progress_announcements: bool
    navigation_assistance: bool
```

### Internationalization Framework

```python
@dataclass
class LocalizationConfig:
    """Localization configuration."""
    ui_language: str             # ISO language code
    phonetic_adaptation: str     # minimal, contextual, full
    date_format: str
    number_format: str
    currency_format: str
    measurement_units: str       # metric, imperial
    
@dataclass
class LocalizationComponent:
    """Internationalization component."""
    component_id: str
    localization_config: LocalizationConfig
    
    # Localization Features
    text_translation: 'TextTranslation'
    phonetic_adaptation: 'PhoneticAdaptation'
    format_localization: 'FormatLocalization'
    content_localization: 'ContentLocalization'
```

## UI State Management Integration

### Learning Session State

```python
@dataclass
class LearningSessionUIState:
    """UI state for learning sessions."""
    session_id: str
    user_id: str
    current_content: str         # Content ID
    ui_configuration: Dict[str, Any]
    interaction_history: List['UIInteraction']
    adaptation_state: 'UIAdaptationState'
    progress_state: 'ProgressUIState'
    feedback_state: 'FeedbackUIState'
    
    # Session Management
    session_start_time: datetime
    last_interaction_time: datetime
    total_interaction_time: int  # seconds
    break_reminders: List[datetime]
    session_objectives: List[str]
    completion_status: str       # in_progress, completed, paused

@dataclass
class UIInteraction:
    """Individual UI interaction record."""
    interaction_id: str
    interaction_type: str        # click, voice, gesture, keyboard
    component_id: str
    timestamp: datetime
    interaction_data: Dict[str, Any]
    response_time: int          # milliseconds
    success: bool
    phonetic_context: Optional[str]
```

## Integration Points

### With Content Management (ADR-010)

```python
class ContentUIIntegration:
    """Integration with content management system."""
    
    async def render_vocabulary_item(
        self,
        vocabulary_item: 'VocabularyItem',
        ui_config: VocabularyUIConfig,
        user_context: 'UserContext'
    ) -> VocabularyUIComponent:
        """Render vocabulary item with appropriate UI."""
        pass
    
    async def render_conversation(
        self,
        conversation: 'ConversationContent',
        ui_config: ConversationUIConfig,
        user_context: 'UserContext'
    ) -> ConversationUIComponent:
        """Render conversation with appropriate UI."""
        pass
    
    async def adapt_ui_for_content(
        self,
        content_type: str,
        content_difficulty: float,
        user_proficiency: float
    ) -> 'UIAdaptationRecommendations':
        """Recommend UI adaptations for content."""
        pass
```

### With Learning Effectiveness (ADR-009)

```python
class EffectivenessUIIntegration:
    """Integration with learning effectiveness analysis."""
    
    async def adapt_ui_based_on_effectiveness(
        self,
        effectiveness_analysis: 'EffectivenessAnalysis',
        current_ui_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt UI based on learning effectiveness."""
        pass
    
    async def collect_ui_effectiveness_data(
        self,
        ui_interactions: List[UIInteraction],
        learning_outcomes: List['LearningOutcome']
    ) -> 'UIEffectivenessData':
        """Collect data on UI effectiveness."""
        pass
    
    async def recommend_ui_improvements(
        self,
        ui_effectiveness_data: 'UIEffectivenessData'
    ) -> List['UIImprovementRecommendation']:
        """Recommend UI improvements based on effectiveness."""
        pass
```

### With AI Framework (ADR-001)

```python
@kernel_function(
    description="Generate personalized UI recommendations",
    name="generate_ui_recommendations"
)
async def generate_ui_recommendations(
    user_profile: str,
    learning_context: str,
    performance_data: str
) -> str:
    """Generate AI-powered UI personalization recommendations."""
    pass

@kernel_function(
    description="Generate phonetic English approximations for UI",
    name="generate_phonetic_english"
)
async def generate_phonetic_english(
    pinyin_text: str,
    tone_marks: str,
    user_english_accent: str
) -> str:
    """Generate English phonetic approximations for pronunciation guidance."""
    pass
```

## Implementation Strategy

### Phase 1: Core UI Components (Weeks 1-3)
1. Implement basic learning session components
2. Create vocabulary and pronunciation learning interfaces
3. Build pronunciation and conversation UI elements
4. Implement basic assessment interfaces

### Phase 2: Adaptive UI Framework (Weeks 4-5)
1. Implement personalization engine
2. Create phonetic English integration
3. Build adaptive layout system
4. Implement real-time UI adaptation

### Phase 3: Progress & Navigation (Weeks 6-7)
1. Implement skill tree visualization
2. Create progress dashboard
3. Build navigation systems
4. Implement achievement and milestone tracking

### Phase 4: Assessment & Feedback (Weeks 8-9)
1. Implement comprehensive assessment interfaces
2. Create real-time feedback systems
3. Build phonetic understanding assessment
4. Implement adaptive assessment features

### Phase 5: Accessibility & Polish (Weeks 10-11)
1. Implement accessibility framework
2. Create internationalization support
3. Optimize performance and responsiveness
4. Conduct usability testing and refinement

## Technology Stack

### Frontend Framework
- **React 18+** with TypeScript for component-based architecture
- **React Native** for mobile applications
- **PWA capabilities** for offline learning support

### UI Component Libraries
- **Custom component library** for Mandarin-specific elements
- **Accessibility-first design system**
- **Phonetic approximation framework**

### State Management
- Integration with **ADR-002 State Management Strategy**
- **Real-time state synchronization** across devices
- **Offline state management** for continued learning

### Performance Optimization
- **Lazy loading** for content components
- **Virtual scrolling** for large skill trees
- **Progressive enhancement** for varied device capabilities

## Success Metrics

### User Experience Metrics
- **Task Completion Rate**: Successful completion of learning tasks (>90%)
- **User Satisfaction**: User-rated interface satisfaction (>4.3/5.0)
- **Engagement Duration**: Average session length increase (>20% improvement)
- **Error Recovery**: Successful recovery from UI errors (>95%)

### Learning Effectiveness Metrics
- **Learning Velocity**: Improved learning speed through UI optimization (>15% improvement)
- **Retention Enhancement**: UI-driven retention improvement (>10% improvement)
- **Phonetic English Effectiveness**: Successful pronunciation learning support (measured via assessments)
- **Accessibility Success**: Successful use by learners with accessibility needs (>90% success rate)

### Technical Performance Metrics
- **UI Responsiveness**: Sub-100ms interaction response times
- **Adaptation Speed**: Real-time UI adaptation (<500ms)
- **Cross-Platform Consistency**: Consistent experience across devices (>95% feature parity)
- **Accessibility Compliance**: WCAG 2.1 AA compliance (100%)

### Adaptive Learning Metrics
- **Personalization Accuracy**: Successful UI personalization (>85% user approval)
- **Phonetic English Effectiveness**: Helpful phonetic approximations (>90% user comprehension)
- **Learning Style Support**: Effective multi-modal learning support (measured per learning style)
- **Difficulty Adaptation**: Appropriate difficulty presentation adjustment (>80% effectiveness)

## Risks and Mitigation

### Phonetic Learning Risks
- **Risk**: Inadequate phonetic approximations causing pronunciation confusion
- **Mitigation**: Linguistic expert review process and learner feedback integration

### Accessibility Risks
- **Risk**: Inadequate accessibility support for diverse learners
- **Mitigation**: Accessibility-first design approach and extensive testing with diverse user groups

### Performance Risks
- **Risk**: UI complexity impacting performance on lower-end devices
- **Mitigation**: Progressive enhancement and adaptive complexity based on device capabilities

### Adaptation Risks
- **Risk**: Over-adaptation leading to inconsistent user experience
- **Mitigation**: Core UI consistency requirements and user control over adaptation levels

## Decision Rationale

This architecture provides:

1. **Comprehensive Mandarin Support**: Specialized UI elements for tones, pronunciation, and phonetic English guidance
2. **Adaptive Learning Experience**: Dynamic UI adaptation based on user performance and preferences
3. **Phonetic English Integration**: Helpful pronunciation guides for English speakers
4. **Accessibility Excellence**: Universal design supporting diverse learners and abilities
5. **Performance Optimization**: Responsive, efficient UI suitable for varied device capabilities
6. **Future Extensibility**: Modular architecture supporting future enhancements and additional languages

The architecture seamlessly integrates with existing ADRs while providing an engaging, effective learning experience for Mandarin language acquisition.

## Status

**Current Status**: Proposed  
**Next Steps**: 
1. Review and approval of UI/UX architecture design
2. Create detailed component specifications and design system
3. Begin Phase 1 implementation (Core UI Components)
4. Set up UI testing framework and accessibility validation

**Dependencies**: 
- ADR-010 (Content Management) for content integration
- ADR-009 (Learning Effectiveness) for adaptive behavior
- ADR-012 (Assessment & Progress Tracking) for assessment UI integration
- ADR-002 (State Management) for UI state management