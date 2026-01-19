<!--
  SYNC IMPACT REPORT
  ==================
  Version change: [NEW] → 1.0.0

  This is the initial constitution ratification for the Shop Monitor project.

  Added principles:
  - I. Real-Time Architecture
  - II. Terminal Aesthetic
  - III. Vault-Centric Design
  - IV. Component Isolation
  - V. Message Classification Compliance

  Added sections:
  - Technology Stack (mandatory requirements)
  - Code Quality Standards
  - Performance Requirements
  - Security Requirements

  Templates requiring updates:
  ✅ plan-template.md - Constitution Check section will reference these principles
  ✅ spec-template.md - Requirements must align with performance/quality standards
  ✅ tasks-template.md - Tasks must respect real-time architecture and component isolation

  Follow-up TODOs: None
-->

# Shop Monitor Constitution

## Core Principles

### I. Real-Time Architecture

All system updates MUST occur via file watching, not polling. File change detection to UI
update latency MUST remain below 100ms at all times. This principle is NON-NEGOTIABLE and
applies to every feature, component, and user-facing interaction.

**Rationale**: Real-time responsiveness is core to the Shop Monitor value proposition.
Polling-based architectures introduce unacceptable latency and resource waste. File
watching ensures immediate propagation of vault changes to the TUI, maintaining system
performance and user trust.

**Requirements**:
- Use `watchdog` library for all file system monitoring
- Event handlers MUST process file changes and trigger UI updates within 100ms
- No background polling loops permitted
- All async operations MUST maintain the latency guarantee

### II. Terminal Aesthetic

The interface MUST adhere to strict terminal aesthetic conventions: black background,
cyan/green color palette exclusively, monospace fonts, and box-drawing characters for UI
layout. Modern UI frameworks (React, Vue, Electron, web views) are explicitly PROHIBITED.

**Rationale**: Shop Monitor is a terminal user interface tool designed for focused,
distraction-free operation. The constrained color palette and terminal rendering enforce
clarity, accessibility, and professional aesthetics. Deviation undermines the product's
design philosophy and user experience consistency.

