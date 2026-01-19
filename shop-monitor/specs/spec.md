# Feature Specification: Shop Monitor - Real-Time Terminal Dashboard

**Feature Branch**: `001-realtime-dashboard`
**Created**: 2026-01-17
**Status**: Draft
**Input**: User description: "Shop Monitor real-time terminal dashboard"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live System Status Monitoring (Priority: P1)

As a shop operator, I need to see real-time metrics and system status at a glance so I can immediately know if the AI employee is functioning correctly and handling customer requests.

**Why this priority**: This is the core value proposition - providing visibility into autonomous AI operations. Without this, users have no way to monitor if their business is running correctly.

**Independent Test**: Can be fully tested by launching the dashboard, creating/modifying files in the vault, and verifying that metrics update within 100ms without any user interaction.

**Acceptance Scenarios**:

1. **Given** the AI Employee Vault contains active orders and messages, **When** I launch the dashboard, **Then** I see current counts for orders, revenue, response times, and pending tasks displayed prominently
2. **Given** the dashboard is running, **When** a new order file is created in the vault, **Then** the order count increments and revenue updates within 100ms without page refresh
3. **Given** the dashboard is running, **When** the vault becomes temporarily unavailable, **Then** the connection status indicator shows "Disconnected" in red and displays the last successful update timestamp
4. **Given** vault files are being modified, **When** I view the dashboard, **Then** the "Last Update" timestamp shows the time of the most recent change detection

---

### User Story 2 - Channel Activity Breakdown (Priority: P2)

As a shop operator, I need to see message volume and types broken down by communication channel (Website, Gmail, WhatsApp) so I can identify which channels are busiest and where attention is needed.

**Why this priority**: Provides actionable insight into customer interaction patterns and helps prioritize support resources across channels.

**Independent Test**: Can be fully tested by populating the vault with messages from different channels with different types, then verifying the dashboard displays accurate counts per channel and type without requiring US1.

**Acceptance Scenarios**:

1. **Given** the vault contains messages from Website, Gmail, and WhatsApp, **When** I view the Channel Activity panel, **Then** I see three distinct sections showing message counts for each channel
2. **Given** each channel has Refund, Support, and Inquiry messages, **When** I view a channel section, **Then** I see the type breakdown (e.g., "Website: 12 Refunds, 8 Support, 5 Inquiries")
3. **Given** a new WhatsApp message file is created with type "Refund", **When** the dashboard updates, **Then** the WhatsApp section increments the Refund count within 100ms
4. **Given** multiple channels are active, **When** I view the panel, **Then** channels are displayed in consistent order (Website, Gmail, WhatsApp) with clear visual separation

---

### User Story 3 - Message Classification Analytics (Priority: P3)

As a shop operator, I need to see success rates and resolution patterns for different message types so I can understand how effectively the AI is handling different categories of customer requests.

**Why this priority**: Provides quality metrics and helps identify areas where the AI may need improvement or human intervention patterns.

**Independent Test**: Can be fully tested by creating messages with varying classification metadata (auto-resolved vs escalated) and verifying the dashboard calculates and displays accurate success rates.

**Acceptance Scenarios**:

1. **Given** the vault contains Refund, Support, and Inquiry messages, **When** I view the Message Classification panel, **Then** I see total counts for each of the three message types
2. **Given** messages have resolution metadata (auto-resolved or escalated), **When** I view classification details, **Then** I see success rates displayed as percentages (e.g., "Support: 85% auto-resolved, 15% escalated")
3. **Given** a message is moved from "Pending" to "Resolved", **When** the dashboard updates, **Then** the auto-resolve rate for that message type recalculates within 100ms
4. **Given** no messages exist for a type, **When** I view the panel, **Then** the type shows "0 messages" rather than displaying an error or blank space

---

### User Story 4 - Pending Task Approval (Priority: P1)

As a shop operator, I need to approve or reject pending tasks directly from the dashboard so I can provide human oversight for critical AI decisions without leaving the terminal interface.

**Why this priority**: This is the key human-in-the-loop feature enabling supervision of autonomous operations. Without this, the tool is read-only and cannot fulfill the approval workflow requirement.

**Independent Test**: Can be fully tested by placing task files in the Pending_Approval folder, clicking Approve/Reject buttons, and verifying files are moved to appropriate folders with the dashboard updating automatically.

**Acceptance Scenarios**:

1. **Given** the Pending_Approval folder contains 3 tasks, **When** I view the Pending Approvals panel, **Then** I see a list of 3 tasks with Approve and Reject buttons for each
2. **Given** a task is displayed in the list, **When** I click the task row, **Then** a modal opens showing the full task content with Approve and Reject action buttons
3. **Given** I have a task modal open, **When** I click "Approve", **Then** the task file moves from Pending_Approval to Approved folder, the modal closes, and the Pending Approvals list updates within 100ms
4. **Given** I have a task modal open, **When** I click "Reject", **Then** the task file moves from Pending_Approval to Rejected folder, the modal closes, and the list updates
5. **Given** I have a task modal open, **When** I press the ESC key, **Then** the modal closes without moving the file
6. **Given** a file move operation fails (permissions, disk full), **When** I attempt to approve/reject, **Then** the dashboard displays an error notification and the task remains in the list

