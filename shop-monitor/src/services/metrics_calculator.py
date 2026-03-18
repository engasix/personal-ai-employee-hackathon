"""MetricsCalculator service for aggregating dashboard statistics."""

import logging
from pathlib import Path
from datetime import datetime, time, date
from typing import List, Optional

from ..models.dashboard_metrics import DashboardMetrics
from ..models.vault_message import VaultMessage
from ..models.order_item import OrderItem
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

    def calculate_metrics(self, target_date: Optional[date] = None) -> DashboardMetrics:
        """Calculate all dashboard metrics for a specific date.

        Args:
            target_date: Date to calculate metrics for (defaults to today)

        Returns:
            DashboardMetrics aggregate with statistics for the specified date
        """
        if target_date is None:
            target_date = date.today()

        metrics = DashboardMetrics(selected_date=target_date)

        try:
            # Calculate file-based metrics with date filtering
            self._calculate_message_metrics(metrics, target_date)

            # Calculate pending task count and list
            self._calculate_pending_tasks(metrics)

            logger.debug(f"Calculated metrics for {target_date}: {metrics.total_orders} orders, "
                        f"${metrics.total_revenue:.2f} revenue, {metrics.pending_count} pending tasks")

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")

        return metrics

    def _calculate_message_metrics(self, metrics: DashboardMetrics, target_date: date):
        """Calculate metrics from message files for a specific date.

        Args:
            metrics: DashboardMetrics object to update
            target_date: Date to filter messages by
        """
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

        # Item lists for drill-down
        orders_list = []
        inquiries_list = []
        refunds_list = []
        support_list = []

        # Revenue accumulator
        total_revenue = 0.0

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

                # Parse timestamp from frontmatter
                timestamp_str = frontmatter.get("timestamp")
                if isinstance(timestamp_str, datetime):
                    timestamp = timestamp_str
                elif isinstance(timestamp_str, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except ValueError:
                        continue
                else:
                    continue

                # Filter by target_date (only count messages from target_date)
                if timestamp.date() != target_date:
                    continue

                # Create OrderItem for this message
                order_item = OrderItem.from_file(file_path, frontmatter, content)

                # Try to create VaultMessage for classification
                message = VaultMessage.from_frontmatter(file_path, frontmatter, content)
                if message:
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

                        # Add to appropriate list
                        if type_name == "Inquiry":
                            inquiries_list.append(order_item)
                        elif type_name == "Refund":
                            refunds_list.append(order_item)
                            total_revenue += order_item.amount
                        elif type_name == "Support":
                            support_list.append(order_item)

                    # Update per-channel type breakdown
                    if channel_name in channel_breakdown and type_name in channel_breakdown[channel_name]:
                        channel_breakdown[channel_name][type_name] += 1
                        channel_breakdown[channel_name]["total"] += 1

                # Count as order if it has an amount
                if order_item.amount > 0:
                    orders_list.append(order_item)
                    total_revenue += order_item.amount

        # Update metrics
        metrics.channel_counts = channel_counts
        metrics.type_counts = type_counts
        metrics.channel_breakdown = channel_breakdown
        metrics.orders_list = orders_list
        metrics.inquiries_list = inquiries_list
        metrics.refunds_list = refunds_list
        metrics.support_list = support_list
        metrics.total_orders = len(orders_list)
        metrics.total_revenue = total_revenue
        metrics.inquiries_count = len(inquiries_list)
        metrics.refunds_count = len(refunds_list)
        metrics.support_count = len(support_list)

        # Calculate auto-resolve rates
        for type_name in type_total:
            if type_total[type_name] > 0:
                rate = (type_resolved[type_name] / type_total[type_name]) * 100
                metrics.auto_resolve_rates[type_name] = round(rate, 1)
            else:
                metrics.auto_resolve_rates[type_name] = 0.0

    def _calculate_pending_tasks(self, metrics: DashboardMetrics):
        """Calculate pending tasks count and populate pending_list.

        Args:
            metrics: DashboardMetrics object to update
        """
        pending_dir = self.vault_path / "Pending_Approval"

        if not pending_dir.exists():
            metrics.pending_count = 0
            metrics.pending_list = []
            return

        pending_list = []

        # Scan for pending task files
        for file_path in pending_dir.glob("*.md"):
            result = self.parser.parse_file(file_path)
            if not result:
                continue

            frontmatter, content = result

            # Create OrderItem for this pending task
            order_item = OrderItem.from_file(file_path, frontmatter, content)
            pending_list.append(order_item)

        # Update metrics
        metrics.pending_count = len(pending_list)
        metrics.pending_list = pending_list

        logger.debug(f"Found {len(pending_list)} pending tasks")

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
