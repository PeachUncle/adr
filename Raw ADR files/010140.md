# ADR 001: Content Management Strategy

**Status:** Accepted  
**Date:** 2025-11-12  
**Decision Makers:** Project Team  
**Related Issues:** Content updates, Security, User experience

---

## Context and Problem Statement

The Laboratório de Fonética UFRJ single-page website requires a content management solution that allows non-technical researchers to update:
- Team member information (names, photos, Lattes links)
- Research publications
- Partner institutions
- General site content

### Constraints
- **Hosting Environment:** Shared WordPress hosting (wisley.net staging, posvernaculas.letras.ufrj.br production)
- **No Database:** Static site architecture with JSON data source
- **No Backend Runtime:** No Node.js, no server-side JavaScript
- **Security Priority:** Minimize attack surface on shared hosting
- **User Profile:** Academic researchers with varying technical proficiency
- **Update Frequency:** Infrequent (quarterly/semester basis)

### Requirements
1. Non-technical users must be able to update content
2. Zero additional security risk on production server
3. No server-side code execution required
4. Simple maintenance and updates
5. Version-controlled and reversible changes

---

## Decision Drivers

### Security
- Shared hosting with WordPress installation on same server
- Public-facing university website (medium-high risk target)
- Limited control over server configuration
- No database for credential storage

### Usability
- Users are researchers, not developers
- Minimal training time required
- Clear, form-based interface preferred
- Visual validation of changes

### Technical
- Static site built with Vite
- Content stored in `public/data.json`
- Deployment via FTP/FileZilla
- Git-based version control

### Maintenance
- Limited ongoing technical support
- Solution must be self-documenting
- Easy to debug and update
- No server-side dependencies

---

## Considered Options

### Option 1: Local HTML Editor + Manual FTP Upload (SELECTED)

**Description:**  
A standalone HTML file (`editor.html`) that runs entirely in the user's browser. Users download `data.json` from the server, edit it locally using forms, then upload the updated file via FTP.

**Pros:**
- ✅ Zero server-side attack surface
- ✅ No authentication system needed
- ✅ Works completely offline
- ✅ Version-controlled in Git repository
- ✅ Can be distributed via email/USB
- ✅ No server configuration required
- ✅ Easy to maintain and update
- ✅ Full rollback capability (Git history)

**Cons:**
- ❌ Requires manual FTP upload step
- ❌ No real-time collaboration
- ❌ Users need FTP credentials
- ❌ Potential for upload errors

**Implementation Cost:** Low  
**Maintenance Cost:** Very Low  
**Security Risk:** None

---

### Option 2: Server-Side PHP Admin Panel

**Description:**  
A PHP-based admin interface (`gestao.php`) hosted on the server with hard-coded credentials for authentication.

**Pros:**
- ✅ Web-based interface (no FTP needed)
- ✅ Direct file updates on server
- ✅ Familiar "login and edit" workflow

**Cons:**
- ❌ Significant security risk (PHP vulnerabilities)
- ❌ Hard-coded credentials = security theater
- ❌ File write permissions = exploit vector
- ❌ Requires CSRF/XSS mitigation
- ❌ Shared hosting may restrict PHP operations
- ❌ `.htaccess` misconfigurations possible
- ❌ WordPress on same server increases risk
- ❌ Session management complexity
- ❌ Requires ongoing security updates

**Implementation Cost:** Medium  
**Maintenance Cost:** High  
**Security Risk:** High

---

### Option 3: Static Site Generator (GitHub Actions/Netlify)

**Description:**  
Move to a modern static hosting platform with built-in CMS (GitHub web interface or Netlify CMS).

**Pros:**
- ✅ Modern workflow
- ✅ Built-in authentication (GitHub accounts)
- ✅ Automatic deployment
- ✅ Zero server risk
- ✅ Collaboration features

**Cons:**
- ❌ Requires hosting migration
- ❌ URL masking needed (posvernaculas.letras.ufrj.br requirement)
- ❌ More complex initial setup
- ❌ Dependency on third-party services
- ❌ Learning curve for GitHub workflow

**Implementation Cost:** High  
**Maintenance Cost:** Low  
**Security Risk:** Very Low

---

## Decision Outcome

**Chosen Option:** Option 1 - Local HTML Editor + Manual FTP Upload

### Rationale

