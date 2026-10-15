# ADR 0001: Next.js Framework Seçimi Landing Page İçin

## Status
✅ **Accepted** - 2025-01-22

## Context
AgentsPalace projesi için modern, performanslı ve SEO-friendly bir landing page geliştirmek gerekiyordu. Aşağıdaki gereksinimler belirlendi:

- **Modern UI/UX**: Blade Runner 2049 estetiği ile futuristik tasarım
- **Performance**: Hızlı yükleme süreleri ve optimize edilmiş bundle size
- **SEO**: Server-side rendering ve meta tag desteği
- **Animation**: Smooth ve etkileyici animasyonlar
- **Developer Experience**: Hızlı geliştirme ve kolay maintenance
- **Scalability**: Gelecekte ek sayfalar ve özellikler eklenebilmesi

## Alternatives Considered

### 1. Create React App (CRA)
- ✅ Basit kurulum
- ❌ SSR desteği yok
- ❌ SEO limitations
- ❌ Bundle optimization manuel

### 2. Vite + React
- ✅ Hızlı development server
- ✅ Modern build tooling
- ❌ SSR için ek konfigürasyon
- ❌ Routing için ek kütüphane

### 3. Gatsby
- ✅ Static site generation
- ✅ SEO-friendly
- ❌ Kompleks öğrenme eğrisi
- ❌ Build time uzun

### 4. Next.js 15
- ✅ Built-in SSR/SSG
- ✅ File-based routing
- ✅ Image optimization
- ✅ Bundle optimization
- ✅ SEO-friendly
- ✅ TypeScript desteği
- ✅ Active community

## Decision
**Next.js 15** framework'ü seçildi çünkü:

1. **Built-in Performance**: Image optimization, automatic code splitting
2. **SEO Optimization**: Server-side rendering ve meta tag yönetimi
3. **Developer Experience**: Hot reload, TypeScript desteği, file-based routing
4. **Production Ready**: Vercel deployment, analytics, monitoring desteği
5. **Ecosystem**: TailwindCSS, Framer Motion ile mükemmel entegrasyon

## Consequences

### Positive
- ✅ **Hızlı development**: File-based routing ve hot reload
- ✅ **SEO performance**: Built-in SSR ve meta tag optimization
- ✅ **Bundle optimization**: Automatic code splitting ve tree shaking
- ✅ **Image optimization**: Built-in next/image component
- ✅ **TypeScript support**: Full TypeScript entegrasyonu
- ✅ **Deployment**: Vercel ile seamless deployment

### Negative
- ❌ **Learning curve**: Next.js specific patterns öğrenme
- ❌ **Bundle size**: React framework overhead
- ❌ **Vendor lock-in**: Next.js specific features kullanımı

### Neutral
- 🔄 **Maintenance**: Regular Next.js updates takibi
- 🔄 **Build complexity**: SSR/SSG considerations

## Implementation Details

```json
{
  "framework": "Next.js 15",
  "styling": "TailwindCSS",
  "animations": "Framer Motion",
  "icons": "Lucide React",
  "typescript": true,
  "eslint": true,
  "deployment": "Vercel"
}
```

## Monitoring & Success Criteria

- **Performance**: Lighthouse score > 90
- **SEO**: Core Web Vitals Green
- **DX**: Build time < 30 seconds
- **Bundle Size**: < 500KB initial load

## Related Documents
- [System Architecture](../architecture/system-architecture.md)
- [Development History](../development-history.md)
- [Production Ready Checklist](../production-ready-checklist.md)

---

**Karar Veren:** AgentsPalace Development Team  
**Tarih:** 2025-01-22  
**Review Date:** 2025-07-22
