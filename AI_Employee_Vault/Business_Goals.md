# Business Goals

## Business Overview

**Name:** FTE Shop **Type:** Digital Product Store — AI Agents & Automation Solutions **Tagline:** _"Hire your next AI employee"_ **Status:** Live (Mock Business for AI Employee Hackathon)

## What We Sell

|Product|Description|Price Range|
|---|---|---|
|Gmail Assistant Agent|Email triage, auto-responses, scheduling|$99 - $299|
|Social Media Manager Agent|Auto-posting, engagement, analytics|$149 - $399|
|Customer Support Agent|FAQ handling, ticket routing, escalation|$199 - $499|
|Data Entry Agent|Form filling, spreadsheet updates, data cleanup|$79 - $199|
|Research Agent|Web research, summarization, report generation|$129 - $349|
|Custom Agent|Built to client specifications|$500+|

## Mission

Demonstrate that an AI Employee can autonomously run an online business selling AI Employees — from lead capture to order fulfillment to customer support.

## Weekly Targets

- [ ] Process all incoming orders within 1 hour
- [ ] Respond to customer inquiries within 30 minutes
- [ ] Post 3x on LinkedIn (case studies, agent tips, industry insights)
- [ ] Post 3x on X (product highlights, customer wins, engagement)
- [ ] Generate weekly CEO briefing every Sunday

## Automation Goals

### Lead Capture & Sales

- Detect inquiries via WhatsApp/Email ("I need an agent for...")
- Auto-respond with product recommendations
- Send pricing and product details
- Flag high-value leads (Custom Agent requests) for human follow-up

### Order Processing

**Order File Structure:** Website generates markdown with:
- Order ID, Date, Status
- Customer Name, Email, Phone
- Product, Price, Payment Status
- Special Requests

**Processing Steps:**

- Confirm order receipt immediately
- Deliver agent documentation/setup instructions via email
- Schedule onboarding call if needed
- Update sales tracking

### Customer Communication

**Message Classification:** All incoming messages (WhatsApp/Gmail) are classified into 3 types:

1. **Refund Request** — Requires human approval, create approval file
2. **Support Request** — Troubleshoot issues, provide technical help
3. **General Inquiry** — Product info, pricing, quotations (auto-respond)

**Response Guidelines:**

- Auto-respond to common questions (pricing, features, setup)
- Provide setup support and troubleshooting
- Escalate refunds and complex issues to human review
- Maintain professional, helpful tone (per Company Handbook)

### Social Media

- Share customer success stories
- Post tips on using AI agents effectively
- Announce new agent products
- Engage with AI/automation community

### Reporting

- Track daily/weekly revenue
- Monitor which agents sell best
- Log customer feedback and feature requests
- Identify bottlenecks in sales pipeline
- Generate CEO briefing with insights

## Key Metrics

|Metric|Target|
|---|---|
|Lead response time|< 30 minutes|
|Order confirmation|< 1 hour|
|Weekly social posts|6 (3 LinkedIn + 3 X)|
|CEO briefing|Every Sunday|
|Customer satisfaction|> 90%|
|Pending approvals resolved|< 24 hours|

## Sales Pipeline

```markdown
INPUT CHANNELS
├─ Website Store → Order Files → Filesystem Watcher
├─ WhatsApp Messages → WhatsApp Watcher
└─ Gmail Messages → Gmail Watcher
        ↓
CLASSIFICATION (for WhatsApp/Gmail)
├─ Refund Request → Approval Required
├─ Support Request → Technical Help
└─ General Inquiry → Auto-Response
        ↓
PROCESSING
Order → Confirm → Deliver → Log
Inquiry → Research → Respond → Log
Support → Troubleshoot → Resolve → Log
Refund → Review → Approve/Deny → Log
        ↓
REPORTING
All transactions → CEO Briefing (Weekly)
```

## Rules of Engagement

See [[Company_Handbook]] for detailed operational guidelines.
