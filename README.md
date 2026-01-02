## v1 – Refactored Architecture

This version introduces a clean architectural separation:
- Controller layer for Cura-specific logic
- View helpers for UI interactions
- Independent core processing pipeline
- Explicit hardware communication layer

The refactor improves:
- Maintainability
- Testability
- Reusability across slicers and hardware platforms