1. **Security is Paramount**  
   The shared hosting environment with WordPress installation makes server-side code unacceptably risky. Option 1 eliminates all server-side attack vectors.

2. **Fits All Constraints**  
   No database, no backend runtime, no server configuration needed. Works within existing infrastructure.

3. **Acceptable User Experience**  
   While manual FTP upload is an extra step, it's a simple, one-file operation. The editing experience itself will be user-friendly with forms and validation.

4. **Future-Proof**  
   The solution is self-contained and can be updated independently. Migration to Option 3 (SSG) remains possible in the future.

5. **Low Maintenance Burden**  
   A single HTML file is easy to maintain, debug, and distribute. No server-side code to update or secure.

### Reversibility

**High:** This decision is easily reversible.
- Editor is a single HTML file that can be replaced
- Can migrate to PHP panel (Option 2) if security concerns are addressed
- Can migrate to SSG (Option 3) if hosting changes
- No permanent changes to site architecture

---

## Implementation Plan

### Phase 1: Core Editor (Week 1-2)
- Create `public/admin/editor.html`
- Implement JSON load/save functionality
- Build forms for all data sections:
  - Team members (with categories)
  - Publications
  - Research projects
  - Partners
- Basic validation (required fields, URL formats)
- User documentation

### Phase 2: Visual Refinements (Week 2-3)
- Integrate laboratory logo (blue color palette)
- Refine color scheme based on logo
- Polish typography and spacing
- Add social media links (Instagram, mailto)
- Test responsive design

### Phase 3: Enhanced Team Section (Week 3-4)
- Implement category subsections:
  - Coordenação (Coordination)
  - Docentes/Pesquisadores (Faculty/Researchers)
  - Discentes de Pós-Graduação (Graduate Students)
  - Discentes de Graduação (Undergraduate Students)
- Multiple display style options:
  - Grid view (default)
  - List view
  - Card view with expanded details
- User preference persistence (localStorage)

### Phase 4: Editor Enhancements (Week 4+)
- Image preview in editor
- Drag-and-drop improvements
- Live preview panel
- Undo/redo functionality
- Export backup before changes
- CSV import for bulk updates

---

## Consequences

### Positive

**Security:**
- Zero new attack surface on server
- No credentials to manage or leak
- No PHP vulnerabilities to patch
- WordPress isolation maintained

**Maintainability:**
- Single HTML file to maintain
- Version-controlled in Git
- Easy to distribute and update
- Clear separation of concerns

**User Experience:**
- Clean, form-based interface
- Offline editing capability
- Immediate validation feedback
- No login friction

**Technical:**
- No server-side dependencies
- Works with existing infrastructure
- Easy rollback via Git
- Can be enhanced incrementally

### Negative

**Workflow:**
- Manual FTP upload required
- No real-time collaboration
- Potential for upload errors
- Users need FTP access/training

**Limitations:**
- Not suitable for frequent updates
- No built-in backup system (rely on Git)
- Image uploads still manual via FTP

### Mitigation Strategies

**For FTP Upload Friction:**
- Create detailed step-by-step guide with screenshots
- Provide video tutorial
- Consider FileZilla project files with saved connections
- Document common error scenarios

**For Collaboration:**
- Implement file locking convention
- Use Git branches for major content changes
- Coordinate updates via calendar/email

**For Backup:**
- Editor includes "Export Backup" button
- Git repository serves as history
- Document rollback procedures

---

## Related Decisions

- **Visual Identity:** Blue color palette from laboratory logo
- **Team Organization:** Hierarchical categories with multiple display options
- **Social Integration:** Links to Instagram, mailto (no embedded forms)
- **Deployment:** Manual via FTP to `/labfonac/` subfolder

---

## References

- [Deployment Guide](../../DEPLOYMENT.md)
- [Image Assets Documentation](../../public/assets/images/README.md)
- [Vite Configuration](../../vite.config.js)

---

## Notes

**Branch for Development:** `feature/local-content-editor`

**Alternative Approaches Preserved:**
- PHP panel code can be developed in separate branch if needed
- SSG migration plan can be documented if hosting situation changes

**Future Enhancements to Consider:**
- GitHub-based workflow (if hosting migrates)
- Automated image optimization
- Content preview before upload
- Multi-language support (if needed)

---

**Approved by:** [Project Team]  
**Implementation Start:** 2025-11-12  
**Review Date:** 2026-02-12 (3 months)
