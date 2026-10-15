# ADR-002: PostgreSQL como Base de Datos Principal

**Estado:** ✅ Aceptada

**Fecha:** 2021-Q1 (Inicio del proyecto)

**Categoría:** Base de Datos

**Autores:** Equipo IBM-I+D, TSS Colombia

---

## Contexto

### Situación

El proyecto WhatHelp Chat API requería una base de datos que pudiera:

- Almacenar datos relacionales (usuarios, agentes, salas, mensajes, áreas)

- Garantizar integridad transaccional (ACID) para operaciones críticas

- Soportar alta concurrencia de lecturas/escrituras

- Permitir consultas complejas con JOINs

- Escalar para miles de mensajes diarios

- Soportar índices para optimización de performance

### Restricciones

**Negocio:**

- **Requisito IBM:** PostgreSQL es el estándar de IBM para sus proyectos (factor decisivo)

- Contrato IBM Cloud incluye servicios de PostgreSQL

- Familiaridad con ecosistema IBM

**Técnicas:**

- Necesidad de transacciones ACID para:
  - Creación de salas con múltiples inserts atómicos
  - Transferencias de conversaciones entre agentes
  - Registro de logs y métricas consistentes

- Relaciones complejas entre entidades (usuarios ↔ salas ↔ agentes ↔ áreas)

- Soporte para índices de performance

**Operacionales:**

- Soporte empresarial disponible

- Herramientas de backup/recovery robustas

- Equipo con conocimiento en SQL

---

## Decisión

**Se decidió:** Usar **PostgreSQL** como base de datos relacional principal.

### Implementación

**Versión en producción:** PostgreSQL 15.x

**Configuración:**
```javascript
// app/config/index.js
postgresql: {
  username: process.env.PG_USERNAME,
  password: process.env.PG_PASSWORD,
  host: process.env.PG_HOST,
  port: process.env.PG_PORT,
  database: process.env.PG_DATABASE,
  schema: 'banco_bogota_chat',
}
```

**Connection Pool:**
```javascript
// app/services/postgresql.js
const pool = new Pool({
  user: config.postgresql.username,
  password: config.postgresql.password,
  host: config.postgresql.host,
  port: config.postgresql.port,
  database: config.postgresql.database,
  // Pool settings optimizados
  max: 20,                          // Máximo 20 conexiones
  min: 5,                           // Mínimo 5 conexiones activas
  idleTimeoutMillis: 30000,         // 30s timeout inactivo
  connectionTimeoutMillis: 30000,   // 30s timeout conexión
  statement_timeout: 30000,         // 30s timeout query
  ssl: sslConfig
});
```

**Schema principal:**
```
banco_bogota_chat
├── agents (agentes de soporte)
├── users (usuarios de WhatsApp)
├── rooms (salas de conversación)
├── messages (mensajes)
├── areas (departamentos/áreas)
├── agent_areas (relación agentes-áreas)
├── agent_rooms (asignación agente-sala)
├── queues (cola de espera)
├── watson_session_ids (sesiones Watson)
├── external_room (integración WhatsApp)
└── ... (20+ tablas)
```

---

## Alternativas Consideradas

### Alternativa 1: MongoDB (NoSQL)

**Descripción:** Base de datos documental NoSQL

**Pros:**

- ✅ Schema flexible (fácil evolución)

- ✅ Excelente para datos semi-estructurados

- ✅ Alta performance en escrituras

- ✅ Escalabilidad horizontal nativa

**Contras:**

- ❌ No es estándar IBM (factor decisivo)

- ❌ Sin soporte ACID fuerte hasta versión 4.0

- ❌ JOINs limitados (desnormalización necesaria)

- ❌ Mayor complejidad en relaciones complejas

- ❌ Equipo más familiarizado con SQL

**Razón de rechazo:** No cumple con requisito IBM, necesidad de transacciones ACID, modelo relacional natural para el dominio

---

### Alternativa 2: MySQL

**Descripción:** Base de datos relacional tradicional

**Pros:**

- ✅ ACID completo

- ✅ Amplia adopción

- ✅ Performance sólido

- ✅ Ecosistema maduro

**Contras:**

- ❌ PostgreSQL es estándar IBM (factor decisivo)

- ❌ Menor soporte para JSON/JSONB

- ❌ Extensibilidad limitada vs PostgreSQL

- ❌ Índices parciales menos avanzados

**Razón de rechazo:** PostgreSQL preferido por IBM, mayores capacidades avanzadas (JSON, full-text search, índices parciales)

---

### Alternativa 3: IBM Db2

**Descripción:** Base de datos empresarial de IBM

**Pros:**

- ✅ Producto IBM (máxima integración)

- ✅ Enterprise-grade

- ✅ Soporte premium

**Contras:**

- ❌ Costo elevado (licenciamiento)

- ❌ Curva de aprendizaje mayor

- ❌ Overhead para aplicación de este tamaño

