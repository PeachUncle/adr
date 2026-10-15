# Pulley Emma Singleton Model Decision

## Context

Emma es un modelo de datos que representa el estado financiero actual del usuario (balance, ingresos, egresos proyectados). Durante el desarrollo se tomó la decisión de implementarlo como singleton en lugar de entidad persistente.

## Decision

Emma es un **singleton calculado**, no una entidad persistente en la base de datos.

## Rationale

### Por qué Emma es singleton

1. **Estado derivado**: Emma es el resultado de cálculos sobre Movements (movimientos reales), no un dato primario
2. **Consistencia garantizada**: Al calcularse siempre desde Movements, no puede desincronizarse
3. **Simplicidad operativa**: No requiere sincronización entre Emma y Movements
4. **Single source of truth**: Movements es la única fuente de verdad; Emma es una vista

### Qué persiste (supuestos)

Emma **SÍ persiste**:
- **Supuestos financieros**: Proyecciones de ingresos y egresos futuros
- **Configuración de cálculo**: Parámetros que afectan cómo se calcula el balance
- **Metadatos**: Fechas de último cálculo, versiones de supuestos

Estos datos se almacenan en una tabla dedicada (ej: `financial_assumptions` o similar).

### Qué NO persiste (dinero)

Emma **NO persiste**:
- **Balance actual**: Se calcula en tiempo real desde Movements
- **Ingresos/egresos históricos**: Ya están en Movements
- **Proyecciones calculadas**: Se recalculan cada vez que se consulta

### Relación con Movements reales

```
Movements (persistente)
    ↓
    ├─→ Cálculo en tiempo real
    │
    └─→ Emma (singleton calculado)
```

**Flujo**:
1. Movements se crean/modifican (persistencia real)
2. Emma se calcula al momento de consulta
3. Supuestos de Emma se persisten por separado
4. Balance de Emma = Suma de Movements + Proyecciones desde supuestos

## Implementation Pattern

```typescript
// Emma se calcula, no se lee de DB
class EmmaService {
  async getCurrentEmma(userId: string): Promise<Emma> {
    // 1. Obtener Movements reales
    const movements = await prisma.movement.findMany({
      where: { userId },
    });
    
    // 2. Obtener supuestos persistidos
    const assumptions = await prisma.financialAssumption.findFirst({
      where: { userId },
    });
    
    // 3. Calcular Emma
    return this.calculateEmma(movements, assumptions);
  }
  
  private calculateEmma(movements: Movement[], assumptions: Assumptions): Emma {
    const balance = movements.reduce((sum, m) => sum + m.amount, 0);
    const projectedIncome = this.projectIncome(assumptions);
    const projectedExpenses = this.projectExpenses(assumptions);
    
    return {
      balance,
      projectedIncome,
      projectedExpenses,
      // ... otros campos calculados
    };
  }
}
```

## Consequences

### Ventajas

- **Consistencia automática**: Imposible que Emma y Movements estén desincronizados
- **Menos complejidad**: No requiere triggers, jobs de sincronización, o lógica de actualización
- **Auditoría clara**: Siempre se puede recalcular Emma desde Movements para verificar

### Limitaciones

- **Performance**: Cálculo en tiempo real puede ser más lento que leer de tabla
- **Caché necesario**: Para sistemas con alto tráfico, puede requerir caché (invalidado cuando cambian Movements)

## Status

Decision: CLOSED
Version: v1.0
Aplicable a: Sistemas con modelo similar (estado derivado de entidades primarias)

