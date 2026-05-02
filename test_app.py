import pytest
import os
from app import parse_readme

README_PATH = os.getenv('README_PATH', 'data/README.md')

def test_parse_readme():
    result = parse_readme(README_PATH)
    assert len(result) > 0

    categories = [c['category'] for c in result]
    assert "Animals" in categories

    animal_apis = next(c['apis'] for c in result if c['category'] == "Animals")
    assert len(animal_apis) > 0
    assert any(api['name'] == 'Cat Facts' for api in animal_apis)  # Check for a specific API
    assert any(api['https'] is True for api in animal_apis)  # Check data types
