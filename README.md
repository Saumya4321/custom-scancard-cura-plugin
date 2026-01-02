## v1 – Application Pipeline Refactor

This version introduces a clean architectural separation:
- Controller layer for Cura-specific logic
- View helpers for UI interactions
- Independent core processing pipeline
- Domain logic is coordinated through a dedicated PrintPipeline abstraction
- Explicit hardware communication layer

The refactor improves:
- Separation of concerns
- Maintainability
- Testability
- Reusability across slicers and hardware platforms


