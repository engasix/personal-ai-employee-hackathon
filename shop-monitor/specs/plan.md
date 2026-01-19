# Implementation Plan: Shop Monitor - Real-Time Terminal Dashboard

**Branch**: `001-realtime-dashboard` | **Date**: 2026-01-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/spec.md`

## Summary

Build a real-time terminal dashboard for monitoring FTE Shop AI Employee operations via Obsidian vault file watching. The dashboard displays live metrics (orders, revenue, response times), channel activity breakdowns (Website/Gmail/WhatsApp), message classification analytics (Refund/Support/Inquiry success rates), and pending task approvals with interactive mouse-clickable buttons. Core technical approach: Python 3.10+ with Textual TUI framework, watchdog for <100ms file system monitoring, python-frontmatter for markdown parsing, message-passing architecture for component isolation.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: Textual (TUI framework), watchdog (file monitoring), python-frontmatter (YAML parsing)
**Storage**: File system only - Obsidian vault markdown files with YAML frontmatter (no database)
**Testing**: pytest for unit/integration tests, Textual's built-in test utilities for widget testing
**Target Platform**: macOS/Linux/Windows terminals with UTF-8 and ANSI color support
**Project Type**: Single project (terminal application)
**Performance Goals**: <100ms file-to-UI latency (p95), <2s initial vault scan, <100MB memory footprint
**Constraints**: Real-time architecture mandatory (no polling), read-only vault access except file moves, terminal aesthetic enforcement (black/cyan/green only)
**Scale/Scope**: Support 1000+ markdown files in vault, 20-item activity stream, multi-panel responsive layout

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Real-Time Architecture ✓ PASS
- **Requirement**: File watching only, <100ms latency
- **Plan Compliance**: Using watchdog library for event-driven file monitoring, Textual's reactive system for <100ms UI updates
- **Validation**: No polling loops, all updates triggered by watchdog events

### Principle II: Terminal Aesthetic ✓ PASS
- **Requirement**: Black background, cyan/green only, Textual framework, box-drawing characters
- **Plan Compliance**: Textual framework enforced, custom CSS for color palette, built-in box-drawing support
- **Validation**: No web frameworks, no custom rendering outside Textual

### Principle III: Vault-Centric Design ✓ PASS
- **Requirement**: Read-only parsing, writes only for file moves, no external storage
- **Plan Compliance**: python-frontmatter for read-only parsing, pathlib/shutil for approved file moves only
- **Validation**: No database, no content modification, path validation for all operations

### Principle IV: Component Isolation ✓ PASS
- **Requirement**: Message-passing only, no shared state, independent widgets
- **Plan Compliance**: Textual's post_message() for all inter-component communication, each widget maintains own state
- **Validation**: No direct widget references, no global state variables

### Principle V: Message Classification Compliance ✓ PASS
- **Requirement**: Hardcoded 3 types (Refund/Support/Inquiry), 3 channels (Website/Gmail/WhatsApp)
- **Plan Compliance**: Enum-based type/channel validation, frontmatter parsing enforces schema
- **Validation**: No dynamic types/channels, invalid messages rejected with errors

### Technology Stack Compliance ✓ PASS
- Python 3.10+: ✓
- Textual framework: ✓
- watchdog library: ✓
- python-frontmatter library: ✓

### Code Quality Standards ✓ PASS
- **Error Handling**: try/except for all file I/O, specific exception handling planned
- **Logging**: Python logging module for file events, UI updates, user actions
- **Configuration**: Environment variables for vault path and settings
- **Graceful Degradation**: Error notifications in UI, continue processing on malformed files

### Performance Requirements ✓ PASS
- **File-to-UI Latency**: <100ms via watchdog + Textual reactive system
- **Vault Scan**: <2s via parallel file processing and metadata caching
- **Memory Footprint**: <100MB via bounded activity stream (20 items) and no content caching

### Security Requirements ✓ PASS
- **Local-Only**: No network requests in scope
- **Path Validation**: All file operations validate paths within vault directory
- **Content Sanitization**: Textual's built-in rendering handles ANSI escaping

**GATE STATUS**: ✅ PASSED - All constitutional requirements satisfied, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command - N/A for TUI app)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
shop-monitor/
├── src/
│   ├── __init__.py
│   ├── monitor.py           # Main entry point, application setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vault_message.py     # VaultMessage entity
│   │   ├── pending_task.py      # PendingTask entity
│   │   ├── activity_event.py    # ActivityEvent entity
│   │   ├── dashboard_metrics.py # DashboardMetrics aggregate
│   │   └── enums.py             # MessageType, Channel, Status enums
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vault_watcher.py     # watchdog file monitoring service
│   │   ├── vault_parser.py      # python-frontmatter parsing
│   │   ├── metrics_calculator.py # Aggregate statistics
│   │   └── file_manager.py      # File move operations
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── metrics_panel.py     # Live metrics display
│   │   ├── channel_panel.py     # Channel activity breakdown
│   │   ├── classification_panel.py # Message classification analytics
│   │   ├── approval_panel.py    # Pending approvals list
│   │   ├── activity_stream.py   # Recent activity feed
│   │   ├── status_bar.py        # Connection status & timestamp
│   │   └── task_modal.py        # Task detail modal
│   ├── app.py               # Textual App main class
│   └── config.py            # Configuration loading (env vars)
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_vault_parser.py
│   │   ├── test_metrics_calculator.py
│   │   └── test_file_manager.py
│   └── integration/
│       ├── test_vault_watcher.py
│       ├── test_ui_updates.py
│       └── test_approval_workflow.py
├── pyproject.toml       # UV project config, dependencies
├── README.md
└── .env.example         # Environment variable template
```

**Structure Decision**: Single project structure chosen because this is a standalone terminal application with no API/frontend separation. All code is Python-based TUI application logic. Tests organized by unit (isolated component testing) and integration (file watching + UI update flows). Widgets separated from services to maintain component isolation per constitutional principle IV.

## Complexity Tracking

**No constitutional violations** - All requirements satisfied without exceptions.

