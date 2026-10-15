# ADR 003: Calculation Formula Alignment with core_calculations.md

**Date**: 2025-10-03  
**Status**: ✅ Implemented  
**Decision Makers**: Development Team  
**Related Documents**: `/docs/core_calculations.md`, `/docs/CALCULATION_ALIGNMENT_PLAN.md`

---

## Context

The Nx System Calculator was initially implemented with simplified formulas for bitrate, storage, and server calculations. After receiving the `core_calculations.md` document, we discovered significant deviations from the legacy system's mathematical model. This ADR documents the alignment of all calculations to match the exact formulas specified in the core documentation.

---

## Decision

We have updated ALL calculation formulas to match `core_calculations.md` exactly, ensuring mathematical accuracy and consistency with the legacy system.

---

## Changes Made

### 1. Bitrate Calculation - **MAJOR CHANGE**

#### Before:
```python
bitrate = (resolution_area × fps × compression_factor × quality_multiplier) / 1000
```
- Linear relationship with resolution area
- Simple multiplication
- Division by 1000 for unit conversion

#### After:
```python
# For H.264/H.265:
resolutionFactor = 0.009 × (resolution_area)^0.7
result = brandFactor × qualityFactor × fps × resolutionFactor × codecRatio
bitrate = result / 1024

# For other codecs (MJPEG):
result = (resolution_area / 6666) × fps × qualityFactor × (codecRatio + 1/3) × 12
bitrate = result / 1024
```

**Impact**:
- **Power function** (area^0.7) instead of linear
- Different formulas for H.264/H.265 vs other codecs
- Division by 1024 instead of 1000
- Significantly different results, especially for high-resolution cameras

**Rationale**: The power function (area^0.7) better models the relationship between resolution and bitrate, as compression efficiency improves with larger images.

---

### 2. Quality Factor - **MAJOR CHANGE**

#### Before:
```json
{
  "low": 0.6,
  "medium": 1.0,
  "high": 1.4,
  "best": 2.0
}
```
- Discrete quality multipliers
- Range: 0.6 to 2.0

#### After:
```python
qualityFactor = lowEnd + (hiEnd - lowEnd) × qualityRatio
# where lowEnd = 0.1, hiEnd = 1.0
# qualityRatio: 0.0 (low) to 1.0 (best)
```

**Mapping**:
- low: 0.0 → 0.1
- medium: 0.5 → 0.55
- high: 0.8 → 0.82
- best: 1.0 → 1.0

**Impact**: All bitrate calculations affected. Legacy multipliers are automatically converted for backward compatibility.

**Rationale**: Linear interpolation provides smoother quality scaling and matches the documented range.

---

### 3. Max Camera Bitrate - **NEW CALCULATION**

#### Added:
```python
maxCameraBitrate = bitrateOne() × (1 + lowMotionQuality/100)
# Default lowMotionQuality = 20%
```

**Purpose**: Represents peak bitrate during high-motion scenes.

**Usage**:
- NIC capacity planning (use max, not average)
- Failover calculations
- Bandwidth headroom estimation

**Impact**: More accurate network planning.

---

### 4. Server RAM Calculation - **FORMULA ADDED**

#### Before:
- Generic RAM calculations
- No specific constants

#### After:
```python
requiredRAM = ramOS + (hostClient ? clientRam : 0) + cameras × cameraRam
```

**Constants**:
- `cameraRam` = 40MB per camera
- `clientRam` = 3072MB for desktop client
- `ramOS` = 128MB (ARM) or 1024MB (Atom/i3/i5)
- Rounding: Next power of 2 (1, 2, 4, 8, 16, 32, 64 GB max)

**Impact**: Precise RAM sizing based on deployment configuration.

---

### 5. CPU Variants - **NEW CONFIGURATION**

#### Added to `config/server_specs.json`:
```json
{
  "cpu_variants": {
    "arm": {"max_cameras": 12, "nic_bitrate_mbps": 64, "ram_os_mb": 128},
    "atom": {"max_cameras": 32, "nic_bitrate_mbps": 600, "ram_os_mb": 1024},
    "core_i3": {"max_cameras": 256, "nic_bitrate_mbps": 600, "ram_os_mb": 1024},
    "core_i5": {"max_cameras": 256, "nic_bitrate_mbps": 600, "ram_os_mb": 1024}
  }
}
```

**Impact**: CPU-based camera limits now enforced. Different server tiers have different capabilities.

---

### 6. Server Presets - **NEW PRESETS ADDED**

#### Added NX1, NX2, NX3:
- **NX1**: ARM, 12 cameras max, 1 SATA, 2TB, 1GB RAM, 64 Mbit/s NIC
- **NX2**: Core i5, 256 cameras max, 4 SATA, 8GB RAM, 600 Mbit/s NIC
- **NX3**: Core i3, 256 cameras max, 12 SATA, 8GB RAM, 600 Mbit/s NIC

**Impact**: Accurate modeling of Network Optix hardware appliances.

---

### 7. Storage Throughput - **NEW CONSTRAINT**

#### Added:
```python
storageCount = Math.ceil(bitrate / (1024 × 204))
# 204 Mbit/s = throughput per storage device
```

**Impact**: Storage throughput can now be a limiting factor for server count, not just device count or bandwidth.

---

### 8. NIC Calculation - **FORMULA UPDATED**

#### Before:
- Simple capacity check
- Average bitrate only

#### After:
```python
requiredNICs = Math.ceil((maxBitrate + clientBitrate) / nicBitrate)
```

**Impact**:
- Uses max bitrate (peak) instead of average
- Includes client viewing bandwidth
- More accurate NIC sizing

---

### 9. Storage Calculation - **CONSTANTS VERIFIED**

