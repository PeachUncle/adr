# ADR-010: Sistema de Colas Basado en Cron Jobs

**Estado:** ⚠️ Deprecated (Migración planeada a BullMQ en Q1 2026)

**Fecha:** 2021-Q2 (Implementación inicial)

**Categoría:** Infraestructura / Procesamiento Asíncrono

**Autores:** Equipo IBM-I+D, TSS Colombia

---

## Contexto

### Situación

El sistema requería procesar tareas asíncronas periódicas:

**Requisitos funcionales:**

- **Transferencia de conversaciones:** Mover salas de cola a agentes disponibles (cada 1 min)

- **Cierre por inactividad:** Cerrar salas inactivas > 10 minutos (cada 1 min)

- **Notificaciones de cola larga:** Alertar cuando cola > 5 personas (cada 2 min)

- **Encuestas automáticas:** Enviar encuestas post-conversación (cada 7 min)

- **Limpieza de archivos:** Borrar archivos temporales viejos (cada 24 hrs)

- **Reportes programados:** Generar reportes diarios/semanales

### Restricciones

**Fase Inicial (2021):**

- Proyecto en etapa temprana

- **Solo 1 instancia** en producción

- Equipo pequeño (2-3 devs)

- Tareas simples y predecibles

- Presupuesto limitado (evitar infraestructura adicional)

**Técnicas:**

- Necesidad de scheduling simple

- No se requería retry logic sofisticado

- Volumen bajo de mensajes (~100-500/día)

---

## Decisión

**Se decidió:** Usar **node-cron** para ejecutar jobs programados directamente en la aplicación.

### Implementación

**Librería utilizada:**
```json
// package.json
{
  "dependencies": {
    "node-cron": "^4.2.1"
  }
}
```

**Configuración de cron jobs:**
```javascript
// app/app.js
const cron = require("node-cron");
const cronRoom = require("./cron/rooms");
const cronQueue = require("./cron/queue");
const event = require("./helpers/queue");

class App {
  crons() {
    // 1. Encolamiento - cada 1 minuto
    cron.schedule("*/1 * * * *", async () => {
      await event.releaseQueue(this.io);
    });

    // 2. Notificación de cola larga - cada 2 minutos
    cron.schedule("*/2 * * * *", async () => {
      await cronQueue.awaitQueue();
    });

    // 3. Cierre por inactividad - cada 1 minuto
    cron.schedule("*/1 * * * *", async () => {
      await cronRoom.close(this.io);
    });

    // 4. Encuestas - cada 7 minutos
    cron.schedule("*/7 * * * *", async () => {
      await cronQueue.awaitSurvey();
    });

    // 5. Limpieza de archivos - cada 24 horas
    cron.schedule("0 0 * * *", async () => {
      await cronRoomFiles.cleanOldFiles();
    });

    // 6. Reportes - diario a las 6 AM
    cron.schedule("0 6 * * *", async () => {
      await cronReport.generateDaily();
    });
  }
}
```

**Ejemplo de job: Transferencia de cola**
```javascript
// app/cron/queue.js
const event = {
  async releaseQueue(io) {
    try {
      // 1. Buscar personas en cola
      const queueSQL = {
        text: `SELECT q.*, r.* FROM queues q 
               JOIN rooms r ON q.room_id = r.id 
               WHERE q.status = 'WAITING' 
               ORDER BY q.created_at ASC`,
      };
      const queue = await postgresql.query(queueSQL);
      
      // 2. Buscar agentes disponibles
      const agentSQL = {
        text: `SELECT * FROM agents 
               WHERE online = true AND active_rooms < rooms 
               ORDER BY active_rooms ASC LIMIT 1`,
      };
      const agent = await postgresql.query(agentSQL);
      
      if (queue.rows.length > 0 && agent.rows.length > 0) {
        // 3. Asignar sala a agente
        const assignment = await room.assignAgentToRoom(
          queue.rows[0].room_id,
          agent.rows[0].id
        );
        
        // 4. Notificar por Socket.IO
        io.to(`AGENT_${agent.rows[0].id}`).emit('NEW_ASSIGNMENT', assignment);
        
        // 5. Actualizar estado de cola
        await queue.updateStatus(queue.rows[0].id, 'ASSIGNED');
      }
    } catch (error) {
      console.error('[CRON] Error en releaseQueue:', error);
    }
  }
};
```

**Prevención de race conditions (implementado):**
```javascript
// app/cron/queue.js
const getStatus = async (val) => {
  const sql = {
    text: `SELECT * FROM general_configurations 
           WHERE code_configuration = $1 FOR UPDATE`,
    values: [val]
  };
  const result = await postgresql.query(sql);
  return result.rows[0];
};

const updateStatus = async (val, status) => {
  const sql = {
    text: `UPDATE general_configurations 
           SET value_configuration = $1 
           WHERE code_configuration = $2`,
    values: [status, val]
  };
  await postgresql.query(sql);
};

// Uso: Lock en base de datos
exports.awaitQueue = async () => {
  const status = await getStatus('QUEUE_LOCK');
  if (status.value_configuration === 'RUNNING') {
    console.log('[CRON] Job already running, skipping');
    return;
  }
  
  await updateStatus('QUEUE_LOCK', 'RUNNING');
  try {
    // ... ejecutar lógica ...
  } finally {
    await updateStatus('QUEUE_LOCK', 'FINALIZED');
  }
};
```

