#!/usr/bin/env python3
"""
reset_vault.py - Clean and reset AI Employee Vault
"""

import json
from pathlib import Path
import shutil
from datetime import datetime

# Configuration
VAULT_PATH = Path('./AI_Employee_Vault')

def reset_vault():
    """Reset the entire vault to initial state"""
    
    print("=" * 60)
    print("VAULT RESET UTILITY")
    print("=" * 60)
    
    # 1. Remove all files from subfolders
    folders_to_clean = [
        'Needs_Action',
        'Pending_Approval',
        'Approved',
        'Done',
        'Plans',
        'Rejected',
        'Inbox',
        'Logs'
    ]
    
    print("\n1. Cleaning subfolders...")
    for folder_name in folders_to_clean:
        folder_path = VAULT_PATH / folder_name
        if folder_path.exists():
            file_count = len(list(folder_path.glob('*')))
            if file_count > 0:
                for file in folder_path.glob('*'):
                    if file.is_file():
                        file.unlink()
                        print(f"   Deleted: {folder_name}/{file.name}")
                print(f"   ✓ Cleaned {folder_name}/ ({file_count} files removed)")
            else:
                print(f"   ✓ {folder_name}/ already empty")
        else:
            print(f"   ! {folder_name}/ doesn't exist")
    
    # 2. Reset orchestrator state
    print("\n2. Resetting orchestrator state...")
    state_file = VAULT_PATH / '.orchestrator_state.json'
    if state_file.exists():
        empty_state = {
            "tasks": [],
            "last_updated": ""
        }
        with open(state_file, 'w') as f:
            json.dump(empty_state, f, indent=2)
        print("   ✓ .orchestrator_state.json reset")
    else:
        print("   ! .orchestrator_state.json doesn't exist")
    
    # 3. Reset Dashboard.md
    print("\n3. Resetting Dashboard.md...")
    dashboard_file = VAULT_PATH / 'Dashboard.md'
    
    default_dashboard = f"""# Dashboard

> Last Updated: {datetime.now().strftime('%Y-%m-%d')} | Auto-refreshed by AI Employee

---

## Today's Snapshot

|Metric|Value|
|---|---|
|Date|{datetime.now().strftime('%Y-%m-%d')}|
|Orders Today|0|
|Revenue Today|$0|
|Pending Tasks|0|
|Awaiting Approval|0|

---

## Weekly Summary

|Metric|This Week|Target|
|---|---|---|
|Total Orders|0|10|
|Revenue|$0|$2,000|
|Leads Received|0|20|
|Conversion Rate|0%|50%|
|Avg Response Time|--|< 30 min|

---

## Task Status

|Folder|Count|
|---|---|
|/Needs_Action|0|
|/Pending_Approval|0|
|/Approved|0|
|/Done (Today)|0|

---

## Recent Activity

|Time|Action|Status|
|---|---|---|
|--|No activity yet|--|

---

## Pending Approvals

|Item|Type|Amount|Created|Action|
|---|---|---|---|---|
|--|No pending approvals|--|--|--|

---

## Social Media

|Platform|Posts This Week|Target|Next Scheduled|
|---|---|---|---|
|LinkedIn|0|3|--|
|X|0|3|--|

---

## Alerts

- [ ] None

---

## Quick Links

- [[Business_Goals]]
- [[Company_Handbook]]
- [[Needs_Action]]
- [[Pending_Approval]]
- [[Done]]
- [[Logs]]
"""
    
    if dashboard_file.exists():
        with open(dashboard_file, 'w') as f:
            f.write(default_dashboard)
        print("   ✓ Dashboard.md reset to default")
    else:
        print("   ! Dashboard.md doesn't exist")
    
    print("\n" + "=" * 60)
    print("✓ VAULT RESET COMPLETE")
    print("=" * 60)
    print("\nYour vault is now clean and ready for testing!")

if __name__ == '__main__':
    # Safety check
    if not VAULT_PATH.exists():
        print(f"ERROR: Vault not found at {VAULT_PATH}")
        exit(1)
    
    print(f"\nThis will reset vault at: {VAULT_PATH.resolve()}")
    confirm = input("Are you sure? (yes/no): ")
    
    if confirm.lower() == 'yes' or confirm.lower() == 'y':
        reset_vault()
    else:
        print("Reset cancelled.")