# ADR-005: Testing Policy and Quality Assurance Strategy

## Status
Accepted

## Context
ValidaHub precisa de uma política de testes robusta que garanta qualidade do código sem criar gargalos no desenvolvimento. Após análise, identificamos problemas comuns em estratégias de teste:

### Problemas Identificados
1. **Gaming de cobertura**: Times inflando métricas com testes triviais
2. **Flaky tests**: Testes intermitentes bloqueando PRs e quebrando confiança
3. **Gargalos no CI**: Pipelines lentos prejudicando produtividade
4. **False positives**: Alta cobertura mas bugs em produção
5. **Falta de determinismo**: Testes passando/falhando aleatoriamente

### Requisitos
- Coverage real que previne bugs, não apenas números altos
- Testes rápidos e confiáveis que não bloqueiam desenvolvimento
- Detecção precoce de regressões e problemas de segurança
- Suporte para múltiplos marketplaces e formatos de dados
- Compliance com LGPD e segurança de dados

## Decision

Adotaremos uma política de testes **pragmática e opinativa** com foco em:

### 1. Coverage Inteligente (Anti-Gaming)
```yaml
Coverage Strategy:
  Diff Coverage: 85% (blocking PR)      # Foco no que mudou
  Directory-based:                       # Targets por criticidade
    - src/services/: 90%
    - src/validators/: 95% 
    - src/domain/: 90%
  Mutation Score: 80% (critical paths)  # Pega false positives
```

### 2. Anti-Flakiness Policy
```yaml
Flaky Management:
  Detection: 3+ intermittent failures in 7 days
  Quarantine: Separate job (non-blocking)
  SLA: 7 days to fix
  Auto-disable: After 30 days
  Target: <0.5% E2E, <0.1% unit
```

### 3. Testing Pyramid
```
     /\
    /  \  E2E (5%) - Critical journeys only
   /____\ Integration (25%) - API, DB, contracts
  /      \ Unit (70%) - Business logic, fast
```

### 4. Test Types & Tools

#### Backend (Python)
- **Unit**: pytest + pytest-xdist (parallel)
- **Coverage**: diff-cover (PR) + mutmut (mutation)
- **Determinism**: freezegun + faker (fixed seeds)
- **Contracts**: pact-python + OpenAPI validation
- **Security**: bandit + semgrep + pip-audit
- **Performance**: locust (smoke PR, full nightly)

#### Frontend (TypeScript)
- **Unit**: Vitest + Testing Library
- **E2E**: Playwright + axe-core (a11y)
- **Visual**: Chromatic/Percy (if needed)
- **Contracts**: MSW + OpenAPI client validation
- **Mutation**: Stryker

### 5. CI/CD Strategy
```yaml
Pipeline:
  PR Checks: <8 min target
    - Unit tests (parallel)
    - Diff coverage check
    - Contract validation
    - Security scan (SAST)
    - Performance smoke
  
  Nightly:
    - Full E2E suite
    - Mutation testing
    - Load testing
    - DAST scan
    - Dependency audit
  
  Ephemeral Env: Preview per PR (Vercel + Neon branch)
```

### 6. Operational Metrics & SLAs

| Metric | Target | Action |
|--------|--------|--------|
| Lead Time (PR → Green) | <10 min | Optimize |
| MTTR (Pipeline Fix) | <1 hour | Alert |
| Change Failure Rate | <5% | Review |
| Flaky Rate | <0.5% E2E, <0.1% unit | Quarantine |
| Critical Path Coverage | ≥95% | Block |

## Consequences

### Positive
- ✅ **Real quality**: Mutation testing catches fake coverage
- ✅ **Fast feedback**: Parallel tests, smart reruns
- ✅ **No flaky blocks**: Quarantine system prevents frustration  
- ✅ **Security built-in**: SAST/DAST/SBOM automated
- ✅ **Deterministic**: Fixed seeds, frozen time
- ✅ **Contract safety**: API changes caught early

### Negative
- ❌ **Initial setup cost**: ~2 weeks to implement fully
- ❌ **Learning curve**: Team needs training on new tools
- ❌ **More dependencies**: Additional test libraries
- ❌ **Storage needs**: Test artifacts and reports

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-engineering tests | High | Start simple, add complexity as needed |
| Slow adoption | Medium | Pair programming, examples, documentation |
| Flaky test accumulation | High | Auto-quarantine + SLA enforcement |
| Coverage gaming | Medium | Mutation testing + code review |

## Implementation Plan

### Phase 1: Foundation (Week 1)
- [x] Testing policy documentation
- [x] CI/CD pipeline setup
- [x] Pytest configuration
- [x] Basic fixtures and examples
- [ ] Install test dependencies

### Phase 2: Coverage & Quality (Week 2)
- [ ] Diff coverage implementation
- [ ] Mutation testing setup
- [ ] Contract tests (OpenAPI)
- [ ] Deterministic fixtures

### Phase 3: Anti-Flakiness (Week 3)
- [ ] Quarantine system
- [ ] Flaky detection automation
- [ ] Performance monitoring
- [ ] Ephemeral environments

### Phase 4: Security & Performance (Week 4)
- [ ] SAST/DAST integration
- [ ] Load testing setup
- [ ] Accessibility tests
- [ ] Visual regression (if needed)

## References

### External
- [Google Testing Blog - Flaky Tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
- [Martin Fowler - Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Mutation Testing](https://github.com/boxed/mutmut)
- [Contract Testing with Pact](https://docs.pact.io/)

### Internal
- [TESTING_POLICY.md](../TESTING_POLICY.md) - Detailed implementation guide
- [test.yml](.github/workflows/test.yml) - CI/CD configuration
- [pytest.ini](apps/api/pytest.ini) - Test configuration

## Decision Makers
- **Author**: Claude (AI Assistant)
- **Reviewed by**: Engineering Team
- **Approved by**: Tech Lead
- **Date**: 2024-08-24

## Notes

### Key Insights from Review
> "Coverage global de 80% pode ser 'jogada'. Foco em diff coverage e diretórios críticos"

> "Flakiness policy com quarantine evita frustração sem ignorar problemas"

> "Mutation testing pega falsos positivos de cobertura"

### Success Criteria
1. **No flaky tests blocking PRs** after 30 days
2. **Mutation score ≥80%** on critical paths  
3. **Lead time <10 min** for 90% of PRs
4. **Zero security criticals** in production
5. **95% developer satisfaction** with test suite

### Future Considerations
- **AI-powered test generation** for edge cases
- **Chaos engineering** for resilience testing
- **Property-based testing** expansion (Hypothesis)
- **Cross-browser visual testing** automation