"""DashboardMetrics aggregate model."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DashboardMetrics:
    """Aggregate statistics for the dashboard.

    Attributes:
        total_orders: Total number of orders today
        total_revenue: Total revenue today
        avg_response_time: Average response time in seconds
        pending_count: Number of pending tasks
        channel_counts: Message counts per channel
        type_counts: Message counts per type
        auto_resolve_rates: Auto-resolution rates per message type
        channel_breakdown: Per-channel type breakdown (e.g., Website: {Refund: 5, Support: 3})
    """
    total_orders: int = 0
    total_revenue: float = 0.0
    avg_response_time: float = 0.0
    pending_count: int = 0
    channel_counts: Dict[str, int] = field(default_factory=dict)
    type_counts: Dict[str, int] = field(default_factory=dict)
    auto_resolve_rates: Dict[str, float] = field(default_factory=dict)
    channel_breakdown: Dict[str, Dict[str, int]] = field(default_factory=dict)

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
