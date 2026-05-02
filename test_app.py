import pytest
from app import parse_readme

def test_parse_readme():
    result = parse_readme('data/README.md')
    assert len(result) > 0
