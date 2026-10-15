# ADR-001: Usar Node.js como Runtime Principal

**Estado:** ✅ Aceptada

**Fecha:** 2021-Q1 (Inicio del proyecto)

**Categoría:** Stack Tecnológico

**Autores:** Equipo IBM-I+D, TSS Colombia

---

## Contexto

### Situación

Al iniciar el proyecto WhatHelp Chat API, se necesitaba seleccionar un runtime/lenguaje de programación para desarrollar una aplicación de chat en tiempo real con las siguientes características:

- Comunicación bidireccional en tiempo real (WebSockets)

- Integración con múltiples servicios externos (IBM Watson, WhatsApp API, Cloud Object Storage)

- Manejo concurrente de múltiples conexiones simultáneas

- API REST para operaciones CRUD

- Sistema de notificaciones push

### Restricciones

**Técnicas:**

- Necesidad de manejar I/O asíncrono eficientemente

- Soporte nativo para WebSockets/Socket.IO

- Rapidez en el desarrollo (time-to-market)

**Equipo:**

- **Experiencia existente en JavaScript** (factor decisivo)

- Equipo familiarizado con el ecosistema npm

- Conocimiento previo de desarrollo web con JS

**Negocio:**

- Proyecto con timeline ajustado

- Necesidad de reutilizar conocimiento existente

- Minimizar curva de aprendizaje

---

## Decisión

**Se decidió:** Usar **Node.js 20.x** como runtime principal para la aplicación backend.

### Implementación

**Versión utilizada:**
```json
// package.json
{
  "name": "api-watshelp-bdb",
  "version": "1.5.0",
  "engines": {
    "node": ">=20.0.0"
  }
}
```

**Dockerfile:**
```dockerfile
FROM --platform=linux/amd64 node:20-slim AS base
```

**Características aprovechadas:**

- Event loop para I/O no bloqueante

- NPM como gestor de dependencias

- Ecosistema rico de librerías (express, socket.io, pg, redis)

- Compatibilidad con servicios IBM Cloud

---

## Alternativas Consideradas

### Alternativa 1: Python (Django/FastAPI)

**Descripción:** Backend en Python con framework web moderno

**Pros:**

- ✅ Excelente para integración con IA/ML

- ✅ Sintaxis limpia y legible

- ✅ Buenas librerías para IBM Watson

**Contras:**

- ❌ Equipo sin experiencia significativa en Python

- ❌ Curva de aprendizaje adicional

- ❌ WebSockets menos maduro que en Node.js

- ❌ Mayor tiempo de desarrollo inicial

**Razón de rechazo:** Falta de experiencia del equipo, tiempo de desarrollo más largo

---

### Alternativa 2: Java (Spring Boot)

**Descripción:** Backend empresarial con Spring Framework

**Pros:**

- ✅ Altamente robusto y enterprise-grade

- ✅ Excelente soporte IBM

- ✅ Fuertemente tipado (menos errores en runtime)

**Contras:**

- ❌ Desarrollo más lento (verboso)

- ❌ Mayor complejidad para funcionalidades simples

- ❌ Equipo sin experiencia en Java backend

- ❌ Overhead de memoria mayor

**Razón de rechazo:** Desarrollo más lento, complejidad innecesaria para el alcance del proyecto, falta de experiencia

---

### Alternativa 3: Go

**Descripción:** Backend en Go para alta concurrencia

**Pros:**

- ✅ Excelente performance

- ✅ Concurrencia nativa (goroutines)

- ✅ Binario compilado (deployment simple)

**Contras:**

- ❌ Equipo completamente sin experiencia en Go

- ❌ Ecosistema más pequeño

- ❌ Curva de aprendizaje significativa

- ❌ Menos librerías para IBM Watson

**Razón de rechazo:** Experiencia cero del equipo, riesgo muy alto para timeline ajustado

---

## Tabla Comparativa de Alternativas

| Criterio | Node.js (Elegido) | Python | Java | Go |
|----------|------------------|--------|------|-----|
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Velocidad desarrollo** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Experiencia equipo** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ☆ |
| **Ecosistema librerías** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **WebSockets/Real-time** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Costo infraestructura** | Bajo | Bajo | Medio-Alto | Bajo |
| **Madurez** | Alta | Alta | Muy Alta | Media |
| **Curva aprendizaje** | Baja | Media | Alta | Alta |

---

## Consecuencias

### ✅ Positivas

1. **Desarrollo rápido:** Equipo pudo comenzar inmediatamente sin capacitación

2. **Ecosistema rico:** Acceso a 2M+ paquetes npm (express, socket.io, pg, redis, ibm-watson)

3. **I/O asíncrono nativo:** Manejo eficiente de múltiples conexiones simultáneas

4. **Comunidad activa:** Fácil encontrar soluciones a problemas comunes

5. **Integración natural con WebSockets:** Socket.IO funciona excelentemente

6. **Menor curva de aprendizaje:** JavaScript también usado en frontend

### ⚠️ Negativas (Trade-offs)

1. **Performance menor que Go/Rust:** Aceptable para nuestro caso de uso

2. **Single-threaded:** Mitigado con cluster mode y múltiples instancias

3. **Tipado débil:** Mayor posibilidad de errores en runtime (sin TypeScript)

4. **Callback hell potencial:** Mitigado con async/await moderno

5. **Consumo de memoria:** Mayor que Go, menor que Java (aceptable)

### 🔄 Neutral

1. **Escalabilidad horizontal necesaria:** Por limitación single-thread (planeado desde inicio)

2. **Necesidad de linters/formatters:** ESLint para mantener calidad de código

3. **Gestión de dependencias:** npm requiere auditorías de seguridad periódicas

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| **Errores en runtime por tipado débil** | Alta | Medio | Validación con express-validator, tests exhaustivos |
| **Performance insuficiente** | Media | Alto | Profiling periódico, optimizaciones (caché, índices DB) |
| **Vulnerabilidades en dependencias** | Media | Alto | `npm audit` automatizado, actualizaciones regulares |
| **Bloqueo del event loop** | Media | Alto | Evitar operaciones CPU-intensive, usar workers si necesario |
| **Memory leaks** | Baja | Alto | Monitoreo de memoria, profiling, buenas prácticas |

---

## Decisiones Relacionadas

- **Ver [ADR-003](./ADR-003-express-framework.md):** Elección de Express.js como framework (compatible con Node.js)

- **Ver [ADR-006](../03-comunicacion/ADR-006-socketio.md):** Socket.IO aprovecha event-driven nature de Node.js

- **Ver [ADR-012](../06-optimizacion/ADR-012-redis-cache.md):** Redis para escalar horizontalmente (compensar single-thread)

---

## Referencias

- [Node.js Official Documentation](https://nodejs.org/docs/latest-v20.x/api/)

- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)

- [Why Node.js for Real-time Applications](https://nodejs.org/en/learn/getting-started/introduction-to-nodejs)

- [npm Registry](https://www.npmjs.com/)

---

## Notas Adicionales

### Evolución Futura

- **Consideración TypeScript:** En evaluación para proyectos futuros, no planeado para este proyecto por costo de migración

- **Node.js 22+ LTS:** Actualización planeada cuando esté disponible

- **Performance monitoring:** Implementar APM (Application Performance Monitoring) si escala

### Lecciones Aprendidas

✅ **Acertada:** La decisión fue correcta dado el contexto del equipo y timeline  
✅ **Productividad alta:** Equipo pudo iterar rápidamente  
⚠️ **Mejoría:** Debió considerarse TypeScript desde el inicio (cost bajo, beneficio alto)

---

📅 **Última actualización:** 18 de diciembre de 2025
