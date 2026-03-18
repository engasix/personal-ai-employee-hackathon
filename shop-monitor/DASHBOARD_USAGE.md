# Shop Monitor Dashboard - Usage Guide

## Overview
The Shop Monitor dashboard now features a modern, date-filterable interface with drill-down capabilities and CEO briefing support.

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│                    FTE SHOP Logo                        │
├─────────────────────────────────────────────────────────┤
│  📅 2026-01-19 (Monday)  [◀ Prev] [Next ▶]            │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┬──────────┬───────────────┐              │
│  │ Orders   │ Revenue  │ Inquiries     │              │
│  │   5      │ $234.50  │      3        │              │
│  ├──────────┼──────────┼───────────────┤              │
│  │ Refunds  │ Support  │ Pending       │              │
│  │   2      │    1     │      3        │              │
│  └──────────┴──────────┴───────────────┘              │
├─────────────────────────────────────────────────────────┤
│         📊 Weekly CEO Briefing (if available)           │
└─────────────────────────────────────────────────────────┘
```

## Features

### 1. Date Selection
- **Current Date**: Displayed at the top with day name
- **Navigation**: Use ◀ Prev and Next ▶ buttons to change date
- **Behavior**: All metrics automatically update when date changes

### 2. Clickable Metrics (6 Tiles)

#### Orders Today
- **Shows**: Total number of orders with amounts > 0
- **Click**: Opens list of all orders for selected date
- **List Shows**: Order #, Customer Name, Amount

#### Revenue
- **Shows**: Sum of all `amount` fields from orders
- **Click**: Opens same list as Orders
- **Format**: $X,XXX.XX

#### Inquiries
- **Shows**: Count of inquiry-type messages
- **Click**: Opens list of all inquiry messages
- **List Shows**: Order #, Customer Name, Amount (usually $0)

#### Refund Requests
- **Shows**: Count of refund-type messages
- **Click**: Opens list of all refund requests
- **List Shows**: Order #, Customer Name, Refund Amount

#### Support Requests
- **Shows**: Count of support-type messages
- **Click**: Opens list of all support requests
- **List Shows**: Order #, Customer Name, Amount

#### Pending Approvals
- **Shows**: Count of items in Pending_Approval folder
- **Click**: Opens list of pending items
- **Special**: Shows Approve/Reject buttons in detail view

### 3. Drill-Down Navigation

**Level 1: Metric Tile** → Click any tile
↓
**Level 2: List Modal** → Shows all items for that metric
- Format: `[Order #] [Customer Name] [$Amount]`
- Click any item to see details
↓
**Level 3: Detail Modal** → Shows full markdown content
- Displays complete order/message information
- For pending approvals: Shows **[✓ Approve]** and **[✗ Reject]** buttons
- Click [Close] to return to list

### 4. Approval Workflow

1. Click **Pending Approvals** tile
2. Select an item from the list
3. Review full details in modal
4. Click **[✓ Approve]** or **[✗ Reject]**
5. File automatically moves to Approved/Rejected folder
6. Dashboard updates in real-time

### 5. CEO Briefing

- **File Format**: `ceo-briefing-YYYY-MM-DD.md` (e.g., `ceo-briefing-2026-01-19.md`)
- **Location**: Vault root directory
- **Display**: Shows green "✓ Weekly briefing available" if file exists
- **Click**: Opens full markdown report in detail modal
- **Updates**: Automatically changes when date is selected

## Running the Dashboard

```bash
# Start the dashboard
python -m src.monitor

# Or with demo vault
VAULT_PATH=demo_vault python -m src.monitor
```

## Keyboard Shortcuts

- **q**: Quit application
- **Tab**: Navigate between elements
- **Enter**: Click focused button/tile
- **Esc**: Close modal windows

## Data Requirements

### Message Files (Inbox, Done, Needs_Action)
Each message file should have frontmatter with:
```yaml
---
type: Inquiry|Refund|Support
channel: Website|Gmail|WhatsApp
status: Pending|Resolved|Escalated
timestamp: 2026-01-19T10:30:00
---
**Customer**: John Doe
**Amount**: $149.99
**Order**: #ORD-12345

Message content here...
```

### Pending Approval Files
```yaml
---
id: TASK-001
description: Brief task description
priority: high|normal|low
timestamp: 2026-01-19T10:30:00
---
**Customer**: Jane Smith
**Amount**: $199.99

Full task details...
```

### CEO Briefing Files
- **Name**: `ceo-briefing-YYYY-MM-DD.md`
- **Location**: Vault root
- **Format**: Standard markdown

## Date Filtering Logic

The dashboard filters messages by comparing:
- File's `timestamp` field → Extracted date (YYYY-MM-DD)
- Selected date in dashboard

**Example**:
- Selected Date: 2026-01-19
- File timestamp: `2026-01-19T14:30:00` → ✓ Included
- File timestamp: `2026-01-18T22:00:00` → ✗ Excluded

**Note**: Pending approvals are always shown regardless of date.

## Demo Data

The demo vault includes sample data for testing:
- **2026-01-17**: 2 messages (1 inquiry, 1 support)
- **2026-01-19**: 1 inquiry
- **Pending**: 3 approval tasks

Navigate between dates using the date picker to see the data change.

## Color Scheme

- **Primary**: Parrot Green (#39ff14)
- **Accent**: Bright Green (#00ff00)
- **Background**: Black (#000000)
- **Hover**: Dark Green Tint (#001a00)

## Troubleshooting

### No data showing
- Check that vault path is correct in `.env`
- Verify message files have `timestamp` field in frontmatter
- Ensure timestamp matches selected date

### Metrics not updating
- Check vault watcher is running (logged at startup)
- Verify file permissions allow reading
- Check logs for any parsing errors

### CEO briefing not showing
- Verify file exists: `vault/ceo-briefing-YYYY-MM-DD.md`
- Check filename matches exact format with selected date
- Ensure file is in vault root (not in subfolder)

## Technical Details

### Customer Info Extraction
The dashboard extracts customer details from markdown content using regex:
- Patterns: `**Customer**: Name` or `Customer: Name`
- Same for `Amount`, `Order`, etc.
- Falls back to "Unknown Customer" if not found

### Revenue Calculation
- Sums all `amount` values from orders
- Includes refund amounts
- Filters by selected date

### Real-time Updates
- Vault watcher monitors filesystem changes
- Checks every 1 second for new events
- Automatically refreshes metrics when files change

## Future Enhancements

Potential features for future development:
- Date range selection (week/month view)
- Export metrics to CSV
- Email notifications for high-priority approvals
- Charts and graphs for trends
- Search/filter within lists
- Bulk approve/reject actions
