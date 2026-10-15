# Dynamic Schema Handling in OpenAPI Kotlin Code Generator

**Status**: Proposed  
**Date**: 2025-01-17  
**Author**: OpenAPI Kotlin Team  

## Problem Statement

The OpenAPI Kotlin code generator currently maps schemas without explicit type definitions to `Any`, which causes runtime serialization errors when using kotlinx.serialization. This issue manifests in real-world APIs like Ory's, where schemas such as `identityTraits` are intentionally left untyped to allow dynamic JSON structures.

### Current Behavior

When the type mapper encounters a schema without a type definition:
```yaml
identityTraits:
  description: "Traits represent an identity's traits..."
  # No type specified - allows any JSON structure
```

It generates:
```kotlin
public typealias identityTraits = Any
```

**This approach is fundamentally flawed** because:
1. The generated code compiles successfully, giving a false sense of correctness
2. At runtime, it fails with: `Serializer has not been found for type 'Any'`
3. Users cannot use the generated API client without manual modifications
4. There is no workaround - the code simply doesn't work

### The Runtime Failure

```kotlin
// Generated code
data class Identity(
    val traits: identityTraits  // typealias for Any
)

// User code - this will fail
val identity = client.getIdentity(id)  // RuntimeException: Serializer has not been found for type 'Any'
```

## Root Cause Analysis

### Why Schemas Are Untyped

1. **Dynamic Data**: Some APIs need to accept arbitrary JSON structures
2. **Schema Flexibility**: The data structure varies based on configuration
3. **Extensibility**: APIs designed to be extended without schema changes
4. **JSON Schema References**: Some schemas reference external JSON schemas dynamically

### Technical Limitations

1. **Type Erasure**: JVM erases generic type information at runtime
2. **kotlinx.serialization**: Requires compile-time type information for serialization
3. **Ktor Integration**: The `body<T>()` function needs serializable types
4. **Any is not serializable**: kotlinx.serialization cannot handle `Any` type without explicit serializers

## Type Hierarchy for Dynamic Data

In kotlinx.serialization.json, there's a clear hierarchy for handling dynamic JSON:

- **`JsonElement`**: Abstract base class that can represent any JSON value
  - `JsonPrimitive`: String, Number, Boolean, Null
  - `JsonObject`: JSON objects (key-value pairs)
  - `JsonArray`: JSON arrays
  
**Key Principle**: Use `JsonElement` as the primary type for dynamic schemas, and use `JsonObject` when we can infer the schema represents an object.

## Proposed Solutions

### Solution 1: Configuration Flag (Simple)

Add a boolean flag to use `JsonElement` for untyped schemas:

```kotlin
data class ModelsConfig(
    // ... existing fields ...
    var useJsonElementForDynamicTypes: Boolean = false
)
```

**Pros:**
- Simple to implement
- Easy to understand
- Backward compatible

**Cons:**
- All-or-nothing approach
- No fine-grained control

### Solution 2: Type Mapping Configuration (Flexible)

Allow explicit type mappings for specific schemas:

```kotlin
data class ModelsConfig(
    // ... existing fields ...
    var schemaTypeOverrides: Map<String, String> = emptyMap()
)
```

Usage:
```kotlin
models {
    schemaTypeOverrides = mapOf(
        "identityTraits" to "kotlinx.serialization.json.JsonElement",
        "DefaultError" to "kotlinx.serialization.json.JsonObject"
    )
}
```

**Pros:**
- Fine-grained control
- Schema-specific handling
- Type-safe

**Cons:**
- Requires manual configuration
- Users need to know schema names

### Solution 3: Strategy Pattern (Extensible)

Define strategies for handling untyped schemas:

```kotlin
enum class UntypedSchemaStrategy {
    USE_ANY,           // Current behavior
    USE_JSON_ELEMENT,  // Use JsonElement
    USE_JSON_OBJECT,   // Use JsonObject for objects
    INFER_FROM_USAGE  // Analyze usage patterns
}

data class ModelsConfig(
    var untypedSchemaStrategy: UntypedSchemaStrategy = UntypedSchemaStrategy.USE_ANY
)
```

**Pros:**
- Clean API
- Extensible for future strategies
- Semantic clarity

