# Shopping Site Frontend - Development Guide

## Project Overview
This is a React-based shopping site application similar to Amazon, focusing on product search, listing, and detail views. The project is scaffolded with Vite, TypeScript, and Material-UI for a modern development experience.

## Architecture Decisions

### Why This Component Structure?
Based on the provided specifications, I have created a scalable architecture that separates concerns and promotes reusability:

#### **Core Components Created:**
1. **Product Search & List Page (/)** - Main landing page with search functionality
2. **Product Detail Page (/products/:id)** - Individual product detail views  
3. **Product Card Component** - Reusable product display component
4. **Search Bar Component** - Centralized search functionality

#### **Directory Structure Rationale:**

**`src/components/`** - Houses reusable UI components
- `common/` - Shared components used across features (SearchBar, ProductCard)
- `ui/` - Basic UI building blocks and styled components

**`src/features/`** - Feature-specific modules following domain-driven design
- `products/` - All product-related components, hooks, and services

**`src/hooks/`** - Custom React hooks for shared logic
- Will contain hooks like `useProductSearch`, `useProductDetail`

**`src/services/`** - API clients and external service integrations
- Product API calls, search services, etc.

**`src/store/`** - State management (Redux Toolkit recommended)
- Global state for search filters, cart, user preferences

**`src/utils/`** - Utility functions and helpers
- Price formatting, image optimization, validation helpers

### Why Material-UI (MUI)?
- **Consistency**: Provides a cohesive design system out of the box
- **Accessibility**: Built-in ARIA support and keyboard navigation
- **Responsive**: Mobile-first responsive components
- **Theming**: Easy dark/light mode switching and brand customization
- **Performance**: Tree-shaking support for optimal bundle size

### Why This Tech Stack?
- **Vite**: Fast development server and optimized builds
- **TypeScript**: Type safety and better developer experience
- **React Router**: Client-side routing for SPA navigation
- **Emotion**: CSS-in-JS solution that works seamlessly with MUI

## Development Guidelines

### Component Development
1. **Functional Components Only**: Use hooks instead of class components
2. **TypeScript First**: Define proper interfaces for all props and state
3. **MUI Components**: Use Material-UI components for consistent styling
4. **Responsive Design**: Ensure all components work on mobile and desktop

### State Management Strategy
- **Local State**: Use `useState` for component-specific state
- **Shared State**: Use Context API or Redux Toolkit for cross-component state
- **Server State**: Consider React Query for API data management

### File Naming Conventions
- Components: `PascalCase.tsx` (e.g., `ProductCard.tsx`)
- Hooks: `camelCase.ts` starting with "use" (e.g., `useProductSearch.ts`)
- Services: `camelCase.ts` (e.g., `productApi.ts`)
- Types: `PascalCase.ts` with `.types.ts` suffix (e.g., `Product.types.ts`)

### Performance Considerations
- Use `React.memo()` for expensive components
- Implement `useCallback` and `useMemo` for optimization
- Lazy load routes and heavy components
- Optimize images and implement proper loading states

### Testing Strategy
- Unit tests for utility functions and hooks
- Component tests using React Testing Library
- Integration tests for user flows
- E2E tests for critical paths (search → detail → cart)

## Next Steps for Development
1. Implement the SearchBar component with autocomplete
2. Create the ProductCard component with proper image handling
3. Build the product list page with filtering and sorting
4. Develop the product detail page with image carousel
5. Add routing between list and detail views
6. Implement responsive grid layouts
7. Add loading states and error handling
8. Integrate with backend APIs

## API Integration Points
- Product search endpoint
- Product detail endpoint  
- Category and filter endpoints
- Image CDN integration
- Review and rating endpoints

This architecture provides a solid foundation for building a scalable e-commerce frontend that can grow with additional features like cart management, user authentication, and checkout flows.

