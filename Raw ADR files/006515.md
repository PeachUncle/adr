# 0 - Uso de Plataforma de Contenedores DOCKER

* Status: accepted 
* Deciders: Equipo completo 
* Date: 6/7/2025, 5:30:18 p. m. 
* Template used: [MADR 3.0.0](https://adr.github.io/madr/) 

Technical Story: Estandarización de entornos, despliegue reproducible y gestión de múltiples servicios desacoplados.

## Context and Problem Statement

El sistema de bolsa de proyectos universitarios está compuesto por múltiples microservicios, micro frontends y servicios externos: autenticación con LinkedIn, formularios dinámicos, historial de proyectos, recomendación de candidatos, notificaciones, motores de búsqueda, mensajería, entre otros.

Todos estos módulos usan tecnologías distintas, lo que genera complejidades para ejecutar, mantener y desplegar el sistema de manera consistente, tanto en desarrollo como en producción.

¿Cómo podemos garantizar que el sistema funcione igual en todos los entornos y facilitar su despliegue modular, escalable y reproducible?

## Decision Drivers 

* Generación automática de candidatos compatibles para un proyecto → Algoritmos de recomendación deben funcionar como microservicio en un contenedor independiente, escalable.

* Visualización estructurada de perfiles compatibles con indicadores de compatibilidad → Necesita desacoplar backends y frontends para facilitar despliegues individuales.

* Recomendación de proyectos personalizados para los usuarios (eliminado) → Aunque eliminado, inicialmente motivó modularización, válida para el resto del sistema.

* Sistema de mensajería interna para conexión entre usuarios → Comunicación asincrónica y procesamiento desacoplado, ideal para contenerizar servicios RabbitMQ y websockets.



## Considered Options

* Opción 1: Usar Docker como plataforma de contenedores.
* Opción 2: Utilizar máquinas virtuales tradicionales para cada servicio.
* Opción 3: Instalar todos los componentes manualmente en cada máquina o entorno.
* Opción 4: Utilizar entornos serverless (funciones, FaaS) para cada módulo.

## Decision Outcome

Chosen option: "Usar Docker como plataforma de contenedores", porque permite empaquetar cada componente del sistema (microservicio o frontend) con sus propias dependencias, garantizando entornos consistentes y facilitando el despliegue modular, tanto en desarrollo como producción.
Es la única opción que cumple con todos los drivers, mantiene el desacoplamiento entre módulos y permite integración fluida con CI/CD, herramientas de testing y despliegue escalable.

### Positive Consequences 

* Estandarización de entornos de desarrollo para todo el equipo.
* Facilita testing local y pruebas de integración end-to-end.
* Despliegue automatizado mediante GitHub Actions, Heroku, Render, Railway u otros.
* Cada módulo puede ser desarrollado y desplegado de forma independiente.
* Compatibilidad con herramientas como docker-compose para levantar todo el sistema de forma orquestada.
* Reduce errores por diferencias entre entornos locales y productivos.


### Negative Consequences 

* Necesidad de aprender y gestionar archivos Dockerfile y docker-compose.yml.
* Consumo de recursos locales (RAM y CPU) si se levantan muchos contenedores.
* Complejidad inicial en configuración para servicios que requieren persistencia (como Firebase, PostgreSQL o Elasticsearch).
* No elimina completamente la necesidad de configuraciones individuales para los contenedores en entornos productivos.


## Pros and Cons of the Options 

### [Docker]

* Bueno, porque permite empaquetar y ejecutar microservicios con diferentes stacks (Node, Python, Java...).
* Bueno, porque facilita la integración de tecnologías como RabbitMQ, Elasticsearch, GraphQL Gateway, etc.
* Bueno, porque facilita despliegue e integración continua.

* Malo, porque agrega una curva de aprendizaje inicial.

### [Máquinas virtuales]

* Bueno, porque simula entornos reales.

* Malo, porque consume más recursos que Docker.
* Malo, porque es difícil automatizar y mantener múltiples máquinas.
* Malo, porque no se adapta bien a arquitecturas desacopladas.

### [Funciones Serverless]

* Bueno, para tareas muy pequeñas.

* Malo, porque dificulta tareas de larga duración o procesamiento intensivo (recomendaciones, integración con GraphQL, etc.)
* Malo, porque introduce latencia y complejidad adicional.