**Cons:**
- Still somewhat inflexible
- May not cover all use cases

### Solution 4: Custom Type Mapper (Maximum Flexibility)

Allow users to provide custom type mapping logic:

```kotlin
interface TypeMappingCustomizer {
    fun mapType(schema: Schema, defaultType: KotlinType): KotlinType?
}

data class ModelsConfig(
    var typeMappingCustomizer: TypeMappingCustomizer? = null
)
```

**Pros:**
- Ultimate flexibility
- Supports complex logic
- Future-proof

**Cons:**
- Complex to implement
- Harder to use
- Potential for user errors

## Recommended Approach: Hybrid Solution

Combine the best aspects of multiple solutions with smart defaults:

```kotlin
data class ModelsConfig(
    // Simple flag for common case
    var useJsonElementForDynamicTypes: Boolean = false,
    
    // What to do when flag is false and dynamic types are found
    var dynamicTypeHandling: DynamicTypeHandling = DynamicTypeHandling.WARN,
    
    // Fine-grained overrides
    var schemaTypeOverrides: Map<String, String> = emptyMap()
)

enum class DynamicTypeHandling {
    ALLOW,  // Generate Any (current behavior - will fail at runtime)
    WARN,   // Generate Any with warning about runtime failure
    FAIL    // Fail generation with helpful error message
}
```

### Smart Type Inference

When `useJsonElementForDynamicTypes = true`, the generator should intelligently choose between `JsonElement` and `JsonObject`:

```kotlin
private fun inferDynamicType(schema: Schema): KotlinType {
    return when {
        // If we can infer it's an object
        schema.type == SchemaType.OBJECT || 
        schema.properties != null || 
        schema.additionalProperties != null -> KotlinType.JsonObject
        
        // If we can infer it's an array
        schema.type == SchemaType.ARRAY || 
        schema.items != null -> KotlinType.JsonArray
        
        // Default to most general type
        else -> KotlinType.JsonElement
    }
}
```

### Implementation Details

1. **Type Mapper Updates**:
```kotlin
class KotlinPoetTypeMapper(
    val basePackage: String,
    val config: ModelsConfig = ModelsConfig()
) : TypeMappingService {
    
    override fun mapType(schema: Schema, nullable: Boolean): KotlinType {
        // Check for explicit overrides first
        schema.name?.let { name ->
            config.schemaTypeOverrides[name]?.let { override ->
                return parseTypeOverride(override, nullable)
            }
        }
        
        // Handle untyped schemas
        if (schema.type == null && !schema.isReference()) {
            if (config.useJsonElementForDynamicTypes) {
                // Use smart type inference
                return inferDynamicType(schema).nullable(nullable)
            } else {
                // Handle based on configured strategy
                when (config.dynamicTypeHandling) {
                    ALLOW -> return KotlinType.Any.nullable(nullable)
                    
                    WARN -> {
                        logger.warn("""
                            Schema '${schema.name}' has no type definition and will be mapped to 'Any'.
                            This will fail at runtime with: "Serializer has not been found for type 'Any'"
                            
                            To fix this, either:
                            1. Set useJsonElementForDynamicTypes = true
                            2. Add a type override: schemaTypeOverrides["${schema.name}"] = "JsonElement"
                            3. Fix the OpenAPI specification to include a type
                        """.trimIndent())
                        return KotlinType.Any.nullable(nullable)
                    }
                    
                    FAIL -> throw IllegalStateException("""
                        Schema '${schema.name}' has no type definition.
                        
                        The generated code would fail at runtime with: "Serializer has not been found for type 'Any'"
                        
                        To fix this, either:
                        1. Set useJsonElementForDynamicTypes = true
                        2. Add a type override: schemaTypeOverrides["${schema.name}"] = "JsonElement"
                        3. Fix the OpenAPI specification to include a type
                    """.trimIndent())
                }
            }
        }
        
        // Continue with normal type mapping...
    }
}
```

