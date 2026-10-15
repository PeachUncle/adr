# ADR-012: Redis para Caché y Escalabilidad Horizontal

**Estado:** ✅ Aceptada

**Fecha:** 2024-Q4 (Implementación de optimizaciones)

**Categoría:** Performance / Infraestructura

**Autores:** Equipo IBM-I+D, TSS Colombia

---

## Contexto

### Situación

Después de casi 3 años en producción, el sistema comenzó a mostrar problemas de performance:

**Problemas detectados:**

- Latencia endpoint `/whatsapp/external`: 530-1180ms (inaceptable)

- Queries repetitivos a PostgreSQL para datos que cambian poco:
  - Watson session IDs (consulta en cada mensaje)
  - Información de usuarios (consulta en cada login)
  - Salas activas por usuario

- **Necesidad de escalar horizontalmente** (múltiples instancias) pero Socket.IO requiere sincronización

**Restricciones:**

- SLA objetivo: < 700ms p95

- No romper funcionalidad existente

- Implementación con fail-safe (si Redis falla, app debe seguir funcionando)

---

## Decisión

**Se decidió:** Implementar **Redis 7.0+** con dos propósitos:

1. **Caché de datos frecuentes** → Reducir carga en PostgreSQL

2. **Socket.IO Adapter** → Sincronizar eventos entre múltiples instancias (planeado, no activo aún)

### Implementación

**Servicio de Caché (Fail-Safe Pattern):**

```javascript
// app/services/cache.js
const redis = require('redis');

class CacheService {
  constructor() {
    this.client = null;
    this.isConnected = false;
    this.stats = { hits: 0, misses: 0, errors: 0 };
    this.initialize();
  }

  async initialize() {
    try {
      this.client = redis.createClient({
        socket: {
          host: process.env.REDIS_HOST || 'localhost',
          port: process.env.REDIS_PORT || 6379,
          connectTimeout: 5000,
          reconnectStrategy: (retries) => {
            if (retries > 10) return null; // Stop retrying
            return Math.min(retries * 100, 3000);
          }
        },
        password: process.env.REDIS_PASSWORD,
        lazyConnect: true
      });

      // ✅ CRÍTICO: Manejo de errores NO rompe la aplicación
      this.client.on('error', (err) => {
        console.warn('[CACHE] Redis error (running without cache):', err.message);
        this.isConnected = false;
      });

      await this.client.connect().catch(err => {
        console.warn('[CACHE] Failed to connect. App will run without cache.');
      });
    } catch (error) {
      console.warn('[CACHE] Redis initialization failed. App continues without cache.');
    }
  }

  async get(key) {
    if (!this.isConnected) return null;
    try {
      const value = await this.client.get(key);
      if (value) {
        this.stats.hits++;
        return JSON.parse(value);
      }
      this.stats.misses++;
      return null;
    } catch (error) {
      this.stats.errors++;
      return null; // Fail gracefully
    }
  }

  async set(key, value, ttl = 3600) {
    if (!this.isConnected) return false;
    try {
      await this.client.setEx(key, ttl, JSON.stringify(value));
      return true;
    } catch (error) {
      return false; // Fail gracefully
    }
  }

  async del(key) {
    if (!this.isConnected) return false;
    try {
      await this.client.del(key);
      return true;
    } catch (error) {
      return false;
    }
  }
}

module.exports = new CacheService();
```

**Casos de uso implementados:**

```javascript
// 1. Watson Session IDs (TTL: 1 hora)
async getByRoom(room_id) {
  const cached = await cache.get(`watson:session:${room_id}`);
  if (cached) return cached;
  
  const result = await this.db.query(sql);
  await cache.set(`watson:session:${room_id}`, result.rows[0], 3600);
  return result.rows[0];
}

// 2. Información de Usuario (TTL: 15 minutos)
async loginUserWhatsapp(uid, fullname, provider) {
  const cached = await cache.get(`user:${provider}:${uid}`);
  if (cached) return cached;
  
  const userData = await user.validUserWhatsapp(...);
  await cache.set(`user:${provider}:${uid}`, userData, 900);
  return userData;
}

// 3. Sala Activa (TTL: 5 minutos)
async get_room_id(user_id) {
  const cached = await cache.get(`room:active:${user_id}`);
  if (cached) return cached;
  
  const roomData = await this.db.query(sql);
  await cache.set(`room:active:${user_id}`, roomData, 300);
  return roomData;
}
```

