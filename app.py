import re

import os

def parse_readme(file_path):
    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r') as f:
        content = f.read()

    # Regex to find category sections
    pattern = r'###\s*(.*?)\n\s*API\s*\|\s*Description\s*\|\s*Auth\s*\|\s*HTTPS\s*\|\s*CORS\s*\n\s*\|\s*(?::?-{3,}\|\s*){4}:?-{3,}\|\s*\n((?:\|\s*.*?\s*\|\s*\n)+)'

    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    result = []
    for cat, rows_block in matches:
        apis = []
        rows = rows_block.strip().split('\n')
        for row in rows:
            row = row.strip()
            if not row or row.startswith('**[') or row.startswith('|:-'):
                continue
            parts = [p.strip() for p in row[1:-1].split('|')]  # remove leading/trailing | and split
            if len(parts) == 5:
                name = parts[0]
                name_match = re.match(r'\[(.*?)\]\((.*?)\)', name)
                api_name = name_match.group(1) if name_match else name
                link = name_match.group(2) if name_match else ''
                desc = parts[1]
                auth = parts[2].replace('`', '') if parts[2] else 'No'
                https = parts[3] == 'Yes'
                cors = parts[4]
                apis.append({
                    "name": api_name,
                    "description": desc,
                    "auth": auth,
                    "https": https,
                    "cors": cors,
                    "link": link
                })
        if apis:  # only add if has apis
            result.append({"category": cat, "apis": apis})

    return result
