# 1. Create project

Date: 2024-03-24

## Status

Accepted

## Context
Se necesita disponer de un servicio que permita consultar precios y tarifas según el ID del producto, la cadena y una fecha de aplicación.

La estructura de la base de datos es la siguiente:
- BRAND_ID: foreign key de la cadena del grupo (1 = ZARA).
- START_DATE , END_DATE: rango de fechas en el que aplica el precio tarifa indicado.
- PRICE_LIST: Identificador de la tarifa de precios aplicable.
- PRODUCT_ID: Identificador código de producto.
- PRIORITY: Desambiguador de aplicación de precios. Si dos tarifas coinciden en un rago de fechas se aplica la de mayor prioridad (mayor valor numérico).
- PRICE: precio final de venta.
- CURR: iso de la moneda.

Y además se solicita testear estos casos:
- Test 1: petición a las 10:00 del día 14 del producto 35455   para la brand 1 (ZARA)
- Test 2: petición a las 16:00 del día 14 del producto 35455   para la brand 1 (ZARA)
- Test 3: petición a las 21:00 del día 14 del producto 35455   para la brand 1 (ZARA) 
- Test 4: petición a las 10:00 del día 15 del producto 35455   para la brand 1 (ZARA) 
- Test 5: petición a las 21:00 del día 16 del producto 35455   para la brand 1 (ZARA) 

## Decision

### Diseño
El diseño de esta API REST se basa en los principios de una Arquitectura Hexagonal, donde se prioriza inicialmente la 
definición de la capa de DOMINIO de la siguiente manera:
- Models: entidades y otras clases de valor.
- Services: interfaces y clases de implementación para los servicios de la aplicación.
- Providers: definiciones de los repositorios (puertos de entrada).
- Exceptions: clases de impl. para el manejo de excepciones personalizadas de la aplicación.
- Contracts: DTOs para el manejo de solicitudes/respuestas entre capas.

Para los adaptadores de infraestructura e interfaz de usuario se tiene en cuenta esta estructura:
- Controllers: implementación para el manejo de peticiones de agentes externos.
- Repositories: implementación para la consulta y manipulación de datos con sistemas de bases de datos y APIs externas.

### Scaffolding:
- CONFIG
- CONTROLLERS
- DOMAIN
  - MODELS
    - ENTITIES
    - ENUMS
    - CONSTANTS
  - SERVICES
  - PROVIDERS
  - CONTRACTS
  - EXCEPTIONS
- REPOSITORIES

### Dependencias
- Java 17
- Maven compiler plugin 3.11.0
- Spring-boot-starter-web 3.2.2
- Spring-boot-starter-test 3.2.2
- Mockito-junit-jupiter 5.1
- Spring-boot-starter-data-jpa (Hibernate + Spring Data JPA + Spring ORM)
- H2 Database 2.2.224
- Flyway core 10.7.1