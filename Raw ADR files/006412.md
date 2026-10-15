# ADR-031: Adoption of PrimeReact as Default UI Component Library

## Status
Accepted

## Date
2025-03-06

## Context
As part of our React-based micro-frontend architecture (ADR-025) and our selection of React as the default frontend framework (ADR-027), we need a comprehensive UI component library that provides:

- A wide range of pre-built, accessible components that follow modern design principles
- Consistent styling and theming capabilities across the application
- Robust documentation and community support
- Compatibility with our TypeScript implementation
- Support for responsive design and mobile-first approach
- Flexibility for customization to match our design system
- Good performance characteristics
- Integration with our React Native mobile development (ADR-028)
- Support for internationalization and localization (ADR-030)
- Accessibility compliance

The choice of UI component library will significantly impact development velocity, visual consistency, user experience, and frontend maintainability across our micro-frontend architecture.

## Decision
We will adopt **PrimeReact** as our default UI component library. PrimeReact provides:

### 1. Component Coverage
- Extensive collection of 80+ UI components covering all common interface needs
- Form controls (inputs, selects, checkboxes, etc.)
- Data display components (tables, trees, charts)
- Navigation components (menus, breadcrumbs, tabs)
- Overlay components (dialogs, tooltips, notifications)
- Advanced components (file upload, rich text editor, calendar)

### 2. Theming and Styling
- Built-in theme engine with multiple pre-designed themes
- Support for custom theme creation
- CSS-in-JS approach with styled-components integration
- Design tokens for consistent styling
- Dark mode support
- Visual theme designer tool

### 3. Technical Characteristics
- Full TypeScript support with comprehensive type definitions
- Responsive design support for all components
- Accessibility compliance with WCAG standards
- Server-side rendering compatibility
- Small bundle size with tree-shaking support
- No external dependencies

### 4. Ecosystem Benefits
- PrimeFlex CSS utility library integration
- PrimeIcons icon library included
- PrimeBlocks UI blocks and templates
- PrimeVue and PrimeNG equivalents for potential Vue/Angular components
- PrimeFaces for server-side implementations
- PrimeReact Mobile companion for React Native

## Implementation Approach

1. **Integration and Setup**
   - Add PrimeReact and its dependencies to the shared dependencies
   - Configure theme system and global styling
   - Implement shared theme provider component
   - Set up PrimeReact configuration at the application shell level
   - Create documentation for component usage guidelines

2. **Component Standardization**
   - Create wrapper components around PrimeReact base components
   - Implement consistent prop interfaces
   - Apply default styling and behavior aligned with our design system
   - Configure default accessibility attributes
   - Document component usage with examples

3. **Design System Integration**
   - Map design tokens to PrimeReact theme variables
   - Create custom theme based on our brand guidelines
   - Implement shared style mixins and utilities
   - Configure responsive breakpoints
   - Establish design-to-code workflow

4. **Micro-Frontend Implementation**
   - Configure PrimeReact for use across micro-frontends
   - Establish shared component library with PrimeReact extensions
   - Create component showcase and documentation
   - Implement versioning strategy for component updates

5. **Mobile Integration**
   - Create parallel React Native components using PrimeReact Mobile
   - Ensure consistent behavior between web and mobile
   - Implement platform-specific optimizations
   - Share theme tokens across platforms

## Consequences

### Positive
- Rich set of ready-to-use components accelerates development
- Consistent styling and behavior across the application
- Robust theming system supports our design requirements
- TypeScript integration improves developer experience
- Accessibility compliance built into components
- Active development and community support
- Cross-platform options for web and mobile
- Comprehensive documentation and examples
- Flexible customization options
- Commercial support available if needed

### Negative
- Learning curve for developers not familiar with PrimeReact
- Some components may require additional customization to match design
- Bundle size considerations for performance-critical applications
- Potential styling conflicts with existing CSS frameworks
- Dependency on third-party library for core UI functionality
- Need to keep up with PrimeReact version updates
- Some advanced components may have licensing considerations

## Alternatives Considered

1. **Material-UI (MUI)**
   - Google Material Design implementation
   - Large community and widespread adoption
   - More opinionated design system
   - Larger bundle size
   - Less flexibility for custom theming
   - Strong TypeScript support
   - Less comprehensive component set compared to PrimeReact

