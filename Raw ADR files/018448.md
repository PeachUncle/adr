# Architectural Decision Record (ADR): Use of Tailwind CSS

## Context

To provide an efficient and flexible approach to interface design, we decided to use **Tailwind CSS** as the primary solution for styling in the application.

## Decision

**Date**: 24/03/2025

The application will use **Tailwind CSS** for styling due to the following reasons:

- **Utility-First Approach**: Allows applying styles directly to HTML classes, reducing the need for custom CSS and speeding up development.
- **Customization**: Offers a highly customizable design system that adapts to the specific needs of the project.
- **Responsiveness**: Makes it easy to create responsive designs with classes that can be easily applied for different screen sizes.
- **Consistency**: Promotes visual consistency by using a defined set of utilities and themes.

## Implementation

### Installation

To install Tailwind CSS, run:

```sh
pnpm add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Configuration

Add the following lines to the `tailwind.config.js` file to configure the paths of the files where Tailwind should be applied:

```javascript
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}', // Adjust according to your project structure
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

### Usage

#### Example Component with Tailwind CSS

```tsx
function Button({ children }) {
  return (
    <button className='bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700'>
      {children}
    </button>
  );
}

function App() {
  return (
    <div className='flex items-center justify-center h-screen'>
      <Button>Click Me</Button>
    </div>
  );
}
```

### Best Practices

- Use **Tailwind CSS** utility classes for styling instead of global CSS or inline styles.
- Maintain consistency in styles by creating reusable components with Tailwind.
- Utilize Tailwind's color and spacing system to ensure cohesive and responsive design.
- Take advantage of Tailwind's customization to meet specific project needs without sacrificing clarity and simplicity.

## Status

**Accepted**

## Consequences

- All future interface developments should prioritize the use of **Tailwind CSS**.
- Developers must adhere to best practices to ensure efficient and maintainable styling.
