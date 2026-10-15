# ADR-002: Gematria Calculation Rules

## Status

Accepted

## Context

The Gematria system requires consistent, accurate Hebrew numerology calculations. Key requirements:

- Academic accuracy following standard Hebrew numerology
- Reproducible calculations for validation
- Support for text preprocessing (nikud removal)
- Clear rules for edge cases (finals, punctuation)

## Decision

Implement Mispar Hechrachi (standard method) with the following rules:

1. **Standard Values**: א=1, ב=2, ..., ת=400
2. **Final Forms**: ך׳=20 (כ), ם׳=40 (מ), ן׳=50 (נ), ף׳=80 (פ), ץ׳=90 (צ)
3. **Text Processing**: Strip nikud/vowels completely using NFKD normalization
4. **Validation**: Triple verification (local calculation + AI confirmation + expected values)

## Rationale

### Mispar Hechrachi Chosen

- **Academic Standard**: Most widely used in Hebrew numerology studies
- **Consistency**: Matches existing biblical gematria research
- **Simplicity**: Clear, reproducible calculations
- **Compatibility**: Aligns with existing golden data

### Final Forms Handling

- **Standard Practice**: Finals have same value as regular forms
- **Rationale**: Represents same letter, different positional form
- **Example**: ך׳ (sofiyot kaf) = 20, same as כ (regular kaf)

### Nikud Stripping Required

- **Consistency**: Removes ambiguity from vowel marks
- **Reproducibility**: Same input always produces same output
- **Performance**: Faster processing without vowel analysis
- **Compatibility**: Matches existing Hebrew text processing

## Alternatives Considered

### Mispar Gadol (Large Method)

- **Pros**: Alternative tradition with different values for finals
- **Cons**: Less common, inconsistent with existing data
- **Rejected**: Would require recalculating all existing values

### Include Nikud in Calculations

- **Pros**: More complete linguistic analysis
- **Cons**: Complex, inconsistent, vowel values not standardized
- **Rejected**: Too complex, not standard practice

### Context-Aware Calculations

- **Pros**: Could account for linguistic context
- **Cons**: Non-deterministic, hard to validate
- **Rejected**: Needs to be mathematical and reproducible

## Implementation Details

### Calculation Algorithm

```python
def calculate_gematria(hebrew_text: str) -> int:
    mapping = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
        'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50, 'ס': 60, 'ע': 70,
        'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400
    }
    clean_text = strip_nikud(hebrew_text)
    return sum(mapping.get(char, 0) for char in clean_text)
```

### Text Normalization

```python
def strip_nikud(hebrew_text: str) -> str:
    # NFKD decomposition
    normalized = unicodedata.normalize('NFKD', hebrew_text)
    # Remove combining marks (nikud) and non-letter chars
    clean = ''.join(c for c in normalized
                   if unicodedata.category(c) == 'Lo'  # Letters only
                   or c in 'כךמםנןפףצץ')  # Allow finals
    # NFC recomposition
    return unicodedata.normalize('NFC', clean)
```

### Validation Test Cases

Based on standard biblical examples:

- אדם = 45 (1+4+40)
- הבל = 37 (5+2+30)
- משיח = 358 (40+300+10+8)
- אלהים = 86 (1+30+5+10+40)
- תורה = 611 (400+6+200+5)

## Consequences

### Positive

- Consistent with academic standards
- Reproducible calculations
- Easy validation and testing
- Compatible with existing data

### Negative

- Strict rules may miss some traditional interpretations
- Requires careful text preprocessing
- No support for alternative calculation methods

### Testing Requirements

- Unit tests for all calculation edge cases
- Validation against known biblical values
- Text preprocessing verification
- Performance benchmarks

## Migration Notes

- Existing data calculated with these rules remains valid
- New calculations must follow same algorithm
- Triple verification ensures accuracy
- Validation test suite prevents regressions

## Related ADRs

- ADR-000: Pipeline validation depends on consistent calculations
- ADR-003: AI verification of calculations (future)
