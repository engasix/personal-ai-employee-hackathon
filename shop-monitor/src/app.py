"""Main Textual App class for Shop Monitor."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static

from .config import get_config
from .services.vault_watcher import VaultWatcher
from .services.metrics_calculator import MetricsCalculator
from .services.vault_parser import VaultParser
from .services.file_manager import FileManager
from .widgets.metrics_panel import MetricsPanel
from .widgets.status_bar import StatusBar
from .widgets.approval_panel import ApprovalPanel
from .widgets.task_modal import TaskModal
from .widgets.channel_panel import ChannelPanel
from .widgets.activity_stream import ActivityStream
from .widgets.classification_panel import ClassificationPanel
from .models.pending_task import PendingTask


logger = logging.getLogger(__name__)


class ShopMonitorApp(App):
    """Shop Monitor - Real-Time Terminal Dashboard.

    Main Textual application class for the Shop Monitor dashboard.
    Displays live metrics, channel activity, pending approvals, and activity stream.
    """

    CSS = """
    Screen {
        background: black;
    }

    Header {
        display: none;
    }

    Footer {
        background: #0a0a0a;
        color: cyan;
        height: 1;
    }

    Container {
        background: black;
    }

    .brand-header {
        height: 5;
        background: #003366;
        border: heavy cyan;
        padding: 1 2;
        text-align: center;
        color: cyan;
    }

    .brand-title {
        text-style: bold;
        color: cyan;
        text-align: center;
    }

    .brand-subtitle {
        color: green;
        text-align: center;
    }

    .panel {
        height: auto;
        border: heavy cyan;
        padding: 1 2;
        margin: 0 1 1 1;
        background: #0a0a0a;
        color: white;
    }

    .panel-title {
        text-style: bold;
        color: cyan;
        text-align: center;
        padding: 0 0 1 0;
    }

    .metrics-panel {
        height: auto;
        min-height: 10;
        border: heavy green;
    }

    .approval-panel {
        height: auto;
        min-height: 12;
    }

    .placeholder {
        color: $text-muted;
        text-align: center;
    }

    .metric-value {
        text-style: bold;
        color: green;
    }

    .error-notification {
        background: red;
        color: white;
        text-style: bold;
        padding: 1;
        border: solid yellow;
        margin: 1;
    }

    .success-notification {
        background: green;
        color: black;
        text-style: bold;
        padding: 1;
        border: solid cyan;
        margin: 1;
    }

    Static {
        color: white;
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

        # Initialize widgets (will be set in compose)
        self.metrics_panel: MetricsPanel = None
        self.status_bar: StatusBar = None
        self.approval_panel: ApprovalPanel = None
        self.channel_panel: ChannelPanel = None
        self.activity_stream: ActivityStream = None
        self.classification_panel: ClassificationPanel = None
        self.notification_widget: Static = None

    def compose(self) -> ComposeResult:
        """Compose the application layout.

        Returns:
            Composed result with all widgets
        """
        # Brand header with FTE SHOP
        brand_header = Static(classes="brand-header")
        brand_header.update("""
[bold cyan]╔═══════════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]                                                                   [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [bold bright_cyan]███████╗████████╗███████╗    ███████╗██╗  ██╗ ██████╗ ██████╗[/bold bright_cyan]  [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [bold bright_cyan]██╔════╝╚══██╔══╝██╔════╝    ██╔════╝██║  ██║██╔═══██╗██╔══██╗[/bold bright_cyan] [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [bold bright_cyan]█████╗     ██║   █████╗      ███████╗███████║██║   ██║██████╔╝[/bold bright_cyan] [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [bold bright_cyan]██╔══╝     ██║   ██╔══╝      ╚════██║██╔══██║██║   ██║██╔═══╝[/bold bright_cyan]  [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [bold bright_cyan]██║        ██║   ███████╗    ███████║██║  ██║╚██████╔╝██║[/bold bright_cyan]      [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [bold bright_cyan]╚═╝        ╚═╝   ╚══════╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝[/bold bright_cyan]      [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]                                                                   [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]           [bold green]🤖 AI Employee Real-Time Monitoring Dashboard 📊[/bold green]          [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]                                                                   [bold cyan]║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════════════════════════════════╝[/bold cyan]
""")
        yield brand_header

        # Main content container
        with ScrollableContainer():
            # Metrics panel
            self.metrics_panel = MetricsPanel()
            yield self.metrics_panel

            # Notification area (initially hidden)
            self.notification_widget = Static("", id="notification")
            yield self.notification_widget

            # Approval panel
            self.approval_panel = ApprovalPanel()
            yield self.approval_panel

            # Channel activity panel
            self.channel_panel = ChannelPanel()
            yield self.channel_panel

            # Activity stream panel
            self.activity_stream = ActivityStream()
            yield self.activity_stream

            # Classification analytics panel
            self.classification_panel = ClassificationPanel()
            yield self.classification_panel

        # Status bar at bottom
        self.status_bar = StatusBar()
        yield self.status_bar

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

            # Update status bar
            self.status_bar.set_connected(True)
            self.status_bar.set_last_update(datetime.now())

            # Initial updates
            self.update_metrics()
            self.update_pending_tasks()

            # Start background workers
            self.start_vault_monitor()

            logger.info("Shop Monitor initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Shop Monitor: {e}")
            self.status_bar.set_connected(False)
            self.show_error(f"Initialization failed: {e}")

    def start_vault_monitor(self):
        """Start background workers to monitor vault changes."""
        self.set_interval(0.1, self.check_vault_events)  # Check every 100ms
        self.set_interval(5.0, self.check_connection)     # Check connection every 5s

    def check_vault_events(self):
        """Check for vault file system events and update UI."""
        if not self.vault_watcher or not self.vault_watcher.is_running:
            return

        # Process any pending events
        if self.vault_watcher.has_events():
            event = self.vault_watcher.get_event(timeout=0)
            if event:
                logger.debug(f"Processing vault event: {event['type']} - {event['path'].name}")

                # Add to activity stream
                if self.activity_stream and 'activity_event' in event:
                    self.activity_stream.add_event(event['activity_event'])

                # Check if event affects pending tasks
                if self._is_pending_approval_event(event):
                    self.update_pending_tasks()

                # Update metrics
                self.update_metrics()

                # Update status bar timestamp
                self.status_bar.set_last_update(datetime.now())

    def _is_pending_approval_event(self, event: dict) -> bool:
        """Check if event affects Pending_Approval folder.

        Args:
            event: Event dictionary

        Returns:
            True if event is in Pending_Approval folder
        """
        path = event['path']
        return 'Pending_Approval' in str(path) or \
               'Approved' in str(path) or \
               'Rejected' in str(path)

    def check_connection(self):
        """Check vault connection status."""
        if not self.vault_watcher:
            return

        is_connected = self.vault_watcher.check_connection()

        # Update status bar
        self.status_bar.set_connected(is_connected)

        # Try to reconnect if disconnected
        if not is_connected:
            logger.warning("Vault disconnected, attempting reconnection...")
            if self.vault_watcher.reconnect():
                logger.info("Vault reconnected successfully")
                self.status_bar.set_connected(True)
                self.update_metrics()
                self.update_pending_tasks()

    def update_metrics(self):
        """Calculate and update dashboard metrics."""
        try:
            # Calculate metrics
            metrics = self.metrics_calculator.calculate_metrics()

            # Update metrics panel
            if self.metrics_panel:
                self.metrics_panel.set_metrics(metrics)

            # Update channel panel
            if self.channel_panel:
                self.channel_panel.set_metrics(metrics)

            # Update classification panel
            if self.classification_panel:
                self.classification_panel.set_metrics(metrics)

            logger.debug(f"Metrics updated: {metrics.total_orders} orders, "
                        f"{metrics.pending_count} pending tasks")

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")

    def update_pending_tasks(self):
        """Load and update pending tasks list."""
        try:
            tasks = self.load_pending_tasks()

            # Update approval panel
            if self.approval_panel:
                self.approval_panel.set_tasks(tasks)

            logger.debug(f"Loaded {len(tasks)} pending tasks")

        except Exception as e:
            logger.error(f"Error updating pending tasks: {e}")

    def load_pending_tasks(self) -> List[PendingTask]:
        """Load pending tasks from Pending_Approval folder.

        Returns:
            List of PendingTask objects
        """
        tasks = []
        pending_dir = self.config.vault_path / "Pending_Approval"

        if not pending_dir.exists():
            logger.warning(f"Pending_Approval directory not found: {pending_dir}")
            return tasks

        # Scan for markdown files
        for file_path in pending_dir.glob("*.md"):
            result = self.vault_parser.parse_file(file_path)
            if not result:
                continue

            frontmatter, content = result

            # Create PendingTask
            task = PendingTask.from_file(file_path, frontmatter, content)
            tasks.append(task)

        # Sort by priority and creation time
        tasks.sort(key=lambda t: (t.priority != "high", t.creation_timestamp), reverse=True)

        return tasks

    def on_approval_panel_task_selected(self, message: ApprovalPanel.TaskSelected) -> None:
        """Handle task selection in approval panel.

        Args:
            message: Task selection message
        """
        logger.info(f"Task selected: {message.task.task_id}")

        # Open task modal
        self.push_screen(TaskModal(message.task))

    def on_task_modal_approve(self, message: TaskModal.Approve) -> None:
        """Handle task approval from modal.

        Args:
            message: Approve message
        """
        logger.info(f"Approving task: {message.task.task_id}")

        # Move file to Approved folder
        success, error = self.file_manager.approve_task(message.task.file_path)

        if success:
            self.show_success(f"Task {message.task.task_id} approved")
            # Update will happen automatically via vault watcher
        else:
            self.show_error(f"Failed to approve task: {error}")

    def on_task_modal_reject(self, message: TaskModal.Reject) -> None:
        """Handle task rejection from modal.

        Args:
            message: Reject message
        """
        logger.info(f"Rejecting task: {message.task.task_id}")

        # Move file to Rejected folder
        success, error = self.file_manager.reject_task(message.task.file_path)

        if success:
            self.show_success(f"Task {message.task.task_id} rejected")
            # Update will happen automatically via vault watcher
        else:
            self.show_error(f"Failed to reject task: {error}")

    def show_error(self, message: str):
        """Display error notification.

        Args:
            message: Error message to display
        """
        logger.error(f"Error notification: {message}")

        if self.notification_widget:
            self.notification_widget.update(f"[bold red]✗ Error:[/bold red] {message}")
            self.notification_widget.add_class("error-notification")
            self.notification_widget.remove_class("success-notification")

            # Clear notification after 5 seconds
            self.set_timer(5.0, self.clear_notification)

    def show_success(self, message: str):
        """Display success notification.

        Args:
            message: Success message to display
        """
        logger.info(f"Success notification: {message}")

        if self.notification_widget:
            self.notification_widget.update(f"[bold green]✓ Success:[/bold green] {message}")
            self.notification_widget.add_class("success-notification")
            self.notification_widget.remove_class("error-notification")

            # Clear notification after 3 seconds
            self.set_timer(3.0, self.clear_notification)

    def clear_notification(self):
        """Clear notification display."""
        if self.notification_widget:
            self.notification_widget.update("")
            self.notification_widget.remove_class("error-notification")
            self.notification_widget.remove_class("success-notification")

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
