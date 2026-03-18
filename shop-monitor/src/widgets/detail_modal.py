"""DetailModal widget for displaying item details with actions."""

import logging
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Markdown
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.message import Message

from ..models.order_item import OrderItem

logger = logging.getLogger(__name__)


class DetailModal(ModalScreen):
    """Modal screen for displaying item details with action buttons.

    Shows full markdown content of the item.
    For pending approval items, shows Approve/Reject buttons.
    """

    DEFAULT_CSS = """
    DetailModal {
        align: center middle;
    }

    #detail-dialog {
        width: 90;
        height: 35;
        border: heavy #96DED1;
        background: #161616;
        padding: 1;
    }

    #detail-header {
        dock: top;
        height: 5;
        background: #161616;
        border-bottom: solid #96DED1;
        padding: 1;
    }

    #detail-title {
        text-align: center;
        text-style: bold;
        color: #FFD700;
    }

    #detail-metadata {
        text-align: center;
        color: white;
        margin-top: 1;
    }

    #detail-content {
        height: 1fr;
        border: solid #96DED1;
        background: #161616;
        margin: 1 0;
        padding: 1;
    }

    #detail-content Markdown {
        background: #161616;
        color: white;
    }

    #detail-buttons {
        dock: bottom;
        height: 3;
        align: center middle;
    }

    #detail-buttons Button {
        margin: 0 2;
        min-width: 15;
    }

    #btn-approve {
        background: #98FB98;
        color: black;
        border: solid #98FB98;
    }

    #btn-approve:hover {
        background: #98FB98;
        color: black;
    }

    #btn-reject {
        background: red;
        color: white;
        border: solid #ff0000;
    }

    #btn-reject:hover {
        background: #ff0000;
        color: white;
    }

    #btn-close {
        background: #161616;
        color: #96DED1;
        border: solid #96DED1;
    }

    #btn-close:hover {
        background: #96DED11A;
        color: #96DED1;
        border: solid #96DED1;
    }
    """

    class Approve(Message):
        """Message emitted when item is approved."""

        def __init__(self, item: OrderItem):
            """Initialize Approve message.

            Args:
                item: The OrderItem being approved
            """
            super().__init__()
            self.item = item

    class Reject(Message):
        """Message emitted when item is rejected."""

        def __init__(self, item: OrderItem):
            """Initialize Reject message.

            Args:
                item: The OrderItem being rejected
            """
            super().__init__()
            self.item = item

    def __init__(self, item: OrderItem, show_actions: bool = False):
        """Initialize the detail modal.

        Args:
            item: OrderItem to display
            show_actions: Whether to show approve/reject buttons
        """
        super().__init__()
        self.item = item
        self.show_actions = show_actions

    def compose(self) -> ComposeResult:
        """Compose the detail modal layout."""
        with Container(id="detail-dialog"):
            # Header with metadata
            with Container(id="detail-header"):
                yield Static(
                    f"📄 {self.item.order_number}",
                    id="detail-title"
                )
                metadata = f"Customer: {self.item.customer_name} | Amount: ${self.item.amount:.2f} | Status: {self.item.status}"
                yield Static(metadata, id="detail-metadata")

            # Content area with markdown
            with ScrollableContainer(id="detail-content"):
                yield Markdown(self.item.full_content)

            # Buttons
            with Horizontal(id="detail-buttons"):
                if self.show_actions:
                    yield Button("✓ Approve", id="btn-approve", variant="success")
                    yield Button("✗ Reject", id="btn-reject", variant="error")
                yield Button("Close", id="btn-close", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button press event
        """
        if event.button.id == "btn-approve":
            self.post_message(self.Approve(self.item))
            logger.info(f"Item approved: {self.item.order_number}")
            self.dismiss()
        elif event.button.id == "btn-reject":
            self.post_message(self.Reject(self.item))
            logger.info(f"Item rejected: {self.item.order_number}")
            self.dismiss()
        elif event.button.id == "btn-close":
            self.dismiss()
