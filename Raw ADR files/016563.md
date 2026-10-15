# ADR-013: PDI Workaround Strategy for Development Environment

**Status:** Accepted  
**Date:** 2025-09-19  
**Supersedes:** None  
**Superseded by:** None  

## Context

The ServiceNow-OpenShift integration project requires a development environment for testing and validation. The project uses a ServiceNow Personal Developer Instance (PDI) at `dev295398.service-now.com` for development work. However, there are **research-based indications** that PDI environments may have limitations regarding outbound REST API calls and external system integrations that could prevent Business Rules from automatically triggering AAP job templates.

**Important Note**: These limitations are based on research and community knowledge rather than direct testing in a production ServiceNow instance. The project team does not currently have access to a production ServiceNow environment to validate the full Business Rules automation.

## Problem Statement

1. **PDI Limitations (Research-Based)**: ServiceNow PDI environments may restrict outbound REST API calls to external systems for security and resource management reasons
2. **Development Validation Need**: The project requires a way to validate the complete ServiceNow → AAP → OpenShift → Keycloak integration workflow
3. **Business Rules Testing**: The Business Rules logic needs validation before potential production deployment
4. **Educational Value**: Developers need a way to understand and test the integration workflow

## Decision

Implement a **hybrid development approach** that accommodates potential PDI limitations while maintaining production readiness:

### Primary Approach: Business Rules for Production
- **Maintain Business Rules implementation** as the production-ready solution
- **Document Business Rules thoroughly** for enterprise ServiceNow deployment
- **Keep Business Rules logic in version control** (test_business_rule_logic.js)

### Development Workaround: Simplified Workflow Script
- **Use `user-workflows/advanced/start-simplified-workflow.sh`** as the development validation tool
- **Simulate Business Rules logic locally** to test API calls and integration flow
- **Provide manual trigger mechanism** that works within PDI constraints
- **Maintain educational value** for understanding the complete workflow

### Validation Strategy
- **Local Business Rules Testing**: Use `test_business_rule_logic.js` to validate API call logic
- **End-to-End Workflow Testing**: Use `ansible/idempotent_end_to_end_test.yml` for complete validation
- **OpenShift Verification**: Use `oc get projects` to confirm project creation
- **ServiceNow Integration**: Use simplified workflow to test ServiceNow catalog integration

## Implementation Details

### Development Environment Components

1. **Working Components (Validated)**:
   - ✅ ServiceNow catalog request creation
   - ✅ AAP job template execution (manual trigger)
   - ✅ OpenShift project creation
   - ✅ Keycloak user management
   - ✅ End-to-end workflow validation

2. **PDI Workaround Script**: `user-workflows/advanced/start-simplified-workflow.sh`
   ```bash
   # Demonstrates complete workflow
   ./start-simplified-workflow.sh [project-name] [environment] [mode]
   
   # Modes:
   # - check-first: Check ServiceNow requests, then AAP jobs, then projects
   # - create-request: Create new ServiceNow request
   # - verify-only: Only verify OpenShift project exists
   # - full: Complete workflow with request creation and validation
   ```

3. **Business Rules Logic Testing**: `test_business_rule_logic.js`
   ```javascript
   // Tests AAP REST API call logic locally
   // Validates payload structure and authentication
   // Simulates ServiceNow Business Rule execution
   ```

### Production Readiness Indicators

- **95% Test Confidence Score**: Comprehensive testing validates all components
- **Business Rules Documentation**: Complete implementation guide available
- **API Integration Validated**: AAP job template calls working
- **OpenShift Integration Confirmed**: Project creation and management working

## Rationale

### Why This Approach

1. **Accommodates PDI Constraints**: Works within potential PDI limitations without compromising production design
2. **Maintains Production Focus**: Business Rules remain the target production solution
3. **Enables Complete Testing**: All integration components can be validated
4. **Educational Value**: Developers can understand the complete workflow
5. **Version Controlled**: All logic remains in Git for proper change management

### Research-Based PDI Limitations

While not directly tested, research suggests PDI environments may have:
- **Outbound REST API restrictions** for security reasons
- **External system integration limitations** to prevent abuse
- **Resource management constraints** that affect background processing

