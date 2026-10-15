# ADR1 Frontend Framework

**Title:** Use TypeScript with React for frontend framework

**Status:** Revised -- Cycle 2

**Context:** 
- Allowed options: JavaScript or TypeScript, with either next.js or React.
- Some team members are familiar with React.
- React's architecture is component-based, which suits the incremental planning steps for this project.  
- TypeScript offers improved maintainability through type safety, which reduces runtime errors and allows safer refactoring.  
- Next.js offers server-side rendering (SSR), which is not a priority for this classroom booking project. The booking tool instead focuses on internal authenticated users.  
- The frontend must support moderate traffic and provide a responsive UI for authenticated users without unnecessary SSR complexity.

**Alternatives Considered:**  
- JavaScript with React: simpler to learn, but lacks static typing and increases risk of runtime errors.  
- Next.js (with TypeScript): good for SSR and search engine optimization (SEO), but overkill for an internal authenticated app and adds unnecessary complexity.  
-  Vue.js: – lightweight and flexible, but not aligned with team skill set. 


**Quantitative Implications:**  
- Estimated 30–50% fewer runtime errors during development due to static typing.    
- Typical bundle size with React and Vite is <300 KB (within acceptable performance thresholds).  
- Strong typing reduces the likelihood of regression errors, lowering maintenance effort in future iterations.

**Decision:** 
Use TypeScript with React for frontend framework.    

**Consequences:**  
- ✅ Reduces training time for team members already familiar with React's usage.  
- ✅ Large set of reusable libraries to increase development speed.  
- ✅ TypeScript improves maintainability and reduces errors.  
- ✅ Component reuse will make future iterations smoother.  
- ✅ Pairs well with Vitest, our testing tool of choice.  
- ✅ Simplifies integration with NestJS and PostgreSQL backend.  


- ❌ Steep learning curve for unfamiliar members.  
- ❌ Vast selection of library components may muddle development options; requires more coordination from the team.  
- ❌ Does not include built-in routing (requires setup with library components; e.g., React Router).  
- ❌ An unclear or inconsistent component hierarchy during early development led to technical debt and additional refactoring work.  
- ❌ Future features may require more careful planning of layout and component responsibilities to avoid similar structural issues.

**Reflection:**  
- The trade-off favors maintainability and developer productivity over initial simplicity.  
- The initial lack of a clear component hierarchy slowed early development and highlighted the importance of planning structure before implementation.  
- Future iterations may focus on improving internal structure (routing, state management, component hierarchy) within the existing React and Docker setup, rather than introducing additional frameworks.

**Related User Stories**
- [User Story 1: Staff can sign-in](https://gitlab.csc.uvic.ca/courses/2025091/SENG350_COSI/teams/group_10_proj/-/issues/1)
- [User Story 4: Staff can view booking history](https://gitlab.csc.uvic.ca/courses/2025091/SENG350_COSI/teams/group_10_proj/-/issues/4)