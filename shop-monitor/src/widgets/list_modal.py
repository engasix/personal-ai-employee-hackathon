"""ListModal widget for displaying list of items."""

import logging
from typing import List
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button, ListView, ListItem, Label
from textual.containers import Container, Vertical, Horizontal
from textual.message import Message

from ..models.order_item import OrderItem

logger = logging.getLogger(__name__)


class ListModal(ModalScreen):
    """Modal screen for displaying a list of items.

    Shows items in a scrollable list with order number, customer name, and amount.
    Emits ItemSelected message when an item is clicked.
    """

    DEFAULT_CSS = """
    ListModal {
        align: center middle;
    }

    #list-dialog {
        width: 80;
        height: 30;
        border: heavy #96DED1;
        background: #161616;
        padding: 1;
    }

    #list-title {
        dock: top;
        height: 3;
        text-align: center;
        text-style: bold;
        color: #96DED1;
        background: #161616;
        border-bottom: solid #96DED1;
        content-align: center middle;
    }

    #list-view {
        height: 1fr;
        border: solid #96DED1;
        background: #161616;
        margin: 1 0;
    }

    ListModal ListItem {
        height: 3;
        background: #161616;
        color: white;
        border-bottom: solid #2a2a2a;
        padding: 0 2;
    }

    ListModal ListItem:hover {
        background: #96DED11A;
        color: #96DED1;
    }

    #list-buttons {
        dock: bottom;
        height: 3;
        align: center middle;
    }

    #list-buttons Button {
        margin: 0 2;
        background: #161616;
        color: #96DED1;
        border: solid #96DED1;
    }

    #list-buttons Button:hover {
        background: #96DED11A;
        color: #96DED1;
        border: solid #96DED1;
    }

    .item-row {
        height: 100%;
        content-align-vertical: middle;
    }

    .item-order {
        width: 20;
        color: #FFD700;
        text-style: bold;
    }

    .item-customer {
        width: 1fr;
        color: white;
    }

    .item-amount {
        width: 15;
        color: #98FB98;
        text-align: right;
        text-style: bold;
    }

    .empty-message {
        height: 100%;
        text-align: center;
        color: $text-muted;
        content-align: center middle;
    }
    """

    class ItemSelected(Message):
        """Message emitted when an item is selected."""

        def __init__(self, item: OrderItem):
            """Initialize ItemSelected message.

            Args:
                item: The selected OrderItem
            """
            super().__init__()
            self.item = item

    def __init__(self, title: str, items: List[OrderItem]):
        """Initialize the list modal.

        Args:
            title: Title for the modal
            items: List of OrderItem objects to display
        """
        super().__init__()
        self.title = title
        self.items = items

    def compose(self) -> ComposeResult:
        """Compose the list modal layout."""
        with Container(id="list-dialog"):
            yield Static(f"📋 {self.title}", id="list-title")

            if not self.items:
                yield Static("No items to display", classes="empty-message")
            else:
                # Create list view
                list_view = ListView(id="list-view")
                for item in self.items:
                    # Format item display
                    order_num = item.order_number
                    customer = item.customer_name
                    amount = f"${item.amount:.2f}" if item.amount > 0 else "-"

                    # Create list item with formatted content
                    list_item = ListItem(
                        Horizontal(
                            Label(order_num, classes="item-order"),
                            Label(customer, classes="item-customer"),
                            Label(amount, classes="item-amount"),
                            classes="item-row"
                        )
                    )
                    # Store item reference
                    list_item.item_data = item
                    list_view.append(list_item)

                yield list_view

            # Buttons
            with Horizontal(id="list-buttons"):
                yield Button("Close", id="btn-close", variant="primary")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection.

        Args:
            event: ListView selection event
        """
        # Get the selected item's data
        if hasattr(event.item, "item_data"):
            item = event.item.item_data
            self.post_message(self.ItemSelected(item))
            logger.info(f"Item selected: {item.order_number}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button press event
        """
        if event.button.id == "btn-close":
            self.dismiss()
