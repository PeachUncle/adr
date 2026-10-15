# ADR-0006: Testing Framework and Strategy

## Status
Accepted

## Date
2025-01-XX

## Context

The PDF Viewer & Editor requires comprehensive testing to ensure:
- PDF rendering works correctly across different file types
- Annotations can be added, edited, and exported reliably
- Performance remains acceptable with large documents
- UI components behave as expected
- No regressions when adding features

**Requirements**:
- Unit tests for business logic
- Component tests for React components
- E2E tests for complete user workflows
- >90% code coverage
- Fast test execution (<30 seconds for unit tests)
- Easy to write and maintain
- Good error messages
- CI/CD integration

## Decision

We will use a **layered testing approach** with:
- **Vitest** for unit and component testing
- **React Testing Library** for component testing
- **Playwright** for E2E testing (to be configured)
- **>90% coverage requirement** enforced

## Consequences

### Positive
- **Fast**: Vitest is extremely fast (Vite-powered)
- **Modern**: Native ESM, TypeScript support
- **Compatible**: Drop-in replacement for Jest
- **Integrated**: Works seamlessly with Vite
- **Good DX**: Watch mode, UI, coverage reports
- **React Support**: Works great with Testing Library
- **Type Safe**: Full TypeScript support
- **Zero Config**: Works out of the box with Vite

### Negative
- **Smaller Ecosystem**: Less mature than Jest (but compatible)
- **Learning Curve**: Slightly different from Jest
- **Playwright Setup**: Requires additional configuration
- **Coverage Overhead**: 90% target requires discipline

### Neutral
- Need to maintain separate E2E test suite
- Must mock PDF.js and pdf-lib in tests
- Snapshot testing available but use sparingly

## Alternatives Considered

### Alternative 1: Jest
- **Description**: Most popular JavaScript testing framework
- **Pros**: 
  - Huge ecosystem
  - Extensive documentation
  - Many plugins
  - Battle-tested
  - Familiar to most developers
- **Cons**: 
  - Slower than Vitest
  - Requires additional configuration for Vite
  - Transform overhead for ESM
  - Larger bundle
- **Why rejected**: Vitest provides better Vite integration and significantly faster execution. Jest requires additional setup for ESM and TypeScript.

### Alternative 2: Cypress
- **Description**: E2E testing framework with component testing
- **Pros**: 
  - All-in-one solution
  - Great debugging experience
  - Time-travel debugging
  - Visual test runner
- **Cons**: 
  - Slower than Vitest for unit tests
  - Heavier weight
  - Different API from Jest/Vitest
  - Requires running in real browser
- **Why rejected**: Overkill for unit tests. Use Playwright for E2E (more modern, faster). Vitest is better for unit/component tests.

### Alternative 3: Testing Library Alone
- **Description**: Just React Testing Library without test runner
- **Pros**: 
  - Minimal dependencies
  - Focus on component testing
  - User-centric testing
- **Cons**: 
  - Still need test runner (Vitest/Jest)
  - No unit testing for services
  - No E2E capabilities
- **Why rejected**: Not a complete solution. Testing Library is for component testing, not a replacement for test runner.

### Alternative 4: No Testing (YOLO)
- **Description**: Skip automated testing
- **Pros**: 
  - Faster initial development
  - No test maintenance
  - No test infrastructure
- **Cons**: 
  - Regressions with every change
  - Hard to refactor confidently
  - Bugs in production
  - Poor code quality
- **Why rejected**: Unacceptable for production application. Testing is essential for quality and confidence.

## Implementation Notes

### Test Structure

```
tests/
├── unit/                    # Unit tests for services/utilities
│   ├── pdf.service.test.ts
│   ├── annotation.service.test.ts
│   └── utils.test.ts
├── component/               # Component tests
│   ├── PDFViewer.test.tsx
│   ├── Toolbar.test.tsx
│   └── EmptyState.test.tsx
├── e2e/                     # End-to-end tests
│   ├── open-document.spec.ts
│   ├── annotate-pdf.spec.ts
│   └── export-pdf.spec.ts
├── fixtures/                # Test files
│   ├── sample.pdf
│   ├── large-document.pdf
│   └── corrupted.pdf
└── utils/                   # Test utilities
    ├── mockPDF.ts
    ├── renderWithProviders.tsx
    └── createMockDocument.ts
```

