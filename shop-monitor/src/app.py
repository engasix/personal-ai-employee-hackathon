"""Main Textual App class for Shop Monitor."""

import logging
from datetime import datetime, date
from pathlib import Path
from typing import List

from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.widgets import Footer, Static
from textual.events import Click

from .config import get_config
from .services.vault_watcher import VaultWatcher
from .services.metrics_calculator import MetricsCalculator
from .services.vault_parser import VaultParser
from .services.file_manager import FileManager
from .widgets.date_picker import DatePicker
from .widgets.metric_tile import MetricTile
from .widgets.list_modal import ListModal
from .widgets.detail_modal import DetailModal
from .widgets.ceo_briefing import CEOBriefing
from .models.dashboard_metrics import DashboardMetrics
from .models.order_item import OrderItem


logger = logging.getLogger(__name__)


class ShopMonitorApp(App):
    """Shop Monitor - Real-Time Terminal Dashboard.

    Main Textual application class for the Shop Monitor dashboard.
    Displays live metrics with date filtering and drill-down capabilities.
    """

    LOGO_COLOR = "#FFD700"
    SUB_LOGO_COLOR = "#98FB98"
    LINES_COLOR = "#96DED1"

    CSS = """
    Screen {
        background: #161616;
    }

    Footer {
        dock: bottom;
        height: 1;
        background: #161616;
        color: #96DED1;
    }

    #logo-section {
        height: 14;
        background: #161616;
        border: heavy #96DED1;
        content-align: center middle;
    }

    #main-container {
        height: auto;
        layout: horizontal;
        margin: 0 1 1 1;
    }

    #left-column {
        width: 50%;
        height: auto;
        padding-right: 1;
    }

    #metrics-grid {
        height: auto;
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1 1;
        margin-bottom: 1;
    }

    #support-tile {
        height: auto;
        width: 100%;
    }

    #right-column {
        width: 50%;
        height: auto;
        border: heavy #96DED1;
        background: #161616;
        padding: 1;
    }

    #pending-title {
        text-align: center;
        text-style: bold;
        color: #96DED1;
        margin-bottom: 1;
    }

    #pending-list {
        height: auto;
    }

    .pending-item {
        height: 3;
        background: #161616;
        color: white;
        border-bottom: solid #2a2a2a;
        padding: 0 1;
    }

    .pending-item:hover {
        background: #96DED11A;
        color: #96DED1;
    }

    .notification {
        dock: top;
        height: 3;
        background: #161616;
        border: solid #96DED1;
        margin: 0 1 1 1;
        padding: 1;
        text-align: center;
        color: white;
    }

    .notification-success {
        background: #001a00;
        border: solid #00ff00;
        color: #00ff00;
    }

    .notification-error {
        background: #1a0000;
        border: solid #ff0000;
        color: #ff0000;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        """Initialize the Shop Monitor app."""
        super().__init__()
        self.title = "Shop Monitor - Real-Time Dashboard"
        self.sub_title = "FTE Shop AI Employee Monitoring"

        # Load configuration
        self.config = get_config()

        # Initialize services
        self.vault_watcher: VaultWatcher = None
        self.metrics_calculator: MetricsCalculator = None
        self.vault_parser: VaultParser = None
        self.file_manager: FileManager = None

        # Current state
        self.current_date = date.today()
        self.current_metrics: DashboardMetrics = None

        # Widget references
        self.date_picker: DatePicker = None
        self.tiles = {}
        self.ceo_briefing: CEOBriefing = None
        self.notification_widget: Static = None

    def compose(self) -> ComposeResult:
        """Compose the application layout.

        Returns:
            Composed result with all widgets
        """
        # Logo section with FTE SHOP branding
        logo_section = Static(id="logo-section")
        logo_section.update(f"""
        [bold {self.LOGO_COLOR}]
            ███████╗████████╗███████╗    ███████╗██╗  ██╗ ██████╗ ██████╗
            ██╔════╝╚══██╔══╝██╔════╝    ██╔════╝██║  ██║██╔═══██╗██╔══██╗
            █████╗     ██║   █████╗      ███████╗███████║██║   ██║██████╔╝
            ██╔══╝     ██║   ██╔══╝      ╚════██║██╔══██║██║   ██║██╔═══╝
            ██║        ██║   ███████╗    ███████║██║  ██║╚██████╔╝██║
            ╚═╝        ╚═╝   ╚══════╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝
        [/bold {self.LOGO_COLOR}]
                        [bold {self.SUB_LOGO_COLOR}] {self.title} [/bold {self.SUB_LOGO_COLOR}]
        """)
        yield logo_section

        # Date picker
        self.date_picker = DatePicker(self.current_date)
        yield self.date_picker

        # Main container with 2 columns
        with Container(id="main-container"):
            # Left column - Metrics
            with Container(id="left-column"):
                # 2x2 grid for first 4 metrics
                with Grid(id="metrics-grid"):
                    self.tiles["orders"] = MetricTile("orders", "Orders Today", "📦", 0, id="tile-orders")
                    yield self.tiles["orders"]

                    self.tiles["sales"] = MetricTile("sales", "Revenue", "💰", 0, id="tile-sales")
                    yield self.tiles["sales"]

                    self.tiles["inquiries"] = MetricTile("inquiries", "Inquiries", "❓", 0, id="tile-inquiries")
                    yield self.tiles["inquiries"]

                    self.tiles["refunds"] = MetricTile("refunds", "Refund Requests", "💵", 0, id="tile-refunds")
                    yield self.tiles["refunds"]

                # Support tile - full width
                self.tiles["support"] = MetricTile("support", "Support Requests", "🛠️", 0, id="support-tile")
                yield self.tiles["support"]

            # Right column - Pending Approvals List
            with Container(id="right-column"):
                yield Static("⏳ Pending Approvals", id="pending-title")

                # Container for pending items
                with Container(id="pending-list"):
                    pass  # Will be populated dynamically

        # CEO Briefing section
        self.ceo_briefing = CEOBriefing(self.config.vault_path, self.current_date)
        yield self.ceo_briefing

        # Notification widget (hidden by default)
        self.notification_widget = Static("", classes="notification")

        yield Footer()

    def on_mount(self) -> None:
        """Handle app mount event."""
        logger.info("Shop Monitor dashboard mounted")

        # Initialize services
        try:
            self.vault_parser = VaultParser()
            self.metrics_calculator = MetricsCalculator(self.config.vault_path)
            self.file_manager = FileManager(self.config.vault_path)
            self.vault_watcher = VaultWatcher(self.config.vault_path, self.vault_parser)

            # Start vault watcher
            self.vault_watcher.start()

            # Initial metrics update
            self.update_metrics(self.current_date)

            # Start background workers
            self.start_vault_monitor()

            logger.info("Shop Monitor initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Shop Monitor: {e}")
            self.show_error(f"Initialization failed: {e}")

    def start_vault_monitor(self):
        """Start background workers to monitor vault changes."""
        self.set_interval(1.0, self.check_vault_events)  # Check every second

    def check_vault_events(self):
        """Check for vault file system events and update UI."""
        if not self.vault_watcher or not self.vault_watcher.is_running:
            return

        # Process any pending events
        if self.vault_watcher.has_events():
            event = self.vault_watcher.get_event(timeout=0)
            if event:
                logger.debug(f"Processing vault event: {event['type']} - {event['path'].name}")

                # Update metrics
                self.update_metrics(self.current_date)

    def update_metrics(self, target_date: date = None):
        """Calculate and update dashboard metrics for a specific date.

        Args:
            target_date: Date to calculate metrics for (defaults to current_date)
        """
        if target_date is None:
            target_date = self.current_date

        try:
            # Calculate metrics for the target date
            metrics = self.metrics_calculator.calculate_metrics(target_date)
            self.current_metrics = metrics

            # Update all metric tiles
            self.tiles["orders"].set_value(metrics.total_orders)
            self.tiles["sales"].set_value(metrics.total_revenue)
            self.tiles["inquiries"].set_value(metrics.inquiries_count)
            self.tiles["refunds"].set_value(metrics.refunds_count)
            self.tiles["support"].set_value(metrics.support_count)

            # Update pending approvals list
            self.update_pending_list(metrics.pending_list)

            logger.debug(f"Metrics updated for {target_date}: {metrics.total_orders} orders, "
                        f"${metrics.total_revenue:.2f} revenue, {metrics.pending_count} pending")

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            self.show_error(f"Failed to update metrics: {e}")

    def on_date_picker_date_changed(self, message: DatePicker.DateChanged) -> None:
        """Handle date change from date picker.

        Args:
            message: DateChanged message with new date
        """
        logger.info(f"Date changed to: {message.new_date}")
        self.current_date = message.new_date

        # Update metrics for new date
        self.update_metrics(message.new_date)

        # Update CEO briefing for new date
        if self.ceo_briefing:
            self.ceo_briefing.set_date(message.new_date)

    def update_pending_list(self, pending_items: List[OrderItem]):
        """Update the pending approvals list.

        Args:
            pending_items: List of OrderItem objects for pending approvals
        """
        # Get the pending list container
        pending_container = self.query_one("#pending-list", Container)

        # Clear existing items
        pending_container.remove_children()

        # Add pending items
        for item in pending_items:
            # Format: Order # | Customer | Amount
            item_text = f"[bold #FFD700]{item.order_number}[/bold #FFD700] | {item.customer_name} | [bold #98FB98]${item.amount:.2f}[/bold #98FB98]"
            item_widget = Static(item_text, classes="pending-item")
            item_widget.item_data = item  # Store reference to the item
            pending_container.mount(item_widget)

        logger.debug(f"Updated pending list with {len(pending_items)} items")

    def on_click(self, event: Click) -> None:
        """Handle clicks on widgets (pending items).

        Args:
            event: Click event
        """
        # Check if clicked widget is a pending item
        if hasattr(event.widget, "classes") and "pending-item" in event.widget.classes:
            if hasattr(event.widget, "item_data"):
                item = event.widget.item_data
                logger.info(f"Pending item clicked: {item.order_number}")
                # Show detail modal with approve/reject options
                self.push_screen(DetailModal(item, show_actions=True))

    def on_metric_tile_tile_clicked(self, message: MetricTile.TileClicked) -> None:
        """Handle metric tile click.

        Args:
            message: TileClicked message with metric type and value
        """
        logger.info(f"Metric tile clicked: {message.metric_type}")

        if not self.current_metrics:
            return

        # Get the appropriate list based on metric type
        items = []
        title = ""

        if message.metric_type == "orders":
            items = self.current_metrics.orders_list
            title = f"Orders - {self.current_date}"
        elif message.metric_type == "sales":
            items = self.current_metrics.orders_list
            title = f"Sales - {self.current_date}"
        elif message.metric_type == "inquiries":
            items = self.current_metrics.inquiries_list
            title = f"Inquiries - {self.current_date}"
        elif message.metric_type == "refunds":
            items = self.current_metrics.refunds_list
            title = f"Refund Requests - {self.current_date}"
        elif message.metric_type == "support":
            items = self.current_metrics.support_list
            title = f"Support Requests - {self.current_date}"
        elif message.metric_type == "pending":
            items = self.current_metrics.pending_list
            title = f"Pending Approvals"

        # Show list modal
        self.push_screen(ListModal(title, items))

    def on_list_modal_item_selected(self, message: ListModal.ItemSelected) -> None:
        """Handle item selection from list modal.

        Args:
            message: ItemSelected message with selected item
        """
        logger.info(f"Item selected: {message.item.order_number}")

        # Show detail modal without approve/reject actions
        # (pending items are handled separately in the right column)
        self.push_screen(DetailModal(message.item, show_actions=False))

    def on_detail_modal_approve(self, message: DetailModal.Approve) -> None:
        """Handle item approval from detail modal.

        Args:
            message: Approve message with item
        """
        logger.info(f"Approving item: {message.item.order_number}")

        # Move file to Approved folder
        success, error = self.file_manager.approve_task(message.item.file_path)

        if success:
            self.show_success(f"Approved: {message.item.order_number}")
            # Update metrics immediately to refresh pending list
            self.update_metrics(self.current_date)
        else:
            self.show_error(f"Failed to approve: {error}")

    def on_detail_modal_reject(self, message: DetailModal.Reject) -> None:
        """Handle item rejection from detail modal.

        Args:
            message: Reject message with item
        """
        logger.info(f"Rejecting item: {message.item.order_number}")

        # Move file to Rejected folder
        success, error = self.file_manager.reject_task(message.item.file_path)

        if success:
            self.show_success(f"Rejected: {message.item.order_number}")
            # Update metrics immediately to refresh pending list
            self.update_metrics(self.current_date)
        else:
            self.show_error(f"Failed to reject: {error}")

    def on_ceo_briefing_briefing_clicked(self, message: CEOBriefing.BriefingClicked) -> None:
        """Handle CEO briefing click.

        Args:
            message: BriefingClicked message with briefing content
        """
        logger.info("CEO briefing clicked")

        # Create a dummy OrderItem for displaying briefing in detail modal
        from .models.order_item import OrderItem
        briefing_item = OrderItem(
            order_number="CEO Briefing",
            customer_name="Executive Summary",
            amount=0.0,
            item_type="Report",
            status="Available",
            timestamp=datetime.now(),
            file_path=Path(""),
            full_content=message.briefing_content
        )

        # Show in detail modal (no actions)
        self.push_screen(DetailModal(briefing_item, show_actions=False))

    def show_error(self, message: str):
        """Display error notification.

        Args:
            message: Error message to display
        """
        logger.error(f"Error notification: {message}")
        # For now, just log (notifications can be enhanced later)

    def show_success(self, message: str):
        """Display success notification.

        Args:
            message: Success message to display
        """
        logger.info(f"Success notification: {message}")
        # For now, just log (notifications can be enhanced later)

    def on_unmount(self) -> None:
        """Handle app unmount event."""
        logger.info("Shop Monitor dashboard unmounting")

        # Stop vault watcher
        if self.vault_watcher:
            self.vault_watcher.stop()

    def action_quit(self) -> None:
        """Handle quit action (q key)."""
        logger.info("Quit action triggered")

        # Clean up
        if self.vault_watcher:
            self.vault_watcher.stop()

        self.exit()


def run_app():
    """Run the Shop Monitor application.

    This is the main entry point for the application.
    """
    try:
        app = ShopMonitorApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to run application: {e}")
        raise