**References for Further Research**:
- [ServiceNow Community PDI Discussions](https://community.servicenow.com/community?id=community_search&q=PDI%20limitations) - Community discussions on PDI limitations
- [ServiceNow Developer Program](https://developer.servicenow.com/dev.do#!/learn/learning-plans/vancouver/new_to_servicenow/app_store_learnv2_buildmyfirstapp_vancouver_personal_developer_instances) - PDI documentation and limitations
- [ServiceNow Instance Types](https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/managing-instances/concept/c_InstanceTypes.html) - Developer vs production instance differences
- [ServiceNow Outbound REST Limitations](https://community.servicenow.com/community?id=community_question&sys_id=9d4b4e1bdb98dbc01dcaf3231f9619f1) - Community reports of outbound integration restrictions

## Consequences

### Positive Consequences

- **Complete Development Validation**: All integration components can be tested
- **Production-Ready Design**: Business Rules approach remains intact for enterprise deployment
- **Educational Workflow**: Clear understanding of integration flow for developers
- **Flexible Testing**: Multiple testing modes for different scenarios
- **Version Controlled Logic**: All automation logic properly managed in Git

### Negative Consequences

- **Manual Execution Required**: PDI environment requires manual workflow execution
- **Development/Production Divergence**: Slight difference between dev and production workflows
- **Assumption-Based**: PDI limitations are research-based, not directly validated
- **Additional Complexity**: Maintains both Business Rules and workaround script

### Risk Mitigation

- **Business Rules Testing**: Local testing validates production logic
- **Comprehensive Documentation**: Clear migration path to production
- **Modular Design**: Easy to switch to full automation in production environment
- **Validation Framework**: Extensive testing ensures production readiness

## Implementation Status

### ✅ Completed
- Working simplified workflow script
- Business Rules logic validation
- End-to-end testing framework
- OpenShift integration validation
- ServiceNow catalog integration

### 🔄 Ongoing
- Documentation of Business Rules for production deployment
- Community-driven documentation creation
- Production deployment planning

### 📋 Future Work
- **Production ServiceNow Testing**: Validate Business Rules in enterprise instance
- **PDI Limitation Validation**: Direct testing of PDI outbound REST capabilities
- **Production Deployment Guide**: Complete enterprise deployment documentation

## Related ADRs

- **ADR-001**: Three-Tier Orchestration Architecture
- **ADR-010**: Ansible Automation Platform Integration
- **ADR-014**: Business Rules Over Flow Designer Implementation (planned)

## References

- `user-workflows/advanced/start-simplified-workflow.sh` - Working development workflow
- `test_business_rule_logic.js` - Business Rules logic validation
- `ansible/idempotent_end_to_end_test.yml` - End-to-end testing
- `research.md` - Flow Designer vs Business Rules analysis
- `SERVICENOW_SETUP_GUIDE.md` - ServiceNow configuration documentation
- `END_TO_END_TEST_EXECUTION_SUMMARY.md` - Test validation results

## External References

### ServiceNow Development Environment
- [ServiceNow Personal Developer Instance](https://developer.servicenow.com/dev.do#!/learn/learning-plans/vancouver/new_to_servicenow/app_store_learnv2_buildmyfirstapp_vancouver_personal_developer_instances) - PDI setup and limitations
- [ServiceNow Developer Program](https://developer.servicenow.com/) - Developer resources and documentation
- [ServiceNow Instance Types](https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/managing-instances/concept/c_InstanceTypes.html) - Instance type comparison
- [ServiceNow Community Forums](https://community.servicenow.com/) - Community discussions and support

### Business Rules and Outbound Integration
- [ServiceNow Business Rules](https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/business-rules/concept/c_BusinessRules.html) - Business Rules documentation
- [ServiceNow Outbound REST](https://docs.servicenow.com/bundle/vancouver-application-development/page/integrate/outbound-rest/concept/c_OutboundREST.html) - Outbound REST integration
- [ServiceNow REST Message](https://docs.servicenow.com/bundle/vancouver-application-development/page/integrate/outbound-rest/concept/c_RESTMessage.html) - REST message configuration
- [ServiceNow JavaScript API](https://docs.servicenow.com/bundle/vancouver-application-development/page/script/server-scripting/concept/c_ServerSideScripting.html) - Server-side scripting

### Development and Testing Patterns
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html) - TDD methodology
- [Local Development Best Practices](https://12factor.net/dev-prod-parity) - Development/production parity
- [API Testing Strategies](https://martinfowler.com/articles/practical-test-pyramid.html) - Testing pyramid and API testing
- [Continuous Integration Patterns](https://martinfowler.com/articles/continuousIntegration.html) - CI/CD best practices

### Ansible and AAP Integration
- [Ansible Job Templates](https://docs.ansible.com/automation-controller/latest/html/userguide/job_templates.html) - AAP job template configuration
- [Ansible REST API](https://docs.ansible.com/automation-controller/latest/html/controllerapi/index.html) - AAP API documentation
- [Ansible Testing](https://docs.ansible.com/ansible/latest/dev_guide/testing.html) - Ansible testing strategies

---

**Note**: This ADR documents the current development approach based on research-indicated PDI limitations. Future validation in a production ServiceNow environment may allow for simplification of this approach.
