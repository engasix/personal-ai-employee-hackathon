"""Integration tests for approval workflow."""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from src.services.file_manager import FileManager
from src.services.vault_parser import VaultParser
from src.models.pending_task import PendingTask


@pytest.fixture
def temp_vault():
    """Create a temporary vault directory."""
    vault_dir = Path(tempfile.mkdtemp())
    
    (vault_dir / "Pending_Approval").mkdir()
    (vault_dir / "Approved").mkdir()
    (vault_dir / "Rejected").mkdir()
    
    yield vault_dir
    
    shutil.rmtree(vault_dir)


def test_end_to_end_approval_workflow(temp_vault):
    """Test complete approval workflow from file to approval."""
    parser = VaultParser()
    file_manager = FileManager(temp_vault)
    
    # 1. Create pending task file
    task_file = temp_vault / "Pending_Approval" / "task-001.md"
    task_content = """---
task_id: TASK-001
description: Test approval task
priority: high
created: 2026-01-19T10:00:00
---

# Test Task

This is a test task for approval workflow.

## Details
- Action: Approve refund
- Amount: $50.00
- Customer: test@example.com
"""
    task_file.write_text(task_content)
    
    # 2. Parse and load task
    result = parser.parse_file(task_file)
    assert result is not None
    
    frontmatter, content = result
    task = PendingTask.from_file(task_file, frontmatter, content)
    
    assert task.task_id == "TASK-001"
    assert task.priority == "high"
    
    # 3. Approve task (file move)
    success, error = file_manager.approve_task(task.file_path)
    
    assert success is True
    assert error is None
    
    # 4. Verify file moved
    assert not task_file.exists()
    approved_file = temp_vault / "Approved" / "task-001.md"
    assert approved_file.exists()
    
    # 5. Verify content preserved
    result = parser.parse_file(approved_file)
    assert result is not None
    frontmatter, content = result
    assert frontmatter['task_id'] == "TASK-001"


def test_end_to_end_rejection_workflow(temp_vault):
    """Test complete rejection workflow."""
    parser = VaultParser()
    file_manager = FileManager(temp_vault)
    
    # Create pending task
    task_file = temp_vault / "Pending_Approval" / "task-002.md"
    task_content = """---
task_id: TASK-002
description: Test rejection task
priority: normal
---

Task content
"""
    task_file.write_text(task_content)
    
    # Parse task
    result = parser.parse_file(task_file)
    frontmatter, content = result
    task = PendingTask.from_file(task_file, frontmatter, content)
    
    # Reject task
    success, error = file_manager.reject_task(task.file_path)
    
    assert success is True
    assert not task_file.exists()
    assert (temp_vault / "Rejected" / "task-002.md").exists()


def test_approval_workflow_with_missing_file(temp_vault):
    """Test approval workflow when file is missing (race condition)."""
    file_manager = FileManager(temp_vault)
    
    # Try to approve non-existent file
    missing_file = temp_vault / "Pending_Approval" / "missing.md"
    
    success, error = file_manager.approve_task(missing_file)
    
    assert success is False
    assert error is not None
    assert "not found" in error.lower()


def test_approval_workflow_with_duplicate(temp_vault):
    """Test approval workflow when approved file already exists."""
    file_manager = FileManager(temp_vault)
    
    # Create pending task
    task_file = temp_vault / "Pending_Approval" / "task-003.md"
    task_file.write_text("Task content")
    
    # Create existing approved file with same name
    existing_file = temp_vault / "Approved" / "task-003.md"
    existing_file.write_text("Existing content")
    
    # Try to approve (should fail)
    success, error = file_manager.approve_task(task_file)
    
    assert success is False
    assert error is not None
    assert "already exists" in error.lower()
    
    # Verify original file still in Pending_Approval
    assert task_file.exists()


def test_multiple_approvals_in_sequence(temp_vault):
    """Test approving multiple tasks in sequence."""
    file_manager = FileManager(temp_vault)
    
    # Create multiple tasks
    tasks = []
    for i in range(3):
        task_file = temp_vault / "Pending_Approval" / f"task-{i}.md"
        task_file.write_text(f"Task {i}")
        tasks.append(task_file)
    
    # Approve all tasks
    for task_file in tasks:
        success, error = file_manager.approve_task(task_file)
        assert success is True
        assert not task_file.exists()
        assert (temp_vault / "Approved" / task_file.name).exists()


def test_mixed_approval_rejection(temp_vault):
    """Test mix of approvals and rejections."""
    file_manager = FileManager(temp_vault)
    
    # Create tasks
    approve_file = temp_vault / "Pending_Approval" / "approve.md"
    approve_file.write_text("Approve this")
    
    reject_file = temp_vault / "Pending_Approval" / "reject.md"
    reject_file.write_text("Reject this")
    
    # Approve one
    success, error = file_manager.approve_task(approve_file)
    assert success is True
    assert (temp_vault / "Approved" / "approve.md").exists()
    
    # Reject other
    success, error = file_manager.reject_task(reject_file)
    assert success is True
    assert (temp_vault / "Rejected" / "reject.md").exists()
    
    # Verify correct destinations
    assert not approve_file.exists()
    assert not reject_file.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
