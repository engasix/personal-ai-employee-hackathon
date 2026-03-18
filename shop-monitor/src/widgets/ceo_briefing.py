"""CEOBriefing widget for displaying weekly executive reports."""

import logging
from pathlib import Path
from datetime import date
from textual.widgets import Static, Markdown
from textual.containers import ScrollableContainer
from textual.events import Click
from textual.message import Message

logger = logging.getLogger(__name__)


class CEOBriefing(Static):
    """Widget for displaying CEO briefing reports.

    Loads and displays weekly CEO briefing markdown files if available.
    Clickable to expand and show full content.
    """

    DEFAULT_CSS = """
    CEOBriefing {
        height: auto;
        min-height: 5;
        border: heavy #96DED1;
        background: #161616;
        padding: 1;
        margin: 1;
    }

    CEOBriefing:hover {
        border: heavy #96DED1;
        background: #96DED11A;
    }

    CEOBriefing .briefing-title {
        text-align: center;
        text-style: bold;
        color: #96DED1;
        margin-bottom: 1;
    }

    CEOBriefing .briefing-available {
        text-align: center;
        color: #98FB98;
        text-style: bold;
    }

    CEOBriefing .briefing-unavailable {
        text-align: center;
        color: $text-muted;
    }

    CEOBriefing .briefing-click {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    class BriefingClicked(Message):
        """Message emitted when briefing is clicked."""

        def __init__(self, briefing_content: str):
            """Initialize BriefingClicked message.

            Args:
                briefing_content: Content of the briefing
            """
            super().__init__()
            self.briefing_content = briefing_content

    def __init__(self, vault_path: Path, target_date: date = None):
        """Initialize the CEO briefing widget.

        Args:
            vault_path: Path to the vault directory
            target_date: Date to load briefing for (defaults to today)
        """
        super().__init__()
        self.vault_path = vault_path
        self.target_date = target_date or date.today()
        self.briefing_content = None
        self.can_focus = True
        self.load_briefing()
        self.update_display()

    def load_briefing(self) -> bool:
        """Load the CEO briefing for the target date.

        Returns:
            True if briefing was found and loaded, False otherwise
        """
        # Construct filename: ceo-briefing-YYYY-MM-DD.md
        filename = f"ceo-briefing-{self.target_date.strftime('%Y-%m-%d')}.md"
        briefing_path = self.vault_path / filename

        if briefing_path.exists():
            try:
                with open(briefing_path, 'r', encoding='utf-8') as f:
                    self.briefing_content = f.read()
                logger.info(f"Loaded CEO briefing: {filename}")
                return True
            except Exception as e:
                logger.error(f"Error loading CEO briefing: {e}")
                self.briefing_content = None
                return False
        else:
            logger.debug(f"CEO briefing not found: {filename}")
            self.briefing_content = None
            return False

    def update_display(self):
        """Update the briefing display."""
        if self.briefing_content:
            content = f"""
[bold #96DED1]═══════════════════════════════════════════════════════[/bold #96DED1]
[bold #96DED1]              📊 WEEKLY CEO BRIEFING 📊                [/bold #96DED1]
[bold #96DED1]═══════════════════════════════════════════════════════[/bold #96DED1]

[bold #98FB98]✓ Weekly briefing available[/bold #98FB98]

[dim]Click to view full report...[/dim]
"""
        else:
            content = f"""
[bold #96DED1]═══════════════════════════════════════════════════════[/bold #96DED1]
[bold #96DED1]              📊 WEEKLY CEO BRIEFING 📊                [/bold #96DED1]
[bold #96DED1]═══════════════════════════════════════════════════════[/bold #96DED1]

[dim]No briefing available for {self.target_date.strftime('%Y-%m-%d')}[/dim]
"""
        self.update(content.strip())

    def set_date(self, new_date: date):
        """Update the target date and reload briefing.

        Args:
            new_date: New date to load briefing for
        """
        self.target_date = new_date
        self.load_briefing()
        self.update_display()

    def on_click(self, event: Click) -> None:
        """Handle click events.

        Args:
            event: Click event
        """
        if self.briefing_content:
            self.post_message(self.BriefingClicked(self.briefing_content))
            logger.info("CEO briefing clicked")
