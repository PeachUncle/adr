# ADR-0003: Content Personalization Strategy

**Date**: 2025-12-12
**Status**: Accepted
**Context**: 001-ai-native-textbook-platform
**Decision Makers**: Chapter Personalizer Agent, Content Implementor

## Context

The platform must personalize content based on:
1. **Hardware Profile**: RTX 4090 vs Jetson Orin Nano vs Other
2. **Expertise Level**: Beginner vs Intermediate vs Advanced

Students with different hardware setups need different code examples (high-VRAM operations vs quantized models). Beginners need more explanations than advanced users.

## Decision

We will use a **Hybrid Personalization Strategy**:
1. **Static Rules** (MVP): Predefined variations stored in YAML configuration
2. **Dynamic Generation** (Future): AI-generated variations on-demand

**MVP Implementation**: Static rule-based personalization with manual content variations.

## Rationale

### Options Considered

**Option 1: Static Rules (Selected for MVP)**
- ✅ **Fast**: No LLM calls, instant response
- ✅ **Predictable**: Quality controlled by humans
- ✅ **Cost-Effective**: Zero API costs
- ✅ **Simple**: Easy to implement and test
- ❌ **Manual Work**: Requires creating variations for each chapter
- ❌ **Limited Flexibility**: Fixed number of variations

**Option 2: Dynamic AI Generation**
- ✅ **Flexible**: Infinite variations possible
- ✅ **Scalable**: No manual content creation
- ❌ **Slow**: Requires LLM call (~2 seconds)
- ❌ **Expensive**: API costs per personalization
- ❌ **Quality Risk**: AI might generate incorrect code

**Option 3: Hybrid (Selected Path)**
- **MVP**: Static rules for core chapters
- **Future**: Dynamic generation for edge cases
- **Best of Both**: Fast common cases, flexible for outliers

### Why Static Rules for MVP?

1. **Performance**: Instant personalization (no API call)
2. **Quality**: Human-verified code examples
3. **Cost**: Zero incremental costs
4. **Hackathon Timeline**: Faster to implement
5. **Upgrade Path**: Can add dynamic generation later

## Implementation Architecture

### Personalization Rules Format

```yaml
# apps/api/src/services/personalization/rules.yaml

chapters:
  module-3-week-8-isaac-sim:
    hardware_variations:
      rtx_4090:
        code_replacements:
          - original: "# Default configuration"
            replacement: |
              # RTX 4090 Configuration
              sim.set_render_mode("ray_tracing")
              sim.set_rtx_settings(samples=256, max_bounces=16)

      jetson_orin_nano:
        code_replacements:
          - original: "# Default configuration"
            replacement: |
              # Jetson Orin Nano Configuration (Optimized)
              sim.set_render_mode("fast")
              sim.set_quantization(int8=True)

    expertise_variations:
      beginner:
        explanation_additions:
          - section: "VSLAM Concepts"
            addition: |
              **Beginner Note**: VSLAM stands for Visual Simultaneous Localization
              and Mapping. Think of it like creating a map while exploring a new place.

      advanced:
        explanation_removals:
          - section: "Basic Setup"
            remove_lines: [1, 5]  # Remove introductory paragraphs
```

### Personalization Service Flow

```
1. User clicks "Personalize" button
   ↓
2. Frontend calls: POST /api/personalization/apply
   {
     "chapter_slug": "module-3-week-8",
     "user_id": "abc123"
   }
   ↓
3. Backend fetches user profile:
   - hardware_type: "jetson_orin_nano"
   - expertise_level: "beginner"
   ↓
4. Backend loads rules.yaml for chapter
   ↓
5. Apply hardware variations:
   - Replace code blocks with Jetson-optimized versions
   ↓
6. Apply expertise variations:
   - Add beginner explanations
   ↓
7. Return personalized MDX content
   ↓
8. Frontend renders personalized chapter
```

### Caching Strategy

