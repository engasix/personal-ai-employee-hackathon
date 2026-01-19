"""ChannelPanel widget for displaying channel activity breakdown."""

import logging
from textual.widgets import Static

from ..models.dashboard_metrics import DashboardMetrics


logger = logging.getLogger(__name__)


class ChannelPanel(Static):
    """Panel displaying message volume and types broken down by channel.

    Shows three sections (Website, Gmail, WhatsApp) with type breakdowns.
    """

    DEFAULT_CSS = """
    ChannelPanel {
        height: auto;
        border: solid cyan;
        padding: 1;
    }

    ChannelPanel .title {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }

    ChannelPanel .channel-section {
        margin: 0 2 1 2;
    }

    ChannelPanel .channel-name {
        color: green;
        text-style: bold;
    }

    ChannelPanel .channel-stats {
        color: white;
        margin-left: 2;
    }

    ChannelPanel .type-stat {
        color: $text-muted;
    }
    """

    def __init__(self):
        """Initialize the channel panel."""
        super().__init__()
        self._metrics = DashboardMetrics()
        self.update_display()

    def update_display(self):
        """Update the channel panel display with current metrics."""
        # Build display content
        content = [
            "[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]",
            "[bold bright_cyan]               📡 CHANNEL ACTIVITY 📡                    [/bold bright_cyan]",
            "[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]",
            "",
        ]

        # Website section
        content.append(self._format_channel_section("Website", "🌐"))

        # Gmail section
        content.append(self._format_channel_section("Gmail", "📧"))

        # WhatsApp section
        content.append(self._format_channel_section("WhatsApp", "💬"))

        content.append("")
        content.append("[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]")

        self.update("\n".join(content))

    def _format_channel_section(self, channel_name: str, emoji: str = "") -> str:
        """Format a channel section with type breakdown.

        Args:
            channel_name: Name of the channel (Website, Gmail, or WhatsApp)
            emoji: Emoji icon for the channel

        Returns:
            Formatted string for the channel section
        """
        # Get channel data
        channel_data = self._metrics.channel_breakdown.get(channel_name, {})
        total = channel_data.get("total", 0)

        # Channel header with total
        lines = [
            f"  [bold green]{emoji} {channel_name}[/bold green]  [bold bright_white]{total} messages[/bold bright_white]"
        ]

        # Type breakdown
        if total > 0:
            refunds = channel_data.get("Refund", 0)
            support = channel_data.get("Support", 0)
            inquiries = channel_data.get("Inquiry", 0)

            lines.append(
                f"    [yellow]↳[/yellow] Refunds: [bold white]{refunds}[/bold white]  "
                f"Support: [bold white]{support}[/bold white]  "
                f"Inquiries: [bold white]{inquiries}[/bold white]"
            )
        else:
            lines.append("    [yellow]↳[/yellow] [dim]No messages[/dim]")

        lines.append("")  # Add spacing between channels

        return "\n".join(lines)

    def set_metrics(self, metrics: DashboardMetrics):
        """Set new metrics and update display.

        Args:
            metrics: DashboardMetrics object with current statistics
        """
        self._metrics = metrics
        logger.debug(f"Channel panel updated: {metrics.channel_counts}")
        self.update_display()

    @property
    def metrics(self) -> DashboardMetrics:
        """Get current metrics.

        Returns:
            Current DashboardMetrics object
        """
        return self._metrics
