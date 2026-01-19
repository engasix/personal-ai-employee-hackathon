"""Configuration loading and validation for Shop Monitor."""

import logging
import os
from pathlib import Path
from typing import Optional


# Logging configuration
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup Python logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )


class Config:
    """Configuration class for Shop Monitor.

    Loads configuration from environment variables with validation.
    """

    def __init__(self):
        """Initialize configuration from environment variables."""
        self._vault_path: Optional[Path] = None
        self._log_level: str = "INFO"
        self._log_file: Optional[str] = None

        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables."""
        # Load .env file if present
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            self._load_env_file(env_file)

        # Vault path (required)
        vault_path_str = os.getenv("VAULT_PATH")
        if vault_path_str:
            self._vault_path = Path(vault_path_str).resolve()

        # Logging configuration
        self._log_level = os.getenv("LOG_LEVEL", "INFO")
        self._log_file = os.getenv("LOG_FILE")

    def _load_env_file(self, env_file: Path):
        """Load environment variables from .env file.

        Args:
            env_file: Path to .env file
        """
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Don't override existing environment variables
                        if key not in os.environ:
                            os.environ[key] = value
        except Exception as e:
            logging.warning(f"Failed to load .env file: {e}")

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Vault path is required
        if not self._vault_path:
            return False, "VAULT_PATH environment variable is required"

        # Check if vault path exists
        if not self._vault_path.exists():
            return False, f"Vault path does not exist: {self._vault_path}"

        # Check if vault path is a directory
        if not self._vault_path.is_dir():
            return False, f"Vault path is not a directory: {self._vault_path}"

        return True, None

    @property
    def vault_path(self) -> Optional[Path]:
        """Get the vault path."""
        return self._vault_path

    @property
    def log_level(self) -> str:
        """Get the log level."""
        return self._log_level

    @property
    def log_file(self) -> Optional[str]:
        """Get the log file path."""
        return self._log_file


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance.

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def load_config() -> Config:
    """Load and validate configuration.

    Returns:
        Config instance

    Raises:
        ValueError: If configuration is invalid
    """
    config = get_config()
    is_valid, error_message = config.validate()

    if not is_valid:
        raise ValueError(f"Configuration error: {error_message}")

    # Setup logging
    setup_logging(config.log_level, config.log_file)

    return config