- **User Profile**: Cached in auth context (no DB call per personalization)
- **Rules**: Loaded once at startup, cached in memory
- **Personalized Content**: NOT cached (generated on-demand, very fast)

## Content Variation Examples

### Hardware-Based Code Examples

**Original (Generic)**:
```python
# Isaac Sim Configuration
sim = IsaacSim()
sim.load_robot("humanoid.usd")
```

**RTX 4090 Version**:
```python
# Isaac Sim Configuration (RTX 4090 - High Fidelity)
sim = IsaacSim(
    render_mode="ray_tracing",
    rtx_samples=256,
    max_bounces=16
)
sim.load_robot("humanoid_high_poly.usd")
# Enable real-time physics simulation with high precision
sim.set_physics_timestep(1/240)  # 240 Hz
```

**Jetson Orin Nano Version**:
```python
# Isaac Sim Configuration (Jetson Orin Nano - Optimized)
sim = IsaacSim(
    render_mode="fast",
    use_quantization=True  # INT8 for faster inference
)
sim.load_robot("humanoid_low_poly.usd")  # Reduced polygon count
# Use coarser physics timestep for performance
sim.set_physics_timestep(1/60)  # 60 Hz
```

### Expertise-Based Explanations

**Beginner**:
> **What is VSLAM?**
> Visual Simultaneous Localization and Mapping (VSLAM) is like creating a map
> while exploring. Imagine you're in a dark room with a flashlight - as you move
> around, you remember where you've been and what you've seen. VSLAM does the
> same using camera images.

**Advanced** (simplified):
> VSLAM: Camera-based pose estimation + sparse/dense mapping with loop closure detection.

## Consequences

### Positive

- **Fast Performance**: Zero latency for personalization
- **High Quality**: Human-verified code examples
- **Cost-Free**: No API costs
- **Predictable**: Consistent results
- **Easy Testing**: Can verify all variations manually

### Negative

- **Manual Work**: Requires creating variations for ~20 key chapters
- **Storage**: YAML files grow with more variations
- **Limited Coverage**: Only personalized chapters with rules
- **Maintenance**: Need to update rules when content changes

### Neutral

- Rule files are version-controlled (easy to review changes)
- Can A/B test different variations
- Easy to add new hardware types (just add to YAML)

## Coverage Plan

**MVP Personalization** (Phases):
1. **Phase 1**: Module 3 (Isaac Sim) - 3 chapters, 2 hardware types
2. **Phase 2**: Module 4 (VLA) - 3 chapters, 2 hardware types
3. **Phase 3**: Module 2 (Gazebo/Unity) - 2 chapters (if time permits)

**Estimated Work**:
- 6-8 chapters × 2 hardware types = 12-16 code variations
- 6-8 chapters × 2 expertise levels = 12-16 explanation variations
- **Total**: ~30 variations to create

## Fallback Strategy

If user has incomplete profile or chapter has no rules:
- **Display Generic Content**: Show original chapter without personalization
- **Button State**: "Personalize" button disabled with tooltip
  - "Complete your hardware profile in Settings to enable personalization"

## Future Enhancement Path

When ready to add dynamic generation:

```python
async def personalize_dynamic(chapter: str, profile: UserProfile):
    # Fallback to dynamic if no static rules
    if chapter not in rules:
        prompt = f"""
        Adapt this code for {profile.hardware_type}:

        {chapter_content}

        Optimize for: {profile.hardware_type}
        """
        return await gemini.generate(prompt)
```

## Compliance

- ✅ **FR-026**: Code examples adapted based on hardware
- ✅ **FR-027**: Explanation depth adjusted by expertise
- ✅ **FR-028**: Toggle on/off instantly
- ✅ **FR-029**: Generic content fallback
- ✅ **SC-003**: 80%+ satisfaction with personalized examples

## Related Decisions

- ADR-0002: RAG System (dynamic content generation precedent)
- ADR-0004: Translation Management (similar static vs dynamic trade-off)

---

**Status**: ✅ **ACTIVE** - Static rules implemented for Modules 3-4