2. **Type Override Parsing**:
```kotlin
private fun parseTypeOverride(override: String, nullable: Boolean): KotlinType {
    return when (override) {
        "JsonElement" -> KotlinType.JsonElement
        "JsonObject" -> KotlinType.JsonObject
        "JsonArray" -> KotlinType.JsonArray
        "Map<String, JsonElement>" -> KotlinType.Map(KotlinType.String, KotlinType.JsonElement)
        else -> {
            // Parse custom type strings
            val parts = override.split(".")
            if (parts.size >= 2) {
                val packageName = parts.dropLast(1).joinToString(".")
                val simpleName = parts.last()
                KotlinType(simpleName, packageName)
            } else {
                KotlinType(override)
            }
        }
    }.nullable(nullable)
}
```

## Usage Examples

### Example 1: Current Behavior (Runtime Failure)

```kotlin
// build.gradle.kts - Default configuration
openApi {
    inputSpec = file("openapi/ory.json")
    packageName = "com.example.api"
    
    models {
        // useJsonElementForDynamicTypes = false (default)
        // dynamicTypeHandling = WARN (default)
    }
}

// Generated code
public typealias identityTraits = Any  // This will fail at runtime!

// User code
val identity = client.getIdentity(id)  // 💥 RuntimeException: Serializer has not been found for type 'Any'
```

### Example 2: Safe Dynamic Type Handling

```kotlin
// build.gradle.kts
openApi {
    inputSpec = file("openapi/ory.json")
    packageName = "com.example.api"
    
    models {
        // Enable JsonElement for all untyped schemas
        useJsonElementForDynamicTypes = true
    }
}

// Generated code
public typealias identityTraits = JsonElement  // Works at runtime!

// User code
val identity = client.getIdentity(id)  // ✅ Works
val traits = identity.traits
when (traits) {
    is JsonObject -> {
        val email = traits["email"]?.jsonPrimitive?.content
    }
    is JsonArray -> {
        // Handle array case
    }
    is JsonPrimitive -> {
        // Handle primitive case
    }
}
```

### Example 3: Specific Schema Overrides

```kotlin
// build.gradle.kts
openApi {
    inputSpec = file("openapi/api.yaml")
    packageName = "com.example.api"
    
    models {
        schemaTypeOverrides = mapOf(
            // Use JsonElement for truly dynamic data
            "identityTraits" to "JsonElement",
            
            // Use JsonObject when we know it's an object
            "metadata" to "JsonObject",
            
            // Use custom type for specific needs
            "customData" to "com.example.CustomData"
        )
    }
}
```

### Example 4: Fail-Fast Configuration

```kotlin
// build.gradle.kts
openApi {
    inputSpec = file("openapi/strict.yaml")
    packageName = "com.example.api"
    
    models {
        // Fail if untyped schemas are found
        dynamicTypeHandling = DynamicTypeHandling.FAIL
    }
}

// This will fail at generation time with a helpful error:
// Schema 'identityTraits' has no type definition.
// The generated code would fail at runtime with: "Serializer has not been found for type 'Any'"
// To fix this, either:
// 1. Set useJsonElementForDynamicTypes = true
// 2. Add a type override: schemaTypeOverrides["identityTraits"] = "JsonElement"
// 3. Fix the OpenAPI specification to include a type
```

### Example 5: Smart Type Inference

```kotlin
// OpenAPI schemas
schemas:
  DynamicObject:
    # No type, but has properties - inferred as JsonObject
    properties:
      id: { type: string }
    additionalProperties: true
    
  DynamicArray:
    # No type, but has items - inferred as JsonArray
    items: { type: string }
    
  TrulyDynamic:
    # No hints - inferred as JsonElement
    description: "Can be any JSON value"

// Generated code with useJsonElementForDynamicTypes = true
public typealias DynamicObject = JsonObject  // Smart inference
public typealias DynamicArray = JsonArray    // Smart inference  
public typealias TrulyDynamic = JsonElement  // Safe default
```

## Migration Strategy

### Phase 1: Add Configuration (Backward Compatible)
1. Add new configuration options with defaults preserving current behavior
2. Update type mapper to respect configuration
3. Add comprehensive tests

### Phase 2: Documentation and Examples
1. Update README with configuration examples
2. Add migration guide for existing users
3. Create example projects demonstrating usage

### Phase 3: Smart Defaults (Breaking Change)
1. Change default to `useJsonElementForDynamicTypes = true`
2. Provide clear upgrade path
3. Major version bump

