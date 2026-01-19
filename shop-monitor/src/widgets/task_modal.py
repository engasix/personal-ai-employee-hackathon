"""TaskModal widget for displaying task details with approve/reject actions."""

import logging
from textual.screen import ModalScreen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Button, Label
from textual.message import Message

from ..models.pending_task import PendingTask


logger = logging.getLogger(__name__)


class TaskModal(ModalScreen):
    """Modal screen displaying full task content with approve/reject buttons.

    Displays the complete task markdown content and provides action buttons.
    """

    DEFAULT_CSS = """
    TaskModal {
        align: center middle;
    }

    TaskModal > Container {
        width: 80%;
        height: 80%;
        background: black;
        border: thick cyan;
    }

    TaskModal .modal-title {
        text-align: center;
        text-style: bold;
        color: cyan;
        background: black;
        padding: 1;
        border-bottom: solid green;
    }

    TaskModal .task-header {
        background: black;
        padding: 1;
        border-bottom: solid dim;
    }

    TaskModal .task-content {
        background: black;
        color: white;
        padding: 1;
        height: 1fr;
    }

    TaskModal .button-container {
        background: black;
        padding: 1;
        border-top: solid dim;
        align: center middle;
    }

    TaskModal Button {
        margin: 0 2;
        min-width: 16;
    }

    TaskModal .approve-button {
        background: green;
        color: black;
    }

    TaskModal .reject-button {
        background: red;
        color: white;
    }

    TaskModal .cancel-button {
        background: dim;
        color: white;
    }

    TaskModal .label-key {
        color: cyan;
        text-style: bold;
    }

    TaskModal .label-value {
        color: white;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    class Approve(Message):
        """Message emitted when approve button is clicked."""

        def __init__(self, task: PendingTask) -> None:
            super().__init__()
            self.task = task

    class Reject(Message):
        """Message emitted when reject button is clicked."""

        def __init__(self, task: PendingTask) -> None:
            super().__init__()
            self.task = task

    def __init__(self, task: PendingTask):
        """Initialize the task modal.

        Args:
            task: PendingTask to display
        """
        super().__init__()
        self.task = task

    def compose(self):
        """Compose the modal layout."""
        with Container():
            # Title
            yield Label(
                f"[bold cyan]Task Details: {self.task.task_id}[/bold cyan]",
                classes="modal-title"
            )

            # Task header with metadata
            with Vertical(classes="task-header"):
                yield Label(
                    f"[cyan]Priority:[/cyan] [yellow]{self.task.priority}[/yellow]"
                )
                yield Label(
                    f"[cyan]Created:[/cyan] {self.task.creation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                yield Label(
                    f"[cyan]File:[/cyan] [dim]{self.task.file_path.name}[/dim]"
                )

            # Task content (scrollable)
            with ScrollableContainer(classes="task-content"):
                # Display full content
                content_lines = self.task.full_content.split('\n')
                for line in content_lines:
                    yield Static(line)

            # Action buttons
            with Horizontal(classes="button-container"):
                yield Button("✓ Approve", variant="success", classes="approve-button", id="approve-btn")
                yield Button("✗ Reject", variant="error", classes="reject-button", id="reject-btn")
                yield Button("Cancel", variant="default", classes="cancel-button", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button press event
        """
        button_id = event.button.id

        if button_id == "approve-btn":
            logger.info(f"Approve button pressed for task: {self.task.task_id}")
            self.post_message(self.Approve(self.task))
            self.dismiss()

        elif button_id == "reject-btn":
            logger.info(f"Reject button pressed for task: {self.task.task_id}")
            self.post_message(self.Reject(self.task))
            self.dismiss()

        elif button_id == "cancel-btn":
            logger.debug("Cancel button pressed")
            self.dismiss()

    def action_cancel(self) -> None:
        """Handle ESC key press to cancel."""
        logger.debug("ESC pressed, closing modal")
        self.dismiss()