- ❌ Menor comunidad/recursos

**Razón de rechazo:** Costo-beneficio no justificado, PostgreSQL cumple todos los requisitos

---

## Tabla Comparativa de Alternativas

| Criterio | PostgreSQL (Elegido) | MongoDB | MySQL | IBM Db2 |
|----------|---------------------|---------|-------|---------|
| **Requisito IBM** | ⭐⭐⭐⭐⭐ | ☆ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **ACID Transactions** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Escalabilidad** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Extensibilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Costo** | Bajo | Bajo | Bajo | Alto |
| **Comunidad** | Muy Alta | Alta | Muy Alta | Media |
| **Soporte JSON** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## Consecuencias

### ✅ Positivas

1. **Integridad de datos garantizada:** ACID en todas las transacciones críticas

2. **Modelo relacional natural:** Entidades del dominio mapean perfectamente a tablas

3. **Índices avanzados:** Soporte para índices parciales, GIN, BRIN (implementado en ADR-013)

4. **JSONB support:** Flexibilidad para datos semi-estructurados cuando necesario

5. **Full-text search:** Capacidades nativas de búsqueda de texto

6. **Extensiones:** PostGIS disponible si se requiere geolocalización

7. **Herramientas robustas:** pgAdmin, pg_stat_statements para monitoring

8. **Comunidad activa:** Fácil encontrar soluciones y mejores prácticas

9. **Compatibilidad IBM Cloud:** Integración nativa con servicios IBM

### ⚠️ Negativas (Trade-offs)

1. **Escalabilidad horizontal compleja:** Requiere sharding manual (no es problema actualmente)

2. **Escrituras más lentas que NoSQL:** Aceptable para volumen actual (mitigado con índices)

3. **Schema rígido:** Cambios requieren migraciones (beneficio en calidad de datos)

4. **Costo de conexiones:** Pool management crítico (implementado correctamente)

### 🔄 Neutral

1. **Migraciones manuales:** Se usan scripts SQL (sin herramienta como Flyway)

2. **Backup strategy:** Responsabilidad del equipo de infraestructura

3. **Monitoring:** Requiere configuración de pg_stat_statements

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| **Connection pool exhaustion** | Media | Alto | Pool configurado con límites (max: 20), timeouts, monitoring |
| **Queries lentos** | Alta | Medio | Índices estratégicos (ADR-013), `EXPLAIN ANALYZE`, statement_timeout |
| **Deadlocks en transacciones** | Baja | Medio | Timeout configurado, orden consistente de locks |
| **Crecimiento de datos descontrolado** | Media | Alto | Archivado de mensajes antiguos, particionamiento si necesario |
| **Backup/recovery** | Baja | Crítico | Strategy de backup automatizado, DR plan |

---

## Decisiones Relacionadas

- **Ver [ADR-013](../06-optimizacion/ADR-013-database-indexes.md):** Índices de performance implementados

- **Ver [ADR-012](../06-optimizacion/ADR-012-redis-cache.md):** Redis como caché para reducir carga en PostgreSQL

- **Relacionado con ADR-008:** Capa de abstracción (`services/postgresql.js`) facilita cambios futuros

---

## Referencias

- [PostgreSQL Official Documentation v15](https://www.postgresql.org/docs/15/)

- [IBM Cloud Databases for PostgreSQL](https://cloud.ibm.com/docs/databases-for-postgresql)

- [Node.js pg Driver](https://node-postgres.com/)

- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## Métricas de Performance

**Estado actual (post-optimizaciones ADR-013):**

- **Consultas comunes:** < 50ms (p95)

- **Creación de sala (transacción):** ~100-150ms

- **Búsqueda de sala activa:** ~20-30ms (con índice)

- **Inserción de mensaje:** ~10-20ms

- **Pool efficiency:** ~85% (5-17 conexiones activas típicamente)

**Mejoras implementadas:**

- 8 índices estratégicos (ADR-013)

- Caché Redis para queries frecuentes (ADR-012)

- Pool optimizado con timeouts

- Statement timeout 30s para prevenir queries infinitos

---

## Notas Adicionales

### Evolución Futura

**Consideraciones si el proyecto escala:**

- **Particionamiento:** Por fecha (mensajes antiguos) si la tabla crece >10M rows

- **Read replicas:** Para separar carga de lectura/escritura

- **Sharding:** Solo si alcanzamos límites de escalabilidad vertical (poco probable)

- **TimescaleDB:** Si necesitamos capacidades time-series avanzadas

### Lecciones Aprendidas

✅ **Acertada:** PostgreSQL cumplió todas las expectativas  
✅ **Índices críticos:** Los índices de ADR-013 fueron transformadores (50-150ms mejoría)  
✅ **Pool management:** Configuración correcta desde inicio previno problemas  
⚠️ **Migraciones:** Debió implementarse herramienta formal (Flyway/Liquibase) desde inicio

---

📅 **Última actualización:** 18 de diciembre de 2025
