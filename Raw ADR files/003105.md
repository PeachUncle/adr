# ADR-006: PAT-006 Mandatory API Verification Protocol

**Status**: 🔴 MANDATORY
**Date**: 2025-11-04
**Deciders**: ECO (Based on SOLARIA Methodology)
**Related**: METODOLOGIA SOLARIA, BRIK-64 Project Learnings

---

## Context and Problem Statement

En proyecto BRIK-64, **39 errores de compilación** fueron causados por asumir APIs sin verificar (ANTI-004: Speculation-Driven Design). Esto resultó en 2+ horas perdidas y código no funcional.

**Pregunta**: ¿Cómo evitar errores de especulación al integrar WordPress REST API en Fase 3?

---

## Decision

**PAT-006 (API Verification Protocol) es MANDATORY antes de Fase 3**

Ningún código de integración frontend se escribirá hasta que:
1. Todas las APIs WordPress REST estén inventariadas
2. Endpoints verificados con Postman
3. Responses documentadas en `docs/api-inventories/`
4. Tipos TypeScript creados basados en responses reales

---

## Rationale

### Evidencia Empírica (BRIK-64 Project)

**Sin PAT-006 (Phase 7.1)**:
```
- Errores de compilación: 39
- Tiempo perdido: 2+ horas
- Código funcional: NO
- Root cause: Asumir Parser::new() existía (no existía)
```

**Con PAT-006 (Phase 7.2)**:
```
- Errores de compilación: 0
- Tiempo invertido PAT-006: 30 min
- Código funcional: SÍ (al primer intento)
- ROI: 2+ horas ahorradas vs 30 min invertidos = 400% ROI
```

### Aplicación a PRILABSA Project

**Riesgo Sin PAT-006**:
- Asumir que `/wp-json/wp/v2/productos` expone ACF fields (puede no ser automático)
- Especular estructura response JSON (puede diferir de esperado)
- Crear tipos TypeScript incorrectos
- Resultado: Errores en runtime, rework, frustración

**Mitigación Con PAT-006**:
- Leer documentación WordPress REST API oficial
- Instalar ACF to REST API plugin y verificar exposure
- Testear con Postman: `GET /wp-json/wp/v2/productos?_embed=true`
- Documentar response real en API inventory
- Crear tipos TypeScript basados en data real
- Resultado: 0 errores, código funcional al primer intento

---

## Protocol Steps

### 1. API Inventory (20 min)
```bash
# Documentar todos los endpoints disponibles
curl http://localhost/wp-json/wp/v2/ | jq .

# Listar rutas de productos
curl http://localhost/wp-json/wp/v2/productos

# Verificar ACF fields expuestos
curl http://localhost/wp-json/wp/v2/productos/1
```

Documentar en `docs/api-inventories/wordpress-rest-api-inventory.md`:
- Endpoints disponibles
- Parámetros aceptados
- Structure de responses
- ACF fields incluidos o no

### 2. Postman Testing (10 min)
- Crear collection "PRILABSA WordPress API"
- Agregar requests:
  - GET /productos (lista)
  - GET /productos/:id (detalle)
  - GET /categorías_productos
  - GET /tags_productos
- Ejecutar y validar responses 200 OK
- Export collection a `testing/postman/`

### 3. Documentation (15 min)
Crear `docs/api-inventories/wordpress-rest-api-inventory.md` con:
```markdown
## Endpoint: GET /wp/v2/productos

**URL**: http://localhost/wp-json/wp/v2/productos
**Method**: GET
**Auth**: Ninguno (public endpoint)

**Query Params**:
- `per_page`: Number (default: 10, max: 100)
- `page`: Number (default: 1)
- `_embed`: Boolean (incluye media y terms)

**Response 200**:
\`\`\`json
{
  "id": 123,
  "title": {"rendered": "Combacid XL"},
  "acf": {
    "descripcion": "...",
    "fotos": [{"url": "..."}],
    "pdf": {"url": "..."}
  },
  "_embedded": {
    "wp:term": [[{name: "Aditivos", slug: "aditivos"}]]
  }
}
\`\`\`
```

### 4. TypeScript Types (10 min)
```typescript
// src/types/wordpress.ts
interface WordPressProduct {
  id: number;
  title: { rendered: string };
  acf: {
    descripcion: string;
    especificaciones: Array<{ key: string; value: string }>;
    // ... based on REAL API response
  };
  _embedded?: {
    'wp:term': Array<Array<{ name: string; slug: string }>>;
  };
}
```

