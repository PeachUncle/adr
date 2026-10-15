# Pulley E2E Over API QA Decision

## Context

Durante el desarrollo se evaluaron dos enfoques para validar que el sistema funciona correctamente:
1. QA de API (tests que validan endpoints directamente)
2. E2E (tests que validan el sistema completo desde la UI)

## Decision

**E2E es la fuente de verdad obligatoria. QA de API es complementario, no suficiente.**

## Rationale

### Por qué QA de API no es suficiente

1. **No valida integración completa**: Los tests de API validan solo el backend, no la interacción frontend-backend
2. **No detecta problemas de UI**: Errores en formularios, validación, renderizado no se detectan
3. **No valida flujos de usuario**: Los usuarios interactúan con la UI, no directamente con APIs
4. **Falsos positivos**: API puede responder correctamente mientras la UI falla
5. **No valida configuración real**: Variables de entorno, URLs, permisos pueden estar mal configurados y API tests pasarían

### Por qué E2E es la fuente de verdad

1. **Valida el sistema completo**: Frontend, backend, base de datos, red, todo junto
2. **Ejercita flujos reales**: Simula exactamente lo que hace el usuario
3. **Detecta problemas de integración**: Errores que solo aparecen cuando todos los componentes trabajan juntos
4. **Evidencia objetiva**: Resultado binario (pass/fail) sin interpretación
5. **Valida configuración real**: Usa las mismas URLs, variables de entorno, permisos que producción

### Ejemplos de problemas que E2E detecta y API QA no

- **Formulario no hace submit**: API está bien, pero el form tiene `noValidate` faltante
- **Validación HTML bloqueando**: API acepta el dato, pero validación HTML previene el submit
- **Overlay interceptando clicks**: API funciona, pero el usuario no puede hacer click
- **Modal no montado**: API responde, pero el form no existe en DOM cuando se intenta usar
- **Errores no visibles**: API retorna error, pero la UI no lo muestra

## Criterio de Aceptación de Features

Un feature se considera **completo y estable** solo cuando:

1. ✅ **E2E tests pasan**: Todos los tests E2E del feature pasan
2. ✅ **Cobertura de flujos**: E2E cubre happy path y al menos un error case
3. ✅ **Tests determinísticos**: No hay flaky tests (pasan consistentemente)
4. ✅ **Validación contra producción/staging**: E2E se ejecuta contra el entorno que se desplegará

**NO es suficiente**:
- ❌ Solo tests unitarios pasando
- ❌ Solo tests de API pasando
- ❌ Build exitoso
- ❌ Validación manual aislada

## Implementation

### Estructura de tests

```
tests/
├── e2e/
│   ├── auth.spec.ts          # Flujos de autenticación
│   ├── movements.spec.ts     # CRUD de movimientos
│   └── emma.spec.ts          # Cálculo de Emma
└── api/
    └── endpoints.spec.ts     # Complementario, no reemplaza E2E
```

### Ejemplo de E2E como gate

```yaml
# .github/workflows/deploy.yml
- name: Run E2E Tests
  run: npm run test:e2e
  env:
    BASE_URL: ${{ secrets.STAGING_URL }}

- name: Deploy to Production
  if: success()  # Solo si E2E pasa
  run: vercel --prod
```

## QA de API como complemento

QA de API sigue siendo útil para:
- **Desarrollo rápido**: Validar endpoints durante desarrollo sin levantar UI completa
- **Debugging**: Aislar problemas de backend
- **Documentación**: Ejemplos de uso de APIs
- **Performance**: Tests de carga de APIs específicas

Pero **nunca reemplaza** E2E para validar que el sistema funciona.

## Status

Decision: CLOSED
Version: v1.0
Aplicable a: Todos los proyectos gobernados por IAS

