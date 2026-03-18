"""DatePicker widget for selecting dates."""

import logging
from datetime import date, timedelta
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Horizontal
from textual.message import Message

logger = logging.getLogger(__name__)


class DatePicker(Static):
    """Date picker widget with prev/next navigation.

    Displays current date with buttons to navigate to previous or next day.
    Emits DateChanged message when date is updated.
    """

    DEFAULT_CSS = """
    DatePicker {
        height: 3;
        border: solid #96DED1;
        padding: 0 1;
        background: #161616;
    }

    DatePicker Horizontal {
        height: 100%;
        align: center middle;
    }

    DatePicker Button {
        min-width: 8;
        margin: 0 1;
        background: #161616;
        color: #96DED1;
        border: solid #96DED1;
    }

    DatePicker Button:hover {
        background: #96DED11A;
        color: #96DED1;
        border: solid #96DED1;
    }

    DatePicker #date-display {
        min-width: 30;
        text-align: center;
        color: #96DED1;
        text-style: bold;
        content-align: center middle;
    }
    """

    class DateChanged(Message):
        """Message emitted when date changes."""

        def __init__(self, new_date: date):
            """Initialize DateChanged message.

            Args:
                new_date: The newly selected date
            """
            super().__init__()
            self.new_date = new_date

    def __init__(self, initial_date: date = None):
        """Initialize the date picker.

        Args:
            initial_date: Starting date (defaults to today)
        """
        super().__init__()
        self._current_date = initial_date or date.today()

    def compose(self) -> ComposeResult:
        """Compose the date picker layout."""
        with Horizontal():
            yield Button("◀ Prev", id="btn-prev")
            yield Static(self._format_date(), id="date-display")
            yield Button("Next ▶", id="btn-next")

    def _format_date(self) -> str:
        """Format the current date for display.

        Returns:
            Formatted date string
        """
        return f"📅 {self._current_date.strftime('%Y-%m-%d (%A)')}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button press event
        """
        if event.button.id == "btn-prev":
            self._change_date(-1)
        elif event.button.id == "btn-next":
            self._change_date(1)

    def _change_date(self, days: int) -> None:
        """Change the selected date.

        Args:
            days: Number of days to add (negative for previous days)
        """
        new_date = self._current_date + timedelta(days=days)
        self._current_date = new_date

        # Update display
        date_display = self.query_one("#date-display", Static)
        date_display.update(self._format_date())

        # Emit message
        self.post_message(self.DateChanged(new_date))
        logger.info(f"Date changed to: {new_date}")

    @property
    def current_date(self) -> date:
        """Get the currently selected date.

        Returns:
            Current date
        """
        return self._current_date

    def set_date(self, new_date: date) -> None:
        """Set the date programmatically.

        Args:
            new_date: Date to set
        """
        self._current_date = new_date

        # Update display
        date_display = self.query_one("#date-display", Static)
        date_display.update(self._format_date())

        logger.info(f"Date set to: {new_date}")