2. **Ant Design**
   - Enterprise-focused design system
   - Comprehensive component library
   - Less flexible theming options
   - Larger bundle size
   - Strong community in Asia
   - Good documentation but less customization
   - Some internationalization challenges

3. **Chakra UI**
   - Accessibility-focused component library
   - Simpler API and learning curve
   - Less comprehensive component set
   - Good theming system based on design tokens
   - Smaller community and ecosystem
   - Less mature than other options
   - Limited advanced components

4. **Custom Component Library**
   - Complete control over design and implementation
   - No external dependencies
   - Significant development and maintenance overhead
   - Requires dedicated team for component development
   - Longer time-to-market for new features
   - Need to implement and test accessibility
   - Higher cost of ownership

## Implementation Notes

### Basic Setup

```typescript
// Install dependencies
// npm install primereact primeicons primeflex

// App.tsx - Application Shell
import React from 'react';
import { PrimeReactProvider } from 'primereact/api';
import { Button } from 'primereact/button';

// Import themes
import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';

// Custom theme configuration
const value = {
  ripple: true,
  inputStyle: 'filled',
  buttonStyle: 'raised',
  locale: 'en',
  theme: 'lara-light-indigo'
};

const App = () => {
  return (
    <PrimeReactProvider value={value}>
      <div className="app-container">
        <header>
          <h1>Aronim Bookstore</h1>
        </header>
        <main>
          <Button label="Primary" />
          <Button label="Secondary" severity="secondary" />
          <Button label="Success" severity="success" />
        </main>
      </div>
    </PrimeReactProvider>
  );
};

export default App;
```

### Custom Theme Configuration

```typescript
// theme/aronim-theme.js
import { createTheme } from 'primereact/api';

export const arominTheme = createTheme('lara-light-indigo', {
  primaryColor: '#3B82F6',
  primaryDarkColor: '#2563EB',
  primaryLightColor: '#60A5FA',
  accentColor: '#E11D48',
  accentDarkColor: '#BE123C',
  accentLightColor: '#FB7185',
  
  // Typography
  fontFamily: 'Inter, system-ui, sans-serif',
  fontSize: '1rem',
  textColor: '#1F2937',
  textSecondaryColor: '#4B5563',
  
  // Spacing
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem'
  },
  
  // Border radius
  borderRadius: '0.375rem',
  
  // Transitions
  transitionDuration: '0.2s'
});
```

### Component Wrapper Example

```typescript
// components/Button/Button.tsx
import React from 'react';
import { Button as PrimeButton } from 'primereact/button';
import type { ButtonProps as PrimeButtonProps } from 'primereact/button';

export interface ButtonProps extends Omit<PrimeButtonProps, 'size'> {
  size?: 'small' | 'medium' | 'large';
  variant?: 'filled' | 'outlined' | 'text';
  fullWidth?: boolean;
}

const sizeClasses = {
  small: 'p-button-sm',
  medium: '',
  large: 'p-button-lg'
};

const variantClasses = {
  filled: '',
  outlined: 'p-button-outlined',
  text: 'p-button-text'
};

export const Button: React.FC<ButtonProps> = ({
  size = 'medium',
  variant = 'filled',
  fullWidth = false,
  className = '',
  ...props
}) => {
  const classes = [
    sizeClasses[size],
    variantClasses[variant],
    fullWidth ? 'w-full' : '',
    className
  ].filter(Boolean).join(' ');

  return <PrimeButton className={classes} {...props} />;
};

export default Button;
```

### DataTable Example with TypeScript