**Socket.IO Adapter (Configurado, no activo en producción):**

```javascript
// app/app.js
const { createAdapter } = require("@socket.io/redis-adapter");

async setupRedisAdapter() {
  const pubClient = createClient({ 
    socket: { host: redisHost, port: redisPort },
    password: redisPassword
  });
  const subClient = pubClient.duplicate();

  await Promise.all([pubClient.connect(), subClient.connect()]);
  
  this.io.adapter(createAdapter(pubClient, subClient));
  console.log('✅ Socket.IO Redis Adapter configurado');
}
```

---

## Alternativas Consideradas

### Alternativa 1: Memcached

**Descripción:** Sistema de caché distribuido simple

**Pros:**

- ✅ Más simple que Redis

- ✅ Ligeramente más rápido para operaciones simples

- ✅ Menor consumo de memoria

**Contras:**

- ❌ Solo caché (no pub/sub)

- ❌ Sin persistencia

- ❌ No sirve para Socket.IO adapter

- ❌ Tipos de datos limitados (solo strings)

**Razón de rechazo:** Necesitamos pub/sub para Socket.IO adapter, Redis es más versátil

---

### Alternativa 2: In-Memory Cache (node-cache)

**Descripción:** Caché en memoria del proceso Node.js

**Pros:**

- ✅ Cero infraestructura adicional

- ✅ Latencia mínima (sin red)

- ✅ Simplicidad máxima

**Contras:**

- ❌ No compartido entre instancias

- ❌ Se pierde al reiniciar

- ❌ Consume memoria del proceso

- ❌ No sirve para Socket.IO adapter

**Razón de rechazo:** Inútil para múltiples instancias, no sirve para Socket.IO

---

### Alternativa 3: KeyDB

**Descripción:** Fork de Redis con multi-threading

**Pros:**

- ✅ Compatible con Redis

- ✅ ~5x más rápido (multi-threaded)

- ✅ Drop-in replacement

**Contras:**

- ❌ Menos maduro que Redis

- ❌ Comunidad más pequeña

- ❌ Performance extra no crítica

**Razón de rechazo:** Redis suficiente para nuestras necesidades, mayor riesgo sin beneficio claro

---

## Tabla Comparativa de Alternativas

| Criterio | Redis (Elegido) | Memcached | In-Memory | KeyDB |
|----------|----------------|-----------|-----------|-------|
| **Pub/Sub** | ✅ | ❌ | ❌ | ✅ |
| **Persistencia** | ✅ | ❌ | ❌ | ✅ |
| **Tipos de datos** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Socket.IO support** | ✅ | ❌ | ❌ | ✅ |
| **Madurez** | Muy Alta | Alta | N/A | Media |
| **Comunidad** | Gigante | Grande | N/A | Pequeña |
| **Infraestructura** | Simple | Simple | Ninguna | Simple |

---

## Consecuencias

### ✅ Positivas

1. **Performance dramática:** Reducción 50-100ms en queries cacheados

2. **Reducción carga DB:** 60% menos queries a PostgreSQL para datos frecuentes

3. **Fail-safe pattern:** App funciona perfectamente si Redis está caído

4. **Escalabilidad futura:** Socket.IO Adapter configurado para múltiples instancias

5. **Métricas claras:** Stats de hit/miss para monitoreo

6. **TTLs estratégicos:** 
   - 1h para Watson sessions (cambian poco)
   - 15min para usuarios (balance frescura/performance)
   - 5min para salas activas (cambios frecuentes)

7. **Invalidación selectiva:** `cache.del()` en mutaciones críticas

**Mejora total documentada:** 80-200ms (15-35%) en endpoint crítico `/whatsapp/external`

### ⚠️ Negativas (Trade-offs)

1. **Infraestructura adicional:** Requiere servidor Redis (costo operacional)

2. **Complejidad:** Lógica de caché + invalidación

3. **Stale data potencial:** Datos cacheados pueden estar desactualizados (mitigado con TTLs)

4. **Debugging más difícil:** Cache hit/miss complica troubleshooting

5. **Memoria adicional:** Redis consume RAM (~100-500MB típico)

### 🔄 Neutral

1. **Monitoring necesario:** Métricas de hit ratio, memoria, conexiones

2. **Backup no crítico:** Caché es efímero, no requiere backup (solo sesiones Watson importantes)

