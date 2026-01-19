---
description: "Task list for Shop Monitor - Real-Time Terminal Dashboard implementation"
---

# Tasks: Shop Monitor - Real-Time Terminal Dashboard

**Input**: Design documents from `/specs/`
**Prerequisites**: plan.md (technical architecture), spec.md (user stories with priorities)

**Tests**: Tests are OPTIONAL - only included where explicitly beneficial for complex logic validation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Python package structure with modular organization per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md (src/, src/models/, src/services/, src/widgets/, tests/unit/, tests/integration/)
- [x] T002 Initialize Python project with pyproject.toml (UV project config) including dependencies: textual, watchdog, python-frontmatter, pytest
- [x] T003 [P] Create .env.example template with VAULT_PATH configuration variable
- [x] T004 [P] Create README.md with installation instructions and single-command launch guidance
- [x] T005 [P] Create all __init__.py files for Python package structure (src/, src/models/, src/services/, src/widgets/, tests/, tests/unit/, tests/integration/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create enums module in src/models/enums.py (MessageType: Refund/Support/Inquiry, Channel: Website/Gmail/WhatsApp, Status: Pending/Resolved/Escalated)
- [x] T007 [P] Create VaultMessage entity model in src/models/vault_message.py (attributes: type, channel, status, timestamp, file_path, content)
- [x] T008 [P] Create PendingTask entity model in src/models/pending_task.py (attributes: task_id, description, priority, creation_timestamp, file_path, full_content)
- [x] T009 [P] Create ActivityEvent entity model in src/models/activity_event.py (attributes: timestamp, event_type, channel, message_type, status_transition, file_path)
- [x] T010 [P] Create DashboardMetrics aggregate model in src/models/dashboard_metrics.py (attributes: total_orders, total_revenue, avg_response_time, pending_count, channel_counts, type_counts, auto_resolve_rates)
- [x] T011 Implement VaultParser service in src/services/vault_parser.py (python-frontmatter parsing, YAML frontmatter extraction, markdown content handling)
- [x] T012 Implement configuration loading in src/config.py (environment variable VAULT_PATH, validation, defaults)
- [x] T013 Setup VaultWatcher service skeleton in src/services/vault_watcher.py (watchdog FileSystemEventHandler base class, event queue structure)
- [x] T014 Create Textual App base class in src/app.py (compose layout structure, CSS loading for black/cyan/green theme, message passing architecture)
- [x] T015 Create main entry point in src/monitor.py (argument parsing, config loading, app initialization, error handling)
- [x] T016 [P] Setup Python logging configuration in src/config.py (file events, UI updates, user actions with timestamps)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Live System Status Monitoring (Priority: P1) 🎯 MVP

**Goal**: Display real-time metrics (orders, revenue, response times, pending tasks) that update within 100ms when vault files change

**Independent Test**: Launch dashboard, create/modify files in vault, verify metrics update within 100ms without user interaction

### Implementation for User Story 1

- [x] T017 [P] [US1] Implement MetricsCalculator service in src/services/metrics_calculator.py (aggregate file counts, parse Dashboard.md metrics, calculate today's stats using midnight local time)
- [x] T018 [P] [US1] Create StatusBar widget in src/widgets/status_bar.py (connection status indicator, last update timestamp display)
- [x] T019 [US1] Create MetricsPanel widget in src/widgets/metrics_panel.py (display order count, revenue, avg response time, pending count with reactive updates)
- [x] T020 [US1] Implement vault file watching in src/services/vault_watcher.py (watchdog event handlers for create/modify/delete/move, event-to-UI message conversion)
- [x] T021 [US1] Integrate VaultWatcher with Textual app in src/app.py (start watcher thread, handle file change messages, trigger MetricsCalculator updates)
- [x] T022 [US1] Connect MetricsPanel to dashboard metrics updates in src/app.py (reactive data binding, post_message handling, <100ms UI refresh)
- [x] T023 [US1] Implement connection state monitoring in src/services/vault_watcher.py (detect vault unavailable, automatic reconnection, error state tracking)
- [x] T024 [US1] Update StatusBar to show connection state changes and last update timestamps

**Checkpoint**: At this point, User Story 1 should be fully functional - dashboard shows live metrics and updates in real-time

---

## Phase 4: User Story 4 - Pending Task Approval (Priority: P1)

**Goal**: Approve or reject pending tasks directly from dashboard with file move operations and automatic UI updates

**Independent Test**: Place task files in Pending_Approval folder, click Approve/Reject buttons, verify files move to appropriate folders and dashboard updates

### Implementation for User Story 4

- [x] T025 [P] [US4] Implement FileManager service in src/services/file_manager.py (move files between folders with path validation, error handling for permissions/locks)
- [x] T026 [P] [US4] Create ApprovalPanel widget in src/widgets/approval_panel.py (list tasks from Pending_Approval, Approve/Reject buttons per task, click handlers)
- [x] T027 [US4] Create TaskModal widget in src/widgets/task_modal.py (ModalScreen for full task content display, Approve/Reject action buttons, ESC key handling)
- [x] T028 [US4] Integrate ApprovalPanel with VaultWatcher in src/app.py (detect Pending_Approval folder changes, update task list within 100ms)
- [x] T029 [US4] Implement approve action in ApprovalPanel (call FileManager to move Pending_Approval → Approved, close modal, handle errors)
- [x] T030 [US4] Implement reject action in ApprovalPanel (call FileManager to move Pending_Approval → Rejected, close modal, handle errors)
- [x] T031 [US4] Add error notification system in src/app.py (display file operation failures, "Task already processed" race condition handling)
- [x] T032 [US4] Implement task detail modal trigger (click task row → open TaskModal with full content)

**Checkpoint**: At this point, User Stories 1 AND 4 should both work independently - live metrics + approval workflow functional

---

## Phase 5: User Story 2 - Channel Activity Breakdown (Priority: P2)

**Goal**: Display message volume and types broken down by communication channel (Website, Gmail, WhatsApp)

**Independent Test**: Populate vault with messages from different channels, verify dashboard displays accurate counts per channel and type

### Implementation for User Story 2

- [x] T033 [US2] Extend MetricsCalculator in src/services/metrics_calculator.py (calculate per-channel message counts, per-type breakdowns within channels)
- [x] T034 [US2] Create ChannelPanel widget in src/widgets/channel_panel.py (three sections for Website/Gmail/WhatsApp, type breakdown display per channel)
- [x] T035 [US2] Integrate ChannelPanel with dashboard metrics in src/app.py (reactive updates when channel messages change, <100ms refresh)
- [x] T036 [US2] Implement channel ordering and visual separation in ChannelPanel (consistent Website → Gmail → WhatsApp order, clear section borders)

**Checkpoint**: At this point, User Stories 1, 4, AND 2 should all work independently

---

## Phase 6: User Story 5 - Recent Activity Stream (Priority: P2)

**Goal**: Display scrolling feed of last 20 AI actions with timestamp, channel, type, and status

**Independent Test**: Trigger various vault changes (creates, moves, updates), verify they appear in activity stream with correct metadata

### Implementation for User Story 5

- [x] T037 [US5] Extend VaultWatcher in src/services/vault_watcher.py (create ActivityEvent objects for all file operations, capture timestamp/channel/type/status)
- [x] T038 [US5] Create ActivityStream widget in src/widgets/activity_stream.py (chronological list display, 20-item bounded buffer, fade-in animation for new items)
- [x] T039 [US5] Implement activity event routing in src/app.py (VaultWatcher events → ActivityStream updates, maintain chronological order)
- [x] T040 [US5] Add auto-scroll and item removal in ActivityStream (newest at top, remove 21st item, scroll behavior)
- [x] T041 [US5] Implement file move operation display in ActivityStream (clear indication format: "Order #1234 moved Website → Resolved")
- [x] T042 [US5] Add empty state handling in ActivityStream (display "No recent activity" when no events exist)

**Checkpoint**: At this point, User Stories 1, 4, 2, AND 5 should all work independently

---

## Phase 7: User Story 3 - Message Classification Analytics (Priority: P3)

**Goal**: Display success rates and resolution patterns for different message types (Refund/Support/Inquiry)

**Independent Test**: Create messages with varying classification metadata (auto-resolved vs escalated), verify dashboard calculates accurate success rates

### Implementation for User Story 3

- [x] T043 [US3] Extend MetricsCalculator in src/services/metrics_calculator.py (calculate per-type counts, auto-resolve vs escalation rates, handle division by zero)
- [x] T044 [US3] Create ClassificationPanel widget in src/widgets/classification_panel.py (display Refund/Support/Inquiry counts, success rate percentages)
- [x] T045 [US3] Integrate ClassificationPanel with dashboard metrics in src/app.py (reactive updates when message status changes, <100ms recalculation)
- [x] T046 [US3] Implement zero-message handling in ClassificationPanel (display "0 messages" for types with no data)

**Checkpoint**: At this point, User Stories 1, 4, 2, 5, AND 3 should all work independently

---

## Phase 8: User Story 6 - Keyboard Navigation and Shortcuts (Priority: P3)

**Goal**: Efficient keyboard shortcuts for dashboard operation without mouse clicks

**Independent Test**: Use only keyboard input to navigate all dashboard functions, verify all critical actions are accessible

### Implementation for User Story 6

- [x] T047 [US6] Implement 'q' keyboard shortcut in src/app.py (graceful application exit on key press)
- [x] T048 [US6] Implement ESC keyboard shortcut for modal close in src/widgets/task_modal.py (close without action)
- [x] T049 [US6] Implement Tab navigation in src/app.py (focus moves to next interactive element in logical order)
- [x] T050 [US6] Implement Enter key for task modal open in src/widgets/approval_panel.py (focused task opens detail modal)

**Checkpoint**: All user stories should now be independently functional with full keyboard accessibility

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T051 [P] Add comprehensive error handling in src/services/vault_parser.py (skip malformed files, log warnings, continue processing)
- [x] T052 [P] Implement graceful degradation in src/services/metrics_calculator.py (handle missing Dashboard.md, fall back to file counts only)
- [x] T053 [P] Add path validation security in src/services/file_manager.py (ensure all file operations stay within vault directory)
- [x] T054 [P] Implement content sanitization in src/widgets/task_modal.py (Textual's built-in ANSI escaping for markdown content)
- [x] T055 [P] Add performance optimization in src/services/vault_watcher.py (event batching for rapid changes, incremental processing)
- [x] T056 [P] Create initial vault scan optimization in src/services/metrics_calculator.py (parallel file processing, metadata caching for <2s scan time)
- [x] T057 [P] Add memory footprint monitoring in src/app.py (bounded buffers, activity stream limit enforcement for <100MB usage)
- [x] T058 [P] Implement responsive layout in src/app.py (terminal resize handling, panel reflow, maintain readability)
- [x] T059 Finalize Textual CSS theme in src/app.py (black background, cyan/green color palette exclusively, box-drawing characters for borders)
- [x] T060 [P] Add integration tests in tests/integration/test_vault_watcher.py (file change → UI update flow validation)
- [x] T061 [P] Add integration tests in tests/integration/test_approval_workflow.py (approve/reject → file move → UI update validation)
- [x] T062 [P] Add integration tests in tests/integration/test_ui_updates.py (<100ms latency validation for file changes)
- [x] T063 [P] Add unit tests in tests/unit/test_vault_parser.py (frontmatter parsing, malformed file handling)
- [x] T064 [P] Add unit tests in tests/unit/test_metrics_calculator.py (aggregate calculations, edge cases)
- [x] T065 [P] Add unit tests in tests/unit/test_file_manager.py (path validation, error handling)
- [x] T066 [P] Update README.md with usage instructions, configuration guide, troubleshooting section
- [x] T067 Run full system validation (launch dashboard, test all 6 user stories independently, verify performance requirements)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P2 → P3 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - May reference widgets from other stories but independently testable

### Within Each User Story

- Core services before widgets
- Widgets before app integration
- Integration before validation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational model creation tasks (T007-T010) can run in parallel
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models and independent widgets within a story marked [P] can run in parallel
- All Polish phase tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# After Foundational phase, launch multiple US1 tasks together:
Task T017: "Implement MetricsCalculator service in src/services/metrics_calculator.py"
Task T018: "Create StatusBar widget in src/widgets/status_bar.py"
# Both can run in parallel (different files, no dependencies)

# Then continue with dependent tasks:
Task T019: "Create MetricsPanel widget in src/widgets/metrics_panel.py"
Task T020: "Implement vault file watching in src/services/vault_watcher.py"
# Continue with integration tasks T021-T024
```

---

## Parallel Example: After Foundational Phase

```bash
# Multiple developers can work on different user stories simultaneously:
Developer A: Phase 3 (User Story 1) - Tasks T017-T024
Developer B: Phase 4 (User Story 4) - Tasks T025-T032
Developer C: Phase 5 (User Story 2) - Tasks T033-T036
# All can proceed in parallel since they depend only on Foundational phase
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 4 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (live metrics monitoring)
4. Complete Phase 4: User Story 4 (approval workflow)
5. **STOP and VALIDATE**: Test User Stories 1 and 4 independently
6. Deploy/demo - fully functional monitoring + approval system

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (P1) → Test independently → Deploy/Demo (metrics monitoring)
3. Add User Story 4 (P1) → Test independently → Deploy/Demo (approval workflow) **← MVP milestone**
4. Add User Story 2 (P2) → Test independently → Deploy/Demo (channel breakdown)
5. Add User Story 5 (P2) → Test independently → Deploy/Demo (activity stream)
6. Add User Story 3 (P3) → Test independently → Deploy/Demo (classification analytics)
7. Add User Story 6 (P3) → Test independently → Deploy/Demo (keyboard shortcuts)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T017-T024)
   - Developer B: User Story 4 (T025-T032)
   - Developer C: User Story 2 (T033-T036)
3. Stories complete and integrate independently
4. Continue with remaining stories in priority order or parallel

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Performance requirements: <100ms file-to-UI latency, <2s initial scan, <100MB memory
- Security: Path validation, content sanitization, read-only vault access (except file moves)
- All file operations must include error handling and logging
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
