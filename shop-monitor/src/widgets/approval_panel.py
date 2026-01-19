"""ApprovalPanel widget for displaying and managing pending task approvals."""

import logging
from pathlib import Path
from typing import List, Optional

from textual.widgets import Static, Button, ListView, ListItem, Label
from textual.containers import Vertical, Horizontal
from textual.message import Message

from ..models.pending_task import PendingTask


logger = logging.getLogger(__name__)


class ApprovalPanel(Static):
    """Panel displaying pending tasks with approve/reject buttons.

    Displays tasks from the Pending_Approval folder and allows
    interactive approval or rejection.
    """

    DEFAULT_CSS = """
    ApprovalPanel {
        height: auto;
        border: solid cyan;
        padding: 1;
    }

    ApprovalPanel .title {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }

    ApprovalPanel ListView {
        height: auto;
        max-height: 20;
        background: black;
        border: none;
    }

    ApprovalPanel ListItem {
        background: black;
        color: white;
        padding: 0 1;
    }

    ApprovalPanel ListItem:hover {
        background: $primary-darken-1;
    }

    ApprovalPanel .task-row {
        width: 100%;
    }

    ApprovalPanel .task-info {
        color: white;
    }

    ApprovalPanel .task-id {
        color: cyan;
        text-style: bold;
    }

    ApprovalPanel .task-priority {
        color: yellow;
    }

    ApprovalPanel .no-tasks {
        color: $text-muted;
        text-align: center;
        padding: 2;
    }

    ApprovalPanel Button {
        margin: 0 1;
    }
    """

    class TaskSelected(Message):
        """Message emitted when a task is selected."""

        def __init__(self, task: PendingTask) -> None:
            super().__init__()
            self.task = task

    class TaskApprove(Message):
        """Message emitted when approve button is clicked."""

        def __init__(self, task: PendingTask) -> None:
            super().__init__()
            self.task = task

    class TaskReject(Message):
        """Message emitted when reject button is clicked."""

        def __init__(self, task: PendingTask) -> None:
            super().__init__()
            self.task = task

    def __init__(self):
        """Initialize the approval panel."""
        super().__init__()
        self._tasks: List[PendingTask] = []
        self._list_view: Optional[ListView] = None

    def compose(self):
        """Compose the approval panel layout."""
        yield Label("[bold cyan]━━━ Pending Approvals ━━━[/bold cyan]", classes="title")

        # Task list container
        with Vertical():
            self._list_view = ListView()
            yield self._list_view

    def set_tasks(self, tasks: List[PendingTask]):
        """Set the list of pending tasks.

        Args:
            tasks: List of PendingTask objects
        """
        self._tasks = tasks
        logger.debug(f"Approval panel updated with {len(tasks)} tasks")
        self.update_display()

    def update_display(self):
        """Update the task list display."""
        if not self._list_view:
            return

        # Clear existing items
        self._list_view.clear()

        if not self._tasks:
            # Show "no tasks" message
            item = ListItem(
                Label("[dim]No pending tasks[/dim]", classes="no-tasks")
            )
            self._list_view.append(item)
            return

        # Add tasks to list
        for task in self._tasks:
            # Create task row with info and buttons
            task_label = self._format_task_label(task)

            with Horizontal(classes="task-row"):
                item_label = Label(task_label, classes="task-info")

            item = ListItem(item_label)
            item.task = task  # Store task reference
            self._list_view.append(item)

    def _format_task_label(self, task: PendingTask) -> str:
        """Format a task for display.

        Args:
            task: PendingTask to format

        Returns:
            Formatted string
        """
        # Truncate description if too long
        desc = task.description
        if len(desc) > 50:
            desc = desc[:47] + "..."

        priority_color = "yellow" if task.priority == "high" else "white"

        return (
            f"[cyan]{task.task_id}[/cyan] "
            f"[{priority_color}][{task.priority}][/{priority_color}] "
            f"{desc}"
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle task selection.

        Args:
            event: Selection event
        """
        if hasattr(event.item, 'task'):
            task = event.item.task
            logger.debug(f"Task selected: {task.task_id}")
            self.post_message(self.TaskSelected(task))

    @property
    def tasks(self) -> List[PendingTask]:
        """Get current tasks.

        Returns:
            List of PendingTask objects
        """
        return self._tasks

    def get_task_by_id(self, task_id: str) -> Optional[PendingTask]:
        """Get a task by its ID.

        Args:
            task_id: Task ID to find

        Returns:
            PendingTask or None if not found
        """
        for task in self._tasks:
            if task.task_id == task_id:
                return task
        return None

    def remove_task(self, task: PendingTask):
        """Remove a task from the list.

        Args:
            task: Task to remove
        """
        if task in self._tasks:
            self._tasks.remove(task)
            self.update_display()
