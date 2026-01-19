"""Unit tests for VaultParser service."""

import pytest
from pathlib import Path
import tempfile
import os

from src.services.vault_parser import VaultParser


def test_parse_valid_file():
    """Test parsing a valid markdown file with frontmatter."""
    parser = VaultParser()
    
    # Create temporary file with valid frontmatter
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""---
type: Support
channel: Gmail
status: Pending
---

Test content here
""")
        temp_path = Path(f.name)
    
    try:
        result = parser.parse_file(temp_path)
        assert result is not None
        
        frontmatter, content = result
        assert frontmatter['type'] == 'Support'
        assert frontmatter['channel'] == 'Gmail'
        assert frontmatter['status'] == 'Pending'
        assert 'Test content' in content
    finally:
        os.unlink(temp_path)


def test_parse_file_not_found():
    """Test parsing a non-existent file."""
    parser = VaultParser()
    
    result = parser.parse_file(Path('/nonexistent/file.md'))
    assert result is None


def test_parse_malformed_frontmatter():
    """Test parsing a file with malformed YAML frontmatter."""
    parser = VaultParser()
    
    # Create temporary file with malformed frontmatter
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""---
type: [unclosed
channel: Gmail
---

Content
""")
        temp_path = Path(f.name)
    
    try:
        result = parser.parse_file(temp_path)
        # Should handle gracefully and return None or empty frontmatter
        # (python-frontmatter is forgiving)
        assert result is not None  # frontmatter library handles this gracefully
    finally:
        os.unlink(temp_path)


def test_parse_file_no_frontmatter():
    """Test parsing a file without frontmatter."""
    parser = VaultParser()
    
    # Create temporary file without frontmatter
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Just regular markdown content")
        temp_path = Path(f.name)
    
    try:
        result = parser.parse_file(temp_path)
        assert result is not None
        
        frontmatter, content = result
        assert len(frontmatter) == 0  # Empty frontmatter
        assert 'regular markdown' in content
    finally:
        os.unlink(temp_path)


def test_validate_frontmatter():
    """Test frontmatter validation."""
    parser = VaultParser()
    
    metadata = {'type': 'Support', 'channel': 'Gmail', 'status': 'Pending'}
    
    # Valid case
    assert parser.validate_frontmatter(metadata, ['type', 'channel'])
    
    # Missing field
    assert not parser.validate_frontmatter(metadata, ['type', 'missing_field'])
    
    # Empty required fields
    assert parser.validate_frontmatter(metadata, [])


def test_extract_field():
    """Test safe field extraction."""
    parser = VaultParser()
    
    metadata = {'type': 'Support', 'count': 42}
    
    # Existing field
    assert parser.extract_field(metadata, 'type') == 'Support'
    assert parser.extract_field(metadata, 'count') == 42
    
    # Missing field with default
    assert parser.extract_field(metadata, 'missing', 'default') == 'default'
    assert parser.extract_field(metadata, 'missing', 0) == 0
    
    # Missing field without default
    assert parser.extract_field(metadata, 'missing') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
