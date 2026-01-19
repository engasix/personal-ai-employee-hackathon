# Shop Monitor - Real-Time Terminal Dashboard

Real-time terminal dashboard for monitoring FTE Shop AI Employee operations via Obsidian vault file watching.

## Features

- **Live Metrics Monitoring**: Real-time display of orders, revenue, response times, and pending tasks
- **Channel Activity Breakdown**: Monitor Website, Gmail, and WhatsApp message volumes
- **Message Classification Analytics**: View success rates for Refund, Support, and Inquiry requests
- **Pending Task Approval**: Approve or reject tasks directly from the terminal interface
- **Recent Activity Stream**: Scrolling feed of the last 20 AI actions
- **Keyboard Shortcuts**: Efficient navigation and control without mouse interaction

## Requirements

- Python 3.10 or higher
- Access to the AI Employee Vault directory
- Terminal with UTF-8 and ANSI color support

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd shop-monitor
```

2. Install dependencies using pip:
```bash
pip install -e .
```

Or with development dependencies:
```bash
pip install -e ".[dev]"
```

3. Configure the vault path:
```bash
cp .env.example .env
# Edit .env and set VAULT_PATH to your AI Employee Vault directory
```

## Usage

Launch the dashboard with a single command:

```bash
python -m src.monitor
```

Or using the entry point:

```bash
python src/monitor.py
```

### Keyboard Shortcuts

- `q` - Quit the application
- `ESC` - Close modal dialogs
- `Tab` - Navigate between interactive elements
- `Enter` - Open task detail modal (when task is focused)

## Configuration

Create a `.env` file in the project root with the following configuration:

```env
# Path to the AI Employee Vault directory (required)
VAULT_PATH=/path/to/AI_Employee_Vault

# Optional: Logging configuration
LOG_LEVEL=INFO
LOG_FILE=shop-monitor.log
```

## Architecture

The dashboard uses:
- **Textual**: Terminal UI framework for responsive layout and widgets
- **watchdog**: File system monitoring for real-time updates (<100ms latency)
- **python-frontmatter**: YAML frontmatter parsing for markdown files

## Project Structure

```
shop-monitor/
├── src/
│   ├── monitor.py           # Main entry point
│   ├── app.py               # Textual App main class
│   ├── config.py            # Configuration loading
│   ├── models/              # Entity models
│   ├── services/            # Business logic services
│   └── widgets/             # Textual UI widgets
├── tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── pyproject.toml           # Project configuration
└── .env                     # Environment configuration
```

## Development

### Running Tests

The project includes comprehensive unit and integration tests:

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/test_vault_parser.py
pytest tests/integration/test_vault_watcher.py

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run with verbose output
pytest -v
```

### Test Suites

- **Unit Tests** (`tests/unit/`):
  - `test_vault_parser.py` - Frontmatter parsing, malformed file handling
  - `test_file_manager.py` - Path validation, security, error handling
  - `test_metrics_calculator.py` - Aggregate calculations, edge cases

- **Integration Tests** (`tests/integration/`):
  - `test_vault_watcher.py` - File change detection, metadata extraction
  - `test_approval_workflow.py` - End-to-end approval/rejection flows

### Performance Requirements

- **UI Update Latency**: <100ms from file change to dashboard update
- **Initial Vault Scan**: <2s for typical vault sizes
- **Memory Footprint**: <100MB for bounded activity stream (20 items)

### Code Quality

- Path validation prevents directory traversal attacks
- All file operations stay within vault directory
- Graceful degradation when Dashboard.md is missing
- Comprehensive error handling with logging
- Content sanitization via Textual's built-in ANSI escaping

## Troubleshooting

### Dashboard shows "Disconnected"
- Verify the `VAULT_PATH` in your `.env` file is correct
- Check that the vault directory exists and is accessible
- Ensure you have read permissions on vault files

### Metrics not updating
- Check that the vault contains files with proper YAML frontmatter
- Verify that `Dashboard.md` exists in the vault root
- Check the log file for parsing errors

### File operations failing
- Ensure you have write permissions for the approval folders
- Check that files are not locked by another application
- Verify the vault structure matches expected format

## License

[License information here]