### Unit Test Example

```typescript
// tests/unit/pdf.service.test.ts
import { describe, it, expect, vi } from 'vitest'
import { PDFService } from '@/services/pdf.service'

describe('PDFService', () => {
  describe('loadDocument', () => {
    it('should load valid PDF file', async () => {
      const file = new File(['mock pdf content'], 'test.pdf', {
        type: 'application/pdf',
      })
      
      const doc = await PDFService.loadDocument(file)
      
      expect(doc).toBeDefined()
      expect(doc.numPages).toBeGreaterThan(0)
    })
    
    it('should reject non-PDF files', async () => {
      const file = new File(['not a pdf'], 'test.txt', {
        type: 'text/plain',
      })
      
      await expect(PDFService.loadDocument(file))
        .rejects.toThrow('Invalid file type')
    })
    
    it('should handle corrupted PDF files', async () => {
      const file = new File(['corrupted'], 'bad.pdf', {
        type: 'application/pdf',
      })
      
      await expect(PDFService.loadDocument(file))
        .rejects.toThrow('Failed to parse PDF')
    })
  })
  
  describe('renderPage', () => {
    it('should render page to canvas', async () => {
      const canvas = document.createElement('canvas')
      const doc = await PDFService.loadDocument(mockPDFFile)
      
      await PDFService.renderPage(doc, 1, canvas, 1.0)
      
      expect(canvas.width).toBeGreaterThan(0)
      expect(canvas.height).toBeGreaterThan(0)
    })
  })
})
```

### Component Test Example

```typescript
// tests/component/Toolbar.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Toolbar } from '@/components/Toolbar/Toolbar'
import { PDFProvider } from '@/hooks/usePDF'

const renderToolbar = () => {
  return render(
    <PDFProvider>
      <Toolbar />
    </PDFProvider>
  )
}

describe('Toolbar', () => {
  it('renders all toolbar buttons', () => {
    renderToolbar()
    
    expect(screen.getByText('Open')).toBeInTheDocument()
    expect(screen.getByLabelText('Zoom In')).toBeInTheDocument()
    expect(screen.getByLabelText('Zoom Out')).toBeInTheDocument()
    expect(screen.getByText('Markup')).toBeInTheDocument()
  })
  
  it('shows page counter when document is loaded', async () => {
    const { rerender } = renderToolbar()
    
    // No counter initially
    expect(screen.queryByText(/Page/)).not.toBeInTheDocument()
    
    // Load document
    const file = new File(['mock'], 'test.pdf', { type: 'application/pdf' })
    const input = screen.getByLabelText('Open file')
    fireEvent.change(input, { target: { files: [file] } })
    
    // Counter appears
    await screen.findByText('Page 1 of 5')
  })
  
  it('updates zoom when zoom buttons clicked', () => {
    renderToolbar()
    
    const zoomIn = screen.getByLabelText('Zoom In')
    const zoomOut = screen.getByLabelText('Zoom Out')
    
    fireEvent.click(zoomIn)
    expect(screen.getByText('110%')).toBeInTheDocument()
    
    fireEvent.click(zoomOut)
    fireEvent.click(zoomOut)
    expect(screen.getByText('90%')).toBeInTheDocument()
  })
})
```

### E2E Test Example (Playwright)

