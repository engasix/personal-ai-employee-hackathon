"""Enums for Shop Monitor data models."""

from enum import Enum


class MessageType(Enum):
    """Types of customer messages."""
    REFUND = "Refund"
    SUPPORT = "Support"
    INQUIRY = "Inquiry"


class Channel(Enum):
    """Communication channels for customer messages."""
    WEBSITE = "Website"
    GMAIL = "Gmail"
    WHATSAPP = "WhatsApp"


class Status(Enum):
    """Status of customer messages and tasks."""
    PENDING = "Pending"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"
