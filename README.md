# Personal AI Employee Hackathon

A local-first autonomous AI agent that manages personal and business affairs 24/7 using Claude Code, Obsidian, and MCP servers.

## Overview

Building a "Digital FTE" (Full-Time Equivalent) — an AI employee that proactively runs **FTE Shop**, an online store selling AI agents and automation solutions.

---

## Demo

[![Personal AI Employee Hackathon](https://img.youtube.com/vi/te5fkBc7bZ4/maxresdefault.jpg)](https://www.youtube.com/watch?v=te5fkBc7bZ4)

---

## Tech Stack

|Component|Purpose|
|---|---|
|**Claude Code**|Reasoning engine — executes tasks and makes decisions|
|**Obsidian**|Workspace — local markdown vault for tasks, plans, and logs|
|**Python Watchers**|Sensors — monitor Gmail, WhatsApp, file system for triggers|
|**MCP Servers**|Actions — send emails, post to social media, external integrations|

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                         │
│        Gmail Watcher | WhatsApp Watcher | File Watcher      │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     OBSIDIAN VAULT                          │
│   /Needs_Action | /Plans | /Pending_Approval | /Done        │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                          │
│           Claude Code + Ralph Wiggum Loop                   │
│           Read → Think → Plan → Execute                     │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     ACTION LAYER                            │
│         MCP Servers + Human-in-the-Loop Approval            │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                        │
│        Orchestrator.py | Watchdog.py | Scheduling           │
└─────────────────────────────────────────────────────────────┘
```

## Roadmap

### Phase 1: Setup & Infrastructure ✅

- [x] Repository setup
- [x] Mock e-commerce business concept defined (FTE Shop — selling AI agents)
- [x] Business accounts setup (Gmail, LinkedIn, X, WhatsApp)
- [x] Obsidian vault setup (folders + Dashboard.md, Company_Handbook.md, Business_Goals.md)

### Phase 2: Perception Layer (Watchers)

- [x] Base watcher pattern implementation
- [x] Gmail watcher + SKILL.md
- [ ] WhatsApp watcher + SKILL.md
- [x] File system watcher + SKILL.md

### Phase 3: Reasoning Layer (Claude Code)

- [ ] Claude Code reading from vault
- [ ] Claude Code writing to vault
- [ ] Reasoning loop that creates Plan.md files
- [ ] Ralph Wiggum loop for autonomous task completion
- [x] Vault operator SKILL.md

### Phase 4: Action Layer (MCP + HITL)

- [ ] Email MCP server (sending emails)
- [ ] Browser MCP server (web automation)
- [ ] Approval request file generation
- [ ] Approval workflow (move to /Approved or /Rejected)
- [ ] Sensitive action thresholds (e.g., orders > $500)

### Phase 5: Social Media Automation

- [ ] LinkedIn posting + SKILL.md
- [ ] X (Twitter) posting + SKILL.md
- [ ] Social media summary generation

### Phase 6: Orchestration Layer

- [x] Orchestrator.py (master process)
- [ ] Watchdog.py (health monitor)
- [ ] PM2 setup for process management
- [ ] Cron/Task Scheduler for scheduled operations
- [ ] Auto-restart on failure

### Phase 7: CEO Briefing (Business Audit)

- [ ] Weekly business audit automation
- [ ] Revenue summary generation
- [ ] Bottleneck identification
- [ ] Proactive suggestions
- [ ] CEO briefing SKILL.md

### Phase 8: Security & Error Handling

- [ ] Credential management (.env, secrets)
- [ ] Audit logging (/Logs)
- [ ] Retry logic for transient errors
- [ ] Graceful degradation
- [ ] Dry-run mode for testing

### Phase 9: Documentation & Submission

- [ ] Architecture documentation
- [ ] Setup instructions
- [ ] Demo video (5-10 min)
- [ ] Lessons learned

## FTE Shop — Mock Business

**What we sell:** AI Agents & Automation Solutions

|Product|Price Range|
|---|---|
|Gmail Assistant Agent|$99 - $299|
|Social Media Manager Agent|$149 - $399|
|Customer Support Agent|$199 - $499|
|Data Entry Agent|$79 - $199|
|Research Agent|$129 - $349|
|Custom Agent|$500+|

## Input Channels & Message Classification

### Input Channels (3)

1. **Website Store** → Orders saved as markdown files → Filesystem watcher
2. **WhatsApp** → Customer messages → WhatsApp watcher
3. **Gmail** → Customer emails → Gmail watcher

### Message Classification (3 Types)

All messages from WhatsApp and Gmail are classified into:

1. **Refund Request** — Customer wants money back (requires approval)
2. **Support Request** — Technical help, issues with delivered agents
3. **General Inquiry** — Product info, quotations, pre-sales questions

### Order File Format

When website creates an order, it generates a markdown file with:

```markdown
# Order #[ORDER_ID]

**Status:** Pending
**Date:** [ISO_DATE]

## Customer Information
- **Name:** [CUSTOMER_NAME]
- **Email:** [CUSTOMER_EMAIL]
- **Phone:** [PHONE_NUMBER]

## Order Details
- **Product:** [PRODUCT_NAME]
- **Price:** $[AMOUNT]
- **Payment Status:** [Paid/Pending]

## Special Requests
[ANY_CUSTOMER_NOTES]

## Processing Notes
[AGENT_UPDATES_HERE]
```

**Order Flow:**

1. Customer places order on website → Order markdown file created
2. Filesystem watcher detects → Creates task in /Needs_Action
3. Claude reads order + Company_Handbook.md → Creates Plan.md
4. Order fulfilled (delivery email sent via MCP)
5. Transaction logged → Moved to /Done → CEO Briefing updated

**Support/Inquiry Flow:**

1. Customer message via WhatsApp/Email → Watcher detects
2. Message classified (Refund/Support/Inquiry)
3. Claude reads + creates response plan
4. Auto-responds (or flags for approval if refund)
5. Transaction logged → CEO Briefing updated

## Progress Log

### Day 0 — Setup (Jan 12, 2026)

- Created repository
- Defined FTE Shop business concept (AI agent store)
- Set up business accounts (Gmail, LinkedIn, X, WhatsApp)
- Installed Obsidian
- Created vault structure (folders + core files)

### Day 1 — Perception & Reasoning (Jan 13, 2026)

- _In progress_

### Day 2+ — Action & Orchestration

- _Coming soon_

## Resources

- [Hackathon Document](https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI/edit?tab=t.0)
- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1) — 10:00 PM every Wednesday
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Ralph Wiggum Loop Reference](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)