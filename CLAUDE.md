# Shopping Site Frontend - Development Guide

## Project Overview

This is a React-based e-commerce frontend application built with TypeScript, Vite, and Material-UI. The architecture follows modern React patterns and is designed for scalability and maintainability.

## Architecture Decisions

### Why This Component Structure?

**Feature-Based Organization**: The project uses a feature-based directory structure rather than a traditional component-type structure. This approach provides several benefits:

- **Scalability**: Each feature (products, cart, auth, account) is self-contained with its own components, hooks, and services
- **Maintainability**: Related code is co-located, making it easier to understand and modify features
- **Team Collaboration**: Different developers can work on different features with minimal conflicts
- **Code Reusability**: Common components are separated into `components/common` and `components/ui` for reuse across features

### What Components Were Created?

**Core Features Structure**:
- `features/products/`: Product search, listing, and detail components
- `features/cart/`: Shopping cart management components  
- `features/auth/`: Authentication and login components
- `features/account/`: User profile and account management
- `components/common/`: Shared business components (SearchBar, ProductCard, etc.)
- `components/ui/`: Pure UI components (Button, Modal, etc.)

**Supporting Infrastructure**:
- `hooks/`: Custom React hooks for shared logic
- `services/`: API clients and external service integrations
- `store/`: State management configuration
- `utils/`: Utility functions and helpers
- `styles/`: Global styles and theme configuration

### Technology Choices

**Material-UI (MUI)**: Chosen for consistent, professional UI components that provide:
- Accessibility out of the box
- Consistent design system
- Comprehensive component library
- Built-in theming support
- Mobile-responsive design

**React Router**: For client-side routing between pages
**TypeScript**: For type safety and better developer experience
**Vite**: For fast development and optimized builds

## Development Guidelines

### Component Development
- Use functional components with hooks exclusively
- Keep components small and focused on single responsibilities
- Use TypeScript interfaces for all props and data structures
- Implement proper error boundaries for robust error handling

### State Management
- Start with local state using useState
- Lift state up when multiple components need access
- Consider global state management (Redux Toolkit) for complex application state
- Use custom hooks to encapsulate and share stateful logic

### API Integration
- Centralize API calls in the `services/` directory
- Use proper error handling for network requests
- Implement loading states for better user experience
- Cache frequently accessed data appropriately

### Styling Approach
- Use Material-UI components as the foundation
- Customize theme in `styles/` directory for brand consistency
- Use sx prop for component-specific styling
- Maintain responsive design principles

### Testing Strategy
- Write unit tests for individual components
- Test custom hooks in isolation
- Implement integration tests for feature workflows
- Use React Testing Library for component testing

## Next Steps for Development

1. **Product Features**: Implement SearchBar, ProductGrid, ProductCard components
2. **Product Details**: Create ProductImageGallery, ProductInfo, ReviewsSection
3. **Shopping Cart**: Build CartItemList, CartSummary, CheckoutButton
4. **User Management**: Develop LoginForm, UserProfile, OrderHistory
5. **API Integration**: Connect components to backend services
6. **State Management**: Implement global state for cart and user data
7. **Testing**: Add comprehensive test coverage
8. **Performance**: Optimize with lazy loading and code splitting

## File Structure Reference

```
src/
├── components/
│   ├── common/          # Shared business components
│   └── ui/              # Pure UI components
├── features/
│   ├── products/        # Product search, listing, details
│   ├── cart/           # Shopping cart functionality
│   ├── auth/           # Authentication
│   └── account/        # User account management
├── hooks/              # Custom React hooks
├── services/           # API clients
├── store/              # State management
├── styles/             # Global styles and themes
├── utils/              # Utility functions
└── pages/              # Page-level components
```

This architecture provides a solid foundation for building a scalable e-commerce application while maintaining code quality and developer productivity.
