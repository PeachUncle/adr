# ADR 002: Calculation Engine Design

## Status
Accepted

## Context
The calculation engine is the core of the Nx System Calculator. It must accurately compute storage requirements, server counts, bandwidth needs, and provide hardware recommendations based on camera configurations. The engine must be:
- Accurate and verifiable against real-world deployments
- Testable with high coverage
- Maintainable and extensible
- Configuration-driven to allow updates without code changes
- Framework-agnostic for potential reuse

## Decision

### Architecture Pattern: Pure Functions with Dependency Injection

The calculation engine will be implemented as a collection of pure functions organized into modules:

```
services/calculations/
├── __init__.py
├── bitrate.py          # Bitrate estimation
├── storage.py          # Storage calculations
├── raid.py             # RAID overhead calculations
├── servers.py          # Server count and distribution
├── bandwidth.py        # Network bandwidth
├── licenses.py         # License counting
└── validators.py       # Input validation
```

### Key Principles

1. **Pure Functions**: All calculation functions are pure (no side effects, deterministic)
2. **Type Safety**: Full type hints with Pydantic models for validation
3. **Configuration-Driven**: All constants loaded from JSON configuration files
4. **Composability**: Small, focused functions that compose into larger calculations
5. **Testability**: Each function independently testable with clear inputs/outputs

### Calculation Flow

```
Input (Pydantic Model)
    ↓
Validation
    ↓
Bitrate Calculation → Storage Calculation → RAID Overhead
    ↓                      ↓                      ↓
Server Count ← Bandwidth Calculation ← Load Distribution
    ↓
License Calculation
    ↓
Output (Pydantic Model)
```

### Example Function Signature

```python
def calculate_bitrate(
    resolution_area: int,
    fps: int,
    codec: CodecConfig,
    quality: str = "medium",
    audio_enabled: bool = False
) -> float:
    """
    Calculate bitrate in Kbps for a camera stream.
    
    Args:
        resolution_area: Total pixels (width × height)
        fps: Frames per second
        codec: Codec configuration with compression factor
        quality: Quality level (low, medium, high, best)
        audio_enabled: Whether audio is recorded
        
    Returns:
        Bitrate in Kbps
    """
    # Pure calculation logic
    pass
```

### Configuration Loading

```python
class ConfigLoader:
    """Singleton for loading and caching configuration."""
    
    @staticmethod
    def load_resolutions() -> List[ResolutionConfig]:
        """Load resolution presets from config/resolutions.json"""
        
    @staticmethod
    def load_codecs() -> List[CodecConfig]:
        """Load codec parameters from config/codecs.json"""
        
    @staticmethod
    def load_raid_types() -> List[RaidConfig]:
        """Load RAID configurations from config/raid_types.json"""
        
    @staticmethod
    def load_server_specs() -> ServerSpecsConfig:
        """Load server specifications from config/server_specs.json"""
```

## Formulas

### Bitrate Calculation
```
bitrate_kbps = (resolution_area × fps × compression_factor × quality_multiplier) / 1000
audio_bitrate = 64 kbps (if enabled)
total_bitrate = video_bitrate + audio_bitrate
```

### Storage Calculation
```
daily_storage_gb = (bitrate_kbps × recording_factor × 86400) / (8 × 1024 × 1024)
total_storage_gb = daily_storage_gb × retention_days
```

### RAID Overhead
```
usable_storage = raw_storage × (raid_usable_percentage / 100) × (1 - filesystem_overhead)
```

### Server Count
```
servers_by_device_count = ceil(total_devices / max_devices_per_server)
servers_by_bandwidth = ceil(total_bitrate_mbps / (nic_capacity_mbps × nic_count × 0.8))
servers_needed = max(servers_by_device_count, servers_by_bandwidth)
servers_with_failover = servers_needed × failover_multiplier
```

## Validation Rules

1. **Device Limits**:
   - Max 256 devices per server (reduced for high-bandwidth cameras)
   - Max 10 servers per site
   - Max 2560 devices per site

2. **Bandwidth Limits**:
   - Total bitrate must not exceed NIC capacity × 0.8 (20% headroom)
   - Warn if approaching 70% of capacity

3. **Storage Limits**:
   - Minimum 1 day retention
   - Maximum 365 days retention (warning above 90 days)

4. **Input Validation**:
   - FPS: 1-100
   - Resolution: Must match preset or custom within bounds
   - Bitrate: If manual, must be > 0

## Error Handling

```python
class CalculationError(Exception):
    """Base exception for calculation errors"""

class ValidationError(CalculationError):
    """Input validation failed"""

class ConstraintViolationError(CalculationError):
    """System constraint exceeded"""
```

## Testing Strategy

1. **Unit Tests**: Each function tested independently
2. **Property-Based Tests**: Use Hypothesis to test invariants
3. **Golden Tests**: Compare against legacy calculator outputs
4. **Edge Cases**: Boundary conditions, extreme values
5. **Integration Tests**: Full calculation pipeline

### Test Coverage Targets
- Line coverage: ≥85%
- Branch coverage: ≥80%
- Mutation score: ≥70%

## Performance Considerations

1. **Caching**: Configuration loaded once and cached
2. **Vectorization**: Use NumPy for bulk calculations when needed
3. **Lazy Evaluation**: Calculate only what's requested
4. **Target**: <100ms for single calculation, <1s for complex multi-site

## Consequences

### Positive
- Easy to test and verify
- Configuration changes don't require code deployment
- Functions can be reused in other contexts
- Clear separation of concerns
- Type safety catches errors early

### Negative
- More files to maintain
- Need to keep configuration in sync with code
- Pure functions may require passing many parameters

### Neutral
- Team needs to understand functional programming concepts
- Configuration validation adds complexity

## Future Enhancements

1. **Caching Layer**: Cache common calculations
2. **Batch Processing**: Optimize for multiple scenarios
3. **ML Integration**: Learn from actual deployments to improve estimates
4. **What-If Analysis**: Compare multiple configurations side-by-side

## References
- Nx Witness System Requirements: https://support.networkoptix.com/
- Video Bitrate Calculation: Industry standards
- RAID Calculator: Standard RAID formulas

## Date
2025-10-03

## Authors
AI Coding Assistant (RISC Protocol v6.0)

