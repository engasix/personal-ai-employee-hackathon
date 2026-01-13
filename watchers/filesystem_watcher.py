"""
File System Watcher
Monitors the /Inbox folder for new files and creates action items.
"""

import shutil
from pathlib import Path
from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """Watches /Inbox folder for new files."""
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Setup Inbox folder
        self.inbox = self.vault_path / 'Inbox'
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files: set = set()
        
        self.logger.info(f'Watching Inbox: {self.inbox}')
    
    def check_for_updates(self) -> list:
        """
        Check /Inbox for new files.
        
        Returns:
            List of new file paths
        """
        new_files = []
        
        for filepath in self.inbox.iterdir():
            # Skip directories and hidden files
            if filepath.is_dir() or filepath.name.startswith('.'):
                continue
            
            # Skip already processed files
            if filepath.name in self.processed_files:
                continue
            
            new_files.append(filepath)
        
        return new_files
    
    def create_action_file(self, item: Path) -> Path:
        """
        Create action file for a dropped file.
        
        Args:
            item: Path to the file in /Inbox
            
        Returns:
            Path to the created action file
        """
        # Generate action file content
        content = f"""---
type: file_drop
original_name: {item.name}
size: {item.stat().st_size}
received: {self.get_timestamp()}
priority: normal
status: pending
---

## File Dropped

A new file has been dropped in the Inbox for processing.

**File:** {item.name}
**Size:** {item.stat().st_size} bytes

## Suggested Actions

- [ ] Review file contents
- [ ] Process according to file type
- [ ] Move to appropriate location
- [ ] Update relevant records
"""
        
        # Create action file in Needs_Action
        action_filename = f"FILE_{item.stem}_{self.get_timestamp().replace(':', '-')}.md"
        action_path = self.needs_action / action_filename
        action_path.write_text(content)
        
        # Mark as processed
        self.processed_files.add(item.name)
        
        return action_path


if __name__ == '__main__':
    import sys
    
    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = '../../AI_Employee_Vault'
    
    # Start watcher
    watcher = FileSystemWatcher(vault_path)
    watcher.run()