```typescript
// tests/e2e/annotate-pdf.spec.ts
import { test, expect } from '@playwright/test'

test.describe('PDF Annotation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5000')
    await page.setInputFiles('input[type="file"]', 'tests/fixtures/sample.pdf')
    await expect(page.locator('.pdf-canvas')).toBeVisible()
  })
  
  test('user can highlight text', async ({ page }) => {
    // Open markup toolbar
    await page.click('[data-testid="markup-button"]')
    
    // Select highlight tool
    await page.click('[data-testid="highlight-tool"]')
    
    // Select text on page (simulate drag)
    const canvas = page.locator('.pdf-canvas').first()
    await canvas.hover({ position: { x: 100, y: 200 } })
    await page.mouse.down()
    await canvas.hover({ position: { x: 300, y: 200 } })
    await page.mouse.up()
    
    // Highlight should appear
    await expect(page.locator('.annotation-highlight')).toBeVisible()
  })
  
  test('user can add signature', async ({ page }) => {
    await page.click('[data-testid="markup-button"]')
    await page.click('[data-testid="signature-tool"]')
    
    // Draw signature
    const signaturePad = page.locator('[data-testid="signature-pad"]')
    await signaturePad.hover({ position: { x: 50, y: 50 } })
    await page.mouse.down()
    // Draw simple line
    await signaturePad.hover({ position: { x: 150, y: 100 } })
    await page.mouse.up()
    
    // Save signature
    await page.click('[data-testid="save-signature"]')
    
    // Signature should appear on page
    await expect(page.locator('.annotation-signature')).toBeVisible()
  })
  
  test('user can export PDF with annotations', async ({ page }) => {
    // Add annotation
    await page.click('[data-testid="markup-button"]')
    await page.click('[data-testid="highlight-tool"]')
    // ... add highlight ...
    
    // Export
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('[data-testid="export-button"]')
    ])
    
    expect(download.suggestedFilename()).toContain('.pdf')
    expect(await download.path()).toBeTruthy()
  })
})
```

### Test Utilities

```typescript
// tests/utils/renderWithProviders.tsx
import { render } from '@testing-library/react'
import { PDFProvider } from '@/hooks/usePDF'

export function renderWithProviders(
  ui: ReactElement,
  options?: {
    initialPDFState?: Partial<PDFContextValue>
  }
) {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <PDFProvider initialState={options?.initialPDFState}>
        {children}
      </PDFProvider>
    )
  }
  
  return render(ui, { wrapper: Wrapper, ...options })
}
```

```typescript
// tests/utils/mockPDF.ts
import { vi } from 'vitest'

export function createMockPDFDocument(pages: number = 5) {
  return {
    numPages: pages,
    getPage: vi.fn((num) => Promise.resolve({
      getViewport: vi.fn(() => ({ width: 800, height: 1000 })),
      render: vi.fn(() => ({ promise: Promise.resolve() })),
      getTextContent: vi.fn(() => Promise.resolve({ items: [] })),
    })),
    destroy: vi.fn(),
  }
}
```

### Coverage Configuration

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json-summary'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'src/components/ui/**', // shadcn components
      ],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 85,
        statements: 90,
      },
    },
  },
})
```

### Package.json Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:unit": "vitest run",
    "test:watch": "vitest watch",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug"
  }
}
```

## Testing Principles

### What to Test
✅ **Do Test**:
- Business logic in services
- Component rendering and interactions
- State management (context, hooks)
- User workflows (E2E)
- Error handling
- Edge cases and boundary conditions
- Accessibility (a11y)

❌ **Don't Test**:
- Implementation details
- External libraries (PDF.js, pdf-lib)
- shadcn/ui components (already tested)
- Simple getters/setters
- Trivial functions

### Test Quality Over Quantity
- Tests should be readable and maintainable
- One assertion per test (when possible)
- Clear test names: `it('should reject invalid PDF files')`
- Arrange-Act-Assert pattern
- Mock external dependencies
- Avoid testing implementation details

### Coverage is Not Everything
- 90% coverage is a guide, not a goal
- Focus on critical paths first
- 100% coverage doesn't mean bug-free
- Quality of tests > quantity of tests

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run lint
      - run: npm run test:coverage
      - run: npm run build
      
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npx playwright install --with-deps
      - run: npm run build
      - run: npm run test:e2e
```

## Performance Testing

```typescript
// tests/performance/large-document.test.ts
import { describe, it, expect } from 'vitest'

describe('Performance', () => {
  it('should load 100-page PDF in <3 seconds', async () => {
    const start = performance.now()
    const doc = await PDFService.loadDocument(large100PagePDF)
    const end = performance.now()
    
    expect(end - start).toBeLessThan(3000)
  })
  
  it('should maintain 60fps during scroll', async () => {
    // Use performance monitoring tools
  })
})
```

## References
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- PRD: Quality requirements
- AGENT.md: Testing workflow
