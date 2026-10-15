# ADR-0001: SarvanOM v2 Implementation Kickoff

**Date**: September 9, 2025  
**Status**: ✅ **ACCEPTED**  
**Deciders**: Senior Staff+ Engineer  
**Consulted**: SarvanOM v2 Documentation Pack (00-16)  
**Informed**: Development Team

---

## 🎯 **Context**

SarvanOM v1 has achieved successful frontend-backend integration with all core services operational. The system is now ready for v2 implementation following the comprehensive documentation pack that defines:

- Strict naming conventions and environment contracts
- Model orchestration with auto-upgrade policies
- Multi-lane retrieval with strict SLOs (5s/7s/10s)
- Qdrant as the sole vector database for dev & prod
- Cosmic Pro design system for frontend
- Comprehensive observability and security requirements

## 🚀 **Decision**

We will implement SarvanOM v2 in-place (no hard reset) following a strict documentation-driven approach with these non-negotiables:

### **Global Constraints**
1. **Latest Stable Only**: Use only latest stable frameworks, libraries, and model families
2. **No Environment Renames**: Keep all existing .env keys unchanged
3. **Canonical Naming**: Use canonical parameter names everywhere (top_k, temperature, max_tokens)
4. **Qdrant Only**: Qdrant is the sole vector DB for dev & prod
5. **Strict SLOs**: 5s (simple), 7s (technical), 10s (research/multimedia) end-to-end
6. **Full Observability**: Every feature must have metrics, logs, and traces

### **Implementation Approach**
1. **Documentation First**: Complete all 14 phases of documentation before any code changes
2. **Sequential Execution**: Implement phases 0-14 in strict order
3. **Validation Gates**: Each phase must be validated before proceeding
4. **No Code Until Docs**: No code changes until all documentation artifacts are complete

## 🔄 **Implementation Plan**

### **Phase 0: Pre-flight & Source of Truth** ✅
- [x] Create master tracking issue
- [x] Create branch: `release/v2`
- [x] Parse current .env file and create `docs/env_inventory.md`
- [x] Add `docs/adr/ADR-0001-v2-kickoff.md`
- [x] Snapshot repo inventory: `docs/review/repo_inventory.md`

### **Phases 1-14: Sequential Documentation**
Following the exact order specified in the implementation prompt, with validation gates between each phase.

## 🎯 **Success Criteria**

### **Phase 0 Completion**
- [x] Master tracking issue created
- [x] Release branch created
- [x] Environment inventory documented
- [x] ADR created and accepted
- [x] Repository inventory completed

### **Overall v2 Success**
- All 14 phases completed with validation
- Documentation artifacts created and approved
- Code implementation follows documentation specifications
- System meets v2 SLOs and requirements

## 🔄 **Rollback Plan**

### **Phase 0 Rollback**
- Revert to main branch if issues arise
- All documentation artifacts are in `docs/` directory
- No code changes made yet

### **Future Phase Rollbacks**
- Each phase will have specific rollback procedures
- Documentation artifacts provide clear rollback paths
- No destructive changes without approval

## 📊 **Consequences**

### **Positive**
- ✅ Systematic, documentation-driven approach
- ✅ Clear validation gates and rollback procedures
- ✅ Maintains existing functionality while upgrading
- ✅ Follows industry best practices for large-scale refactoring

### **Negative**
- ⚠️ Longer initial phase due to comprehensive documentation
- ⚠️ Sequential approach may be slower than parallel development
- ⚠️ Requires discipline to not skip documentation phases

### **Neutral**
- 📋 Extensive documentation will improve long-term maintainability
- 📋 Clear contracts will reduce future integration issues
- 📋 Systematic approach reduces risk of breaking changes

## 🔍 **Alternatives Considered**

### **Alternative 1: Parallel Development**
- **Rejected**: Risk of breaking existing functionality
- **Reason**: Current system is working; need systematic approach

### **Alternative 2: Hard Reset**
- **Rejected**: Would lose all existing progress and integrations
- **Reason**: v1 integration is successful; build upon it

### **Alternative 3: Incremental Changes**
- **Rejected**: Would not follow v2 documentation specifications
- **Reason**: v2 requires comprehensive architectural changes

## 📋 **Next Steps**

1. Complete Phase 0: Repository inventory
2. Begin Phase 1: Contracts & naming guardrails
3. Follow sequential implementation through Phase 14
4. Validate each phase before proceeding
5. Implement code changes only after documentation completion

---

## 📚 **References**

- SarvanOM v2 Documentation Pack (00-16)
- Current system integration success report
- Environment inventory analysis
- Implementation tracking issue

---

*This ADR will be updated as implementation progresses through the phases.*
