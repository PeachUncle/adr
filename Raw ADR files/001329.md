# ADR-010: PropertyLoader Pattern

**Status:** Accepted
**Date:** 2024-11
**Updated:** 2025-11-11
**Deciders:** Development Team
**Related Issues:** #1, #2, #10, #22
**Related Views:** `view-logical.md`, `view-data.md`

---

## Context

Camera properties must be:
1. Validated before sending to Sony SDK (prevent SDK errors)
2. Mapped between SDK values and display values
3. Synchronized between Air-Side and Ground-Side
4. Extensible (easy to add new properties)

This is the implementation pattern for ADR-002 (Specification-First).

---

## Decision

**PropertyLoader Pattern:** Single class loading and managing property specifications

**Core Concept:** Load JSON specs once at startup, provide validation/mapping services

**Key Methods:**
- `loadSpecs()` - Load JSON from file/assets
- `isValidValue(property, value)` - Validate against specs
- `sdkToDisplay(property, sdk_value)` - Map SDK → UI
- `displayToSdk(property, display_value)` - Map UI → SDK
- `getValidValues(property)` - Get all valid values (for dropdowns)

---

## Implementation

### Air-Side (C++)

```cpp
class PropertyLoader {
private:
    std::map<std::string, PropertySpec> specs_;

public:
    void loadSpecs(const std::string& spec_dir) {
        // Load all JSON files from spec_dir
        for (auto& file : fs::directory_iterator(spec_dir)) {
            auto spec = parseJsonSpec(file.path());
            specs_[spec.property_name] = spec;
        }
    }

    bool isValidValue(const std::string& property, const std::string& value) const {
        auto it = specs_.find(property);
        if (it == specs_.end()) return false;

        const auto& valid_values = it->second.values;
        return std::find_if(valid_values.begin(), valid_values.end(),
            [&](const PropertyValue& pv) {
                return pv.display_value == value;
            }) != valid_values.end();
    }

    std::string displayToSdk(const std::string& property, const std::string& display) const {
        // Map "1/250" → "0x00010014"
        auto it = specs_.find(property);
        for (const auto& pv : it->second.values) {
            if (pv.display_value == display) {
                return pv.sdk_value;
            }
        }
        throw std::runtime_error("Invalid value");
    }
};
```

### Ground-Side (Kotlin)

```kotlin
class PropertyLoader(private val context: Context) {
    private val specs = mutableMapOf<String, PropertySpec>()

    fun loadSpecs() {
        val assetManager = context.assets
        assetManager.list("specs")?.forEach { filename ->
            val json = assetManager.open("specs/$filename").bufferedReader().use { it.readText() }
            val spec = Json.decodeFromString<PropertySpec>(json)
            specs[spec.propertyName] = spec
        }
    }

    fun isValidValue(property: String, value: String): Boolean {
        val spec = specs[property] ?: return false
        return spec.values.any { it.displayValue == value }
    }

    fun getValidValues(property: String): List<String> {
        return specs[property]?.values
            ?.sortedBy { it.sortOrder }
            ?.map { it.displayValue }
            ?: emptyList()
    }
}
```

---

## Pattern Benefits

✅ **Single Responsibility:** PropertyLoader only manages specs (not camera control)
✅ **Testable:** Easy to unit test with mock JSON
✅ **Reusable:** Same pattern in C++ and Kotlin
✅ **Cacheable:** Load once, query many times (fast)

---

## Usage Examples

### Validate Command (Air-Side)

```cpp
void CommandHandler::handleSetProperty(const Command& cmd) {
    auto property = cmd.payload["property"];
    auto value = cmd.payload["value"];

    if (!propertyLoader.isValidValue(property, value)) {
        return sendError("INVALID_PROPERTY_VALUE");
    }

    auto sdk_value = propertyLoader.displayToSdk(property, value);
    camera->setProperty(property, sdk_value);
}
```

### Populate Dropdown (Ground-Side)

```kotlin
@Composable
fun IsoSelector(viewModel: CameraViewModel) {
    val validValues = propertyLoader.getValidValues("iso")

    DropdownMenu(
        items = validValues,
        onSelect = { viewModel.setIso(it) }
    )
}
```

---

## Alternatives Considered

### Alternative 1: Hardcoded Maps

**Rejection:** See ADR-002 (sync issues, not extensible)

### Alternative 2: Runtime Property Discovery

**Rejection:** See ADR-002 (network dependency, latency)

### Alternative 3: Code Generation

**Rejection:** See ADR-002 (build complexity)

---

## Related Decisions

- **ADR-002:** Specification-First Property Management (this is the implementation)
- **ADR-011:** JSON Protocol (same JSON format for specs and messages)

---

## References

- Logical View: `view-logical.md` (PropertyLoader in both Air and Ground components)
- Data View: `view-data.md` (Property specification sync)
- LESSONS_LEARNED.md: Issue #22 (manual focus commands failed due to missing PropertyLoader validation)