---

### User Story 5 - Recent Activity Stream (Priority: P2)

As a shop operator, I need to see a scrolling feed of recent AI actions so I can quickly scan what has happened and identify any unusual patterns or issues.

**Why this priority**: Provides operational awareness and audit trail visibility. Less critical than approval workflow but important for monitoring and troubleshooting.

**Independent Test**: Can be fully tested by triggering various vault changes (file creates, moves, updates) and verifying they appear in the activity stream with correct metadata and timestamps.

**Acceptance Scenarios**:

1. **Given** the dashboard is running, **When** vault changes occur, **Then** I see a chronological list of the last 20 actions showing timestamp, channel, type, and status
2. **Given** the activity stream has 20 items, **When** a new action occurs, **Then** the newest action appears at the top with a fade-in animation and the oldest (21st) item is removed
3. **Given** multiple actions occur rapidly, **When** I view the stream, **Then** actions appear in correct chronological order without duplicates or missing entries
4. **Given** an action involves a file move, **When** it appears in the stream, **Then** I see clear indication of the operation (e.g., "Order #1234 moved Website → Resolved")
5. **Given** no recent activity exists, **When** I view the stream, **Then** it displays "No recent activity" rather than showing an empty list

---

### User Story 6 - Keyboard Navigation and Shortcuts (Priority: P3)

As a shop operator, I need efficient keyboard shortcuts so I can operate the dashboard without relying on mouse clicks during high-volume periods.

**Why this priority**: Enhances productivity for power users but not essential for core functionality.

**Independent Test**: Can be fully tested by using only keyboard input to navigate all dashboard functions and verifying all critical actions are accessible.

**Acceptance Scenarios**:

1. **Given** the dashboard is running, **When** I press 'q', **Then** the application exits gracefully
2. **Given** a task modal is open, **When** I press ESC, **Then** the modal closes without performing any action
3. **Given** the dashboard has focus, **When** I press Tab, **Then** focus moves to the next interactive element in logical order
4. **Given** a task in the approval list has focus, **When** I press Enter, **Then** the task detail modal opens

---

### Edge Cases

- What happens when the vault path does not exist or becomes unavailable mid-session?
  - Dashboard shows "Disconnected" status, displays last known metrics, and automatically reconnects when path becomes available

- What happens when a markdown file lacks required frontmatter fields (type, channel)?
  - File is skipped with a warning logged, dashboard continues processing other files, error count displayed in status bar

- What happens when file move operations fail due to permissions or locks?
  - Error notification displayed to user, file remains in original location, operation can be retried

- What happens when the vault contains thousands of files?
  - Initial scan completes within 2 seconds (per constitution), subsequent updates remain <100ms using incremental processing

- What happens when multiple rapid file changes occur simultaneously?
  - Events are queued and processed sequentially, UI updates batched to maintain <100ms perceived latency

- What happens when a user attempts to approve/reject the same task twice (race condition)?
  - First operation succeeds, second operation detects missing file and displays "Task already processed" message

- What happens when the terminal window is resized?
  - Dashboard layout adjusts responsively, panels reflow to fit new dimensions, content remains readable

- What happens when Dashboard.md (metrics source) is malformed or missing?
  - Dashboard falls back to file-count based metrics only, displays warning that detailed analytics unavailable

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST monitor the AI Employee Vault directory using file system watching (no polling)
- **FR-002**: System MUST detect file changes (create, modify, delete, move) and trigger UI updates within 100ms
- **FR-003**: System MUST parse markdown files with YAML frontmatter to extract metadata (type, channel, status)
- **FR-004**: System MUST display current metrics including today's order count, revenue, average response time, and pending task queue depth
- **FR-005**: System MUST aggregate metrics from both file counts and Dashboard.md content
- **FR-006**: System MUST display channel breakdown showing message counts for Website, Gmail, and WhatsApp with type subcategories
- **FR-007**: System MUST calculate and display message classification statistics (Refund, Support, Inquiry) with auto-resolve vs escalation rates
- **FR-008**: System MUST list tasks from the Pending_Approval folder with interactive Approve and Reject buttons
- **FR-009**: System MUST display task details in a modal when a task is clicked
- **FR-010**: System MUST move task files between folders (Pending_Approval → Approved or Rejected) when buttons are clicked
- **FR-011**: System MUST display the last 20 actions in chronological order with timestamp, channel, type, and status
- **FR-012**: System MUST show new activity items with a fade-in animation and auto-scroll behavior
- **FR-013**: System MUST display connection status indicator showing "Connected" or "Disconnected" state
- **FR-014**: System MUST display last update timestamp showing when the most recent vault change was detected
- **FR-015**: System MUST support 'q' keyboard shortcut to quit the application
- **FR-016**: System MUST support ESC keyboard shortcut to close modal dialogs
- **FR-017**: System MUST render using terminal aesthetic with black background and cyan/green color palette exclusively
- **FR-018**: System MUST use box-drawing characters for panel borders and visual layout structure
- **FR-019**: System MUST support mouse-clickable buttons and interactive elements
- **FR-020**: System MUST be launchable with a single command (python monitor.py or equivalent)
- **FR-021**: System MUST handle file operation errors gracefully with user-visible error notifications
- **FR-022**: System MUST log all file change events, UI updates, and user actions with timestamps
- **FR-023**: System MUST validate all file paths to ensure they are within the configured vault directory
- **FR-024**: System MUST sanitize markdown content before terminal display to prevent injection attacks
- **FR-025**: System MUST skip malformed files (missing frontmatter, invalid YAML) and continue processing others
- **FR-026**: System MUST complete initial vault scan within 2 seconds for vaults containing up to 1000 files
- **FR-027**: System MUST maintain memory footprint below 100MB during normal operation

