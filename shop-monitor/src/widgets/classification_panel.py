"""ClassificationPanel widget for displaying message classification analytics."""

import logging
from textual.widgets import Static

from ..models.dashboard_metrics import DashboardMetrics


logger = logging.getLogger(__name__)


class ClassificationPanel(Static):
    """Panel displaying message classification success rates and patterns.

    Shows statistics for each message type (Refund, Support, Inquiry) including
    total counts and auto-resolution success rates.
    """

    DEFAULT_CSS = """
    ClassificationPanel {
        height: auto;
        border: solid cyan;
        padding: 1;
    }

    ClassificationPanel .title {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }

    ClassificationPanel .type-section {
        margin: 0 2 1 2;
    }

    ClassificationPanel .type-name {
        color: green;
        text-style: bold;
    }

    ClassificationPanel .type-stats {
        color: white;
        margin-left: 2;
    }

    ClassificationPanel .success-rate {
        color: cyan;
        text-style: bold;
    }

    ClassificationPanel .rate-high {
        color: green;
        text-style: bold;
    }

    ClassificationPanel .rate-medium {
        color: yellow;
        text-style: bold;
    }

    ClassificationPanel .rate-low {
        color: red;
        text-style: bold;
    }
    """

    def __init__(self):
        """Initialize the classification panel."""
        super().__init__()
        self._metrics = DashboardMetrics()
        self.update_display()

    def update_display(self):
        """Update the classification panel display with current metrics."""
        # Build display content
        content = [
            "[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]",
            "[bold bright_cyan]         🎯 MESSAGE CLASSIFICATION ANALYTICS 🎯          [/bold bright_cyan]",
            "[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]",
            "",
        ]

        # Display each message type
        message_types = [
            ("Refund", "💵"),
            ("Support", "🛠️"),
            ("Inquiry", "❓")
        ]
        for type_name, emoji in message_types:
            content.append(self._format_type_section(type_name, emoji))

        content.append("[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]")

        self.update("\n".join(content))

    def _format_type_section(self, type_name: str, emoji: str = "") -> str:
        """Format a message type section with statistics.

        Args:
            type_name: Name of the message type (Refund, Support, or Inquiry)
            emoji: Emoji icon for the type

        Returns:
            Formatted string for the type section
        """
        # Get type data
        count = self._metrics.type_counts.get(type_name, 0)
        success_rate = self._metrics.auto_resolve_rates.get(type_name, 0.0)

        # Type header with count
        lines = []

        if count == 0:
            # Zero message case
            lines.append(
                f"  [bold green]{emoji} {type_name}[/bold green]  [dim]0 messages[/dim]"
            )
            lines.append(f"    [yellow]↳[/yellow] Success Rate: [dim]N/A[/dim]")
        else:
            # Has messages
            lines.append(
                f"  [bold green]{emoji} {type_name}[/bold green]  [bold bright_white]{count} messages[/bold bright_white]"
            )

            # Success rate with color coding
            rate_color = self._get_rate_color(success_rate)
            lines.append(
                f"    [yellow]↳[/yellow] Success Rate: [{rate_color}]{success_rate:.1f}%[/{rate_color}]"
            )

        lines.append("")  # Add spacing

        return "\n".join(lines)

    def _get_rate_color(self, rate: float) -> str:
        """Get color coding for success rate.

        Args:
            rate: Success rate percentage (0-100)

        Returns:
            Color name for the rate
        """
        if rate >= 80.0:
            return "green bold"
        elif rate >= 50.0:
            return "yellow bold"
        else:
            return "red bold"

    def set_metrics(self, metrics: DashboardMetrics):
        """Set new metrics and update display.

        Args:
            metrics: DashboardMetrics object with current statistics
        """
        self._metrics = metrics
        logger.debug(f"Classification panel updated: {metrics.type_counts}")
        self.update_display()

    @property
    def metrics(self) -> DashboardMetrics:
        """Get current metrics.

        Returns:
            Current DashboardMetrics object
        """
        return self._metrics
