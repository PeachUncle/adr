# ADR-001: Use Next.js 14+ for Full-Stack Framework

## Status

✅ **Accepted**

**Date:** 27. Oktober 2025

## Context

Ich brauche ein Framework für die AI-Freelancer-Plattform, das sowohl Frontend als auch Backend abdeckt. Als Solo-Developer ist es wichtig, ein Framework zu wählen, das:

- Produktiv ist (schnelle Entwicklung)
- Modernen Best Practices folgt
- Gute TypeScript-Integration hat
- Einfach zu deployen ist
- Performance-optimiert ist

## Decision

Ich verwende **Next.js 14+ mit App Router** als Full-Stack-Framework.

### Warum Next.js?

**Frontend-Vorteile:**

- ✅ React-basiert (moderne, etablierte Library)
- ✅ Server Components (weniger Client-JS, bessere Performance)
- ✅ Built-in Routing (App Router, file-based)
- ✅ Automatisches Code-Splitting
- ✅ Image Optimization (`next/image`)
- ✅ Font Optimization
- ✅ Excellent TypeScript Support

**Backend-Vorteile:**

- ✅ API Routes (kein separater Backend-Server nötig)
- ✅ Server Actions (mutations ohne API-Endpoints)
- ✅ Middleware (Auth, Rate Limiting)
- ✅ Cron Jobs (Vercel Cron oder externe Lösungen)

**Solo-Dev Vorteile:**

- ✅ Einheitliche Codebase (Frontend + Backend)
- ✅ Shared Types (TypeScript end-to-end)
- ✅ Weniger Context-Switching
- ✅ Einfacheres Deployment (ein Container)

**Deployment:**

- ✅ Vercel (native, zero-config)
- ✅ Docker (AWS ECS, Google Cloud Run)
- ✅ Self-Hosted möglich

## Alternatives Considered

### Alternative 1: Vite + React + Express (separate Backend)

**Pros:**

- ✅ Flexibler (separate Frontend/Backend)
- ✅ Vite ist schneller im Development
- ✅ Kann Backend in anderer Sprache schreiben (z.B. Go, Python)

**Cons:**

- ❌ Zwei separate Deployments
- ❌ Mehr Setup-Aufwand
- ❌ Keine shared Types ohne zusätzliche Tools
- ❌ Mehr Complexity für Solo-Dev

**Warum nicht gewählt:**
Next.js Full-Stack ist für Solo-Dev effizienter. Die Backend-Requirements sind nicht so komplex, dass ein separater Server nötig wäre.

### Alternative 2: Remix

**Pros:**

- ✅ Modernes Full-Stack-Framework
- ✅ Gute TypeScript-Integration
- ✅ Server-first Architektur

**Cons:**

- ❌ Kleineres Ecosystem als Next.js
- ❌ Weniger etabliert
- ❌ Weniger Community-Support
- ❌ Weniger Tutorials/Resources

**Warum nicht gewählt:**
Next.js ist etablierter, hat größeres Ecosystem, mehr Ressourcen. Für MVP ist Ecosystem wichtiger als cutting-edge Features.

### Alternative 3: Create React App (CRA)

**Pros:**

- ✅ Einfach für reine Frontend-Apps

**Cons:**

- ❌ **Veraltet** (React-Team empfiehlt CRA nicht mehr)
- ❌ Kein Backend
- ❌ Keine Server Components
- ❌ Schlechtere Performance

**Warum nicht gewählt:**
CRA ist deprecated. Next.js ist der offizielle Nachfolger.

## Rationale

**Warum App Router (vs. Pages Router)?**

- ✅ Server Components (default)
- ✅ Moderne Architektur (Zukunft von Next.js)
- ✅ Bessere Performance (weniger Client-JS)
- ✅ Layouts & Templates
- ❌ Neue API (Lernkurve), aber lohnt sich langfristig

**Trade-offs:**

- **Pro:** Schnellere Entwicklung, weniger Boilerplate, gutes Ecosystem
- **Con:** Vendor Lock-in (Next.js-specific patterns), Framework-Overhead

## Consequences

### Positive

1. **Schnelle Entwicklung**
   - Unified Codebase reduziert Context-Switching
   - Weniger Setup-Zeit
   - Shared TypeScript Types

2. **Bessere Performance**
   - Server Components reduzieren Client-JS Bundle
   - Automatische Optimierungen (Code Splitting, Images, Fonts)

3. **Einfacheres Deployment**
   - Ein Docker-Container für Frontend + Backend
   - AWS ECS mit einem Service (statt zwei)

4. **Gutes Ecosystem**
   - Viele Next.js-kompatible Libraries
   - shadcn/ui (komponiert mit Next.js)
   - Große Community

### Negative

1. **Vendor Lock-in**
   - Code ist Next.js-specific (z.B. Server Actions, App Router)
   - Migration zu anderem Framework wäre aufwendig
   - **Mitigation:** Business Logic in separate Modules (`/src/lib`) auslagern

2. **Learning Curve**
   - App Router ist relativ neu (2023)
   - Server Components Konzept muss verstanden werden
   - **Mitigation:** Gute Dokumentation, viele Tutorials

3. **Framework Overhead**
   - Next.js bringt mehr als nötig (z.B. ISR, Edge Runtime)
   - Bundle Size größer als minimale React-App
   - **Mitigation:** Akzeptabel für Produktivität

## Implementation Notes

- **Version:** Next.js 14+ (latest stable)
- **Rendering:** Server Components (default), Client Components nur wo nötig
- **Routing:** App Router (`/app` directory)
- **API:** tRPC über API Routes (siehe ADR-003)
- **Auth:** NextAuth.js v5 (siehe ADR-004)
- **Styling:** Tailwind CSS + shadcn/ui (siehe ADR-006)

## Follow-up Actions

- [x] Next.js 14+ installieren
- [x] App Router konfigurieren
- [x] TypeScript konfigurieren
- [x] Folder Structure definieren (siehe ARCHITECTURE.md)

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [App Router Migration Guide](https://nextjs.org/docs/app/building-your-application/upgrading/app-router-migration)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)

---

**Author:** Max Mustermann
**Date:** 27. Oktober 2025
**Status:** Accepted
