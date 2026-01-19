"""VaultParser service for parsing markdown files with YAML frontmatter."""

import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import frontmatter


logger = logging.getLogger(__name__)


class VaultParser:
    """Service for parsing Obsidian vault markdown files.

    This service uses python-frontmatter to extract YAML frontmatter
    and markdown content from vault files.
    """

    @staticmethod
    def parse_file(file_path: Path) -> Optional[Tuple[Dict[str, Any], str]]:
        """Parse a markdown file and extract frontmatter and content.

        Args:
            file_path: Path to the markdown file

        Returns:
            Tuple of (frontmatter_dict, content_string) or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            # Extract frontmatter as dictionary
            metadata = dict(post.metadata)

            # Extract content
            content = post.content

            return metadata, content

        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return None
        except PermissionError:
            logger.warning(f"Permission denied reading file: {file_path}")
            return None
        except frontmatter.FrontmatterError as e:
            logger.warning(f"Frontmatter parsing error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}")
            return None

    @staticmethod
    def validate_frontmatter(metadata: Dict[str, Any], required_fields: list) -> bool:
        """Validate that frontmatter contains required fields.

        Args:
            metadata: Frontmatter dictionary
            required_fields: List of required field names

        Returns:
            True if all required fields are present, False otherwise
        """
        return all(field in metadata for field in required_fields)

    @staticmethod
    def extract_field(metadata: Dict[str, Any], field: str, default: Any = None) -> Any:
        """Safely extract a field from frontmatter with a default value.

        Args:
            metadata: Frontmatter dictionary
            field: Field name to extract
            default: Default value if field is missing

        Returns:
            Field value or default
        """
        return metadata.get(field, default)
