"""PendingTask entity model."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class PendingTask:
    """Represents a task awaiting approval.

    Attributes:
        task_id: Unique identifier for the task
        description: Brief description of the task
        priority: Task priority level
        creation_timestamp: When the task was created
        file_path: Path to the task markdown file
        full_content: Complete markdown content of the task
    """
    task_id: str
    description: str
    priority: str
    creation_timestamp: datetime
    file_path: Path
    full_content: str

    @classmethod
    def from_file(cls, file_path: Path, frontmatter: dict, content: str) -> "PendingTask":
        """Create PendingTask from file path, frontmatter, and content.

        Args:
            file_path: Path to the task markdown file
            frontmatter: Parsed YAML frontmatter dictionary
            content: Full markdown content

        Returns:
            PendingTask instance
        """
        task_id = frontmatter.get("id", file_path.stem)
        description = frontmatter.get("description", content[:100])
        priority = frontmatter.get("priority", "normal")

        # Parse timestamp
        timestamp_str = frontmatter.get("timestamp") or frontmatter.get("created")
        if isinstance(timestamp_str, datetime):
            timestamp = timestamp_str
        elif isinstance(timestamp_str, str):
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        return cls(
            task_id=task_id,
            description=description,
            priority=priority,
            creation_timestamp=timestamp,
            file_path=file_path,
            full_content=content
        )
