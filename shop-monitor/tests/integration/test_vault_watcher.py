"""Integration tests for VaultWatcher service."""

import pytest
from pathlib import Path
import tempfile
import shutil
import time

from src.services.vault_watcher import VaultWatcher
from src.services.vault_parser import VaultParser


@pytest.fixture
def temp_vault():
    """Create a temporary vault directory."""
    vault_dir = Path(tempfile.mkdtemp())
    (vault_dir / "Inbox").mkdir()
    (vault_dir / "Done").mkdir()
    
    yield vault_dir
    
    shutil.rmtree(vault_dir)


def test_vault_watcher_detect_file_creation(temp_vault):
    """Test that VaultWatcher detects file creation events."""
    parser = VaultParser()
    watcher = VaultWatcher(temp_vault, parser)
    
    try:
        watcher.start()
        
        # Create a test file
        test_file = temp_vault / "Inbox" / "test_create.md"
        test_file.write_text("""---
type: Inquiry
channel: Website
---

Test content
""")
        
        # Wait for event processing
        time.sleep(0.5)
        
        # Check for events
        assert watcher.has_events()
        
        event = watcher.get_event(timeout=1)
        assert event is not None
        assert event['type'] == 'created'
        assert event['path'].name == 'test_create.md'
        assert 'activity_event' in event
        
    finally:
        watcher.stop()


def test_vault_watcher_detect_file_modification(temp_vault):
    """Test that VaultWatcher detects file modification events."""
    parser = VaultParser()
    watcher = VaultWatcher(temp_vault, parser)
    
    # Create file before starting watcher
    test_file = temp_vault / "Inbox" / "test_modify.md"
    test_file.write_text("Initial content")
    
    try:
        watcher.start()
        
        # Modify the file
        time.sleep(0.2)
        test_file.write_text("Modified content")
        
        # Wait for event processing
        time.sleep(0.5)
        
        # Check for events
        assert watcher.has_events()
        
        event = watcher.get_event(timeout=1)
        assert event is not None
        assert event['type'] == 'modified'
        
    finally:
        watcher.stop()


def test_vault_watcher_detect_file_deletion(temp_vault):
    """Test that VaultWatcher detects file deletion events."""
    parser = VaultParser()
    watcher = VaultWatcher(temp_vault, parser)
    
    # Create file before starting watcher
    test_file = temp_vault / "Inbox" / "test_delete.md"
    test_file.write_text("Content to delete")
    
    try:
        watcher.start()
        
        # Delete the file
        time.sleep(0.2)
        test_file.unlink()
        
        # Wait for event processing
        time.sleep(0.5)
        
        # Check for events
        assert watcher.has_events()
        
        event = watcher.get_event(timeout=1)
        assert event is not None
        assert event['type'] == 'deleted'
        
    finally:
        watcher.stop()


def test_vault_watcher_detect_file_move(temp_vault):
    """Test that VaultWatcher detects file move events."""
    parser = VaultParser()
    watcher = VaultWatcher(temp_vault, parser)
    
    # Create file before starting watcher
    source_file = temp_vault / "Inbox" / "test_move.md"
    source_file.write_text("Content to move")
    
    try:
        watcher.start()
        
        # Move the file
        time.sleep(0.2)
        dest_file = temp_vault / "Done" / "test_move.md"
        shutil.move(str(source_file), str(dest_file))
        
        # Wait for event processing
        time.sleep(0.5)
        
        # Check for events
        assert watcher.has_events()
        
        event = watcher.get_event(timeout=1)
        assert event is not None
        assert event['type'] == 'moved'
        assert 'activity_event' in event
        
        # Check status transition
        activity_event = event['activity_event']
        assert activity_event.status_transition is not None
        assert 'Inbox' in activity_event.status_transition
        assert 'Done' in activity_event.status_transition
        
    finally:
        watcher.stop()


def test_vault_watcher_connection_check(temp_vault):
    """Test VaultWatcher connection monitoring."""
    parser = VaultParser()
    watcher = VaultWatcher(temp_vault, parser)
    
    try:
        watcher.start()
        
        # Check connection
        assert watcher.check_connection()
        assert watcher.connected
        assert watcher.is_running
        
    finally:
        watcher.stop()


def test_vault_watcher_metadata_extraction(temp_vault):
    """Test that VaultWatcher extracts metadata from files."""
    parser = VaultParser()
    watcher = VaultWatcher(temp_vault, parser)
    
    try:
        watcher.start()
        
        # Create file with metadata
        test_file = temp_vault / "Inbox" / "test_metadata.md"
        test_file.write_text("""---
type: Support
channel: Gmail
status: Pending
---

Test with metadata
""")
        
        # Wait for event processing
        time.sleep(0.5)
        
        event = watcher.get_event(timeout=1)
        assert event is not None
        
        activity_event = event['activity_event']
        assert activity_event is not None
        assert activity_event.channel is not None
        assert activity_event.message_type is not None
        
    finally:
        watcher.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
