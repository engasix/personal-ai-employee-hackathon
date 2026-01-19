"""Main entry point for Shop Monitor."""

import argparse
import logging
import sys
from pathlib import Path

from .config import load_config, setup_logging
from .app import run_app


logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Shop Monitor - Real-Time Terminal Dashboard for FTE Shop AI Employee"
    )

    parser.add_argument(
        "--vault-path",
        type=Path,
        help="Path to the AI Employee Vault directory (overrides VAULT_PATH env var)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (optional)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Shop Monitor v0.1.0"
    )

    return parser.parse_args()


def main():
    """Main entry point for Shop Monitor.

    Parses arguments, loads configuration, and launches the dashboard.
    """
    # Parse command line arguments
    args = parse_arguments()

    # Setup basic logging first
    setup_logging(args.log_level, args.log_file)

    logger.info("Starting Shop Monitor...")

    try:
        # Override VAULT_PATH from command line if provided
        if args.vault_path:
            import os
            os.environ["VAULT_PATH"] = str(args.vault_path.resolve())

        # Load and validate configuration
        config = load_config()

        logger.info(f"Configuration loaded successfully")
        logger.info(f"Vault path: {config.vault_path}")

        # Run the Textual app
        run_app()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nError: {e}", file=sys.stderr)
        print("\nPlease ensure:", file=sys.stderr)
        print("1. VAULT_PATH environment variable is set in .env file", file=sys.stderr)
        print("2. The vault path exists and is accessible", file=sys.stderr)
        print("3. You have read permissions on the vault directory", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Shop Monitor interrupted by user")
        print("\nShop Monitor stopped by user")
        sys.exit(0)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
