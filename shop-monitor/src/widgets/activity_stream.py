"""ActivityStream widget for displaying recent AI actions."""

import logging
from collections import deque
from typing import Deque

from textual.widgets import Static
from textual.reactive import reactive

from ..models.activity_event import ActivityEvent


logger = logging.getLogger(__name__)


class ActivityStream(Static):
    """Scrolling feed of last 20 AI actions with timestamps.

    Displays chronological list of vault activities including file
    operations, status transitions, and message metadata.
    """

    DEFAULT_CSS = """
    ActivityStream {
        height: auto;
        border: solid cyan;
        padding: 1;
    }

    ActivityStream .title {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }

    ActivityStream .activity-item {
        margin: 0 1;
        color: white;
    }

    ActivityStream .activity-item-new {
        margin: 0 1;
        color: green;
        text-style: bold;
    }

    ActivityStream .empty-state {
        color: $text-muted;
        text-align: center;
        margin: 2;
    }

    ActivityStream .timestamp {
        color: cyan;
    }

    ActivityStream .event-created {
        color: green;
    }

    ActivityStream .event-modified {
        color: yellow;
    }

    ActivityStream .event-deleted {
        color: red;
    }

    ActivityStream .event-moved {
        color: magenta;
    }
    """

    MAX_ITEMS = 20

    def __init__(self):
        """Initialize the activity stream."""
        super().__init__()
        self._events: Deque[ActivityEvent] = deque(maxlen=self.MAX_ITEMS)
        self.update_display()

    def update_display(self):
        """Update the activity stream display with current events."""
        # Build display content
        content = [
            "[bold cyan]━━━ Recent Activity ━━━[/bold cyan]\n",
        ]

        if not self._events:
            content.append("[dim]No recent activity[/dim]")
        else:
            # Display events in chronological order (newest first)
            for event in self._events:
                content.append(self._format_activity_item(event))

        self.update("\n".join(content))

    def _format_activity_item(self, event: ActivityEvent) -> str:
        """Format an activity event for display.

        Args:
            event: ActivityEvent to format

        Returns:
            Formatted string for the activity item
        """
        # Timestamp
        timestamp_str = event.timestamp.strftime("%H:%M:%S")
        parts = [f"[cyan]{timestamp_str}[/cyan]"]

        # Event type with color coding
        event_type_colored = self._colorize_event_type(event.event_type)
        parts.append(event_type_colored)

        # Channel (if available)
        if event.channel:
            parts.append(f"[green]{event.channel.value}[/green]")

        # Message type (if available)
        if event.message_type:
            parts.append(f"[yellow]{event.message_type.value}[/yellow]")

        # Status transition (for move events)
        if event.status_transition:
            parts.append(f"[magenta]{event.status_transition}[/magenta]")

        # File name
        file_name = event.file_path.name
        parts.append(f"[dim]({file_name})[/dim]")

        return " | ".join(parts)

    def _colorize_event_type(self, event_type: str) -> str:
        """Apply color coding to event type.

        Args:
            event_type: Event type string

        Returns:
            Colored event type string
        """
        color_map = {
            "created": "green",
            "modified": "yellow",
            "deleted": "red",
            "moved": "magenta",
        }

        color = color_map.get(event_type, "white")
        return f"[{color}]{event_type.upper()}[/{color}]"

    def add_event(self, event: ActivityEvent):
        """Add a new activity event to the stream.

        Args:
            event: ActivityEvent to add
        """
        # Add to beginning (newest first)
        self._events.appendleft(event)

        # Bounded buffer automatically removes oldest item when exceeding MAX_ITEMS
        logger.debug(f"Activity added: {event.event_type} - {event.file_path.name}")

        # Update display
        self.update_display()

    def clear_events(self):
        """Clear all events from the stream."""
        self._events.clear()
        logger.debug("Activity stream cleared")
        self.update_display()

    @property
    def event_count(self) -> int:
        """Get current number of events in the stream.

        Returns:
            Number of events
        """
        return len(self._events)

    @property
    def events(self) -> list:
        """Get list of current events.

        Returns:
            List of ActivityEvent objects
        """
        return list(self._events)
