---
id: 002
title: Shop Monitor Specification Creation
stage: spec
date: 2026-01-17
surface: agent
model: claude-sonnet-4-5
feature: realtime-dashboard
branch: 001-realtime-dashboard
user: masif
command: /sp.specify
labels: ["specification", "shop-monitor", "real-time-dashboard", "tui", "vault-monitoring"]
links:
  spec: specs/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/spec.md
  - specs/checklists/requirements.md
tests:
  - N/A
---

## Prompt

Create specification for Shop Monitor - real-time terminal dashboard for monitoring FTE Shop AI Employee.

  Problem: AI employee operates autonomously via Obsidian vault markdown files. No visibility into activity, pending tasks, or metrics. Need real-time monitoring with human approval capability.

  Solution: Interactive terminal UI (Textual) showing live vault metrics, channel activity, message classifications, and pending approvals with mouse-clickable actions.

  User stories:
  1. See live metrics: orders count, revenue, response times, pending tasks - updated in real-time
  2. Monitor channel activity: Website orders, Gmail messages, WhatsApp messages with type breakdowns
  3. View message classification: Refund/Support/Inquiry counts with auto-resolve vs escalated rates
  4. Approve/reject pending tasks: click buttons to move files between approval folders
  5. See recent activity: scrolling stream of last 20 actions with timestamp/channel/type/status
  6. Know system is live: connection status indicator, last update timestamp

  Functional requirements:
  - Real-time vault monitoring: watchdog watches ../AI_Employee_Vault/ folders
  - Metrics panel: today's orders, revenue, avg response time, queue counts (from file counts + Dashboard.md)
  - Channel activity panel: Website/Gmail/WhatsApp with message type breakdowns
  - Message classification panel: Orders/Inquiry/Support/Refund with success rates
  - Pending approvals panel: list tasks from /Pending_Approval with approve/reject buttons
  - Recent activity stream: last 20 actions, auto-scroll, fade-in animation for new items
  - Task detail view: modal showing full task content with approve/reject actions
  - Live status: last update timestamp

  Technical architecture:
  Single Python application using Textual.
  Components: VaultWatcher (watchdog monitoring), VaultParser (frontmatter parsing), MetricsCalculator (aggregate stats), TextualApp (UI with reactive widgets).
  Data flow: watchdog event → parse files → calculate metrics → post_message → widgets react → UI updates (<100ms total).
  Approve/reject: button click → move file between folders → watchdog detects → UI updates.

  UI layout: Single screen with Static containers for panels, DataTable for task lists, Button widgets for actions, ModalScreen for task details, Label for metrics. Black background, cyan/green styling, box-drawing borders via Textual CSS.

  Success criteria: zero polling, <100ms latency, terminal aesthetic, mouse-clickable, single command (python monitor.py), keyboard shortcuts (q=quit, ESC=close modal).

  Out of scope: historical charts, authentication, config UI, theme toggle, inline editing.

## Response snapshot

Created specification at `specs/spec.md` for feature branch `001-realtime-dashboard`.

Specification includes:
- 6 prioritized user stories (2 P1, 2 P2, 2 P3) with independent test criteria
- 27 functional requirements covering real-time monitoring, UI interactions, and performance
- 5 key entities (VaultMessage, PendingTask, ActivityEvent, DashboardMetrics, VaultConnectionState)
- 10 measurable success criteria (all technology-agnostic)
- 8 edge cases with handling strategies
- Assumptions section documenting vault structure and runtime dependencies
- Out of Scope section clearly bounding the feature

Quality validation checklist created at `specs/checklists/requirements.md`:
- All items PASSED
- No [NEEDS CLARIFICATION] markers
- No implementation details leaked into specification
- All requirements testable and unambiguous
- Success criteria focus on user outcomes, not implementation metrics

Status: Ready for `/sp.plan` - Implementation planning phase

## Outcome

- ✅ Impact: Complete specification enabling implementation planning for Shop Monitor dashboard
- 🧪 Tests: Acceptance scenarios defined for all 6 user stories (27 total scenarios)
- 📁 Files: Created specs/spec.md, specs/checklists/requirements.md
- 🔁 Next prompts: /sp.plan for implementation planning, /sp.clarify if any requirements need refinement
- 🧠 Reflection: Spec successfully captures all user requirements with clear priorities, measurable outcomes, and bounded scope. Technical details appropriately omitted to maintain technology-agnostic focus.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist validation PASSED (12/12 items)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
