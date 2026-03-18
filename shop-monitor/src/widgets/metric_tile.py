"""MetricTile widget for displaying clickable metrics."""

import logging
from textual.widgets import Static
from textual.message import Message
from textual.events import Click

logger = logging.getLogger(__name__)


class MetricTile(Static):
    """Clickable metric tile widget.

    Displays a metric with an icon, label, and value.
    Emits TileClicked message when clicked.
    """

    DEFAULT_CSS = """
    MetricTile {
        height: 100%;
        background: #161616;
        border: heavy #96DED1;
        padding: 1 2;
        color: white;
        content-align: center middle;
    }

    MetricTile:hover {
        border: heavy #96DED1;
        background: #96DED11A;
    }

    MetricTile:focus {
        border: heavy #96DED1;
        background: #96DED11A;
    }

    MetricTile .tile-icon {
        text-align: center;
        text-style: bold;
        color: #FFD700;
        margin-bottom: 1;
    }

    MetricTile .tile-label {
        text-align: center;
        color: #96DED1;
        text-style: bold;
        margin-bottom: 1;
    }

    MetricTile .tile-value {
        text-align: center;
        color: white;
        text-style: bold;
        margin-top: 1;
    }
    """

    class TileClicked(Message):
        """Message emitted when tile is clicked."""

        def __init__(self, metric_type: str, metric_value: any):
            """Initialize TileClicked message.

            Args:
                metric_type: Type of metric (e.g., 'orders', 'sales', 'inquiries')
                metric_value: Value of the metric
            """
            super().__init__()
            self.metric_type = metric_type
            self.metric_value = metric_value

    def __init__(
        self,
        metric_type: str,
        label: str,
        icon: str = "",
        value: any = 0,
        **kwargs
    ):
        """Initialize the metric tile.

        Args:
            metric_type: Type of metric (used for identification)
            label: Display label for the metric
            icon: Emoji icon for the metric
            value: Current value of the metric
            **kwargs: Additional keyword arguments for Static
        """
        super().__init__(**kwargs)
        self.metric_type = metric_type
        self.label = label
        self.icon = icon
        self.value = value
        self.can_focus = True
        self.update_display()

    def update_display(self):
        """Update the tile display with current values."""
        # Format value based on type
        if self.metric_type == "sales":
            value_str = f"${self.value:,.2f}"
        else:
            value_str = str(self.value)

        content = f"""
[bold #FFD700]{self.icon}[/bold #FFD700]

[bold #96DED1]{self.label}[/bold #96DED1]

[bold bright_white]{value_str}[/bold bright_white]
"""
        self.update(content.strip())

    def set_value(self, new_value: any):
        """Update the metric value.

        Args:
            new_value: New value for the metric
        """
        self.value = new_value
        self.update_display()

    def on_click(self, event: Click) -> None:
        """Handle click events.

        Args:
            event: Click event
        """
        # Emit TileClicked message
        self.post_message(self.TileClicked(self.metric_type, self.value))
        logger.info(f"Metric tile clicked: {self.metric_type} = {self.value}")
