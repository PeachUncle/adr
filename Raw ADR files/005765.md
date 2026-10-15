# 0004. Soporte Multi-Turno en Toma de Asistencias

## Estado
**Aceptado** - 2025-11-22

## Contexto

### Problema Original

El sistema ALCAL originalmente permitía tomar asistencia de un curso para **un solo turno a la vez**:

```
Usuario selecciona:
- Fecha: 2025-11-22
- Curso: 1° A - Técnico en Programación
- Turno: Mañana    ← Solo un turno

Resultado: 
- 30 alumnos × 1 turno = 30 registros de Asistencia
```

**Limitación**: Si el curso tiene clases en Mañana y Tarde, el usuario debe:
1. Tomar asistencia para Mañana
2. Volver a cargar la página
3. Tomar asistencia para Tarde

**Problema**: Proceso lento, propenso a errores, mala UX.

### Caso de Uso Real

**Escenario**: Curso "1° B - Bachiller" tiene clases todos los días en:
- Turno Mañana (8:00 - 12:00)
- Turno Tarde (13:00 - 17:00)

El preceptor necesita marcar asistencia para ambos turnos simultáneamente porque algunos alumnos:
- Estuvieron presente en Mañana pero faltaron a Tarde
- Llegaron tarde solo a un turno
- Tienen justificativo para un turno específico

## Decisión

**Implementar soporte multi-turno**: Permitir seleccionar **múltiples turnos** simultáneamente al tomar asistencia por curso.

### Implementación

#### 1. Template: Select Múltiple

```html
<!-- tomar_asistencia_curso.html -->
<select id="turno" name="turno_id" class="form-select" multiple required>
    <option value="">-- Seleccione Turnos --</option>
    {% for turno in turnos %}
    <option value="{{ turno.id }}">{{ turno.get_nombre_display }}</option>
    {% endfor %}
</select>
```

**UX**: Usuario mantiene `Ctrl` (Windows/Linux) o `Cmd` (Mac) y selecciona múltiples turnos.

#### 2. JavaScript: Enviar IDs como CSV

```javascript
function cargarAlumnos() {
    const turnoSelect = document.getElementById('turno');
    const turnoIds = Array.from(turnoSelect.selectedOptions)
        .map(o => o.value)
        .filter(v => v)
        .join(',');  // "1,2" o "1,2,3"
    
    fetch(`/lista_alumnos_curso/?curso_id=${cursoId}&turno_id=${turnoIds}`)
        .then(...)
}
```

#### 3. Vista: Procesar CSV de Turnos

```python
@login_required
def lista_alumnos_curso(request):
    turno_ids_param = request.GET.get('turno_id')  # "1,2,3"
    turno_ids = []
    if turno_ids_param:
        turno_ids = [int(t) for t in turno_ids_param.split(',') if t.isdigit()]
    
    # Buscar asistencias existentes para TODOS los turnos
    if turno_ids:
        asistencias = Asistencia.objects.filter(
            curso=curso,
            fecha=fecha,
            turno_id__in=turno_ids  # Query con __in
        )
```

#### 4. Guardado: Crear Asistencia por Turno

```python
@login_required
def guardar_asistencia_curso(request):
    turno_id_str = request.POST.get('turno_id')  # "1,2"
    turno_ids = [int(t) for t in turno_id_str.split(',') if t.isdigit()]
    
    with transaction.atomic():
        for turno_id in turno_ids:
            turno = get_object_or_404(Turno, pk=turno_id)
            for key, value in request.POST.items():
                if key.startswith('asistencia_'):
                    alumno_id = key.split('_')[1]
                    codigo_str = value
                    
                    Asistencia.objects.update_or_create(
                        alumno=alumno,
                        fecha=fecha,
                        turno=turno,  # Crea una fila por turno
                        defaults={'curso': curso, 'codigo': codigo, ...}
                    )
```

**Resultado**: Para 30 alumnos × 2 turnos = **60 registros de Asistencia** creados en una sola operación.

## Consecuencias

### Positivas

✅ **Eficiencia**: Un solo formulario para múltiples turnos  
✅ **UX mejorada**: Menos clics, menos tiempo  
✅ **Menos errores**: No hay que recordar qué turno ya se procesó  
✅ **Flexibilidad**: Usuario elige 1, 2 o 3 turnos según necesidad  
✅ **Atomicidad**: `transaction.atomic()` garantiza que todo se guarda o nada  
✅ **Carga de existentes**: Si ya hay asistencias, se muestran para cualquier turno seleccionado  

### Negativas

⚠️ **UX del select múltiple**: No es obvio para usuarios cómo seleccionar múltiples (requiere Ctrl/Cmd)  
⚠️ **Validación client-side**: Debe verificar que al menos 1 turno esté seleccionado  
⚠️ **Performance**: Guardar 3 turnos × 40 alumnos = 120 inserts (mitigado con `update_or_create` y transaction)  

### Mitigaciones

**UX del select múltiple**:
- Añadir tooltip explicativo: "Mantén Ctrl/Cmd para seleccionar varios"
- Considerar futuro: Cambiar a checkboxes para mejor UX
- Agregar indicador visual de cuántos turnos seleccionados

**Performance**:
- Usar `bulk_create()` si no se necesita actualizar existentes
- Añadir índice de BD en `(alumno, fecha, turno)` para `update_or_create`
- Mostrar loading spinner durante guardado

## Casos de Uso Soportados

### Caso 1: Asistencia Normal (1 Turno)
Usuario selecciona solo "Mañana" → 30 alumnos × 1 turno = 30 registros.

### Caso 2: Asistencia Completa (2 Turnos)
Usuario selecciona "Mañana" y "Tarde" → 30 alumnos × 2 turnos = 60 registros.

### Caso 3: Escuela Nocturna (3 Turnos)
Usuario selecciona "Mañana", "Tarde" y "Noche" → 30 alumnos × 3 turnos = 90 registros.

### Caso 4: Actualización Parcial
Usuario ya guardó asistencia para "Mañana". Vuelve a cargar seleccionando solo "Tarde" → Solo actualiza turnos de Tarde.

## Decisiones Relacionadas

- **ADR-0005**: Cierre parcial de asistencias (permite cerrar turnos independientemente)
- **ADR-0002**: URLs centralizadas (todas las rutas de asistencia en `alcal/urls.py`)

## Alternativas Consideradas

### Opción A: Modal por Turno
Abrir modal separado para cada turno.
**Descartado**: Más clics, peor UX.

### Opción B: Tabs por Turno
Tabs en el formulario, cada tab un turno.
**Descartado**: No permite guardar múltiples turnos simultáneamente.

### Opción C: Checkboxes para Turnos
Reemplazar `<select multiple>` con checkboxes.
**Pendiente**: Mejor UX, considerar para futuro.

## Referencias

- `asistencias/views.py` - Funciones `lista_alumnos_curso`, `guardar_asistencia_curso`
- `asistencias/templates/asistencias/tomar_asistencia_curso.html` - Select múltiple
- `.agent/project_rules.md` - Sección "Características Específicas del Proyecto"
- `ARCHITECTURE.md` - Sección "Flujos Principales"
