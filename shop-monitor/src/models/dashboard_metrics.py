"""DashboardMetrics aggregate model."""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List


@dataclass
class DashboardMetrics:
    """Aggregate statistics for the dashboard.

    Attributes:
        selected_date: Date for which metrics are calculated
        total_orders: Total number of orders for selected date
        total_revenue: Total revenue for selected date (sum of amounts)
        avg_response_time: Average response time in seconds
        pending_count: Number of pending tasks
        inquiries_count: Count of inquiry messages
        refunds_count: Count of refund requests
        support_count: Count of support requests
        channel_counts: Message counts per channel
        type_counts: Message counts per type
        auto_resolve_rates: Auto-resolution rates per message type
        channel_breakdown: Per-channel type breakdown (e.g., Website: {Refund: 5, Support: 3})
        orders_list: Detailed list of orders (for drill-down)
        inquiries_list: Detailed list of inquiries
        refunds_list: Detailed list of refund requests
        support_list: Detailed list of support requests
        pending_list: Detailed list of pending approvals
    """
    selected_date: date = field(default_factory=date.today)
    total_orders: int = 0
    total_revenue: float = 0.0
    avg_response_time: float = 0.0
    pending_count: int = 0
    inquiries_count: int = 0
    refunds_count: int = 0
    support_count: int = 0
    channel_counts: Dict[str, int] = field(default_factory=dict)
    type_counts: Dict[str, int] = field(default_factory=dict)
    auto_resolve_rates: Dict[str, float] = field(default_factory=dict)
    channel_breakdown: Dict[str, Dict[str, int]] = field(default_factory=dict)
    orders_list: List = field(default_factory=list)
    inquiries_list: List = field(default_factory=list)
    refunds_list: List = field(default_factory=list)
    support_list: List = field(default_factory=list)
    pending_list: List = field(default_factory=list)

    def __post_init__(self):
        """Initialize default dictionaries if not provided."""
        if not self.channel_counts:
            self.channel_counts = {
                "Website": 0,
                "Gmail": 0,
                "WhatsApp": 0
            }

        if not self.type_counts:
            self.type_counts = {
                "Refund": 0,
                "Support": 0,
                "Inquiry": 0
            }

        if not self.auto_resolve_rates:
            self.auto_resolve_rates = {
                "Refund": 0.0,
                "Support": 0.0,
                "Inquiry": 0.0
            }

        if not self.channel_breakdown:
            self.channel_breakdown = {
                "Website": {"Refund": 0, "Support": 0, "Inquiry": 0, "total": 0},
                "Gmail": {"Refund": 0, "Support": 0, "Inquiry": 0, "total": 0},
                "WhatsApp": {"Refund": 0, "Support": 0, "Inquiry": 0, "total": 0},
            }
