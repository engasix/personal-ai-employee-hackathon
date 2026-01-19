# Shop Monitor MVP - Demo Guide

## 🎉 Demo Vault Ready

A fully functional demo vault has been created with realistic test data to showcase the MVP functionality.

## Demo Vault Contents

### 📊 Dashboard Metrics (Dashboard.md)
- **47 orders** processed today
- **$8,234.50** in revenue
- **4 minutes 5 seconds** average response time
- **3 pending tasks** requiring approval

### 📋 Pending Tasks (Pending_Approval/)

1. **TASK-001** - Refund approval for defective product
   - Priority: HIGH 🔴
   - Customer: Sarah Johnson
   - Amount: $149.99
   - Clear shipping damage case

2. **TASK-002** - Bulk order discount approval
   - Priority: NORMAL 🟡
   - Client: TechCorp Solutions
   - 50 units, 15% discount requested
   - First-time corporate order

3. **TASK-003** - Return exception request
   - Priority: HIGH 🔴
   - Customer: Michael Chen
   - Outside 30-day window but unopened
   - Good customer, reasonable explanation

### 📬 Messages Across Channels

**Inbox** (Pending):
- Website inquiry about laptop compatibility
- Gmail support ticket for shipping tracking

**Needs_Action**:
- WhatsApp refund request (wrong item shipped - HIGH PRIORITY)

**Done** (Resolved):
- Website inquiry resolved (product availability)
- Gmail support resolved (password reset)

## Running the Demo

### Option 1: Interactive TUI (Recommended)

```bash
python -m src.monitor
```

Or:

```bash
python src/monitor.py
```

### Option 2: Validation Test Suite

```bash
python test_mvp.py
```

This runs comprehensive tests without launching the TUI.

## What You'll See in the TUI

### 1. Live Metrics Panel
```
━━━ Live Metrics ━━━
  Orders Today: 47
  Revenue: $8,234.50
  Avg Response Time: 4m 5s
  Pending Tasks: 3
```

### 2. Pending Approvals Panel
```
━━━ Pending Approvals ━━━
  TASK-001 [high] Approve refund for defective product
  TASK-002 [normal] Approve bulk order discount for...
  TASK-003 [high] Process return outside 30-day window
```

### 3. Status Bar (Bottom)
```
● Connected  |  Last Update: 2026-01-17 22:30:45
```

## Demo Workflow

### Test Approval Process

1. **Launch Dashboard**
   ```bash
   python -m src.monitor
   ```

2. **View Pending Tasks**
   - See 3 tasks listed in the Pending Approvals panel

3. **Open Task Details**
   - Click on "TASK-001" (or any task)
   - Modal opens showing:
     - Task ID and priority
     - Creation timestamp
     - Full task content with details

4. **Approve Task**
   - Click ✓ **Approve** button in modal
   - Modal closes automatically
   - Green success notification appears: "Task TASK-001 approved"
   - Task disappears from pending list within 100ms
   - File moves to `demo_vault/Approved/`

5. **Verify File Move**
   ```bash
   ls demo_vault/Approved/
   # You should see: task-001-refund-approval.md
   ```

### Test Rejection Process

1. **Click Another Task** (e.g., TASK-002)

2. **Reject Task**
   - Click ✗ **Reject** button
   - Red notification appears
   - Task disappears from list
   - File moves to `demo_vault/Rejected/`

### Test Real-Time Updates

1. **Keep Dashboard Running**

2. **In Another Terminal**, add a new task:
   ```bash
   cat > demo_vault/Pending_Approval/task-004-new.md <<'EOF'
   ---
   id: TASK-004
   description: New urgent task
   priority: high
   timestamp: 2026-01-17T23:00:00
   ---

   # New Task

   This task should appear immediately in the dashboard.
   EOF
   ```

3. **Watch Dashboard**
   - New task appears in Pending Approvals panel within 100ms
   - Pending count updates automatically
   - Last Update timestamp updates

## Keyboard Shortcuts

- `q` - Quit application (with cleanup)
- `ESC` - Close modal without action
- `Click` - Select task to view details
- `Mouse` - Navigate and click buttons

## File Structure After Testing

```
demo_vault/
├── Dashboard.md              # Metrics data
├── Inbox/                    # 2 pending messages
├── Needs_Action/             # 1 urgent message
├── Done/                     # 2 resolved messages
├── Pending_Approval/         # 1-2 tasks (after approving some)
├── Approved/                 # Approved tasks moved here
├── Rejected/                 # Rejected tasks moved here
└── [Other folders...]
```

## What to Look For

### ✅ MVP Features Working

1. **Real-Time Metrics**
   - Metrics display correctly from Dashboard.md
   - Channel breakdown shows message counts
   - Pending count matches files in Pending_Approval

2. **Live Updates (<100ms)**
   - File changes detected immediately
   - UI updates without manual refresh
   - Status bar timestamp updates on changes

3. **Task Approval Workflow**
   - Tasks listed with priorities
   - Modal shows full content
   - Approve/Reject moves files correctly
   - Notifications confirm actions
   - Error handling for failures

4. **Connection Monitoring**
   - Status shows "Connected" in green
   - Last update timestamp displayed
   - Auto-reconnect if vault becomes unavailable

5. **Terminal Aesthetic**
   - Black background
   - Cyan borders and labels
   - Green text for metrics
   - Red/green for status indicators

## Error Testing

### Test Race Condition

1. Approve a task (e.g., TASK-001)
2. Try to approve it again (file already moved)
3. Error notification: "Task already processed"

### Test Permission Error

```bash
# Make a task read-only
chmod 444 demo_vault/Pending_Approval/task-002-bulk-order.md

# Try to approve it in dashboard
# Error notification: "Permission denied"
```

## Performance Notes

- **Startup**: Dashboard loads within 2 seconds
- **File Detection**: <100ms from file change to UI update
- **Memory Usage**: Should stay under 100MB
- **Responsiveness**: No lag when clicking or navigating

## Next Steps After Demo

1. **Deploy with Real Vault**
   - Update `.env` with actual AI Employee Vault path
   - Test with production data

2. **Implement Remaining Features** (P2, P3)
   - Channel Activity Breakdown (Phase 5)
   - Recent Activity Stream (Phase 6)
   - Message Classification Analytics (Phase 7)
   - Keyboard Navigation (Phase 8)

3. **Add Polish** (Phase 9)
   - Unit and integration tests
   - Performance optimization
   - Additional error handling
   - Documentation updates

## Troubleshooting

### Dashboard Won't Start

```bash
# Check configuration
python -c "from src.config import load_config; load_config()"

# Check imports
python test_mvp.py
```

### Metrics Not Showing

- Verify `demo_vault/Dashboard.md` exists
- Check file has proper frontmatter (YAML between `---`)
- Check LOG_FILE for errors

### Tasks Not Appearing

- Verify files in `demo_vault/Pending_Approval/`
- Check files have `.md` extension
- Check frontmatter has `id`, `description`, `priority`

### Connection Shows "Disconnected"

- Verify VAULT_PATH in `.env` is correct
- Check vault directory exists and is accessible
- Review `shop-monitor.log` for details

## Demo Success Criteria

✅ All tests in test_mvp.py pass
✅ Dashboard launches without errors
✅ Metrics display correctly
✅ 3 tasks visible in Pending Approvals
✅ Task modal opens on click
✅ Approve/Reject moves files correctly
✅ Notifications appear and auto-dismiss
✅ Real-time updates work (<100ms)
✅ Status bar shows connected state
✅ Keyboard shortcuts work (q to quit, ESC to close)

---

**Demo Status**: ✅ READY - All components validated and working
