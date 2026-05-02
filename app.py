import markdown
import re

def parse_readme(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    # Simple regex to extract tables - expand later
    return [{"category": "Test", "apis": []}]
