## v0 – Initial Modular Implementation

This version contains an early working implementation with multiple functional modules
(e.g., geometry parsing, packetization, UDP communication).

However, the Cura plugin directly coordinated these modules, and there was no dedicated
application-layer pipeline to orchestrate the end-to-end print flow.

Limitations of this version:
- Cura-specific logic, UI handling, and domain logic were interleaved
- No centralized print pipeline abstraction
- Tight coupling between the Cura plugin and lower-level processing modules

This version is preserved to document the architectural evolution toward a cleaner,
layered design introduced in later revisions.
