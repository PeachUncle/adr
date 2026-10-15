# ADR-0002: RAG vs. Context-Only Approach für Code-Generierung

## Status
🤔 **PROPOSED** - 2025-09-09

## Context
Für die AI-basierte Code-Generierung stehen zwei Hauptansätze zur Verfügung:

1. **Context-Only**: Nur PR-Metadaten (Titel, Beschreibung, veränderte Dateien) an LLM senden
2. **RAG (Retrieval-Augmented Generation)**: Zusätzlich relevante Code-Snippets, Dokumentation und Patterns einbeziehen

## Decision Options

### **Option A: Context-Only (MVP Approach)**
```typescript
interface PatchGenerationInput {
  intent: string;
  prMetadata: {
    title: string;
    description: string;
    files: string[];
    // Kein actual file content
  };
}
```

**✅ Pros:**
- Einfache Implementierung
- Niedrige Latenz (< 2s)
- Minimale Infrastruktur
- Privacy-friendly (kein Code-Content übertragen)
- Geringere LLM Token Costs

**❌ Cons:**
- Begrenzte Code-Qualität
- Keine projektspezifischen Patterns
- Generische Lösungen ohne Kontext

### **Option B: RAG-Enhanced (Future)**
```typescript
interface EnhancedPatchInput {
  intent: string;
  prMetadata: PrMetadata;
  relevantCode: RetrievedCodeSnippets;
  projectContext: {
    patterns: CodingPattern[];
    dependencies: string[];
    conventions: StyleGuide;
  };
}
```

**✅ Pros:**
- Höhere Code-Qualität
- Projektspezifische Patterns
- Konsistenz mit bestehendem Code
- Intelligentere Lösungsvorschläge

**❌ Cons:**
- Komplexe Infrastruktur (Vector DB, Embeddings)
- Höhere Latenz (5-10s)
- Privacy-Concerns (Code-Indexierung)
- Höhere Betriebskosten

## Current Decision: **Option A - Context-Only**

### **Rationale**
1. **MVP-Focus**: Schneller Proof-of-Concept für Business Value
2. **Privacy**: Kein Code-Content verlässt das System
3. **Simplicity**: Reduzierte Komplexität für ersten Rollout
4. **Performance**: Ziel P95 ≤ 15s ist mit Context-Only erreichbar

### **Implementation Strategy**
```typescript
// Phase 1: Context-Only
const simplePrompt = `
Intent: ${intent}
PR Context: ${prMeta.title} - ${prMeta.description}
Files: ${prMeta.files.join(', ')}
Generate unified diff patch.
`;

// Future Phase 2: RAG-Enhanced
const enhancedPrompt = `
${simplePrompt}
Relevant Code Patterns: ${retrievedPatterns}
Project Dependencies: ${projectDeps}
Style Guidelines: ${styleGuide}
`;
```

## Migration Path to RAG

### **Phase 2 Requirements** (6+ Monate)
1. **Vector Database**: Pinecone oder Azure Cognitive Search
2. **Code Indexing Pipeline**: Automated embedding generation
3. **Retrieval Logic**: Semantic search für relevante Code-Snippets
4. **Privacy Controls**: Opt-in für Code-Indexierung pro Repository

### **Success Metrics for Migration Decision**
- Context-Only Quality Score < 80% für komplexe Intents
- Developer Request für projektspezifische Patterns > 20/Monat
- Verfügbare Engineering Capacity für RAG Infrastruktur

## Consequences

### **Short-term (MVP)**
- ✅ Schnelle Time-to-Market
- ✅ Einfache Wartung und Deployment
- ⚠️ Begrenzte Code-Qualität für komplexe Projekte

### **Long-term (RAG Migration)**
- 🔄 Infrastruktur-Investment erforderlich
- ✅ Deutlich bessere Code-Qualität erwartet
- ⚠️ Privacy-Governance Framework erforderlich

## Review Criteria
**Next Review**: Nach 3 Monaten MVP-Betrieb
**Trigger**: Wenn Context-Only Success Rate < 85% oder Developer Feedback Score < 3.5/5

## Related ADRs
- ADR-0001: LLM Gateway Provider-Agnostisch
- ADR-0003: Local vs. Cloud LLM Default Strategy

## References
- [RAG Architecture Options](../c4/workspace.dsl)
- [Privacy Requirements](../security/privacy-framework.md)
- Performance Benchmarks: Not yet implemented (placeholder for future evaluation framework)