## Testing Strategy

### Unit Tests
```kotlin
@Test
fun `untyped schema maps to Any by default with warning`() {
    val mapper = KotlinPoetTypeMapper("com.example")
    val schema = Schema(type = null, name = "TestSchema")
    
    // Should log warning
    assertEquals(KotlinType.Any, mapper.mapType(schema, false))
    // Verify warning was logged
}

@Test
fun `untyped schema fails when configured to fail`() {
    val config = ModelsConfig(
        dynamicTypeHandling = DynamicTypeHandling.FAIL
    )
    val mapper = KotlinPoetTypeMapper("com.example", config)
    val schema = Schema(type = null, name = "TestSchema")
    
    assertThrows<IllegalStateException> {
        mapper.mapType(schema, false)
    }
}

@Test
fun `smart type inference for object-like schemas`() {
    val config = ModelsConfig(useJsonElementForDynamicTypes = true)
    val mapper = KotlinPoetTypeMapper("com.example", config)
    
    // Schema with properties should infer JsonObject
    val objectSchema = Schema(type = null, properties = mapOf("id" to Schema()))
    assertEquals(KotlinType.JsonObject, mapper.mapType(objectSchema, false))
    
    // Schema with items should infer JsonArray
    val arraySchema = Schema(type = null, items = Schema())
    assertEquals(KotlinType.JsonArray, mapper.mapType(arraySchema, false))
    
    // Schema with no hints should use JsonElement
    val dynamicSchema = Schema(type = null)
    assertEquals(KotlinType.JsonElement, mapper.mapType(dynamicSchema, false))
}

@Test
fun `schema type override takes precedence`() {
    val config = ModelsConfig(
        schemaTypeOverrides = mapOf("Custom" to "JsonObject")
    )
    val mapper = KotlinPoetTypeMapper("com.example", config)
    val schema = Schema(name = "Custom", type = null)
    assertEquals(KotlinType.JsonObject, mapper.mapType(schema, false))
}
```

### Integration Tests
- Test with Ory API specification
- Test with Petstore API
- Test custom configurations
- Test serialization/deserialization

## Benefits

1. **Flexibility**: Users can choose the appropriate strategy
2. **Backward Compatibility**: Default behavior unchanged
3. **Real-World Support**: Handles APIs like Ory correctly
4. **Future-Proof**: Extensible for new requirements
5. **Type Safety**: Maintains compile-time type checking where possible

## Risks and Mitigations

### Risk 1: Complexity
**Mitigation**: Provide sensible defaults and clear documentation

### Risk 2: Performance
**Mitigation**: Type mapping happens at code generation time, no runtime impact

### Risk 3: User Confusion
**Mitigation**: Clear examples and migration guide

## References

- [kotlinx.serialization documentation](https://github.com/Kotlin/kotlinx.serialization/blob/master/docs/serializers.md)
- [OpenAPI Specification - Schema Object](https://spec.openapis.org/oas/v3.0.3#schema-object)
- [Ory API Schema Design](https://www.ory.sh/docs/kratos/concepts/identity-user-model)
- [Related Issue: Map Serialization](./map-serialization-issue.md)

## Decision

Implement the hybrid approach with:
1. **`useJsonElementForDynamicTypes`** flag for enabling safe dynamic type handling
2. **`dynamicTypeHandling`** enum (ALLOW/WARN/FAIL) for controlling behavior when flag is false
3. **`schemaTypeOverrides`** map for fine-grained control
4. **Smart type inference** to choose between JsonElement, JsonObject, and JsonArray

This approach:
- Maintains backward compatibility (default still generates Any with warning)
- Provides clear migration path (enable flag or add overrides)
- Prevents silent runtime failures (warnings/errors at generation time)
- Uses the most appropriate type based on schema hints

## Summary

The current behavior of mapping untyped schemas to `Any` is problematic because it creates code that compiles but fails at runtime. The proposed solution uses kotlinx.serialization's `JsonElement` hierarchy to properly handle dynamic JSON data, with smart inference to use more specific types when possible. Users can opt-in to the safe behavior while maintaining full control over type mapping.