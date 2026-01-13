# Personal AI Employee Hackathon

A local-first autonomous AI agent that manages personal and business affairs 24/7 using Claude Code, Obsidian, and MCP servers.

## Overview

Building a "Digital FTE" (Full-Time Equivalent) — an AI employee that proactively runs **FTE Shop**, an online store selling AI agents and automation solutions.

## Tech Stack

|Component|Purpose|
|---|---|
|**Claude Code**|Reasoning engine — executes tasks and makes decisions|
|**Obsidian**|Workspace — local markdown vault for tasks, plans, and logs|
|**Python Watchers**|Sensors — monitor Gmail, WhatsApp, file system for triggers|
|**MCP Servers**|Actions — send emails, post to social media, external integrations|

## Architecture

```
External Sources (Gmail, WhatsApp, Website Orders)
        ↓
   Watcher Scripts (Python)
        ↓
   Obsidian Vault (/Needs_Action, /Plans, /Done)
        ↓
   Claude Code (Read → Think → Plan → Execute)
        ↓
   Human Approval (/Pending_Approval → /Approved)
        ↓
   MCP Servers (External Actions)
```

## Roadmap

### Phase 1: Setup & Infrastructure

- [x] Repository setup
- [x] Mock e-commerce business concept defined (FTE Shop — selling AI agents)
- [x] Business accounts setup (Gmail, LinkedIn, X, WhatsApp)
- [x] Obsidian vault setup (folders + Dashboard.md, Company_Handbook.md, Business_Goals.md)

### Phase 2: Claude Code Integration

- [ ] Claude Code reading from vault
- [ ] Claude Code writing to vault
- [ ] Reasoning loop that creates Plan.md files

### Phase 3: Watchers (Perception Layer)

- [ ] Base watcher pattern implementation
- [ ] Gmail watcher
- [ ] WhatsApp watcher
- [ ] File system watcher

### Phase 4: Human-in-the-Loop

- [ ] Approval request file generation
- [ ] Approval workflow (move to /Approved or /Rejected)
- [ ] Sensitive action thresholds (e.g., payments > $500)

### Phase 5: MCP Servers (Action Layer)

- [ ] Email MCP server (sending emails)
- [ ] Browser MCP server (web automation)

### Phase 6: Social Media Automation

- [ ] LinkedIn posting automation
- [ ] X (Twitter) posting automation
- [ ] Social media summary generation

### Phase 7: Scheduling & Process Management

- [ ] Cron/Task Scheduler setup
- [ ] PM2 for watcher process management
- [ ] Auto-restart on failure
- [ ] Startup persistence

### Phase 8: CEO Briefing (Business Audit)

- [ ] Weekly business audit automation
- [ ] Revenue summary generation
- [ ] Bottleneck identification
- [ ] Proactive suggestions

### Phase 9: Agent Skills

- [ ] Gmail watcher skill (SKILL.md)
- [ ] WhatsApp watcher skill (SKILL.md)
- [ ] LinkedIn poster skill (SKILL.md)
- [ ] X poster skill (SKILL.md)
- [ ] CEO briefing skill (SKILL.md)
- [ ] Approval workflow skill (SKILL.md)

### Phase 10: Documentation

- [ ] Architecture documentation
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

**Sales Pipeline:**

1. Customer inquiry via WhatsApp/Email/Website
2. AI Employee auto-responds with product info
3. Order placed → Payment confirmed
4. Delivery via email (setup docs)
5. Follow-up for feedback

## Progress Log

### Day 0 — Setup (Jan 12, 2026)

- Created repository
- Defined FTE Shop business concept (AI agent store)
- Set up business accounts (Gmail, LinkedIn, X, WhatsApp)
- Installed Obsidian
- Created vault structure (folders + core files)

### Day 1 — Foundation (Jan 13, 2026)

- _Coming soon_

### Day 2 — Automation (Jan 14, 2026)

- _Coming soon_

## Resources

- [Hackathon Document](https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI/edit?tab=t.0)
- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1) — 10:00 PM every Wednesday
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)