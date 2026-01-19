"""MetricsPanel widget for displaying live dashboard metrics."""

import logging
from textual.widgets import Static
from textual.containers import Grid

from ..models.dashboard_metrics import DashboardMetrics


logger = logging.getLogger(__name__)


class MetricsPanel(Static):
    """Panel displaying live metrics: orders, revenue, response time, pending tasks.

    Updates reactively when new metrics are received.
    """

    DEFAULT_CSS = """
    MetricsPanel {
        height: auto;
        border: solid cyan;
        padding: 1;
    }

    MetricsPanel .title {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }

    MetricsPanel .metric {
        margin: 0 2;
    }

    MetricsPanel .metric-label {
        color: green;
        text-style: bold;
    }

    MetricsPanel .metric-value {
        color: white;
        text-style: bold;
    }
    """

    def __init__(self):
        """Initialize the metrics panel."""
        super().__init__()
        self._metrics = DashboardMetrics()
        self.update_display()

    def update_display(self):
        """Update the metrics panel display with current metrics."""
        # Format response time
        if self._metrics.avg_response_time > 0:
            response_time_seconds = self._metrics.avg_response_time
            if response_time_seconds < 60:
                time_display = f"{response_time_seconds:.1f}s"
            else:
                minutes = int(response_time_seconds // 60)
                seconds = int(response_time_seconds % 60)
                time_display = f"{minutes}m {seconds}s"
        else:
            time_display = "N/A"

        # Build display with bigger, more readable text
        content = [
            "[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]",
            "[bold bright_cyan]                    📊 LIVE METRICS 📊                   [/bold bright_cyan]",
            "[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]",
            "",
            f"  [bold green]📦 Orders Today[/bold green]          [bold bright_white]{self._metrics.total_orders}[/bold bright_white]",
            "",
            f"  [bold green]💰 Revenue[/bold green]               [bold bright_white]${self._metrics.total_revenue:.2f}[/bold bright_white]",
            "",
            f"  [bold green]⚡ Avg Response Time[/bold green]     [bold bright_white]{time_display}[/bold bright_white]",
            "",
            f"  [bold green]⏳ Pending Tasks[/bold green]         [bold bright_white]{self._metrics.pending_count}[/bold bright_white]",
            "",
            "[bold bright_cyan]═══════════════════════════════════════════════════════[/bold bright_cyan]",
        ]

        self.update("\n".join(content))

    def set_metrics(self, metrics: DashboardMetrics):
        """Set new metrics and update display.

        Args:
            metrics: DashboardMetrics object with current statistics
        """
        self._metrics = metrics
        logger.debug(f"Metrics updated: {metrics.total_orders} orders, "
                    f"{metrics.pending_count} pending")
        self.update_display()

    @property
    def metrics(self) -> DashboardMetrics:
        """Get current metrics.

        Returns:
            Current DashboardMetrics object
        """
        return self._metrics