### Key Entities

- **VaultMessage**: Represents a customer message markdown file with attributes: type (Refund/Support/Inquiry), channel (Website/Gmail/WhatsApp), status (Pending/Resolved/Escalated), timestamp, file path, content

- **PendingTask**: Represents a task awaiting approval with attributes: task ID, description, priority, creation timestamp, file path, full content

- **ActivityEvent**: Represents a logged action with attributes: timestamp, event type (create/move/update), channel, message type, status transition, file path

- **DashboardMetrics**: Aggregate statistics with attributes: total orders, total revenue, average response time, pending count, per-channel message counts, per-type classification counts, auto-resolve rates

- **VaultConnectionState**: System health status with attributes: connection status (connected/disconnected), last update timestamp, error message (if disconnected), watched path

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can launch the dashboard with a single terminal command and see live metrics within 2 seconds
- **SC-002**: System detects vault file changes and updates the UI in under 100 milliseconds (p95 latency)
- **SC-003**: Operators can approve or reject pending tasks using mouse clicks without switching to another application
- **SC-004**: Dashboard processes vaults containing 1000+ markdown files without performance degradation
- **SC-005**: System continues operating correctly when vault becomes temporarily unavailable, automatically reconnecting when restored
- **SC-006**: Operators can identify the busiest communication channel and message type distribution at a glance (under 5 seconds from dashboard view)
- **SC-007**: All critical functions (view metrics, approve tasks, monitor activity) are accessible via keyboard shortcuts without requiring mouse interaction
- **SC-008**: System maintains memory usage below 100MB during continuous 8-hour operation
- **SC-009**: Dashboard displays accurate metrics that match manual file counts in the vault (100% accuracy)
- **SC-010**: Operators receive immediate visual feedback (error notifications) when file operations fail, with clear guidance on resolution

## Assumptions

- The AI Employee Vault follows the standard structure: /Inbox, /Needs_Action, /Plans, /Done, /Logs, /Pending_Approval, /Approved, /Rejected, /Accounting, /Invoices, /Briefings, with root files Dashboard.md, Company_Handbook.md, Business_Goals.md
- Markdown files use YAML frontmatter with standardized field names (type, channel, status, timestamp, priority, etc.)
- Messages are stored as individual markdown files with channel and type metadata in frontmatter (not in hierarchical channel/type folders)
- Dashboard.md exists in a known location and follows a parseable format for extracting aggregated metrics
- The Shop Monitor will run on the same machine as the vault (local file system access)
- Terminal supports standard ANSI colors and UTF-8 box-drawing characters
- Python 3.10+ runtime environment is available
- Operators have read permissions on vault files and write permissions for moving files between approval folders
- Today's metrics are defined as files created/modified since midnight local time
- Revenue calculation logic exists in Dashboard.md or can be derived from order file metadata
- Response time metrics are available in file metadata or Dashboard.md

## Out of Scope

- Historical trend charts or time-series visualizations
- User authentication or multi-user access control
- Configuration UI for changing vault paths or settings
- Theme customization or dark mode toggle
- Inline editing of message content or task details
- Exporting metrics to external formats (CSV, JSON, etc.)
- Email or push notifications for critical events
- Integration with external APIs or databases
- Mobile or web-based interface
- Multi-vault monitoring (only one vault per dashboard instance)

## Clarifications

### Session 2026-01-17

- Q: What is the exact folder hierarchy within the AI Employee Vault that the dashboard needs to monitor? → A: Per AI Employee Hackathon architecture document, vault structure includes: /Inbox, /Needs_Action (watcher drops), /Plans (Claude-generated), /Done (completed), /Logs (audit trail), /Pending_Approval, /Approved, /Rejected, /Accounting (transactions), /Invoices, /Briefings (CEO reports), plus root files Dashboard.md, Company_Handbook.md, Business_Goals.md. Messages are individual markdown files with channel/type metadata in YAML frontmatter, not hierarchical channel folders.
