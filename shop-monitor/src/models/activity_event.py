"""ActivityEvent entity model."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .enums import MessageType, Channel, Status


@dataclass
class ActivityEvent:
    """Represents a logged action in the vault.

    Attributes:
        timestamp: When the event occurred
        event_type: Type of event (create/move/update/delete)
        channel: Communication channel (if applicable)
        message_type: Type of message (if applicable)
        status_transition: Status change description (if applicable)
        file_path: Path to the file involved in the event
    """
    timestamp: datetime
    event_type: str
    file_path: Path
    channel: Optional[Channel] = None
    message_type: Optional[MessageType] = None
    status_transition: Optional[str] = None

    def to_display_string(self) -> str:
        """Convert event to human-readable display string.

        Returns:
            Formatted string for display in activity stream
        """
        timestamp_str = self.timestamp.strftime("%H:%M:%S")
        file_name = self.file_path.name

        parts = [timestamp_str]

        if self.channel:
            parts.append(self.channel.value)

        if self.message_type:
            parts.append(self.message_type.value)

        parts.append(self.event_type)

        if self.status_transition:
            parts.append(self.status_transition)

        parts.append(f"({file_name})")

        return " | ".join(parts)
