"""
Tests for utils module
"""
import os
import tempfile
import json
import pytest
from src.utils.helpers import (
    load_json_file, 
    save_json_file, 
    sanitize_filename,
    create_id,
    merge_dicts
)

class TestHelpers:
    """Test helper utility functions."""
    
    def test_load_json_file_success(self):
        """Test loading a valid JSON file."""
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value"}, f)
            temp_path = f.name
            
        try:
            # Load the file
            result = load_json_file(temp_path)
            assert result == {"key": "value"}
        finally:
            # Clean up
            os.unlink(temp_path)
            
    def test_load_json_file_nonexistent(self):
        """Test loading a non-existent JSON file."""
        result = load_json_file("/path/does/not/exist.json", default_value={"default": True})
        assert result == {"default": True}
        
    def test_save_json_file(self):
        """Test saving data to a JSON file."""
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
            
        try:
            # Save data to the file
            data = {"key": "value", "nested": {"item": 123}}
            success = save_json_file(temp_path, data)
            assert success is True
            
            # Verify the file was created with the correct content
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
                assert saved_data == data
        finally:
            # Clean up
            os.unlink(temp_path)
            
    def test_sanitize_filename(self):
        """Test sanitizing filenames."""
        # Test with invalid characters
        assert sanitize_filename('file<with>invalid:chars?.txt') == 'file_with_invalid_chars_.txt'
        
        # Test empty or just dots
        assert sanitize_filename('') == 'unnamed_file'
        assert sanitize_filename('.') == 'unnamed_file'
        assert sanitize_filename('..') == 'unnamed_file'
        
        # Test valid filename
        assert sanitize_filename('valid_filename.txt') == 'valid_filename.txt'
        
    def test_create_id(self):
        """Test ID creation."""
        # Test basic ID creation
        id1 = create_id()
        assert isinstance(id1, str)
        assert len(id1) > 10  # Basic length check
        
        # Test with prefix
        id2 = create_id("test")
        assert id2.startswith("test_")
        
        # Test uniqueness
        id3 = create_id()
        assert id1 != id3
        
    def test_merge_dicts(self):
        """Test dictionary merging."""
        # Test basic merge
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        result = merge_dicts(dict1, dict2)
        assert result == {"a": 1, "b": 2, "c": 3, "d": 4}
        
        # Test merge with overwrite
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = merge_dicts(dict1, dict2, overwrite=True)
        assert result == {"a": 1, "b": 3, "c": 4}
        
        # Test merge without overwrite
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = merge_dicts(dict1, dict2, overwrite=False)
        assert result == {"a": 1, "b": 2, "c": 4}
        
        # Test nested merge
        dict1 = {"a": 1, "nested": {"x": 10, "y": 20}}
        dict2 = {"b": 2, "nested": {"y": 30, "z": 40}}
        result = merge_dicts(dict1, dict2)
        assert result == {"a": 1, "b": 2, "nested": {"x": 10, "y": 30, "z": 40}}