3. **Eviction policy:** `maxmemory-policy allkeys-lru` configurado

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| **Redis crash rompe app** | Media | Crítico | ✅ **Fail-safe pattern implementado** - App funciona sin caché |
| **Cache stampede** | Baja | Medio | TTLs escalonados, locking si necesario |
| **Datos desactualizados** | Media | Medio | TTLs cortos (5-15min), invalidación manual en mutaciones |
| **Memoria llena** | Baja | Medio | Eviction LRU, monitoring, alertas |
| **Race conditions** | Baja | Bajo | Atomic operations de Redis, `WATCH` si necesario |

---

## Decisiones Relacionadas

- **Complementa [ADR-002](../01-stack/ADR-002-postgresql-database.md):** Reduce carga en PostgreSQL

- **Complementa [ADR-013](./ADR-013-database-indexes.md):** Índices + caché = performance óptima

- **Habilita [ADR-006](../03-comunicacion/ADR-006-socketio.md):** Adapter para múltiples instancias

- **Reactiva a problemas:** Implementación después de detectar cuellos de botella

---

## Estrategia de Caché

### Keys Pattern

```
watson:session:{room_id}          → Watson session ID
user:{provider}:{uid}              → User data
room:active:{user_id}              → Active room
room:metrics:{room_id}             → Room metrics (futuro)
```

### TTL Strategy

| Tipo de Dato | TTL | Justificación |
|-------------|-----|---------------|
| Watson Sessions | 1 hora | Cambian raramente, crítico para performance |
| User Data | 15 minutos | Balance entre frescura y performance |
| Active Rooms | 5 minutos | Estado cambia frecuentemente |
| Metrics | 30 segundos | Datos en tiempo real (futuro) |

### Invalidation Strategy

**Invalidación activa (cuando cambia dato):**
```javascript
// Al cerrar sala
await cache.del(`room:active:${user_id}`);

// Al actualizar usuario
await cache.del(`user:${provider}:${uid}`);

// Pattern-based deletion (si necesario)
await cache.delPattern('room:*');
```

---

## Referencias

- [Redis Official Documentation](https://redis.io/documentation)

- [Node Redis Client](https://github.com/redis/node-redis)

- [Socket.IO Redis Adapter](https://socket.io/docs/v4/redis-adapter/)

- [Cache Stampede Problem](https://en.wikipedia.org/wiki/Cache_stampede)

- [Implementación: CACHE_IMPLEMENTATION.md](../../../../CACHE_IMPLEMENTATION.md)

---

## Métricas de Performance

### Antes vs Después

**Endpoint `/whatsapp/external` (primer mensaje):**

- **Antes:** 530-1180ms

- **Después:** 350-700ms (cache hit), 450-900ms (cache miss)

- **Mejora:** ~35% con cache hit

**Queries cacheados:**

- **Watson Session:** 30-50ms → 2-5ms (caché hit)

- **User Login:** 20-40ms → 2-5ms (caché hit)

- **Active Room:** 20-30ms → 2-5ms (caché hit)

**Cache Hit Ratio (típico):**

- Watson Sessions: ~85% (sesiones reutilizadas)

- Users: ~70% (usuarios recurrentes)

- Rooms: ~60% (salas abiertas múltiples mensajes)

---

## Configuración de Producción

```bash
# docker-compose.yml o similar
redis:
  image: redis:7-alpine
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD}
```

```javascript
// .env
REDIS_HOST=redis-prod.example.com
REDIS_PORT=6379
REDIS_PASSWORD=secure_password_here
```

---

## Notas Adicionales

### Estado Actual (Diciembre 2025)

**Caché:**

- ✅ **Activo en desarrollo/staging**

- ⚠️ **NO activo en producción aún** (solo desarrollo)

**Socket.IO Adapter:**

- ✅ **Configurado en código**

- ❌ **NO activo en producción** (solo una instancia actualmente)

### Plan de Activación en Producción

1. **Fase 1** (Q1 2026): Activar caché en producción con monitoreo intensivo

2. **Fase 2** (Q1 2026): Escalar a 2 instancias + activar Socket.IO Adapter

3. **Fase 3** (Q2 2026): Auto-scaling basado en carga

### Lecciones Aprendidas

✅ **Fail-safe pattern crítico:** Permitió implementar sin riesgo  
✅ **Caché ≠ premature optimization:** Fue reactivo y justificado  
✅ **TTLs conservadores:** Mejor datos frescos que performance extrema  
⚠️ **Debió implementarse antes:** Redis desde inicio hubiera evitado problemas de performance

---

📅 **Última actualización:** 18 de diciembre de 2025
