"""FileManager service for file operations in the vault."""

import logging
import shutil
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class FileManager:
    """Service for managing file operations in the vault.

    Handles file moves with path validation and error handling.
    """

    def __init__(self, vault_path: Path):
        """Initialize the file manager.

        Args:
            vault_path: Path to the vault directory
        """
        self.vault_path = vault_path

    def move_file(self, source: Path, destination_folder: str) -> tuple[bool, Optional[str]]:
        """Move a file to a destination folder within the vault.

        Args:
            source: Source file path
            destination_folder: Name of destination folder (e.g., 'Approved', 'Rejected')

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate source file exists
            if not source.exists():
                error_msg = f"Source file not found: {source.name}"
                logger.error(error_msg)
                return False, error_msg

            # Validate source is within vault
            if not self._is_path_in_vault(source):
                error_msg = f"Source file not in vault: {source}"
                logger.error(error_msg)
                return False, error_msg

            # Build destination path
            dest_folder = self.vault_path / destination_folder
            dest_path = dest_folder / source.name

            # Create destination folder if it doesn't exist
            dest_folder.mkdir(parents=True, exist_ok=True)

            # Validate destination is within vault
            if not self._is_path_in_vault(dest_path):
                error_msg = f"Destination path not in vault: {dest_path}"
                logger.error(error_msg)
                return False, error_msg

            # Check if destination file already exists
            if dest_path.exists():
                error_msg = f"File already exists in {destination_folder}: {source.name}"
                logger.warning(error_msg)
                return False, error_msg

            # Move the file
            shutil.move(str(source), str(dest_path))

            logger.info(f"Moved file: {source.name} -> {destination_folder}/")
            return True, None

        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            logger.error(error_msg)
            return False, error_msg

        except OSError as e:
            error_msg = f"File system error: {e}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error moving file: {e}"
            logger.exception(error_msg)
            return False, error_msg

    def approve_task(self, task_file_path: Path) -> tuple[bool, Optional[str]]:
        """Approve a task by moving it to the Approved folder.

        Args:
            task_file_path: Path to the task file

        Returns:
            Tuple of (success, error_message)
        """
        logger.info(f"Approving task: {task_file_path.name}")
        return self.move_file(task_file_path, "Approved")

    def reject_task(self, task_file_path: Path) -> tuple[bool, Optional[str]]:
        """Reject a task by moving it to the Rejected folder.

        Args:
            task_file_path: Path to the task file

        Returns:
            Tuple of (success, error_message)
        """
        logger.info(f"Rejecting task: {task_file_path.name}")
        return self.move_file(task_file_path, "Rejected")

    def _is_path_in_vault(self, path: Path) -> bool:
        """Validate that a path is within the vault directory.

        Args:
            path: Path to validate

        Returns:
            True if path is within vault
        """
        try:
            # Resolve to absolute paths
            path_resolved = path.resolve()
            vault_resolved = self.vault_path.resolve()

            # Check if path starts with vault path
            return str(path_resolved).startswith(str(vault_resolved))

        except Exception as e:
            logger.error(f"Error validating path: {e}")
            return False

    def delete_file(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Delete a file from the vault (with safety checks).

        Args:
            file_path: Path to the file to delete

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate file exists
            if not file_path.exists():
                error_msg = f"File not found: {file_path.name}"
                logger.error(error_msg)
                return False, error_msg

            # Validate file is within vault
            if not self._is_path_in_vault(file_path):
                error_msg = f"File not in vault: {file_path}"
                logger.error(error_msg)
                return False, error_msg

            # Delete the file
            file_path.unlink()

            logger.info(f"Deleted file: {file_path.name}")
            return True, None

        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Error deleting file: {e}"
            logger.exception(error_msg)
            return False, error_msg
