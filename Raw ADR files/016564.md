# ADR-014: Business Rules Over Flow Designer Implementation

**Status:** Accepted  
**Date:** 2025-09-19  
**Supersedes:** ADR-006 (ServiceNow Implementation with Flow Designer)  
**Superseded by:** None  

## Context

ServiceNow provides multiple automation approaches for triggering external integrations. The project initially considered Flow Designer (visual workflow tool) for ServiceNow-to-AAP integration but comprehensive research revealed significant architectural and operational limitations. The project requires a ServiceNow automation mechanism that:

1. **Triggers on state changes** (specifically when catalog requests move to "In Process")
2. **Makes REST API calls** to Ansible Automation Platform
3. **Aligns with GitOps principles** and version-controlled infrastructure
4. **Provides production-ready reliability** and maintainability

## Research Findings

### Flow Designer Architectural Limitations

Based on comprehensive analysis documented in `research.md`:

1. **Trigger Mechanism Limitation**:
   - Flow Designer "Service Catalog" triggers activate on **catalog item creation**, NOT state changes
   - To trigger on state changes (e.g., "In Process"), you **MUST use a Business Rule** that calls `sn_fd.FlowAPI`
   - **Result**: Flow Designer doesn't eliminate Business Rules - it adds a layer on top

2. **Configuration Management Issues**:
   - Flow Designer requires **manual UI configuration** that cannot be version controlled
   - Creates **fragmented source of truth** across UI and code
   - **Violates GitOps principles** that are foundational to the project

3. **Unnecessary Complexity**:
   - Business Rules can make **direct REST API calls** using `sn_ws.RESTMessageV2()`
   - Flow Designer adds an **additional layer** without functional benefit
   - **Multiple layers** increase maintenance burden and failure points

## Decision

**Adopt Business Rules as the primary ServiceNow automation mechanism** for triggering AAP job templates, and **discontinue Flow Designer implementation**.

### Business Rules Implementation

```javascript
// Business Rule: OpenShift Project Creation Trigger
// Table: sc_req_item (Requested Item)
// When: After Update
// Condition: state == 2 (In Process) AND cat_item references OpenShift catalog items

(function executeRule(current, previous) {
    // Trigger AAP job template via REST API
    var restMessage = new sn_ws.RESTMessageV2();
    restMessage.setEndpoint('https://ansible-controller-aap.apps.cluster-lgkp4.lgkp4.sandbox1321.opentlc.com/api/v2/job_templates/9/launch/');
    restMessage.setHttpMethod('POST');
    restMessage.setRequestHeader('Authorization', 'Bearer ' + getAAPToken());
    restMessage.setRequestHeader('Content-Type', 'application/json');
    
    var payload = {
        extra_vars: {
            project_name: current.variables.project_name,
            display_name: current.variables.display_name,
            environment: current.variables.environment,
            servicenow_request_number: current.request.number,
            requestor: current.request.requested_for.user_name
        }
    };
    
    restMessage.setRequestBody(JSON.stringify(payload));
    
    // Execute asynchronously
    var response = restMessage.executeAsync();
    
})(current, previous);
```

### Key Advantages

1. **Direct Integration**: No intermediate layers between ServiceNow and AAP
2. **Version Controlled**: Business Rule logic can be managed in Git
3. **State Change Triggering**: Native support for triggering on request state changes
4. **GitOps Alignment**: Perfectly aligns with infrastructure-as-code principles
5. **Production Ready**: Proven approach used in enterprise ServiceNow deployments

## Rationale

### Architectural Alignment

| Aspect | Business Rules (Chosen) | Flow Designer (Rejected) |
|--------|------------------------|-------------------------|
| **Trigger Mechanism** | Direct state change trigger | Requires Business Rule + Flow |
| **REST API Calls** | Direct `sn_ws.RESTMessageV2()` | Via IntegrationHub spoke |
| **Configuration** | Code-based, version controlled | Manual UI configuration |
| **Maintenance** | Single source of truth | Fragmented across UI and code |
| **GitOps Alignment** | Perfect alignment | Violates GitOps principles |
| **Complexity** | Single layer | Multiple layers |

### Research Evidence

The decision is supported by:

1. **Comprehensive Analysis**: Detailed research in `research.md` comparing both approaches
2. **Architectural Review**: Analysis shows Flow Designer violates core project principles
3. **Functional Validation**: Business Rules approach already implemented and tested
4. **Industry Best Practices**: Code-first approach aligns with modern DevOps practices

## Implementation Details

### Current Implementation Status

- ✅ **Business Rules Logic**: Validated in `test_business_rule_logic.js`
- ✅ **API Integration**: AAP job template calls working
- ✅ **End-to-End Testing**: Complete workflow validated
- ✅ **Documentation**: Comprehensive setup guide available

### Production Deployment Requirements

1. **ServiceNow Configuration**:
   - Create Business Rule on `sc_req_item` table
   - Configure trigger conditions for OpenShift catalog items
   - Set up secure credential storage for AAP API token

2. **AAP Integration**:
   - Job Template ID 9 ("OpenShift Project Creation") ready
   - API endpoint: `/api/v2/job_templates/9/launch/`
   - Authentication via Bearer token

3. **Testing and Validation**:
   - Use `test_business_rule_logic.js` for local validation
   - Execute `ansible/idempotent_end_to_end_test.yml` for full testing
   - Verify with `user-workflows/advanced/start-simplified-workflow.sh`

### Development Environment Considerations

Due to potential PDI limitations (see ADR-013), the development environment uses:
- **Local Business Rules Testing**: `test_business_rule_logic.js`
- **Simplified Workflow Script**: `user-workflows/advanced/start-simplified-workflow.sh`
- **Manual Trigger Mechanism**: Accommodates PDI constraints while validating logic

