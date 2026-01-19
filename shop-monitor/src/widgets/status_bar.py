"""StatusBar widget for displaying connection status and last update timestamp."""

import logging
from datetime import datetime

from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Horizontal


logger = logging.getLogger(__name__)


class StatusBar(Static):
    """Status bar widget showing connection status and last update time.

    Displays:
    - Connection status (Connected/Disconnected)
    - Last update timestamp
    """

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text;
        padding: 0 1;
    }

    StatusBar .connected {
        color: green;
    }

    StatusBar .disconnected {
        color: red;
    }

    StatusBar .timestamp {
        color: cyan;
    }
    """

    def __init__(self):
        """Initialize the status bar."""
        super().__init__()
        self._connected = False
        self._last_update: datetime = None
        self.update_display()

    def update_display(self):
        """Update the status bar display."""
        # Connection status
        if self._connected:
            status_text = "[green]● Connected[/green]"
        else:
            status_text = "[red]● Disconnected[/red]"

        # Last update timestamp
        if self._last_update:
            timestamp_str = self._last_update.strftime("%Y-%m-%d %H:%M:%S")
            timestamp_text = f"[cyan]Last Update: {timestamp_str}[/cyan]"
        else:
            timestamp_text = "[dim]Last Update: Never[/dim]"

        # Combine status and timestamp
        self.update(f"{status_text}  |  {timestamp_text}")

    def set_connected(self, connected: bool):
        """Set the connection status.

        Args:
            connected: True if connected, False otherwise
        """
        if self._connected != connected:
            self._connected = connected
            logger.info(f"Connection status changed: {'Connected' if connected else 'Disconnected'}")
            self.update_display()

    def set_last_update(self, timestamp: datetime):
        """Set the last update timestamp.

        Args:
            timestamp: Timestamp of the last update
        """
        self._last_update = timestamp
        self.update_display()

    @property
    def connected(self) -> bool:
        """Get the current connection status.

        Returns:
            True if connected, False otherwise
        """
        return self._connected

    @property
    def last_update(self) -> datetime:
        """Get the last update timestamp.

        Returns:
            Last update timestamp or None
        """
        return self._last_update
