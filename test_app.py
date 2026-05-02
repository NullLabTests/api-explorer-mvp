import pytest
import os
from app import parse_readme

README_PATH = os.getenv('README_PATH', 'data/README.md')

def test_parse_readme():
    """Test basic parsing of README."""
    result = parse_readme(README_PATH)
    assert len(result) > 0

    categories = [c['category'] for c in result]
    assert "Animals" in categories

    animal_apis = next(c['apis'] for c in result if c['category'] == "Animals")
    assert len(animal_apis) > 0
    assert any(api['name'] == 'Cat Facts' for api in animal_apis)
    assert any(api['https'] is True for api in animal_apis)

def test_parse_full():
    """Test full parsing using standard path."""
    result = parse_readme(README_PATH)
    assert any(d['category'] == 'Animals' for d in result)

def test_empty_file(tmp_path):
    """Test parsing an empty file."""
    empty_path = tmp_path / "empty.md"
    empty_path.write_text("")
    result = parse_readme(empty_path)
    assert result == []

def test_no_tables(tmp_path):
    """Test parsing a file with no tables."""
    no_table_path = tmp_path / "no_table.md"
    no_table_path.write_text("### Some Category\nSome text without table.")
    result = parse_readme(no_table_path)
    assert result == []

def test_extra_cells(tmp_path):
    """Test parsing a table row with extra cells."""
    md = """
### Test Category

| Name | Description |
|------|-------------|
| API1 | Desc1 |
| API2 | Desc2 | Extra | 
    """
    path = tmp_path / "extra.md"
    path.write_text(md.strip())
    result = parse_readme(path)
    assert len(result) == 1
    assert result[0]['category'] == 'Test Category'
    assert len(result[0]['apis']) == 2
    assert result[0]['apis'][1]['name'] == 'API2'
    assert result[0]['apis'][1]['description'] == 'Desc2'  # Extra ignored

def test_fewer_cells(tmp_path):
    """Test parsing a table row with fewer cells."""
    md = """
### Test Category

| Name | Description |
|------|-------------|
| API1 | Desc1 |
| API2 | 
    """
    path = tmp_path / "fewer.md"
    path.write_text(md.strip())
    result = parse_readme(path)
    assert len(result) == 1
    assert len(result[0]['apis']) == 2
    assert result[0]['apis'][1]['name'] == 'API2'
    assert result[0]['apis'][1]['description'] == ''  # Padded with empty

def test_file_not_found():
    """Test parsing a non-existent file."""
    with pytest.raises(FileNotFoundError):
        parse_readme("nonexistent.md")

def test_invalid_markdown(tmp_path):
    """Test parsing invalid markdown that doesn't form a table."""
    invalid_md = """
### Category

| Name 
This is invalid
    """
    invalid_path = tmp_path / "invalid.md"
    invalid_path.write_text(invalid_md.strip())
    result = parse_readme(invalid_path)
    assert result == []  # No valid table
