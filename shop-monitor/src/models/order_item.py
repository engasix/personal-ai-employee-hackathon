"""OrderItem entity model for detailed item display."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class OrderItem:
    """Represents an order/message item with customer details.

    This model is used for displaying items in list views and detail modals.
    It extracts key information from vault files for dashboard display.

    Attributes:
        order_number: Order or message ID
        customer_name: Name of the customer
        amount: Transaction amount (0.0 for non-order items)
        item_type: Type of item (Order, Refund, Support, Inquiry, etc.)
        status: Current status
        timestamp: Creation timestamp
        file_path: Path to the source markdown file
        full_content: Complete markdown content for detail view
    """
    order_number: str
    customer_name: str
    amount: float
    item_type: str
    status: str
    timestamp: datetime
    file_path: Path
    full_content: str

    @classmethod
    def from_file(cls, file_path: Path, frontmatter: dict, content: str) -> "OrderItem":
        """Create OrderItem from file path, frontmatter, and content.

        Parses both frontmatter and content to extract customer details.

        Args:
            file_path: Path to the markdown file
            frontmatter: Parsed YAML frontmatter dictionary
            content: Full markdown content

        Returns:
            OrderItem instance
        """
        # Extract from frontmatter
        order_number = frontmatter.get("id", file_path.stem)
        item_type = frontmatter.get("type", "Unknown")
        status = frontmatter.get("status", "Pending")

        # Parse timestamp
        timestamp_str = frontmatter.get("timestamp") or frontmatter.get("created")
        if isinstance(timestamp_str, datetime):
            timestamp = timestamp_str
        elif isinstance(timestamp_str, str):
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        # Parse content for customer details
        customer_name = cls._extract_field_from_content(content, "Customer")
        amount_str = cls._extract_field_from_content(content, "Amount")

        # Parse amount
        amount = 0.0
        if amount_str:
            # Remove $ and parse
            try:
                amount = float(amount_str.replace("$", "").replace(",", "").strip())
            except ValueError:
                amount = 0.0

        # If no customer name found, try to extract from content
        if not customer_name:
            customer_name = "Unknown Customer"

        return cls(
            order_number=order_number,
            customer_name=customer_name,
            amount=amount,
            item_type=item_type,
            status=status,
            timestamp=timestamp,
            file_path=file_path,
            full_content=content
        )

    @staticmethod
    def _extract_field_from_content(content: str, field_name: str) -> Optional[str]:
        """Extract a field value from markdown content.

        Looks for patterns like "**Customer**: John Doe" or "Customer: John Doe"

        Args:
            content: Markdown content to search
            field_name: Field name to look for

        Returns:
            Extracted value or None if not found
        """
        import re

        # Try pattern: **Field**: Value
        pattern1 = rf'\*\*{field_name}\*\*:\s*(.+?)(?:\n|$)'
        match = re.search(pattern1, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try pattern: Field: Value
        pattern2 = rf'{field_name}:\s*(.+?)(?:\n|$)'
        match = re.search(pattern2, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None
