import pytest
import os
from app import parse_readme, get_categories, search_apis, get_apis_for_category

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

# Additional tests for app logic

def test_get_categories():
    """Test extracting categories from data."""
    data = [{'category': 'A', 'apis': []}, {'category': 'B', 'apis': []}]
    assert get_categories(data) == ['A', 'B']
    assert get_categories([]) == []

def test_search_apis():
    """Test searching APIs by query."""
    data = [{'category': 'A', 'apis': [{'name': 'Test API', 'description': 'A test description'}]}]
    results = search_apis(data, 'test')
    assert len(results) == 1
    assert results[0]['name'] == 'Test API'

    results = search_apis(data, 'foo')
    assert len(results) == 0

def test_get_apis_for_category():
    """Test getting APIs for a specific category."""
    data = [{'category': 'A', 'apis': [{'name': 'API1'}, {'name': 'API2'}]}]
    assert len(get_apis_for_category(data, 'A')) == 2
    assert get_apis_for_category(data, 'B') == []

from unittest.mock import patch, Mock
import requests
from app import test_api

# Tests for test_api function
def test_test_api_get_success():
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.text = '{"key": "value"}'
        mock_request.return_value = mock_response
        response = test_api("GET", "http://example.com", '{"param": "val"}', "", "None", "", "", "")
        assert response.json() == {"key": "value"}
        mock_request.assert_called_with("GET", "http://example.com", params={"param": "val"}, json=None, headers={})

def test_test_api_post_with_body():
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"result": "ok"}
        mock_request.return_value = mock_response
        response = test_api("POST", "http://example.com", "", '{"data": "test"}', "None", "", "", "")
        assert response.json() == {"result": "ok"}
        mock_request.assert_called_with("POST", "http://example.com", params={}, json={"data": "test"}, headers={})

def test_test_api_with_auth_header():
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        test_api("GET", "http://example.com", "", "", "API Key", "secret", "Authorization", "Header")
        mock_request.assert_called_with("GET", "http://example.com", params={}, json=None, headers={"Authorization": "secret"})

def test_test_api_with_auth_query():
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        test_api("GET", "http://example.com", "", "", "API Key", "secret", "api_key", "Query Param")
        mock_request.assert_called_with("GET", "http://example.com", params={"api_key": "secret"}, json=None, headers={})

def test_test_api_invalid_params():
    with pytest.raises(ValueError, match="Invalid JSON in query params"):
        test_api("GET", "http://example.com", "invalid json", "", "None", "", "", "")

def test_test_api_invalid_body():
    with pytest.raises(ValueError, match="Invalid JSON in request body"):
        test_api("POST", "http://example.com", "", "invalid json", "None", "", "", "")

def test_test_api_request_exception():
    with patch('requests.request') as mock_request:
        mock_request.side_effect = requests.RequestException("Connection error")
        with pytest.raises(requests.RequestException):
            test_api("GET", "http://example.com", "", "", "None", "", "", "")