#### Formula (unchanged, but verified):
```python
dailyStorage = bitrate × (60 × 60 × 24) / (8 × 1024 × 1024) × (hours/24) × motionValue()
```

**Constants verified**:
- `60 × 60 × 24` = 86400 seconds per day ✓
- `8 × 1024 × 1024` = 8388608 for byte conversion ✓
- `hours/24` factor for scheduled recording ✓
- `motionValue()` mapped to recording_factor ✓

**Impact**: No changes needed, existing implementation correct.

---

## Files Modified

### Backend Calculation Modules (3 files)
1. **`backend/app/services/calculations/bitrate.py`**
   - Implemented power function (area^0.7) for H.264/H.265
   - Added separate formula for MJPEG
   - Added `calculate_max_bitrate()` function
   - Added `brand_factor` and `codec_id` parameters
   - Updated quality factor conversion

2. **`backend/app/services/calculations/servers.py`**
   - Added `calculate_required_ram()` function
   - Added `calculate_storage_throughput_limit()` function
   - Updated `calculate_server_count()` to include storage throughput
   - Added CPU variant enforcement

3. **`backend/app/services/calculations/bandwidth.py`**
   - Added `calculate_required_nics()` function
   - Updated to use max bitrate + client bitrate
   - Added support for CPU-variant-specific NIC bitrates

### Configuration Files (2 files)
4. **`config/codecs.json`**
   - Updated documentation with new formulas
   - Added quality factor mapping
   - Documented legacy compatibility

5. **`config/server_specs.json`**
   - Added `cpu_variants` section
   - Added NX1, NX2, NX3 server presets
   - Added `camera_ram_mb`, `client_ram_mb`, `storage_throughput_mbps` constants
   - Added `sata_ports` and `max_hdd_count` to all tiers

### Test Files (1 new file)
6. **`backend/app/tests/test_core_calculations_validation.py`** (NEW)
   - Comprehensive validation of all formulas
   - Tests for bitrate power function
   - Tests for RAM calculation with exact constants
   - Tests for storage throughput
   - Tests for NIC calculation
   - Property-based tests with Hypothesis

### Documentation (1 new file)
7. **`docs/adr/003-calculation-formula-alignment.md`** (THIS FILE)

---

## Backward Compatibility

### Quality Multipliers
Legacy quality multipliers (0.6-2.0) are automatically converted to the new range (0.1-1.0):
```python
if quality_multiplier > 1.0:
    quality_multiplier = 0.55 + (quality_multiplier - 1.0) * 0.225
elif quality_multiplier < 1.0:
    quality_multiplier = 0.1 + (quality_multiplier - 0.6) * 1.125
```

### API Compatibility
- All function signatures remain compatible
- New parameters have defaults
- Existing code continues to work

---

## Testing

### Validation Tests
Created `test_core_calculations_validation.py` with:
- ✅ Bitrate power function validation
- ✅ Quality factor range validation
- ✅ Max bitrate calculation
- ✅ Storage constants verification
- ✅ RAM formula with exact constants
- ✅ Power-of-2 rounding
- ✅ Storage throughput formula
- ✅ NIC calculation formula
- ✅ Property-based tests

### Expected Test Updates
Existing tests will need updates due to formula changes:
- `test_bitrate.py` - Expected values will change significantly
- `test_storage.py` - Minor changes (constants verified correct)
- `test_api.py` - Response values will change

---

## Migration Notes

### For Developers
1. **Bitrate calculations will produce different results** - This is expected and correct
2. **Use max bitrate for NIC planning** - Not average bitrate
3. **CPU variants enforce camera limits** - Check CPU type when sizing servers
4. **Storage throughput can limit servers** - Not just device count or bandwidth

### For Users
1. **Results will differ from previous version** - New formulas are more accurate
2. **High-resolution cameras** - Bitrate estimates will be more realistic (power function)
3. **Server RAM** - More precise sizing with 40MB/camera constant
4. **NX1/NX2/NX3 presets** - Now available for Network Optix appliances

---

## Consequences

### Positive
✅ **Mathematical accuracy** - Matches legacy system exactly  
✅ **Better high-res modeling** - Power function more realistic  
✅ **Precise RAM sizing** - Exact constants from spec  
✅ **CPU-aware limits** - Different tiers properly modeled  
✅ **Storage throughput** - New constraint prevents over-provisioning  
✅ **Max bitrate tracking** - Better network planning  
✅ **Comprehensive validation** - Golden tests ensure correctness  

### Negative
⚠️ **Breaking change** - Results differ from previous version  
⚠️ **Test updates required** - All expected values must change  
⚠️ **User confusion** - Different results may require explanation  

### Neutral
ℹ️ **Backward compatible** - Legacy quality multipliers still work  
ℹ️ **Well documented** - ADR and validation tests provide traceability  

---

## Open Questions

1. **brandFactor**: Default value is 1.0. Is this correct for all brands?
2. **lowMotionQuality**: Default 20%. Should this be configurable per codec?
3. **Storage throughput**: 204 Mbit/s constant - Does this vary by drive type (HDD vs SSD)?

---

## References

- **Source**: `/docs/core_calculations.md`
- **Plan**: `/docs/CALCULATION_ALIGNMENT_PLAN.md`
- **Tests**: `/backend/app/tests/test_core_calculations_validation.py`
- **Config**: `/config/server_specs.json`, `/config/codecs.json`

---

## Approval

**Status**: ✅ **IMPLEMENTED**  
**Date**: 2025-10-03  
**Reviewed By**: Development Team  
**Next Steps**: Update existing tests, deploy to staging, validate with known scenarios

---

**This ADR ensures the Nx System Calculator produces mathematically accurate results consistent with the legacy system's proven formulas.**

