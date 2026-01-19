"""VaultWatcher service for monitoring vault file system changes."""

import logging
from pathlib import Path
from typing import Callable, Optional
from queue import Queue
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from ..models.activity_event import ActivityEvent
from ..models.vault_message import VaultMessage
from ..models.enums import MessageType, Channel, Status


logger = logging.getLogger(__name__)


class VaultEventHandler(FileSystemEventHandler):
    """Handler for vault file system events.

    This handler processes file create, modify, delete, and move events
    and queues them for processing by the dashboard.
    """

    def __init__(self, event_queue: Queue, vault_path: Path, parser=None):
        """Initialize the event handler.

        Args:
            event_queue: Queue for file system events
            vault_path: Path to the vault directory
            parser: Optional VaultParser for parsing file metadata
        """
        super().__init__()
        self.event_queue = event_queue
        self.vault_path = vault_path
        self.parser = parser
        self.last_event_time = datetime.now()

    def on_created(self, event: FileSystemEvent):
        """Handle file creation events.

        Args:
            event: File system event
        """
        if not event.is_directory and self._is_markdown_file(event.src_path):
            logger.debug(f"File created: {event.src_path}")
            self._queue_event("created", event.src_path)

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events.

        Args:
            event: File system event
        """
        if not event.is_directory and self._is_markdown_file(event.src_path):
            logger.debug(f"File modified: {event.src_path}")
            self._queue_event("modified", event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events.

        Args:
            event: File system event
        """
        if not event.is_directory and self._is_markdown_file(event.src_path):
            logger.debug(f"File deleted: {event.src_path}")
            self._queue_event("deleted", event.src_path)

    def on_moved(self, event: FileSystemEvent):
        """Handle file move events.

        Args:
            event: File system event
        """
        if not event.is_directory and self._is_markdown_file(event.dest_path):
            logger.debug(f"File moved: {event.src_path} -> {event.dest_path}")
            self._queue_event("moved", event.dest_path, src_path=event.src_path)

    def _is_markdown_file(self, path: str) -> bool:
        """Check if file is a markdown file.

        Args:
            path: File path

        Returns:
            True if file has .md extension
        """
        return path.endswith('.md')

    def _queue_event(self, event_type: str, file_path: str, src_path: Optional[str] = None):
        """Queue a file system event for processing.

        Args:
            event_type: Type of event (created/modified/deleted/moved)
            file_path: Path to the file
            src_path: Source path for move events
        """
        path = Path(file_path)

        # Create ActivityEvent with metadata
        activity_event = self._create_activity_event(event_type, path, src_path)

        # Also keep basic event data for backward compatibility
        event_data = {
            "type": event_type,
            "path": path,
            "src_path": Path(src_path) if src_path else None,
            "timestamp": datetime.now(),
            "activity_event": activity_event  # Include ActivityEvent object
        }
        self.event_queue.put(event_data)
        self.last_event_time = datetime.now()

    def _create_activity_event(self, event_type: str, file_path: Path, src_path: Optional[str] = None) -> ActivityEvent:
        """Create an ActivityEvent from file system event.

        Args:
            event_type: Type of event (created/modified/deleted/moved)
            file_path: Path to the file
            src_path: Source path for move events

        Returns:
            ActivityEvent object
        """
        # Try to extract message metadata if parser available
        channel = None
        message_type = None
        status_transition = None

        if self.parser and file_path.exists():
            try:
                result = self.parser.parse_file(file_path)
                if result:
                    frontmatter, content = result

                    # Try to extract channel and type
                    try:
                        if "channel" in frontmatter:
                            channel = Channel(frontmatter["channel"])
                        if "type" in frontmatter:
                            message_type = MessageType(frontmatter["type"])
                    except (ValueError, KeyError):
                        pass  # Invalid enum value, leave as None

            except Exception as e:
                logger.debug(f"Could not parse file metadata: {e}")

        # Generate status transition for move events
        if event_type == "moved" and src_path:
            src = Path(src_path)
            status_transition = f"{src.parent.name} → {file_path.parent.name}"

        return ActivityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            file_path=file_path,
            channel=channel,
            message_type=message_type,
            status_transition=status_transition
        )


class VaultWatcher:
    """Service for watching vault directory for file changes.

    Uses watchdog library to monitor file system events and notify
    the dashboard of changes in real-time.
    """

    def __init__(self, vault_path: Path, parser=None):
        """Initialize the vault watcher.

        Args:
            vault_path: Path to the vault directory to watch
            parser: Optional VaultParser for parsing file metadata
        """
        self.vault_path = vault_path
        self.parser = parser
        self.event_queue: Queue = Queue()
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[VaultEventHandler] = None
        self.is_running = False
        self._connected = False
        self._last_check = datetime.now()
        self._error_message: Optional[str] = None

    def start(self):
        """Start watching the vault directory.

        Raises:
            ValueError: If vault path does not exist
        """
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        logger.info(f"Starting vault watcher for: {self.vault_path}")

        # Create event handler with parser
        self.event_handler = VaultEventHandler(self.event_queue, self.vault_path, self.parser)

        # Create and configure observer
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.vault_path),
            recursive=True
        )

        # Start observer
        self.observer.start()
        self.is_running = True
        self._connected = True
        self._error_message = None

        logger.info("Vault watcher started successfully")

    def stop(self):
        """Stop watching the vault directory."""
        if self.observer and self.is_running:
            logger.info("Stopping vault watcher")
            self.observer.stop()
            self.observer.join(timeout=5)
            self.is_running = False
            logger.info("Vault watcher stopped")

    def get_event(self, timeout: Optional[float] = None) -> Optional[dict]:
        """Get the next event from the queue.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Event dictionary or None if queue is empty
        """
        try:
            return self.event_queue.get(timeout=timeout)
        except:
            return None

    def has_events(self) -> bool:
        """Check if there are pending events.

        Returns:
            True if events are pending
        """
        return not self.event_queue.empty()

    def check_connection(self) -> bool:
        """Check if vault connection is still active.

        Returns:
            True if connected and vault is accessible
        """
        self._last_check = datetime.now()

        # Check if vault path still exists
        if not self.vault_path.exists():
            if self._connected:
                logger.warning(f"Vault path no longer exists: {self.vault_path}")
                self._connected = False
                self._error_message = "Vault path not found"
            return False

        # Check if observer is still running
        if not self.is_running or not self.observer or not self.observer.is_alive():
            if self._connected:
                logger.warning("Vault watcher observer is not running")
                self._connected = False
                self._error_message = "Watcher not running"
            return False

        # All checks passed
        if not self._connected:
            logger.info("Vault connection restored")
            self._connected = True
            self._error_message = None

        return True

    def reconnect(self) -> bool:
        """Attempt to reconnect to the vault.

        Returns:
            True if reconnection successful
        """
        logger.info("Attempting to reconnect to vault...")

        try:
            # Stop existing observer if running
            if self.observer and self.is_running:
                self.stop()

            # Try to start again
            self.start()
            return True

        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            self._error_message = str(e)
            return False

    @property
    def connected(self) -> bool:
        """Get connection status.

        Returns:
            True if connected
        """
        return self._connected

    @property
    def error_message(self) -> Optional[str]:
        """Get error message if disconnected.

        Returns:
            Error message or None
        """
        return self._error_message

    @property
    def last_check(self) -> datetime:
        """Get timestamp of last connection check.

        Returns:
            Last check timestamp
        """
        return self._last_check