---

## Alternativas Consideradas

### Alternativa 1: BullMQ (Redis-based Queue)

**Descripción:** Sistema de colas robusto con Redis

**Pros:**

- ✅ Retry logic automático

- ✅ Priorización de jobs

- ✅ Manejo de fallos sofisticado

- ✅ Dashboard para monitoring

- ✅ Distribuido (múltiples workers)

- ✅ Job scheduling avanzado

- ✅ Concurrency control

**Contras:**

- ❌ **Requiere Redis** (infraestructura adicional)

- ❌ Mayor complejidad inicial

- ❌ Curva de aprendizaje

- ❌ Overhead para tareas simples

**Razón de rechazo (2021):** Complejidad innecesaria, solo 1 instancia, no justificaba Redis adicional

**Estado actual (2024):** ⚠️ **DEBIÓ ELEGIRSE DESDE INICIO** - Redis ya existe, problemas de race conditions

---

### Alternativa 2: Agenda.js (MongoDB-based)

**Descripción:** Job scheduler con MongoDB

**Pros:**

- ✅ Persistencia de jobs

- ✅ Retry logic

- ✅ Dashboard

**Contras:**

- ❌ Requiere MongoDB (no usamos)

- ❌ Overhead adicional

**Razón de rechazo:** No usamos MongoDB, PostgreSQL no es ideal para queue

---

### Alternativa 3: AWS SQS / Cloud Queues

**Descripción:** Servicio de colas managed

**Pros:**

- ✅ Fully managed

- ✅ Escalabilidad infinita

- ✅ Retry automático

**Contras:**

- ❌ Costo adicional

- ❌ Vendor lock-in

- ❌ Latencia de red

**Razón de rechazo:** Costo, dependencia cloud, on-premise deployment

---

### Alternativa 4: RabbitMQ

**Descripción:** Message broker robusto

**Pros:**

- ✅ Enterprise-grade

- ✅ Muy robusto

- ✅ Protocolo AMQP

**Contras:**

- ❌ Infraestructura pesada

- ❌ Complejidad operacional

- ❌ Overkill para este proyecto

**Razón de rechazo:** Complejidad excesiva

---

## Tabla Comparativa de Alternativas

| Criterio | node-cron (Elegido) | BullMQ | Agenda | RabbitMQ |
|----------|---------------------|--------|--------|----------|
| **Simplicidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Robustez** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Escalabilidad** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Infraestructura** | Ninguna | Redis | MongoDB | RabbitMQ Server |
| **Retry logic** | Manual | Automático | Automático | Automático |
| **Multi-instancia** | ⚠️ Problemático | ✅ Nativo | ✅ Sí | ✅ Sí |
| **Costo operacional** | Bajo | Medio | Medio | Alto |
| **Adecuado para 1 instancia** | ✅ | ✅ | ✅ | ⚠️ |
| **Adecuado para múltiples** | ❌ | ✅ | ✅ | ✅ |

---

## Consecuencias

### ✅ Positivas (Inicialmente)

1. **Implementación rápida:** 1-2 días para tener todos los crons funcionando

2. **Cero infraestructura:** No requiere servicios adicionales

3. **Simple de debuggear:** Logs directos en aplicación

4. **Costo cero:** No servicios externos

5. **Adecuado para 1 instancia:** Funcionó perfectamente en fase inicial

### ⚠️ Negativas (Descubiertas con el Tiempo)

1. **❌ CRÍTICO: Race conditions con múltiples instancias**
   - Si escala a 2+ instancias, jobs se ejecutan duplicados
   - Ejemplo: 2 agentes reciben misma sala, transacciones duplicadas
   

2. **❌ Sin retry automático**
   - Si job falla, se pierde hasta próxima ejecución
   - No hay persistencia de intentos fallidos

3. **❌ Sin monitoreo centralizado**
   - Logs dispersos en múltiples instancias
   - No hay dashboard de jobs

4. **❌ Sin priorización**
   - Todos los jobs misma prioridad
   - No se pueden priorizar transferencias urgentes

5. **❌ Acoplamiento al proceso**
   - Si app se reinicia, jobs en ejecución se pierden

6. **❌ Difícil de testar**
   - Testing de cron jobs complicado

### 🔄 Neutral

1. **Mitigación con DB locks:** Funciona pero es hack

2. **Scheduling limitado:** Suficiente para casos actuales

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación (Implementada) | Efectividad |
|--------|-------------|---------|---------------------------|-------------|
| **Race conditions múltiples instancias** | Alta | Crítico | DB locks (`FOR UPDATE`) | ⚠️ Funciona pero frágil |
| **Job failures sin recovery** | Media | Alto | Try-catch + logging | ⚠️ Detecta pero no recupera |
| **Cron overlap** | Media | Medio | Check status antes de ejecutar | ✅ Efectivo |
| **App restart pierde jobs** | Baja | Medio | Ninguna | ❌ Sin mitigación |
| **Memory leaks en jobs** | Baja | Alto | Timeouts, monitoring | ✅ Detecta temprano |