### 5. Validation (5 min)
- Revisar con AGENT THETA: ¿API inventory completo?
- ECO verifica: ¿Todos endpoints necesarios documentados?
- Aprobar inicio Fase 3 solo si PAT-006 100% completo

**Total Time**: ~30 min
**ROI**: 2+ horas ahorradas

---

## Alternatives Considered

### Alternative 1: "YOLO - Asumir y arreglar después"
**Approach**: Implementar frontend asumiendo estructura API
**Rejected Because**:
- ❌ Evidencia empírica: 39 errores en BRIK-64
- ❌ 2+ horas perdidas
- ❌ Código no funcional
- ❌ Frustración equipo
- ❌ Viola metodología SOLARIA

### Alternative 2: "Partial verification"
**Approach**: Verificar solo algunos endpoints
**Rejected Because**:
- ❌ Inconsistente (puede faltar endpoints críticos)
- ❌ No garantiza 0 errores
- ❌ Tiempo ahorrado marginal vs full PAT-006

---

## Consequences

### Positive
- ✅ 0 errores de especulación (garantizado)
- ✅ Código funcional al primer intento
- ✅ 2+ horas ahorradas en debugging
- ✅ Tipos TypeScript correctos desde inicio
- ✅ Confianza 100% en implementación

### Negative
- ⏱️ 30 minutos invertidos antes de Fase 3 (overhead aceptable)
- 📋 Documentación adicional (pero útil para mantenimiento)

### Neutral
- 🔵 Requiere disciplina (ECO enforce mandatory)
- 🔵 AGENT THETA bloqueado hasta PAT-006 completo

---

## Implementation Plan

### Immediate (Pre-Fase 3)
- [ ] AGENT SIGMA completa Fase 2 (backend + ACF)
- [ ] AGENT SIGMA ejecuta PAT-006 (30 min)
- [ ] AGENT SIGMA crea API inventory document
- [ ] AGENT SIGMA crea Postman collection
- [ ] ECO valida completeness
- [ ] ECO aprueba inicio Fase 3

### Enforcement
```python
# ECO validation logic
def validate_phase3_start():
    if not exists('docs/api-inventories/wordpress-rest-api-inventory.md'):
        raise BlockerError('PAT-006 MANDATORY: API inventory missing')

    if not exists('testing/postman/prilabsa-api.postman_collection.json'):
        raise BlockerError('PAT-006 MANDATORY: Postman collection missing')

    if not all_endpoints_documented():
        raise BlockerError('PAT-006 MANDATORY: Incomplete endpoint documentation')

    return 'APPROVED: Phase 3 can start'
```

---

## Validation

### Success Criteria
- ✅ API inventory document complete
- ✅ Postman collection con responses 200 OK
- ✅ Tipos TypeScript creados basados en responses reales
- ✅ AGENT THETA implementa integración sin errores

### Metrics
- **Before (Without PAT-006)**:
  - Expected errors: 10-30 (especulación)
  - Time wasted: 1-2 horas
- **After (With PAT-006)**:
  - Expected errors: 0
  - Time wasted: 0
  - Time invested: 30 min
  - **ROI**: 200-400%

---

## Related Patterns

- **PAT-006**: API Verification Protocol (este ADR)
- **ANTI-004**: Speculation-Driven API Design (antipatrón evitado)
- **ADR-004**: (BRIK-64) PAT-006 Made Mandatory (precedente)

---

**Approved by**: ECO (MANDATORY enforcement)
**Review date**: 2025-11-04
**Next Review**: Post-Fase 3 (validar 0 errores logrados)

---

## Appendix: BRIK-64 Reference

**Context**: Rust project con múltiples crates
**Phase 7.1**: Implementar servidor sin PAT-006
**Result**: 39 compilation errors, 2+ hours debugging
**Root Cause**: Asumir `Parser::new()` existía (no existía)
**Fix Phase 7.2**: Aplicar PAT-006, leer APIs reales
**Result**: 0 errors, código funcional
**Lesson**: "Es mejor verificar una vez que asumir mil veces"

**Aplicación PRILABSA**: Mismo principio, diferente tecnología (PHP/WordPress vs Rust), mismo resultado esperado (0 errores con PAT-006).