**Requirements**:
- Black background (#000000 or terminal default)
- Cyan (#00FFFF) and green (#00FF00) for text and UI elements only
- Textual framework widgets exclusively
- Box-drawing characters (─ │ ┌ ┐ └ ┘ ├ ┤) for borders and layout
- No images, gradients, or custom fonts

### III. Vault-Centric Design

Markdown files in the Obsidian vault are the single source of truth. The system operates in
read-only mode for content parsing; writes are permitted ONLY for file move operations
(e.g., moving messages between folders). All business logic, UI state, and data presentation
derive from vault file contents and frontmatter metadata.

**Rationale**: Users manage their data in Obsidian. Shop Monitor augments their workflow
without introducing data duplication, sync conflicts, or proprietary formats. Read-only
parsing ensures Shop Monitor never corrupts user data, maintaining trust and reliability.

**Requirements**:
- Use `python-frontmatter` for parsing markdown files
- Read file contents and YAML frontmatter only; never modify content
- File moves permitted using OS-level operations (shutil.move or pathlib)
- No external databases, caches, or state stores for message content
- Validate all file paths before read/write operations

### IV. Component Isolation

Each UI widget MUST operate independently. Components communicate exclusively via
message-passing (Textual message system). Direct method calls between widgets, shared
mutable state, and tight coupling are PROHIBITED.

**Rationale**: Component isolation ensures maintainability, testability, and parallel
development. Message-based communication decouples components, enabling independent
evolution, unit testing without mocks, and future extensibility without cascading changes.

**Requirements**:
- All inter-component communication via Textual's `post_message()` API
- Each widget maintains its own internal state
- No direct widget-to-widget method invocations
- No global state variables shared between components
- Components MUST be testable in isolation

### V. Message Classification Compliance

The system MUST support exactly three message types (Refund, Support, Inquiry) across
exactly three channels (Website, Gmail, WhatsApp). This classification scheme is
NON-NEGOTIABLE and embedded in the vault structure, UI design, and all business logic.

**Rationale**: The three-type, three-channel taxonomy is foundational to the Shop Monitor
domain model. Users organize their customer communications using this structure. Features
that violate this taxonomy break the user's mental model and data organization.

**Requirements**:
- Hardcoded message types: Refund, Support, Inquiry (no dynamic types)
- Hardcoded channels: Website, Gmail, WhatsApp (no dynamic channels)
- Frontmatter MUST include `type` and `channel` fields matching these values
- UI components MUST filter, display, and count messages by type and channel
- No "Other" or "Unknown" categories; invalid messages rejected with clear errors

## Technology Stack

**NON-NEGOTIABLE**: The following technologies are required. Substitutions are prohibited
without a Major version constitution amendment.

- **Python**: Version 3.10 or higher
- **TUI Framework**: Textual (latest stable version)
- **File Monitoring**: watchdog library
- **Markdown Parsing**: python-frontmatter library

**Rationale**: These technologies form the architectural foundation. Python 3.10+ provides
modern async features, type hints, and ecosystem maturity. Textual delivers terminal UI
capabilities matching our aesthetic requirements. Watchdog ensures cross-platform file
watching. Python-frontmatter handles YAML frontmatter parsing reliably.

## Code Quality Standards

### Error Handling

Error handling is MANDATORY for all file operations (read, write, move, watch). Every file
I/O operation MUST be wrapped in try/except blocks with explicit exception handling.

**Required practices**:
- Catch specific exceptions (FileNotFoundError, PermissionError, etc.)
- Log all errors with context (file path, operation, timestamp)
- Provide graceful degradation (skip malformed files, continue processing)
- Never use bare `except:` clauses
- Surface critical errors to the user via UI notifications

### Logging

Structured logging is REQUIRED for:
- File change events (path, change type, timestamp)
- UI update operations (widget, action, duration)
- User actions (navigation, file moves, filters applied)

**Required practices**:
- Use Python `logging` module (INFO level minimum)
- Include timestamps, log levels, and context in all log messages
- Log to both file and console (console for development, file for production)
- Never log sensitive customer data (message content, personal info)

### Configuration Management

No hardcoded file paths permitted. All paths, settings, and configurable values MUST use:
- Environment variables (via `python-dotenv` or equivalent)
- Configuration files (TOML, YAML, or JSON)
- Command-line arguments for runtime overrides

**Required practices**:
- Vault path MUST be configurable
- Color scheme MUST be configurable (within cyan/green palette)
- Polling intervals MUST be configurable (though polling itself is prohibited)
- Provide sensible defaults for all configuration values

### Graceful Degradation

The system MUST handle failures without crashing. When errors occur:
- Display error notifications in the TUI (non-blocking)
- Continue operating on unaffected components
- Retry transient failures (file locks, permissions) with exponential backoff
- Provide fallback behavior (e.g., skip malformed files, use default values)

## Performance Requirements

The following performance budgets are MANDATORY and MUST be verified during development:

- **File Change to UI Update**: Maximum 100ms latency (p95)
- **Full Vault Scan**: Maximum 2 seconds for initial load and complete rescan
- **Memory Footprint**: Maximum 100MB resident memory under normal operation

**Rationale**: Shop Monitor is a lightweight tool for rapid triage and response. High
latency or memory consumption degrades user experience and violates the "terminal tool"
philosophy. These budgets ensure responsiveness on standard hardware.

**Verification**:
- Profile file watching and UI update paths during development
- Test with representative vault sizes (1000+ markdown files)
- Monitor memory usage during extended operation
- Include performance regression tests in CI (if applicable)

## Security Requirements

Shop Monitor is a local-only tool operating on user-controlled data. Security requirements
focus on data integrity and safe file handling:

### Local-Only Operation

- No network requests permitted (except for future webhook/API integrations explicitly
  specified in feature specs)
- No data transmission to external services
- No telemetry or analytics collection

### Path Validation

All file paths MUST be validated before use:
- Confirm paths are within the configured vault directory (prevent directory traversal)
- Reject symbolic links pointing outside the vault
- Sanitize user-provided paths (e.g., from command-line arguments)

### Content Sanitization

Terminal display content MUST be sanitized to prevent terminal injection attacks:
- Escape ANSI control sequences in user-generated content (markdown files)
- Strip or escape characters that could manipulate terminal state
- Use Textual's built-in text rendering (which handles sanitization)

## Governance

This constitution supersedes all other development practices, coding preferences, and
implementation details. When conflicts arise, the constitution takes precedence.

### Amendment Process

1. Propose amendment with clear rationale and impact analysis
2. Document affected features, code, and templates
3. Increment constitution version according to semantic versioning:
   - **MAJOR**: Backward-incompatible changes (removing/redefining principles)
   - **MINOR**: Adding new principles or sections
   - **PATCH**: Clarifications, wording improvements, typo fixes
4. Update all dependent templates and documentation
5. Commit with message: `docs: amend constitution to vX.Y.Z (summary)`

### Compliance Review

All features MUST pass constitution compliance checks:
- Architecture reviews verify adherence to Core Principles
- Code reviews validate Code Quality Standards
- Performance testing confirms Performance Requirements
- Security reviews ensure Security Requirements

### Complexity Justification

Any feature violating constitution principles MUST be justified in the implementation plan's
"Complexity Tracking" section. Justifications MUST explain:
- Why the violation is necessary
- Why simpler constitutional alternatives are insufficient
- How the violation is minimized and contained

**Version**: 1.0.0 | **Ratified**: 2026-01-17 | **Last Amended**: 2026-01-17
