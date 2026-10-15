# ADR-004: API-First Design for Future SDK Development

**Status:** Accepted  
**Date:** 2025-06-12  
**Deciders:** Platform Team, Architecture Team  
**Consulted:** Development Team  
**Informed:** All Engineers  

## Context

Our shared services need to be designed with future flexibility in mind. We anticipate the need to:

- Package services as standalone npm packages
- Generate SDKs for different programming languages
- Support third-party integrations
- Enable external API access (with proper authentication)
- Maintain backward compatibility as the platform evolves

### Requirements

- **API-First Design**: All functionality must be available via well-documented APIs
- **SDK Generation**: APIs should be designed to support automatic SDK generation
- **Versioning**: Clear API versioning strategy for backward compatibility
- **Documentation**: Comprehensive, interactive API documentation
- **Type Safety**: Strong typing that can be exported to SDKs
- **Packageability**: Services should be packageable as standalone modules
- **Standardization**: Consistent API patterns across all services

## Decision

We will implement an API-first design using:

1. **OpenAPI 3.0 Specification** for all APIs
2. **Automatic SDK Generation** from OpenAPI specs
3. **Semantic Versioning** for API versions
4. **Modular Service Design** for packageability
5. **Comprehensive Documentation** with interactive examples
6. **Type-Safe Client Libraries** for TypeScript and JavaScript

## Implementation Strategy

### 1. OpenAPI 3.0 Specification

All APIs will be documented using OpenAPI 3.0 with comprehensive schemas:

```typescript
// services/shared-services/src/main.ts
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  const config = new DocumentBuilder()
    .setTitle('Internal Tools Shared Services API')
    .setDescription('Comprehensive API for internal tooling platform')
    .setVersion('1.0.0')
    .addBearerAuth()
    .addApiKey(
      { type: 'apiKey', name: 'X-API-Key', in: 'header' },
      'api-key'
    )
    .addServer('http://localhost:3001', 'Development')
    .addServer('https://api.company.com', 'Production')
    .build();
  
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);
  
  // Export OpenAPI spec for SDK generation
  const fs = require('fs');
  fs.writeFileSync('./openapi.json', JSON.stringify(document, null, 2));
  
  await app.listen(3001);
}
```

### 2. SDK Generation Strategy

Automated SDK generation for multiple languages:

```json
{
  "scripts": {
    "generate:openapi": "npm run build && node dist/generate-openapi.js",
    "generate:sdk:typescript": "openapi-generator-cli generate -i openapi.json -g typescript-fetch -o packages/shared-client/generated",
    "generate:sdk:javascript": "openapi-generator-cli generate -i openapi.json -g javascript -o sdks/javascript",
    "generate:sdk:python": "openapi-generator-cli generate -i openapi.json -g python -o sdks/python",
    "generate:sdk:go": "openapi-generator-cli generate -i openapi.json -g go -o sdks/go",
    "generate:sdks": "npm run generate:openapi && npm run generate:sdk:typescript && npm run generate:sdk:javascript && npm run generate:sdk:python && npm run generate:sdk:go"
  }
}
```

### 3. API Versioning Strategy

Semantic versioning with backward compatibility:

```typescript
// Version management
const API_VERSIONS = {
  v1: {
    version: '1.0.0',
    deprecated: false,
    supportedUntil: null,
  },
  v2: {
    version: '2.0.0',
    deprecated: false,
    supportedUntil: null,
    changes: [
      'Breaking: User roles changed from string to object',
      'Added: New notification types',
    ]
  }
};

// Versioned controllers
@Controller('api/v1/users')
export class UsersV1Controller {
  // v1 implementation
}

@Controller('api/v2/users')
export class UsersV2Controller {
  // v2 implementation with new features
}
```

### 4. Package Structure for SDK Distribution

```typescript
// packages/auth-service/package.json
{
  "name": "@internal-tools/auth-service",
  "version": "1.0.0",
  "description": "Authentication service for internal tools platform",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "peerDependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/jwt": "^10.0.0"
  }
}

// Packageable auth service
export { AuthModule } from './auth.module';
export { AuthService } from './auth.service';
export { AuthController } from './auth.controller';
export * from './dto';
export * from './guards';
```

## Benefits

### API-First Benefits
- **Consistent Interface**: All functionality available via documented APIs
- **Early Integration**: Frontend and backend teams can work in parallel
- **Third-Party Integration**: External systems can integrate easily
- **Testing**: APIs can be tested independently of implementation

### SDK Generation Benefits
- **Multi-Language Support**: Automatic SDK generation for various languages
- **Type Safety**: Generated SDKs include full type information
- **Consistency**: All SDKs have the same interface and behavior
- **Maintenance**: SDKs stay in sync with API changes automatically

### Packageability Benefits
- **Modular Distribution**: Services can be distributed as npm packages
- **Flexible Deployment**: Services can be deployed independently
- **Reusability**: Services can be used in different contexts
- **Version Management**: Independent versioning for each service

## Consequences

### Positive
- **Future-Proof**: Easy to add new languages and platforms
- **Developer Experience**: Excellent tooling and documentation
- **Integration-Ready**: Third-party systems can integrate easily
- **Consistent APIs**: Uniform patterns across all services
- **Automatic Documentation**: Always up-to-date API documentation

### Negative
- **Initial Complexity**: More setup required for API-first design
- **Generated Code**: SDK code may not be perfectly optimized
- **Maintenance Overhead**: Need to maintain SDK generation process

### Mitigations
- **Tooling Investment**: Build good tooling for SDK generation
- **Documentation**: Comprehensive guides for SDK usage
- **Testing**: Automated testing of generated SDKs
- **Community**: Involve community in SDK improvement

## Review Date

This design will be reviewed in 6 months (December 2025) to assess:
- SDK adoption and usage
- API consistency and quality
- Developer satisfaction with generated SDKs
- Maintenance overhead