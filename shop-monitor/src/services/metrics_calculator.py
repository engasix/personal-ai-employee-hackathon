"""MetricsCalculator service for aggregating dashboard statistics."""

import logging
from pathlib import Path
from datetime import datetime, time
from typing import List, Optional

from ..models.dashboard_metrics import DashboardMetrics
from ..models.vault_message import VaultMessage
from ..models.enums import MessageType, Channel, Status
from .vault_parser import VaultParser


logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Service for calculating aggregate statistics from vault files.

    Processes vault files to calculate metrics like order counts, revenue,
    response times, and message classification statistics.
    """

    def __init__(self, vault_path: Path):
        """Initialize the metrics calculator.

        Args:
            vault_path: Path to the vault directory
        """
        self.vault_path = vault_path
        self.parser = VaultParser()

    def calculate_metrics(self) -> DashboardMetrics:
        """Calculate all dashboard metrics.

        Returns:
            DashboardMetrics aggregate with current statistics
        """
        metrics = DashboardMetrics()

        try:
            # Calculate file-based metrics
            self._calculate_message_metrics(metrics)

            # Try to load Dashboard.md for additional metrics
            self._load_dashboard_metrics(metrics)

            # Calculate pending task count
            metrics.pending_count = self._count_pending_tasks()

            logger.debug(f"Calculated metrics: {metrics.total_orders} orders, "
                        f"{metrics.pending_count} pending tasks")

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")

        return metrics

    def _calculate_message_metrics(self, metrics: DashboardMetrics):
        """Calculate metrics from message files.

        Args:
            metrics: DashboardMetrics object to update
        """
        # Get today's date range (since midnight)
        today_start = datetime.combine(datetime.now().date(), time.min)

        # Initialize counters
        channel_counts = {"Website": 0, "Gmail": 0, "WhatsApp": 0}
        type_counts = {"Refund": 0, "Support": 0, "Inquiry": 0}
        type_resolved = {"Refund": 0, "Support": 0, "Inquiry": 0}
        type_total = {"Refund": 0, "Support": 0, "Inquiry": 0}

        # Per-channel type breakdown
        channel_breakdown = {
            "Website": {"Refund": 0, "Support": 0, "Inquiry": 0, "total": 0},
            "Gmail": {"Refund": 0, "Support": 0, "Inquiry": 0, "total": 0},
            "WhatsApp": {"Refund": 0, "Support": 0, "Inquiry": 0, "total": 0},
        }

        # Scan for message files in common directories
        message_dirs = [
            self.vault_path / "Inbox",
            self.vault_path / "Needs_Action",
            self.vault_path / "Done",
            self.vault_path / "Pending_Approval",
        ]

        for message_dir in message_dirs:
            if not message_dir.exists():
                continue

            for file_path in message_dir.glob("*.md"):
                result = self.parser.parse_file(file_path)
                if not result:
                    continue

                frontmatter, content = result

                # Try to create VaultMessage
                message = VaultMessage.from_frontmatter(file_path, frontmatter, content)
                if not message:
                    continue

                # Only count messages from today
                if message.timestamp < today_start:
                    continue

                # Update channel counts
                channel_name = message.channel.value
                if channel_name in channel_counts:
                    channel_counts[channel_name] += 1

                # Update type counts
                type_name = message.type.value
                if type_name in type_counts:
                    type_counts[type_name] += 1
                    type_total[type_name] += 1

                    # Track resolved messages for auto-resolve rate
                    if message.status == Status.RESOLVED:
                        type_resolved[type_name] += 1

                # Update per-channel type breakdown
                if channel_name in channel_breakdown and type_name in channel_breakdown[channel_name]:
                    channel_breakdown[channel_name][type_name] += 1
                    channel_breakdown[channel_name]["total"] += 1

        # Update metrics
        metrics.channel_counts = channel_counts
        metrics.type_counts = type_counts
        metrics.channel_breakdown = channel_breakdown

        # Calculate auto-resolve rates
        for type_name in type_total:
            if type_total[type_name] > 0:
                rate = (type_resolved[type_name] / type_total[type_name]) * 100
                metrics.auto_resolve_rates[type_name] = round(rate, 1)
            else:
                metrics.auto_resolve_rates[type_name] = 0.0

    def _load_dashboard_metrics(self, metrics: DashboardMetrics):
        """Load additional metrics from Dashboard.md if available.

        Args:
            metrics: DashboardMetrics object to update
        """
        dashboard_path = self.vault_path / "Dashboard.md"

        if not dashboard_path.exists():
            logger.debug("Dashboard.md not found, using file-based metrics only")
            return

        result = self.parser.parse_file(dashboard_path)
        if not result:
            logger.warning("Failed to parse Dashboard.md")
            return

        frontmatter, content = result

        # Extract metrics from frontmatter
        metrics.total_orders = self.parser.extract_field(frontmatter, "total_orders", 0)
        metrics.total_revenue = self.parser.extract_field(frontmatter, "total_revenue", 0.0)
        metrics.avg_response_time = self.parser.extract_field(frontmatter, "avg_response_time", 0.0)

        logger.debug(f"Loaded metrics from Dashboard.md: {metrics.total_orders} orders, "
                    f"${metrics.total_revenue} revenue")

    def _count_pending_tasks(self) -> int:
        """Count pending tasks in Pending_Approval folder.

        Returns:
            Number of pending tasks
        """
        pending_dir = self.vault_path / "Pending_Approval"

        if not pending_dir.exists():
            return 0

        # Count markdown files in Pending_Approval
        pending_files = list(pending_dir.glob("*.md"))
        return len(pending_files)

    def calculate_channel_breakdown(self, messages: List[VaultMessage]) -> dict:
        """Calculate message breakdown by channel.

        Args:
            messages: List of VaultMessage objects

        Returns:
            Dictionary with channel breakdown statistics
        """
        breakdown = {
            "Website": {"Refund": 0, "Support": 0, "Inquiry": 0},
            "Gmail": {"Refund": 0, "Support": 0, "Inquiry": 0},
            "WhatsApp": {"Refund": 0, "Support": 0, "Inquiry": 0},
        }

        for message in messages:
            channel_name = message.channel.value
            type_name = message.type.value

            if channel_name in breakdown and type_name in breakdown[channel_name]:
                breakdown[channel_name][type_name] += 1

        return breakdown
