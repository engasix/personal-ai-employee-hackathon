"""
Base Watcher Pattern
Template class for all watchers to inherit.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """Abstract base class for all watchers."""
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md file in Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file
        """
        pass
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def run(self):
        """Main loop - runs forever, checking for updates."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Watching vault: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f'Created action file: {filepath}')
            except KeyboardInterrupt:
                self.logger.info('Watcher stopped by user')
                break
            except Exception as e:
                self.logger.error(f'Error: {e}')
            
            time.sleep(self.check_interval)
