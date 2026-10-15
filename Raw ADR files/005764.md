# 0003. Adoptar Bootstrap 5 como Framework CSS

## Estado
**Aceptado** - 2025-11-22

## Contexto

El proyecto ALCAL necesitaba un framework CSS para:
- Diseño responsive
- Componentes UI consistentes (botones, forms, cards, tables)
- Sistema de grid
- Utilities de espaciado y colores

### Opciones Evaluadas

**Bootstrap 5**:
- Framework CSS más popular
- Componentes completos listos para usar
- Excelente documentación
- Grid responsive
- Compatible con Django

**Tailwind CSS**:
- Utility-first approach
- Muy customizable
- Requiere build process (PostCSS)
- Archivos más pequeños (con purge)

**Material UI / Materialize**:
- Diseño Material Design
- Componentes ricos
- Más opinado en diseño

**Pure CSS / Foundation**:
- Más ligeros que Bootstrap
- Menos componentes predefinidos

## Decisión

**Adoptar Bootstrap 5.3.2 como framework CSS principal**, complementado con sistema de diseño personalizado ALCAL Premium.

### Razones

1. **Simplicidad de integración**: Solo CDN, no requiere build process
2. **Componentes completos**: Cards, modals, dropdowns, navbars listos
3. **Compatibilidad Django**: Funciona perfectamente con templates Django
4. **Documentación**: Excelente docs en español e inglés
5. **Comunidad**: Soluciones disponibles para problemas comunes
6. **Responsive**: Grid system robusto y utilities responsive
7. **Accesibilidad**: ARIA labels y semántica correcta por defecto

### Por Qué NO Tailwind

- Requiere configuración de build (webpack/PostCSS)
- Más complejo de integrar con Django
- Curva de aprendizaje mayor
- Archivos HTML más verbosos

## Consecuencias

### Positivas

✅ **Desarrollo rápido**: Componentes listos para usar  
✅ **Consistencia visual**: Sistema predefinido de colores, espaciado, tipografía  
✅ **Responsive out-of-the-box**: `col-md-*`, `d-none d-lg-block`, etc.  
✅ **Iconos incluidos**: Bootstrap Icons (+ FontAwesome legacy)  
✅ **JavaScript incluido**: Modals, dropdowns, tooltips funcionan sin código adicional  
✅ **Fácil personalización**: Variables CSS y clases custom `alcal-*`  

### Negativas

⚠️ **Tamaño**: ~150KB CSS (mitigado con CDN y cache)  
⚠️ **Look generic**: Muchos sitios usan Bootstrap (mitigado con ALCAL Premium)  
⚠️ **Dependencia externa**: Si CDN cae, estilos no cargan (mitigado con fallback local)

### Sistema ALCAL Premium

Para diferenciar el diseño, creamos **ALCAL Premium Design System**:

**Archivo**: `static/css/alcal-premium.css`

**Elementos custom**:
```css
/* Colores primarios ALCAL */
.btn-alcal-primary { background: linear-gradient(...); }
.text-alcal-primary { color: #2563eb; }
.bg-alcal-primary { background: #2563eb; }

/* Sidebar custom */
.sidebar { /* estilos propios */ }
.sidebar-nav { /* estilos propios */ }

/* Cards premium */
.card-premium { 
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border-radius: 12px;
}
```

**Carga en templates**:
```html
<!-- Bootstrap 5 CDN -->
<link href="https://cdn.jsdelivr.net/.../bootstrap.min.css" rel="stylesheet">

<!-- ALCAL Premium (override de Bootstrap) -->
<link rel="stylesheet" href="{% static 'css/alcal-premium.css' %}">
```

### Impacto en el Código

**Template base** (`base_modern.html`):
- Carga Bootstrap 5.3.2 desde CDN
- Carga Bootstrap Icons
- Carga alcal-premium.css
- Incluye bootstrap.bundle.min.js (con Popper)

**Componentes usados**:
- `.card`, `.card-header`, `.card-body`, `.card-footer`
- `.table`, `.table-hover`, `.table-responsive`
- `.btn`, `.btn-primary`, `.btn-outline-*`, `.btn-sm`
- `.form-control`, `.form-select`, `.form-label`
- `.alert`, `.alert-success`, `.alert-danger`
- `.badge`, `.bg-success`, `.bg-danger`
- Grid: `.container`, `.row`, `.col-md-*`

**Reglas de uso**:
- **TODOS los templates** heredan de `base_modern.html`
- **NO usar estilos inline** (usar clases de Bootstrap o ALCAL)
- **Preferir Bootstrap Icons** (`bi bi-*`) sobre FontAwesome

## Alternativas Consideradas y Descartadas

| Framework | Por qué se descartó |
|-----------|---------------------|
| **Tailwind CSS** | Requiere build process, más complejo para Django |
| **Bulma** | Menos componentes JavaScript, comunidad más pequeña |
| **Foundation** | Menos popular, documentación inferior |
| **Material UI** | Muy opinado, difícil de personalizar |
| **Pure CSS** | Muy minimalista, faltan componentes |

## Decisiones Futuras

Si el proyecto crece significativamente, considerar:
- Migrar a Tailwind + PostCSS para mayor control
- Implementar theme switcher (light/dark)
- Crear biblioteca de componentes Vue/React con Bootstrap

## Referencias

- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- `static/css/alcal-premium.css` - Sistema de diseño custom
- `templates/base_modern.html` - Template base con Bootstrap
- `.agent/project_rules.md` - Sección "Frontend & Design System"
