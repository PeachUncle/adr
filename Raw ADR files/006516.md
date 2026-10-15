# 1 - Uso de GraphQL Federation como Gateway de APIs

* Status: accepted 
* Deciders: Todo el  Equipo 
* Date: 6/7/2025, 6:13:59 p. m. 
* Template used: [MADR 3.0.0](https://adr.github.io/madr/) 

Technical Story: El sistema se compone de múltiples microservicios independientes y desacoplados, tanto del lado del backend como del frontend (micro frontends). Se necesita una forma flexible, eficiente y escalable de unificar la comunicación entre estos servicios, especialmente para el consumo desde la interfaz de usuario.

## Context and Problem Statement

El sistema requiere consumir datos de diferentes dominios (usuarios, perfiles, proyectos, recomendaciones, historial, mensajería, etc.) alojados en distintos microservicios. El frontend necesita acceder de manera eficiente y unificada a estos datos sin tener que hacer múltiples llamadas REST ni preocuparse por la ubicación real de cada servicio.

¿Cómo permitir que la UI consuma los datos necesarios de manera centralizada, sin acoplarse a los microservicios subyacentes ni sobrecargar al equipo con múltiples contratos REST?

## Decision Drivers 

* D02 - Generación automática de candidatos compatibles para un proyecto → La lógica de recomendaciones está desacoplada, y necesita acceder a perfiles y proyectos.
* D03 - Visualización estructurada de perfiles compatibles con indicadores de compatibilidad → Se requiere unificar la información entre módulos para mostrar resultados ricos.
* D04 - Recomendación de proyectos personalizados para usuarios (descartado) → Originalmente requería orquestación de múltiples dominios (aún relevante para diseño general).
* D05, D06 - Mensajería interna e historial de proyectos → Distintos servicios deben compartir identificadores y perfiles de usuario.
* D07 - Formulario dinámico de proyectos → La estructura del formulario depende de datos de otros módulos y debe poder evolucionar sin romper la API.

## Considered Options

* Opción 1: GraphQL Federation
* Opción 2: REST API Gateway (como Express Gateway, Zuul)
* Opción 3: GraphQL monolítico con resolvers en un solo backend
* Opción 4: gRPC entre microservicios + frontend con REST central

## Decision Outcome

Chosen option: GraphQL Federation, porque permite mantener la independencia y modularidad de cada subdominio (perfil, historial, recomendación, mensajería), mientras los unifica bajo un esquema común para el frontend.

### Positive Consequences 

* Unificación de múltiples microservicios bajo una sola API GraphQL para el frontend.
* Escalabilidad: cada subdominio mantiene su propio esquema y puede escalar o actualizarse de forma independiente.
* Menor acoplamiento entre frontend y backend.
* Contratos bien definidos para cada subdominio, ideal para equipos distribuidos.
* Integración natural con Apollo Client en el frontend (React).
* Facilita documentación automática de todo el sistema.

### Negative Consequences 

* Requiere aprendizaje inicial en Federation (esquemas, subgraphs, gateway).
* Mayor complejidad de infraestructura si no se orquesta adecuadamente.
* No todos los tipos de validación pueden hacerse de forma cruzada entre subdominios (requiere diseño anticipado).

## Pros and Cons of the Options 

### [GraphQL Federation]

* Bien, porque cada módulo (perfil, historial, recomendación) mantiene su propio schema.
* Bien, porque permite evolución y despliegue independiente.
* Bien, porque Apollo Gateway resuelve automáticamente la unión de esquemas.

* Mal, porque requiere tooling específico (Apollo, URQL, o similares).

### [REST API Gateway]

* Bien, porque es simple de implementar.

* Mal, por su escasa flexibilidad para evolución de esquemas complejos.
* Mal, porque el frontend necesita múltiples llamadas o construir lógica adicion

### [option 3]


* Good, because [argument a]
* Good, because [argument b]
* Bad, because [argument c]
* … <!-- numbers of pros and cons can vary -->

## Links 

* https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/federation