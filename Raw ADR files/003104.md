# ADR-001: WordPress Headless vs Payload CMS

**Status**: ✅ ACCEPTED
**Date**: 2025-11-04
**Deciders**: CTO, ECO
**Related**: MASTER-PLAN.md, ADR-002

---

## Context and Problem Statement

El proyecto requiere un CMS headless para gestionar 105 productos dinámicamente. Se evaluaron dos opciones principales: WordPress Headless y Payload CMS.

**Pregunta**: ¿Qué CMS headless usar para gestionar el catálogo de productos de PRILABSA?

---

## Decision

**Seleccionado**: WordPress 6.6+ en modo Headless

---

## Rationale

### Ventajas WordPress Headless
1. **Experiencia Previa**: Cliente ya conoce WordPress (curva aprendizaje 0)
2. **Plugins Gratuitos**: ACF, JWT Auth, CORS todos gratuitos
3. **Hosting Listo**: GoDaddy ya tiene WordPress en productos.prilabsa.com
4. **Documentación**: Amplia comunidad y recursos
5. **Madurez**: 20+ años de desarrollo, probado en producción
6. **REST API Estándar**: `/wp-json/wp/v2/` bien documentada
7. **Admin UI**: Intuitiva para usuarios no-técnicos
8. **Costo**: $0 setup (solo hosting ~$5/mes)

### Desventajas Mitigadas
- **Performance**: Mitigado con SWR cache en frontend + pagination
- **Overhead PHP**: Aceptable para catálogo de 105 productos
- **Seguridad**: Hardening + JWT auth + CORS configurado

---

## Alternatives Considered

### Alternative 1: Payload CMS (Node.js)
**Approach**:
- Modern CMS built on Node.js + TypeScript
- More flexible, developer-friendly
- Better performance potencial

**Rejected Because**:
- ❌ Requiere hosting Node.js (GoDaddy no listo)
- ❌ Curva aprendizaje alta para cliente
- ❌ Setup más complejo (Express + MongoDB/PostgreSQL)
- ❌ Sin experiencia previa del equipo
- ❌ Plugins ecosystem menor
- ❌ Costo hosting mayor (~$20/mes VPS)
- ❌ Timeline 8 semanas en riesgo

### Alternative 2: Headless CMS SaaS (Strapi, Contentful)
**Approach**:
- CMS cloud-hosted (SaaS)
- 0 infrastructure management
- APIs modernas

**Rejected Because**:
- ❌ Costo mensual ($29-99/mes según plan)
- ❌ Dependencia vendor lock-in
- ❌ Migración de contenido compleja
- ❌ Límites de requests API (planes gratuitos muy limitados)

---

## Consequences

### Positive
- ✅ Setup rápido (1 semana Fase 1)
- ✅ Cliente puede gestionar contenido inmediatamente
- ✅ Costo bajo (<$50 setup)
- ✅ Timeline 8 semanas realista
- ✅ Soporte comunidad amplio

### Negative
- ⚠️ PHP dependency (menos moderno que Node.js)
- ⚠️ Performance no óptima vs CMS moderno (mitigado con cache)
- ⚠️ Overhead WordPress core (mitigado con headless mode)

### Neutral
- 🔵 Requiere aprender WordPress REST API (bien documentada)
- 🔵 ACF plugin dependency (gratuito, mantenido activamente)

---

## Implementation Plan

### Immediate
- [x] Decidir WordPress Headless
- [ ] Fase 1: Setup WordPress local (XAMPP/Docker)
- [ ] Fase 2: Configurar ACF + REST API

### Long Term
- [ ] Evaluar migración a Payload CMS si requerimientos crecen significativamente (post 1 año)
- [ ] Monitoring performance WordPress API (si <500ms p95 → OK)

---

## Validation

### Success Criteria
- ✅ API response time <500ms (p95)
- ✅ Cliente gestiona productos sin ayuda técnica
- ✅ Setup completo en ≤2 semanas (Fase 1+2)
- ✅ Costo total <$50 (excl. hosting mensual)

### Metrics
- Before: 0 productos dinámicos, data estática
- After: 105 productos gestionables, updates sin deploy

---

**Approved by**: CTO (Pendiente)
**Review date**: 2025-11-04
**Next Review**: Post-Fase 2 (evaluar performance API)
