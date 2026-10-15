# ADR-002: FHIR Terminology Integration

## Status
Accepted

## Context
The intake application currently uses hard-coded values for dropdowns (gender, language, appointment types/statuses). This creates maintenance overhead, limits extensibility, and doesn't align with FHIR standards for terminology management. We have access to FHIR terminology services through Aidbox that provide standardized ValueSets.

## Decision
We will integrate FHIR terminology services using ValueSet operations to replace all hard-coded dropdown values with dynamic, standards-compliant terminology.

## Rationale

### Standards Compliance
- **FHIR ValueSets**: Use official HL7 FHIR ValueSets (administrative-gender, languages, appointmentstatus)
- **Terminology operations**: Leverage `ValueSet/$expand` for dynamic dropdown population
- **Consistent coding**: Ensure generated FHIR resources use proper codes and systems

### Developer Experience & Maintainability
- **Generic approach**: Single `useValueSet()` hook handles all terminology needs
- **Convenience hooks**: Named hooks (`useAdministrativeGender()`) for common ValueSets
- **Type safety**: Operation return types inferred from operation names
- **Extensibility**: Adding new terminology requires only one line of code

### User Experience
- **Dynamic content**: Dropdowns reflect current terminology without code updates
- **Searchable dropdowns**: Large ValueSets (languages) support filtering via `filter` parameter
- **Proper error handling**: Clear error messages when terminology services unavailable
- **Loading states**: Responsive UI during terminology fetches

### Architecture Benefits
- **Separation of concerns**: Terminology logic separated from UI components
- **Caching strategy**: React Query provides intelligent caching (24hr stale time)
- **Future-proof**: New ValueSets automatically supported without code changes

## Implementation Details

### Operation Type Mapping
```typescript
export type OperationResultMap = {
  'ValueSet/$expand': ValueSet;
  'ValueSet/$validate-code': Parameters;
  'CodeSystem/$lookup': Parameters;
  // Extensible for future operations
}

export type OperationName = keyof OperationResultMap;
```

### Generic Aidbox Operations
```typescript
async op<T extends OperationName>(
  operation: T,
  params: Record<string, any> | Parameters
): Promise<OperationResultMap[T]>
```

### Terminology Hook Pattern
```typescript
// Generic hook (internal)
function useValueSet(url: string, options?: { count?: number; filter?: string })

// Convenience hooks (public API)
export const useAdministrativeGender = () => 
  useValueSet('http://hl7.org/fhir/ValueSet/administrative-gender');

export const useLanguages = (filter?: string) => 
  useValueSet('http://hl7.org/fhir/ValueSet/languages', { 
    count: 20, 
    ...(filter && { filter }) 
  });
```

### Component Integration
```typescript
export default function PatientForm() {
  const { data: genderOptions = [], isLoading, error } = useAdministrativeGender();
  
  if (error) return <div className="error">Error loading terminology: {error.message}</div>;
  
  return (
    <select disabled={isLoading}>
      {isLoading ? (
        <option>Loading...</option>
      ) : (
        genderOptions.map(option => (
          <option key={option.code} value={option.code}>
            {option.display}
          </option>
        ))
      )}
    </select>
  );
}
```

## Migration Strategy

### Phase 1: Foundation
1. Extend Aidbox service with operation support
2. Create terminology hooks infrastructure
3. Add operation type mappings

### Phase 2: Component Migration (Incremental)
1. PatientForm.tsx (gender, language dropdowns)
2. AppointmentForm.tsx (appointment types, statuses)  
3. PatientIntake.tsx (gender dropdown)
4. Display logic updates

### Phase 3: Enhancement
1. Add search/filtering for large ValueSets
2. Implement additional ValueSets as needed
3. Error boundary improvements

## Error Handling Philosophy
- **Fail gracefully**: Show clear error messages, don't break forms
- **User-friendly**: Explain terminology service unavailability
- **Retry mechanisms**: Allow users to retry failed terminology loads
- **Development parity**: Same error handling in dev and production

## Performance Considerations
- **Long cache times**: 24-hour stale time for terminology (rarely changes)
- **Selective loading**: Only fetch terminology when components mount
- **Filter-based search**: Use server-side filtering for large ValueSets
- **Background refetch**: Update terminology in background without UX interruption

## Testing Strategy
- **Real services**: Test against actual Aidbox terminology services
- **Error scenarios**: Test network failures, invalid ValueSets
- **FHIR compliance**: Validate that generated resources use proper codes
- **Performance**: Ensure terminology loading doesn't block critical UI

## Future Considerations
- **Custom ValueSets**: Framework supports organization-specific terminology
- **Multilingual support**: ValueSet expansions can include language-specific displays
- **Terminology validation**: Add `ValueSet/$validate-code` for form validation
- **Offline support**: Consider local terminology caching for offline scenarios

## References
- [FHIR R4 Terminology Module](https://hl7.org/fhir/R4/terminology-module.html)
- [ValueSet $expand Operation](https://hl7.org/fhir/R4/valueset-operation-expand.html)
- [FHIR Administrative Gender ValueSet](http://hl7.org/fhir/ValueSet/administrative-gender)
- [Aidbox Terminology Services](https://docs.aidbox.app/terminology)