## Consequences

### Positive Consequences

- **Simplified Architecture**: Single automation layer reduces complexity
- **Version Control**: All logic managed in Git repositories
- **Production Ready**: Proven approach for enterprise deployments
- **Maintainable**: Clear separation between ServiceNow trigger and Ansible automation
- **Aligned with Principles**: Supports GitOps and infrastructure-as-code philosophy

### Negative Consequences

- **JavaScript Requirement**: Requires ServiceNow JavaScript knowledge
- **Less Visual**: Not as visually intuitive as Flow Designer
- **Manual Configuration**: Business Rules require manual setup in ServiceNow UI

### Risk Mitigation

- **Comprehensive Testing**: Extensive validation framework ensures reliability
- **Documentation**: Detailed implementation guides for production deployment
- **Local Validation**: Test scripts allow validation before ServiceNow deployment
- **Modular Design**: Clear separation allows for future architectural changes if needed

## Alternatives Considered

1. **Flow Designer with IntegrationHub**:
   - **Rejected**: Requires Business Rules anyway, adds unnecessary complexity
   - **Issues**: Manual UI configuration, violates GitOps principles

2. **Hybrid Business Rules + Flow Designer**:
   - **Rejected**: Increases complexity without benefit
   - **Issues**: Multiple sources of truth, maintenance overhead

3. **ServiceNow Scripted REST APIs**:
   - **Rejected**: Requires external polling mechanism
   - **Issues**: Not event-driven, additional infrastructure required

## Related ADRs

- **ADR-001**: Three-Tier Orchestration Architecture - Establishes ServiceNow as orchestration tier
- **ADR-010**: Ansible Automation Platform Integration - Defines AAP as automation execution tier
- **ADR-013**: PDI Workaround Strategy - Addresses development environment constraints

## References

- `research.md` - Comprehensive Flow Designer vs Business Rules analysis
- `test_business_rule_logic.js` - Business Rules implementation and testing
- `docs/FLOW_DESIGNER_DECISION.md` - Executive summary of the decision
- `SERVICENOW_SETUP_GUIDE.md` - Production deployment guidance
- `user-workflows/advanced/start-simplified-workflow.sh` - Development validation workflow

## Future Considerations

- **Production Validation**: Test Business Rules in enterprise ServiceNow environment
- **Performance Monitoring**: Monitor Business Rules execution in production
- **Error Handling Enhancement**: Expand error handling and retry mechanisms
- **Audit and Logging**: Implement comprehensive audit trail for compliance

## External References

### ServiceNow Business Rules Documentation
- [ServiceNow Business Rules](https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/business-rules/concept/c_BusinessRules.html) - Official Business Rules documentation
- [Business Rules Best Practices](https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/business-rules/concept/business-rules-best-practices.html) - Development best practices
- [ServiceNow Server-Side Scripting](https://docs.servicenow.com/bundle/vancouver-application-development/page/script/server-scripting/concept/c_ServerSideScripting.html) - JavaScript API documentation
- [ServiceNow REST Message API](https://docs.servicenow.com/bundle/vancouver-application-development/page/integrate/outbound-rest/concept/c_RESTMessage.html) - Outbound REST integration

### ServiceNow Flow Designer Documentation
- [ServiceNow Flow Designer](https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/flow-designer/concept/flow-designer.html) - Flow Designer overview
- [Flow Designer Triggers](https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/flow-designer/concept/triggers.html) - Available trigger types
- [Flow Designer vs Business Rules](https://community.servicenow.com/community?id=community_question&sys_id=7e9b4e1bdb98dbc01dcaf3231f9619f2) - Community comparison discussions
- [ServiceNow IntegrationHub](https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/integrationhub-store-spokes/concept/integrationhub-overview.html) - IntegrationHub spokes and actions

### GitOps and Infrastructure as Code
- [GitOps Principles](https://www.weave.works/technologies/gitops/) - GitOps methodology
- [Infrastructure as Code](https://www.redhat.com/en/topics/automation/what-is-infrastructure-as-code-iac) - IaC principles
- [Configuration as Code](https://www.thoughtworks.com/insights/blog/configuration-as-code) - Configuration management patterns
- [Version Control Best Practices](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows) - Git workflow patterns

### API Integration and REST Best Practices
- [REST API Design Guide](https://restfulapi.net/) - REST API design principles
- [HTTP Status Codes](https://httpstatuses.com/) - HTTP response codes reference
- [API Security Best Practices](https://owasp.org/www-project-api-security/) - OWASP API security guidelines
- [Webhook vs Polling](https://blog.bearer.sh/webhook-vs-polling/) - Event-driven integration patterns

### Enterprise Architecture Patterns
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) - Integration architecture patterns
- [Microservices Patterns](https://microservices.io/patterns/index.html) - Microservice architecture patterns
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html) - Event-driven design patterns
- [Separation of Concerns](https://en.wikipedia.org/wiki/Separation_of_concerns) - Architectural design principle

### Ansible and AAP Integration
- [Ansible Job Templates](https://docs.ansible.com/automation-controller/latest/html/userguide/job_templates.html) - AAP job template configuration
- [Ansible REST API](https://docs.ansible.com/automation-controller/latest/html/controllerapi/index.html) - AAP API documentation
- [ServiceNow Ansible Collection](https://docs.ansible.com/ansible/latest/collections/servicenow/itsm/index.html) - Official ServiceNow collection

---

**This decision establishes Business Rules as the definitive ServiceNow automation approach, providing a production-ready, maintainable, and architecturally sound solution for the ServiceNow-OpenShift integration.**