---

## Decisiones Relacionadas

- **Motivó [ADR-012](../06-optimizacion/ADR-012-redis-cache.md):** Redis disponible, podría usarse para BullMQ

- **Bloqueado por ADR-008:** Monolito facilita cron in-process

- **Problema para escalabilidad:** Conflicto con planes de múltiples instancias

---

## Lecciones Aprendidas

### 🔴 Decisión LAMENTADA

**En retrospectiva (2024):**

✅ **Fue correcta para fase inicial:**

- 1 instancia

- Equipo pequeño

- Tareas simples

- Presupuesto limitado

❌ **Debió planificarse escalabilidad desde inicio:**

- Redis eventual fue necesario de todos modos (ADR-012)

- BullMQ hubiera sido "gratis" con Redis

- Race conditions son dolor de cabeza constante

### Costo de NO elegir BullMQ:

1. **Tiempo perdido:** ~2-3 semanas debugging race conditions

2. **Bugs en producción:** Salas duplicadas, notificaciones duplicadas

3. **Complejidad añadida:** DB locks frágiles

4. **Limitación de escalabilidad:** Impide agregar instancias sin riesgo

### ¿Qué hubiéramos hecho diferente?

**Opción A: BullMQ desde día 1**

- Costo inicial: +2 días setup Redis

- Beneficio: Sin problemas de race conditions nunca

**Opción B: Refactor temprano**

- Al alcanzar 500 mensajes/día → migrar

- No esperar a tener problemas

---

## Plan de Migración (Q1 2026)

### Fase 1: Setup BullMQ (Semana 1-2)

```javascript
// Nuevo: app/queues/index.js
const Queue = require('bull');

const transferQueue = new Queue('transfer', {
  redis: {
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT,
  }
});

const roomCloseQueue = new Queue('room-close', { redis: {...} });
const surveyQueue = new Queue('survey', { redis: {...} });

// Process jobs
transferQueue.process(async (job) => {
  await event.releaseQueue(job.data.io);
});

// Schedule jobs
transferQueue.add({}, { repeat: { cron: '*/1 * * * *' } });
```

### Fase 2: Migración Gradual (Semana 3-4)

1. **Duplicar jobs:** Cron + BullMQ en paralelo

2. **Monitorear:** Verificar comportamiento idéntico

3. **Deshabilitar cron:** Uno por uno

4. **Validar:** Producción solo con BullMQ

### Fase 3: Cleanup (Semana 5)

1. Remover `node-cron` de dependencies

2. Eliminar archivos `app/cron/`

3. Remover DB locks de `general_configurations`

4. Documentar nueva arquitectura

### Beneficios Esperados

- ✅ Sin race conditions

- ✅ Retry automático

- ✅ Dashboard de monitoring

- ✅ Escalabilidad horizontal segura

- ✅ Mejor observabilidad

---

## Referencias

- [node-cron Documentation](https://www.npmjs.com/package/node-cron)

- [BullMQ Documentation](https://docs.bullmq.io/)

- [Distributed Cron Problems](https://engineering.linkedin.com/blog/2021/fixing-distributed-cron)

- [Why Message Queues](https://www.cloudamqp.com/blog/when-to-use-rabbitmq-or-apache-kafka.html)

---

## Métricas Actuales

**Jobs ejecutándose:**

- `releaseQueue`: Cada 1 min (~1,440 ejecuciones/día)

- `awaitQueue`: Cada 2 min (~720 ejecuciones/día)

- `closeRoom`: Cada 1 min (~1,440 ejecuciones/día)

- `awaitSurvey`: Cada 7 min (~206 ejecuciones/día)

**Problemas registrados (últimos 6 meses):**

- Race conditions: ~15 incidentes

- Jobs fallidos: ~40 (sin retry)

- Duplicación de tareas: ~8 incidentes

**Tiempo estimado de migración:** 4-5 semanas  
**ROI estimado:** Alto (elimina clase de bugs completa)

---

## Notas Adicionales

### Alternativa Temporal: Cron Único

Si no se puede migrar a BullMQ inmediatamente:

```javascript
// Ejecutar crons solo en instancia primaria
const isPrimaryInstance = process.env.PRIMARY_INSTANCE === 'true';

if (isPrimaryInstance) {
  console.log('✅ Primary instance - Starting cron jobs');
  this.crons();
} else {
  console.log('⏸️ Secondary instance - Skipping cron jobs');
}
```

**Pros:**

- ✅ Solución rápida

- ✅ Evita race conditions

**Contras:**

- ❌ Single point of failure

- ❌ Si primary cae, crons no ejecutan

---

📅 **Última actualización:** 18 de diciembre de 2025  
⚠️ **Estado:** Deprecated - Migración a BullMQ planeada para Q1 2026
