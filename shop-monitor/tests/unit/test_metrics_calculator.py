"""Unit tests for MetricsCalculator service."""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from src.services.metrics_calculator import MetricsCalculator


@pytest.fixture
def temp_vault():
    """Create a temporary vault directory with test data."""
    vault_dir = Path(tempfile.mkdtemp())
    
    # Create standard folders
    (vault_dir / "Inbox").mkdir()
    (vault_dir / "Done").mkdir()
    (vault_dir / "Needs_Action").mkdir()
    (vault_dir / "Pending_Approval").mkdir()
    
    yield vault_dir
    
    # Cleanup
    shutil.rmtree(vault_dir)


def test_calculate_metrics_empty_vault(temp_vault):
    """Test metrics calculation with empty vault."""
    calculator = MetricsCalculator(temp_vault)
    
    metrics = calculator.calculate_metrics()
    
    assert metrics.total_orders == 0
    assert metrics.pending_count == 0
    assert all(count == 0 for count in metrics.channel_counts.values())
    assert all(count == 0 for count in metrics.type_counts.values())


def test_calculate_metrics_with_messages(temp_vault):
    """Test metrics calculation with sample messages."""
    calculator = MetricsCalculator(temp_vault)
    
    # Create test messages with today's date
    today = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    msg1 = temp_vault / "Inbox" / "msg1.md"
    msg1.write_text(f"""---
type: Support
channel: Gmail
status: Pending
timestamp: {today}
---

Test message 1
""")
    
    msg2 = temp_vault / "Done" / "msg2.md"
    msg2.write_text(f"""---
type: Refund
channel: WhatsApp
status: Resolved
timestamp: {today}
---

Test message 2
""")
    
    metrics = calculator.calculate_metrics()
    
    assert metrics.type_counts['Support'] == 1
    assert metrics.type_counts['Refund'] == 1
    assert metrics.channel_counts['Gmail'] == 1
    assert metrics.channel_counts['WhatsApp'] == 1


def test_auto_resolve_rate_calculation(temp_vault):
    """Test auto-resolution rate calculation."""
    calculator = MetricsCalculator(temp_vault)
    
    today = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    # Create 3 support messages: 2 resolved, 1 pending
    for i in range(2):
        msg = temp_vault / "Done" / f"resolved_{i}.md"
        msg.write_text(f"""---
type: Support
channel: Gmail
status: Resolved
timestamp: {today}
---

Resolved message {i}
""")
    
    msg = temp_vault / "Inbox" / "pending.md"
    msg.write_text(f"""---
type: Support
channel: Gmail
status: Pending
timestamp: {today}
---

Pending message
""")
    
    metrics = calculator.calculate_metrics()
    
    # 2 out of 3 support messages resolved = 66.7%
    assert metrics.type_counts['Support'] == 3
    assert 66 <= metrics.auto_resolve_rates['Support'] <= 67


def test_division_by_zero_handling(temp_vault):
    """Test that division by zero is handled gracefully."""
    calculator = MetricsCalculator(temp_vault)
    
    # No messages - should not crash
    metrics = calculator.calculate_metrics()
    
    # All rates should be 0.0
    assert metrics.auto_resolve_rates['Support'] == 0.0
    assert metrics.auto_resolve_rates['Refund'] == 0.0
    assert metrics.auto_resolve_rates['Inquiry'] == 0.0


def test_count_pending_tasks(temp_vault):
    """Test pending task counting."""
    calculator = MetricsCalculator(temp_vault)
    
    # Create pending tasks
    for i in range(3):
        task = temp_vault / "Pending_Approval" / f"task_{i}.md"
        task.write_text(f"Task {i}")
    
    metrics = calculator.calculate_metrics()
    
    assert metrics.pending_count == 3


def test_graceful_degradation_no_dashboard(temp_vault):
    """Test graceful degradation when Dashboard.md is missing."""
    calculator = MetricsCalculator(temp_vault)
    
    # No Dashboard.md file - should not crash
    metrics = calculator.calculate_metrics()
    
    # Should fall back to defaults
    assert metrics.total_orders == 0
    assert metrics.total_revenue == 0.0
    assert metrics.avg_response_time == 0.0


def test_load_dashboard_metrics(temp_vault):
    """Test loading metrics from Dashboard.md."""
    calculator = MetricsCalculator(temp_vault)
    
    # Create Dashboard.md
    dashboard = temp_vault / "Dashboard.md"
    dashboard.write_text("""---
total_orders: 47
total_revenue: 8234.50
avg_response_time: 245.5
---

Dashboard content
""")
    
    metrics = calculator.calculate_metrics()
    
    assert metrics.total_orders == 47
    assert metrics.total_revenue == 8234.50
    assert metrics.avg_response_time == 245.5


def test_channel_breakdown_calculation(temp_vault):
    """Test per-channel type breakdown calculation."""
    calculator = MetricsCalculator(temp_vault)
    
    today = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    # Website inquiries
    for i in range(2):
        msg = temp_vault / "Inbox" / f"web_{i}.md"
        msg.write_text(f"""---
type: Inquiry
channel: Website
status: Pending
timestamp: {today}
---

Website inquiry {i}
""")
    
    # Gmail support
    msg = temp_vault / "Done" / "gmail.md"
    msg.write_text(f"""---
type: Support
channel: Gmail
status: Resolved
timestamp: {today}
---

Gmail support
""")
    
    metrics = calculator.calculate_metrics()
    
    assert metrics.channel_breakdown['Website']['Inquiry'] == 2
    assert metrics.channel_breakdown['Website']['total'] == 2
    assert metrics.channel_breakdown['Gmail']['Support'] == 1
    assert metrics.channel_breakdown['Gmail']['total'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