```typescript
// components/BookTable/BookTable.tsx
import React, { useState } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { InputText } from 'primereact/inputtext';
import { FilterMatchMode } from 'primereact/api';

interface Book {
  id: string;
  title: string;
  author: string;
  genre: string;
  price: number;
  rating: number;
  publishDate: Date;
}

interface BookTableProps {
  books: Book[];
  loading: boolean;
  onRowSelect?: (book: Book) => void;
}

export const BookTable: React.FC<BookTableProps> = ({ books, loading, onRowSelect }) => {
  const [filters, setFilters] = useState({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    title: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    author: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    genre: { value: null, matchMode: FilterMatchMode.EQUALS },
  });
  
  const [globalFilterValue, setGlobalFilterValue] = useState('');

  const onGlobalFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    let _filters = { ...filters };
    
    _filters['global'].value = value;
    
    setFilters(_filters);
    setGlobalFilterValue(value);
  };

  const renderHeader = () => {
    return (
      <div className="flex justify-content-between align-items-center">
        <h5 className="m-0">Books Catalog</h5>
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText 
            value={globalFilterValue} 
            onChange={onGlobalFilterChange} 
            placeholder="Search..." 
          />
        </span>
      </div>
    );
  };

  const priceBodyTemplate = (rowData: Book) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(rowData.price);
  };

  const dateBodyTemplate = (rowData: Book) => {
    return new Intl.DateTimeFormat('en-US').format(rowData.publishDate);
  };

  const header = renderHeader();

  return (
    <DataTable 
      value={books} 
      paginator 
      rows={10}
      rowsPerPageOptions={[5, 10, 25]} 
      dataKey="id"
      filters={filters}
      filterDisplay="menu"
      loading={loading}
      responsiveLayout="scroll"
      globalFilterFields={['title', 'author', 'genre']}
      header={header}
      emptyMessage="No books found."
      onRowSelect={onRowSelect && (e => onRowSelect(e.data))}
      selectionMode={onRowSelect ? 'single' : undefined}
    >
      <Column field="title" header="Title" sortable filter />
      <Column field="author" header="Author" sortable filter />
      <Column field="genre" header="Genre" sortable filter />
      <Column field="price" header="Price" body={priceBodyTemplate} sortable />
      <Column field="rating" header="Rating" sortable />
      <Column field="publishDate" header="Published" body={dateBodyTemplate} sortable />
    </DataTable>
  );
};

export default BookTable;
```

### Internationalization Integration

```typescript
// i18n/PrimeReactI18nProvider.tsx
import React from 'react';
import { PrimeReactProvider, PrimeReactContext } from 'primereact/api';
import { useTranslation } from 'react-i18next';

// PrimeReact locale imports
import { locale as enLocale } from 'primereact/locale/en.json';
import { locale as esLocale } from 'primereact/locale/es.json';
import { locale as frLocale } from 'primereact/locale/fr.json';
import { locale as deLocale } from 'primereact/locale/de.json';

const localeMap = {
  en: enLocale,
  es: esLocale,
  fr: frLocale,
  de: deLocale
};

interface PrimeReactI18nProviderProps {
  children: React.ReactNode;
}

export const PrimeReactI18nProvider: React.FC<PrimeReactI18nProviderProps> = ({ children }) => {
  const { i18n } = useTranslation();
  const currentLocale = i18n.language.split('-')[0];
  
  // Get the PrimeReact context value from the parent provider
  const parentContext = React.useContext(PrimeReactContext);
  
  // Merge the parent context with our locale
  const value = {
    ...parentContext,
    locale: localeMap[currentLocale] || localeMap.en
  };
  
  return (
    <PrimeReactProvider value={value}>
      {children}
    </PrimeReactProvider>
  );
};

export default PrimeReactI18nProvider;
```

### Mobile Integration with React Native

```typescript
// mobile/components/Button.tsx
import React from 'react';
import { Button as PrimeButton } from 'primereact/button';
import { StyleSheet } from 'react-native';

// Props and implementation similar to web version
// with React Native specific adjustments
```

## Compliance Verification
- Accessibility testing of all components against WCAG 2.1 standards
- Performance testing of component rendering and interactions
- Responsive design testing across device sizes
- Browser compatibility testing
- Theme consistency verification
- Bundle size analysis
- TypeScript type checking
- Integration testing with our micro-frontend architecture

## References
- PrimeReact Documentation: https://primereact.org/
- PrimeReact GitHub Repository: https://github.com/primefaces/primereact
- PrimeFlex Documentation: https://primeflex.org/
- PrimeIcons: https://primereact.org/icons/
- React TypeScript Documentation: https://reactjs.org/docs/static-type-checking.html#typescript
- WCAG Accessibility Guidelines: https://www.w3.org/WAI/standards-guidelines/wcag/
- Material-UI (Alternative): https://mui.com/
- Ant Design (Alternative): https://ant.design/
- Chakra UI (Alternative): https://chakra-ui.com/
