"""VaultMessage entity model."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .enums import MessageType, Channel, Status


@dataclass
class VaultMessage:
    """Represents a customer message markdown file from the vault.

    Attributes:
        type: Type of message (Refund/Support/Inquiry)
        channel: Communication channel (Website/Gmail/WhatsApp)
        status: Current status (Pending/Resolved/Escalated)
        timestamp: When the message was created
        file_path: Path to the markdown file in the vault
        content: Full markdown content of the message
    """
    type: MessageType
    channel: Channel
    status: Status
    timestamp: datetime
    file_path: Path
    content: str

    @classmethod
    def from_frontmatter(cls, file_path: Path, frontmatter: dict, content: str) -> Optional["VaultMessage"]:
        """Create VaultMessage from parsed frontmatter and content.

        Args:
            file_path: Path to the markdown file
            frontmatter: Parsed YAML frontmatter dictionary
            content: Markdown content

        Returns:
            VaultMessage instance or None if required fields are missing
        """
        try:
            message_type = MessageType(frontmatter.get("type", ""))
            channel = Channel(frontmatter.get("channel", ""))
            status = Status(frontmatter.get("status", "Pending"))

            # Parse timestamp - handle various formats
            timestamp_str = frontmatter.get("timestamp")
            if isinstance(timestamp_str, datetime):
                timestamp = timestamp_str
            elif isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str)
            else:
                timestamp = datetime.now()

            return cls(
                type=message_type,
                channel=channel,
                status=status,
                timestamp=timestamp,
                file_path=file_path,
                content=content
            )
        except (ValueError, KeyError):
            # Invalid or missing required fields
            return None
