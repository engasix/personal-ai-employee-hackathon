"""Unit tests for FileManager service."""

import pytest
from pathlib import Path
import tempfile
import shutil
import os

from src.services.file_manager import FileManager


@pytest.fixture
def temp_vault():
    """Create a temporary vault directory."""
    vault_dir = Path(tempfile.mkdtemp())
    
    # Create standard folders
    (vault_dir / "Pending_Approval").mkdir()
    (vault_dir / "Approved").mkdir()
    (vault_dir / "Rejected").mkdir()
    
    yield vault_dir
    
    # Cleanup
    shutil.rmtree(vault_dir)


def test_move_file_success(temp_vault):
    """Test successful file move within vault."""
    manager = FileManager(temp_vault)
    
    # Create test file
    source_file = temp_vault / "Pending_Approval" / "test.md"
    source_file.write_text("test content")
    
    # Move file
    success, error = manager.move_file(source_file, "Approved")
    
    assert success is True
    assert error is None
    assert not source_file.exists()
    assert (temp_vault / "Approved" / "test.md").exists()


def test_move_file_not_found(temp_vault):
    """Test moving a non-existent file."""
    manager = FileManager(temp_vault)
    
    source_file = temp_vault / "Pending_Approval" / "nonexistent.md"
    
    success, error = manager.move_file(source_file, "Approved")
    
    assert success is False
    assert error is not None
    assert "not found" in error.lower()


def test_move_file_outside_vault(temp_vault):
    """Test path validation prevents moving files outside vault."""
    manager = FileManager(temp_vault)
    
    # Create file outside vault
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("test")
        outside_file = Path(f.name)
    
    try:
        success, error = manager.move_file(outside_file, "Approved")
        
        assert success is False
        assert error is not None
        assert "not in vault" in error.lower()
    finally:
        os.unlink(outside_file)


def test_move_file_already_exists(temp_vault):
    """Test moving file when destination already exists."""
    manager = FileManager(temp_vault)
    
    # Create source and destination files
    source_file = temp_vault / "Pending_Approval" / "test.md"
    source_file.write_text("source content")
    
    dest_file = temp_vault / "Approved" / "test.md"
    dest_file.write_text("existing content")
    
    success, error = manager.move_file(source_file, "Approved")
    
    assert success is False
    assert error is not None
    assert "already exists" in error.lower()


def test_is_path_in_vault(temp_vault):
    """Test path validation."""
    manager = FileManager(temp_vault)
    
    # Valid path within vault
    valid_path = temp_vault / "Pending_Approval" / "test.md"
    assert manager._is_path_in_vault(valid_path) is True
    
    # Path outside vault
    outside_path = Path("/tmp/outside.md")
    assert manager._is_path_in_vault(outside_path) is False


def test_approve_task(temp_vault):
    """Test task approval."""
    manager = FileManager(temp_vault)
    
    # Create test task
    task_file = temp_vault / "Pending_Approval" / "task.md"
    task_file.write_text("task content")
    
    success, error = manager.approve_task(task_file)
    
    assert success is True
    assert error is None
    assert (temp_vault / "Approved" / "task.md").exists()


def test_reject_task(temp_vault):
    """Test task rejection."""
    manager = FileManager(temp_vault)
    
    # Create test task
    task_file = temp_vault / "Pending_Approval" / "task.md"
    task_file.write_text("task content")
    
    success, error = manager.reject_task(task_file)
    
    assert success is True
    assert error is None
    assert (temp_vault / "Rejected" / "task.md").exists()


def test_delete_file(temp_vault):
    """Test file deletion."""
    manager = FileManager(temp_vault)
    
    # Create test file
    test_file = temp_vault / "Pending_Approval" / "delete_me.md"
    test_file.write_text("content")
    
    success, error = manager.delete_file(test_file)
    
    assert success is True
    assert error is None
    assert not test_file.exists()


def test_delete_file_outside_vault(temp_vault):
    """Test deletion prevents files outside vault."""
    manager = FileManager(temp_vault)
    
    # Create file outside vault
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("test")
        outside_file = Path(f.name)
    
    try:
        success, error = manager.delete_file(outside_file)
        
        assert success is False
        assert error is not None
        assert "not in vault" in error.lower()
        assert outside_file.exists()  # File should still exist
    finally:
        os.unlink(outside_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
